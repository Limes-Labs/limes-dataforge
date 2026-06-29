from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HIDDEN_METRIC = "hidden_val_loss"
PUBLIC_SCORE_FIELDS = {
    "hidden_val_loss",
    "public_proxy_loss",
    "baseline_public_proxy_loss",
    "public_proxy_delta",
}
PUBLIC_METRIC_FIELDS = {
    "public_proxy_improvement",
    "kept_ratio",
    "dedup_rate",
    "selection_hash",
    "baseline_selection_hash",
    "runtime_seconds",
    "dataset_hash",
}
REPLAY_FIELDS = {"trusted_runner", "seed_count", "scaled_audit"}
BASE_ENTRY_FIELDS = {
    "challenge",
    "submission_id",
    "status",
    "commit",
    "score",
    "metrics",
    "replay",
    "links",
}
PRE_VERIFIED_STATUSES = {"local", "candidate"}
POST_VERIFIED_STATUSES = {"verified", "promoted", "replicated", "scaled"}
PROMOTED_OR_LATER = {"promoted", "replicated", "scaled"}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _missing_fields(payload: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in payload)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_entry(entry: dict[str, Any], contract: dict[str, Any], index: int) -> list[str]:
    prefix = f"entries[{index}]"
    errors: list[str] = []
    missing = _missing_fields(entry, BASE_ENTRY_FIELDS)
    if missing:
        errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        return errors

    if entry["challenge"] != contract.get("challenge"):
        errors.append(f"{prefix}.challenge does not match verifier contract")

    status = entry.get("status")
    if status not in contract.get("status_model", []):
        errors.append(f"{prefix}.status is not in the verifier status model")

    score = entry.get("score")
    metrics = entry.get("metrics")
    replay = entry.get("replay")
    links = entry.get("links")
    if not isinstance(score, dict):
        errors.append(f"{prefix}.score must be an object")
        score = {}
    if not isinstance(metrics, dict):
        errors.append(f"{prefix}.metrics must be an object")
        metrics = {}
    if not isinstance(replay, dict):
        errors.append(f"{prefix}.replay must be an object")
        replay = {}
    if not isinstance(links, dict):
        errors.append(f"{prefix}.links must be an object")
        links = {}

    for field_group, payload, required in [
        ("score", score, PUBLIC_SCORE_FIELDS),
        ("metrics", metrics, PUBLIC_METRIC_FIELDS),
        ("replay", replay, REPLAY_FIELDS),
    ]:
        missing = _missing_fields(payload, required)
        if missing:
            errors.append(f"{prefix}.{field_group} missing fields: {', '.join(missing)}")

    hidden_value = score.get(HIDDEN_METRIC)
    if status in PRE_VERIFIED_STATUSES and hidden_value is not None:
        errors.append(f"{prefix}.{HIDDEN_METRIC} must be null before verified status")
    if status in POST_VERIFIED_STATUSES and not _is_number(hidden_value):
        errors.append(f"{prefix}.{HIDDEN_METRIC} must be numeric for verified or later status")
    if status in POST_VERIFIED_STATUSES and not replay.get("trusted_runner"):
        errors.append(f"{prefix}.replay.trusted_runner is required for verified or later status")
    if status in PROMOTED_OR_LATER and not links.get("result_card"):
        errors.append(f"{prefix}.links.result_card is required for promoted or later status")
    seed_count = replay.get("seed_count", 0)
    if status in {"replicated", "scaled"} and (
        not _is_positive_int(seed_count) or seed_count < 2
    ):
        errors.append(f"{prefix}.replay.seed_count must be >= 2 for replicated or scaled status")
    if status == "scaled" and replay.get("scaled_audit") is not True:
        errors.append(f"{prefix}.replay.scaled_audit must be true for scaled status")
    return errors


def validate_payload(payload: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("challenge") != contract.get("challenge"):
        errors.append("payload challenge does not match verifier contract")
    if payload.get("source") == "example-fixture":
        disclaimer = str(payload.get("disclaimer", "")).lower()
        if "not an official leaderboard" not in disclaimer:
            errors.append("example fixture disclaimer must say it is not an official leaderboard")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["payload entries must be a non-empty list"]
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entries[{index}] must be an object")
            continue
        errors.extend(_validate_entry(entry, contract, index))
    return errors
