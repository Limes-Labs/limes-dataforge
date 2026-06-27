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


def _module(name: str):
    return importlib.import_module(f"solution.{name}")


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
    selected_text = "\n".join(str(doc["text"]) for doc in applied["documents"])
    heldout_text = PUBLIC_HELDOUT.read_text(encoding="utf-8")
    score = {
        "public_proxy_loss": byte_unigram_bpb(selected_text, heldout_text),
        "kept_ratio": applied["kept_ratio"],
        "dedup_rate": applied["dedup_rate"],
        "runtime_seconds": time.perf_counter() - started,
        "dataset_hash": dataset_hash(),
        "selected_document_ids": [doc["id"] for doc in applied["documents"]],
    }
    return score
