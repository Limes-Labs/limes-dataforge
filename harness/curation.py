from __future__ import annotations

import hashlib
import importlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA = ROOT / "data" / "public_smoke" / "documents.jsonl"
PUBLIC_HELDOUT = ROOT / "data" / "public_smoke" / "heldout.txt"
DEFAULT_CONFIG = ROOT / "configs" / "submission.json"
PUBLIC_BASELINE_NAME = "public_smoke_all_nonempty_dedup_short_to_long"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_documents(path: Path = PUBLIC_DATA) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            if "id" not in item or "text" not in item:
                raise ValueError(f"document line {line_number} must contain id and text")
            documents.append(item)
    return documents


def dataset_hash() -> str:
    digest = hashlib.sha256()
    for path in (PUBLIC_DATA, PUBLIC_HELDOUT):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def selection_hash(documents: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for document in documents:
        digest.update(str(document.get("id", "")).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(document.get("text", "")).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _module(name: str):
    return importlib.import_module(f"solution.{name}")


def _normalized_text(document: dict[str, Any]) -> str:
    return " ".join(str(document.get("text", "")).lower().split())


def apply_solution(documents: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    filter_mod = _module("filter")
    rank_mod = _module("rank_documents")
    dedup_mod = _module("dedup")
    curriculum_mod = _module("curriculum")

    kept = [doc for doc in documents if bool(filter_mod.keep_document(dict(doc), config))]
    ranked = sorted(
        kept,
        key=lambda doc: (-float(rank_mod.score_document(dict(doc), config)), str(doc["id"])),
    )
    deduped = list(dedup_mod.deduplicate_documents([dict(doc) for doc in ranked], config))
    ordered = list(curriculum_mod.order_documents([dict(doc) for doc in deduped], config))

    original_count = len(documents)
    kept_count = len(kept)
    final_count = len(ordered)
    return {
        "documents": ordered,
        "kept_ratio": kept_count / original_count if original_count else 0.0,
        "dedup_rate": (kept_count - final_count) / kept_count if kept_count else 0.0,
    }


def apply_public_baseline(documents: list[dict[str, Any]]) -> dict[str, Any]:
    kept = [dict(doc) for doc in documents if str(doc.get("text", "")).strip()]
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for document in kept:
        fingerprint = _normalized_text(document)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduped.append(document)
    ordered = sorted(deduped, key=lambda doc: (len(str(doc.get("text", ""))), str(doc.get("id", ""))))
    original_count = len(documents)
    kept_count = len(kept)
    final_count = len(ordered)
    return {
        "documents": ordered,
        "kept_ratio": kept_count / original_count if original_count else 0.0,
        "dedup_rate": (kept_count - final_count) / kept_count if kept_count else 0.0,
    }


def byte_unigram_bpb(train_text: str, heldout_text: str) -> float:
    if not train_text.strip():
        return 99.0
    train_bytes = train_text.encode("utf-8")
    heldout_bytes = heldout_text.encode("utf-8")
    counts = Counter(train_bytes)
    vocab = 256
    total = len(train_bytes) + vocab
    loss_bits = 0.0
    for byte in heldout_bytes:
        probability = (counts.get(byte, 0) + 1) / total
        loss_bits -= math.log2(probability)
    return loss_bits / max(1, len(heldout_bytes))


def public_score(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    import time

    started = time.perf_counter()
    documents = load_documents()
    config = load_json(config_path)
    applied = apply_solution(documents, config)
    baseline = apply_public_baseline(documents)
    selected_text = "\n".join(str(doc["text"]) for doc in applied["documents"])
    baseline_text = "\n".join(str(doc["text"]) for doc in baseline["documents"])
    heldout_text = PUBLIC_HELDOUT.read_text(encoding="utf-8")
    public_proxy_loss = byte_unigram_bpb(selected_text, heldout_text)
    baseline_public_proxy_loss = byte_unigram_bpb(baseline_text, heldout_text)
    score = {
        "public_proxy_loss": public_proxy_loss,
        "baseline_public_proxy_loss": baseline_public_proxy_loss,
        "public_proxy_delta": public_proxy_loss - baseline_public_proxy_loss,
        "public_proxy_improvement": baseline_public_proxy_loss - public_proxy_loss,
        "kept_ratio": applied["kept_ratio"],
        "dedup_rate": applied["dedup_rate"],
        "selected_document_count": len(applied["documents"]),
        "selected_byte_count": len(selected_text.encode("utf-8")),
        "selection_hash": selection_hash(applied["documents"]),
        "baseline_name": PUBLIC_BASELINE_NAME,
        "baseline_document_count": len(baseline["documents"]),
        "baseline_kept_ratio": baseline["kept_ratio"],
        "baseline_dedup_rate": baseline["dedup_rate"],
        "baseline_selection_hash": selection_hash(baseline["documents"]),
        "runtime_seconds": time.perf_counter() - started,
        "dataset_hash": dataset_hash(),
        "selected_document_ids": [doc["id"] for doc in applied["documents"]],
    }
    return score
