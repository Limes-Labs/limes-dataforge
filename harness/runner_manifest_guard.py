from __future__ import annotations

import json
from pathlib import Path
from typing import Any


VALID_RUNNER_STATUSES = {"example", "pending-freeze", "frozen"}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "challenge",
    "source",
    "runner_id",
    "runner_status",
    "clean_checkout_required",
    "network_disabled",
    "dependency_lock",
    "hidden_data_manifest",
    "training_protocol",
    "seed_policy",
    "replay_outputs",
    "anti_cheat",
}
REQUIRED_DEPENDENCY_LOCK = {"kind", "digest", "python", "packages"}
REQUIRED_HIDDEN_MANIFEST = {"path", "hash_algorithm", "hidden_data_bundled", "shard_sets"}
REQUIRED_TRAINING_PROTOCOL = {
    "model_family",
    "tokenizer",
    "optimizer",
    "schedule",
    "token_budget",
    "downstream_mini_eval",
}
REQUIRED_REPLAY_OUTPUTS = {
    "replay_result_json",
    "result_card_markdown",
    "runner_log",
    "selection_hash",
    "dataset_hash",
}
REQUIRED_ANTI_CHEAT = {
    "candidate_selection_uses_hidden_data",
    "hidden_scores_returned_to_candidates",
    "public_or_hidden_contamination_check_required",
    "network_disabled_during_scoring",
    "forbidden_paths_checked",
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _missing_fields(payload: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in payload)


def _require_object(payload: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = payload.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return {}
    return value


def _require_list(payload: dict[str, Any], field: str, errors: list[str]) -> list[Any]:
    value = payload.get(field)
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []
    return value


def validate_manifest(manifest: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = _missing_fields(manifest, REQUIRED_TOP_LEVEL)
    if missing:
        errors.append("runner manifest missing fields: " + ", ".join(missing))
        return errors

    if manifest.get("challenge") != contract.get("challenge"):
        errors.append("runner manifest challenge does not match verifier contract")
    if manifest.get("source") == "example-schema-only":
        disclaimer = str(manifest.get("disclaimer", "")).lower()
        if "not an official runner" not in disclaimer:
            errors.append("example runner manifest disclaimer must say it is not an official runner")
    if manifest.get("runner_status") not in VALID_RUNNER_STATUSES:
        errors.append("runner_status must be example, pending-freeze, or frozen")
    if manifest.get("clean_checkout_required") is not True:
        errors.append("clean_checkout_required must be true")
    if manifest.get("network_disabled") is not True:
        errors.append("network_disabled must be true")

    dependency_lock = _require_object(manifest, "dependency_lock", errors)
    missing_dependency = _missing_fields(dependency_lock, REQUIRED_DEPENDENCY_LOCK)
    if missing_dependency:
        errors.append("dependency_lock missing fields: " + ", ".join(missing_dependency))
    for field in ["kind", "digest", "python"]:
        if field in dependency_lock and not _non_empty_string(dependency_lock[field]):
            errors.append(f"dependency_lock.{field} must be a non-empty string")
    packages = dependency_lock.get("packages")
    if "packages" in dependency_lock and not isinstance(packages, list):
        errors.append("dependency_lock.packages must be a list")

    hidden_manifest = _require_object(manifest, "hidden_data_manifest", errors)
    missing_hidden = _missing_fields(hidden_manifest, REQUIRED_HIDDEN_MANIFEST)
    if missing_hidden:
        errors.append("hidden_data_manifest missing fields: " + ", ".join(missing_hidden))
    expected_hidden_policy = contract.get("hidden_data_policy", {})
    if hidden_manifest.get("path") != expected_hidden_policy.get("manifest_path_on_trusted_runners"):
        errors.append("hidden_data_manifest.path must match verifier contract")
    if hidden_manifest.get("hash_algorithm") != expected_hidden_policy.get("hash_algorithm"):
        errors.append("hidden_data_manifest.hash_algorithm must match verifier contract")
    if hidden_manifest.get("hidden_data_bundled") is not False:
        errors.append("hidden_data_manifest.hidden_data_bundled must be false")
    shard_sets = _require_list(hidden_manifest, "shard_sets", errors)
    if not shard_sets:
        errors.append("hidden_data_manifest.shard_sets must not be empty")
    for index, shard_set in enumerate(shard_sets):
        if not isinstance(shard_set, dict):
            errors.append(f"hidden_data_manifest.shard_sets[{index}] must be an object")
            continue
        for field in ["id", "purpose", "hash"]:
            if not _non_empty_string(shard_set.get(field)):
                errors.append(f"hidden_data_manifest.shard_sets[{index}].{field} must be a non-empty string")

    training_protocol = _require_object(manifest, "training_protocol", errors)
    missing_training = _missing_fields(training_protocol, REQUIRED_TRAINING_PROTOCOL)
    if missing_training:
        errors.append("training_protocol missing fields: " + ", ".join(missing_training))
    contract_training = contract.get("training_protocol", {})
    for field in ["model_family", "tokenizer", "optimizer", "schedule", "token_budget"]:
        if training_protocol.get(field) != contract_training.get(field):
            errors.append(f"training_protocol.{field} must match verifier contract")

    seed_policy = _require_object(manifest, "seed_policy", errors)
    if seed_policy != contract_training.get("seed_policy"):
        errors.append("seed_policy must match verifier contract training_protocol.seed_policy")

    replay_outputs = _require_object(manifest, "replay_outputs", errors)
    missing_outputs = _missing_fields(replay_outputs, REQUIRED_REPLAY_OUTPUTS)
    if missing_outputs:
        errors.append("replay_outputs missing fields: " + ", ".join(missing_outputs))

    anti_cheat = _require_object(manifest, "anti_cheat", errors)
    missing_anti_cheat = _missing_fields(anti_cheat, REQUIRED_ANTI_CHEAT)
    if missing_anti_cheat:
        errors.append("anti_cheat missing fields: " + ", ".join(missing_anti_cheat))
    if anti_cheat.get("candidate_selection_uses_hidden_data") is not False:
        errors.append("anti_cheat.candidate_selection_uses_hidden_data must be false")
    if anti_cheat.get("hidden_scores_returned_to_candidates") is not False:
        errors.append("anti_cheat.hidden_scores_returned_to_candidates must be false")
    if anti_cheat.get("public_or_hidden_contamination_check_required") is not True:
        errors.append("anti_cheat.public_or_hidden_contamination_check_required must be true")
    if anti_cheat.get("network_disabled_during_scoring") is not True:
        errors.append("anti_cheat.network_disabled_during_scoring must be true")
    if anti_cheat.get("forbidden_paths_checked") is not True:
        errors.append("anti_cheat.forbidden_paths_checked must be true")

    return errors
