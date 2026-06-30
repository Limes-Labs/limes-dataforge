from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from harness.curation import (
    DEFAULT_CONFIG,
    PUBLIC_DATA,
    PUBLIC_HELDOUT,
    PUBLIC_STRESS_DATA,
    PUBLIC_STRESS_HELDOUT,
    apply_solution,
    dataset_hash,
    load_documents,
    load_json,
    selection_hash,
    stress_dataset_hash,
)


ROOT = Path(__file__).resolve().parents[1]
SOLUTION_FILES = [
    ROOT / "solution" / "filter.py",
    ROOT / "solution" / "rank_documents.py",
    ROOT / "solution" / "dedup.py",
    ROOT / "solution" / "curriculum.py",
]
FORBIDDEN_STATIC_PATTERNS = [
    "data/public_smoke",
    "documents.jsonl",
    "heldout.txt",
    "stress_heldout",
    "verifier_data",
    "hidden",
    "score.json",
    "PUBLIC_HELDOUT",
    "PUBLIC_DATA",
    "PUBLIC_STRESS",
]
MAX_HELDOUT_4GRAM_OVERLAP = 0.20


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[index:index + n]) for index in range(max(0, len(tokens) - n + 1))}


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _selected_payload(data_path: Path, heldout_path: Path, config: dict[str, Any]) -> dict[str, Any]:
    documents = load_documents(data_path)
    applied = apply_solution(documents, config)
    selected = applied["documents"]
    selected_text = "\n".join(str(document.get("text", "")) for document in selected)
    heldout_text = heldout_path.read_text(encoding="utf-8")
    return {
        "documents": documents,
        "selected": selected,
        "selected_text": selected_text,
        "heldout_text": heldout_text,
        "kept_ratio": applied["kept_ratio"],
        "dedup_rate": applied["dedup_rate"],
        "selection_hash": selection_hash(selected),
    }


def scan_forbidden_static_patterns(paths: list[Path] = SOLUTION_FILES) -> list[str]:
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_STATIC_PATTERNS:
            if pattern in text:
                errors.append(f"{_display_path(path)} contains forbidden public-boundary token {pattern!r}")
    return errors


def _audit_heldout_overlap(config: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    details: dict[str, Any] = {}
    for label, data_path, heldout_path in [
        ("public", PUBLIC_DATA, PUBLIC_HELDOUT),
        ("stress", PUBLIC_STRESS_DATA, PUBLIC_STRESS_HELDOUT),
    ]:
        payload = _selected_payload(data_path, heldout_path, config)
        selected_4grams = _ngrams(_tokens(payload["selected_text"]), 4)
        heldout_4grams = _ngrams(_tokens(payload["heldout_text"]), 4)
        overlap = selected_4grams.intersection(heldout_4grams)
        overlap_ratio = len(overlap) / max(1, len(heldout_4grams))
        exact_heldout_present = bool(payload["heldout_text"].strip()) and (
            payload["heldout_text"].strip() in payload["selected_text"]
        )
        details[f"{label}_heldout_4gram_overlap_ratio"] = overlap_ratio
        details[f"{label}_heldout_4gram_overlap_count"] = len(overlap)
        details[f"{label}_heldout_exact_substring"] = exact_heldout_present
        if overlap_ratio > MAX_HELDOUT_4GRAM_OVERLAP:
            errors.append(
                f"{label} selected text overlaps heldout 4-grams at {overlap_ratio:.3f}, "
                f"above {MAX_HELDOUT_4GRAM_OVERLAP:.3f}"
            )
        if exact_heldout_present:
            errors.append(f"{label} selected text contains the exact heldout text")
    details["max_allowed_heldout_4gram_overlap"] = MAX_HELDOUT_4GRAM_OVERLAP
    return {"ok": not errors, "errors": errors, "warnings": [], "details": details}


def _audit_selection_bounds(config: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    details: dict[str, Any] = {}
    for label, data_path, heldout_path in [
        ("public", PUBLIC_DATA, PUBLIC_HELDOUT),
        ("stress", PUBLIC_STRESS_DATA, PUBLIC_STRESS_HELDOUT),
    ]:
        payload = _selected_payload(data_path, heldout_path, config)
        selected = payload["selected"]
        selected_ids = [str(document.get("id", "")) for document in selected]
        details[f"{label}_input_document_count"] = len(payload["documents"])
        details[f"{label}_selected_document_count"] = len(selected)
        details[f"{label}_kept_ratio"] = payload["kept_ratio"]
        details[f"{label}_dedup_rate"] = payload["dedup_rate"]
        details[f"{label}_selection_hash"] = payload["selection_hash"]
        if not selected:
            errors.append(f"{label} selection is empty")
        if len(set(selected_ids)) != len(selected_ids):
            errors.append(f"{label} selection contains duplicate document ids")
        if len(selected) > len(payload["documents"]):
            errors.append(f"{label} selection is larger than the input document pool")
        if not 0.0 <= float(payload["kept_ratio"]) <= 1.0:
            errors.append(f"{label} kept_ratio is outside [0, 1]")
        if not 0.0 <= float(payload["dedup_rate"]) <= 1.0:
            errors.append(f"{label} dedup_rate is outside [0, 1]")
    return {"ok": not errors, "errors": errors, "warnings": [], "details": details}


def _audit_source_diversity(config: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    details: dict[str, Any] = {}
    for label, data_path, heldout_path in [
        ("public", PUBLIC_DATA, PUBLIC_HELDOUT),
        ("stress", PUBLIC_STRESS_DATA, PUBLIC_STRESS_HELDOUT),
    ]:
        payload = _selected_payload(data_path, heldout_path, config)
        sources = sorted({str(document.get("source", "")) for document in payload["selected"]})
        details[f"{label}_source_count"] = len(sources)
        details[f"{label}_sources"] = sources
        if len(sources) < 2:
            warnings.append(f"{label} selection uses fewer than two source labels; justify this in the result card")
    return {"ok": True, "errors": [], "warnings": warnings, "details": details}


def _audit_static_boundary(config: dict[str, Any]) -> dict[str, Any]:
    errors = scan_forbidden_static_patterns()
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": [],
        "details": {
            "scanned_files": [str(path.relative_to(ROOT)) for path in SOLUTION_FILES],
            "forbidden_patterns": FORBIDDEN_STATIC_PATTERNS,
        },
    }


def _run_audit(name: str, audit: Callable[[dict[str, Any]], dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    try:
        result = audit(config)
    except Exception as exc:  # pragma: no cover - exercised by CLI behavior.
        return {"name": name, "ok": False, "errors": [f"{type(exc).__name__}: {exc}"], "warnings": [], "details": {}}
    result["name"] = name
    return result


def run_public_audit(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = load_json(config_path)
    audits: list[tuple[str, Callable[[dict[str, Any]], dict[str, Any]]]] = [
        ("heldout_ngram_overlap", _audit_heldout_overlap),
        ("selection_bounds", _audit_selection_bounds),
        ("source_diversity_warning", _audit_source_diversity),
        ("solution_static_boundary", _audit_static_boundary),
    ]
    results = [_run_audit(name, audit, config) for name, audit in audits]
    return {
        "challenge": "limes-dataforge",
        "ok": all(result["ok"] for result in results),
        "audit_count": len(results),
        "dataset_hash": dataset_hash(),
        "stress_dataset_hash": stress_dataset_hash(),
        "audits": results,
    }


def dumps_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
