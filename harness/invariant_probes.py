from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

from harness.curation import DEFAULT_CONFIG, apply_solution, load_documents, load_json, selection_hash


ROOT = Path(__file__).resolve().parents[1]


def _normalized_text(document: dict[str, Any]) -> str:
    return " ".join(str(document.get("text", "")).lower().split())


def _selected_texts(result: dict[str, Any]) -> list[str]:
    return [_normalized_text(document) for document in result.get("documents", [])]


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _bounded_result(result: dict[str, Any]) -> None:
    documents = result.get("documents")
    _assert(isinstance(documents, list), "result documents must be a list")
    _assert(0.0 <= float(result.get("kept_ratio", -1.0)) <= 1.0, "kept_ratio out of range")
    _assert(0.0 <= float(result.get("dedup_rate", -1.0)) <= 1.0, "dedup_rate out of range")
    seen_ids: set[str] = set()
    for index, document in enumerate(documents):
        _assert(isinstance(document, dict), f"selected document {index} must be an object")
        document_id = str(document.get("id", ""))
        _assert(bool(document_id), f"selected document {index} has empty id")
        _assert(document_id not in seen_ids, f"selected document id repeated: {document_id}")
        seen_ids.add(document_id)
        _assert("text" in document, f"selected document {document_id} has no text")


def _probe_deterministic_public_score(config: dict[str, Any]) -> dict[str, Any]:
    documents = load_documents()
    first = apply_solution(documents, config)
    second = apply_solution(documents, config)
    _bounded_result(first)
    _bounded_result(second)
    first_hash = selection_hash(first["documents"])
    second_hash = selection_hash(second["documents"])
    _assert(first_hash == second_hash, "selection hash changed across identical runs")
    return {"selection_hash": first_hash, "selected_document_count": len(first["documents"])}


def _probe_public_id_remap_stability(config: dict[str, Any]) -> dict[str, Any]:
    documents = load_documents()
    remapped = []
    for index, document in enumerate(documents):
        item = dict(document)
        item["id"] = f"probe-remap-{index:03d}"
        remapped.append(item)
    original = apply_solution(documents, config)
    changed = apply_solution(remapped, config)
    _bounded_result(original)
    _bounded_result(changed)
    _assert(
        _selected_texts(original) == _selected_texts(changed),
        "selection changed after public document ids were remapped",
    )
    return {"selected_document_count": len(original["documents"])}


def _probe_inputs_are_not_mutated(config: dict[str, Any]) -> dict[str, Any]:
    documents = load_documents()
    before = copy.deepcopy(documents)
    result = apply_solution(documents, config)
    _bounded_result(result)
    _assert(documents == before, "apply_solution mutated input documents")
    return {"selected_document_count": len(result["documents"])}


def _probe_synthetic_documents_do_not_crash(config: dict[str, Any]) -> dict[str, Any]:
    documents = [
        {"id": "probe-empty", "source": "technical", "text": "   "},
        {
            "id": "probe-useful",
            "source": "technical",
            "text": "A useful synthetic document records evidence, costs, and failure modes for replay.",
        },
        {
            "id": "probe-useful-dup",
            "source": "technical",
            "text": "  a useful synthetic document records evidence, costs, and failure modes for replay.  ",
        },
        {
            "id": "probe-other",
            "source": "manual",
            "text": "Another candidate-only note checks unicode words, byte counts, and deterministic order.",
        },
    ]
    result = apply_solution(copy.deepcopy(documents), config)
    _bounded_result(result)
    input_ids = {document["id"] for document in documents}
    selected_ids = {str(document.get("id", "")) for document in result["documents"]}
    _assert(selected_ids.issubset(input_ids), "selected ids must come from input documents")
    return {
        "selected_document_count": len(result["documents"]),
        "selection_hash": selection_hash(result["documents"]),
    }


def _run_probe(name: str, probe: Callable[[dict[str, Any]], dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    try:
        details = probe(config)
    except Exception as exc:  # pragma: no cover - exercised by CLI behavior.
        return {"name": name, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"name": name, "ok": True, "details": details}


def run_invariant_probes(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = load_json(config_path)
    probes: list[tuple[str, Callable[[dict[str, Any]], dict[str, Any]]]] = [
        ("deterministic_public_selection", _probe_deterministic_public_score),
        ("public_id_remap_stability", _probe_public_id_remap_stability),
        ("input_documents_are_not_mutated", _probe_inputs_are_not_mutated),
        ("synthetic_documents_do_not_crash", _probe_synthetic_documents_do_not_crash),
    ]
    results = [_run_probe(name, probe, config) for name, probe in probes]
    return {
        "challenge": "limes-dataforge",
        "ok": all(result["ok"] for result in results),
        "probe_count": len(results),
        "probes": results,
    }


def dumps_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
