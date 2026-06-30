from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any


VALID_BASELINE_STATUSES = {"example", "pending-freeze", "frozen"}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "challenge",
    "source",
    "baseline_id",
    "baseline_status",
    "runner_id",
    "runner_manifest_hash",
    "dependency_lock_digest",
    "dataset_hash",
    "code_hash",
    "selection_hash",
    "method",
    "primary_metric",
    "direction",
    "seed_policy",
    "seeds",
    "aggregate",
    "seed_results",
    "replay_constraints",
    "promotion_use",
}
REQUIRED_AGGREGATE = {
    "hidden_val_loss",
    "public_val_loss",
    "downstream_mini_eval",
    "train_seconds",
    "tokens_per_second",
    "peak_memory_mb",
}
REQUIRED_SEED_RESULT = {"seed", "hidden_val_loss", "public_val_loss", "downstream_mini_eval"}
REQUIRED_REPLAY_CONSTRAINTS = {
    "clean_checkout",
    "network_disabled",
    "candidate_selection_uses_hidden_data",
    "hidden_scores_returned_to_candidates",
}
REQUIRED_PROMOTION_USE = {
    "used_for_promoted_comparison",
    "minimum_promoted_seeds",
    "comparison_metric",
    "direction",
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


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


def _almost_equal(left: Any, right: Any) -> bool:
    return _is_number(left) and _is_number(right) and abs(float(left) - float(right)) <= 1e-12


def validate_record(record: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = _missing_fields(record, REQUIRED_TOP_LEVEL)
    if missing:
        errors.append("baseline record missing fields: " + ", ".join(missing))
        return errors

    if record.get("challenge") != contract.get("challenge"):
        errors.append("baseline record challenge does not match verifier contract")
    if record.get("source") == "example-schema-only":
        disclaimer = str(record.get("disclaimer", "")).lower()
        if "not an official baseline" not in disclaimer:
            errors.append("example baseline record disclaimer must say it is not an official baseline")
    if record.get("baseline_status") not in VALID_BASELINE_STATUSES:
        errors.append("baseline_status must be example, pending-freeze, or frozen")
    if record.get("primary_metric") != contract.get("official_primary_metric"):
        errors.append("primary_metric must match verifier contract official_primary_metric")
    if record.get("direction") != contract.get("score_direction"):
        errors.append("direction must match verifier contract score_direction")

    for field in [
        "baseline_id",
        "runner_id",
        "runner_manifest_hash",
        "dependency_lock_digest",
        "dataset_hash",
        "code_hash",
        "selection_hash",
        "method",
    ]:
        if not _non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")

    contract_seed_policy = contract.get("training_protocol", {}).get("seed_policy")
    seed_policy = _require_object(record, "seed_policy", errors)
    if seed_policy != contract_seed_policy:
        errors.append("seed_policy must match verifier contract training_protocol.seed_policy")

    seeds = _require_list(record, "seeds", errors)
    if not seeds or any(not isinstance(seed, int) for seed in seeds):
        errors.append("seeds must be a non-empty list of integers")
    if len(set(seeds)) != len(seeds):
        errors.append("seeds must not contain duplicates")

    aggregate = _require_object(record, "aggregate", errors)
    missing_aggregate = _missing_fields(aggregate, REQUIRED_AGGREGATE)
    if missing_aggregate:
        errors.append("aggregate missing fields: " + ", ".join(missing_aggregate))
    for field in REQUIRED_AGGREGATE:
        if field in aggregate and not _is_number(aggregate[field]):
            errors.append(f"aggregate.{field} must be numeric")

    seed_results = _require_list(record, "seed_results", errors)
    if len(seed_results) != len(seeds):
        errors.append("seed_results length must match seeds length")
    result_seeds: list[int] = []
    hidden_losses: list[float] = []
    public_losses: list[float] = []
    for index, result in enumerate(seed_results):
        if not isinstance(result, dict):
            errors.append(f"seed_results[{index}] must be an object")
            continue
        missing_result = _missing_fields(result, REQUIRED_SEED_RESULT)
        if missing_result:
            errors.append(f"seed_results[{index}] missing fields: " + ", ".join(missing_result))
        if isinstance(result.get("seed"), int):
            result_seeds.append(result["seed"])
        else:
            errors.append(f"seed_results[{index}].seed must be an integer")
        for field in ["hidden_val_loss", "public_val_loss", "downstream_mini_eval"]:
            if field in result and not _is_number(result[field]):
                errors.append(f"seed_results[{index}].{field} must be numeric")
        if _is_number(result.get("hidden_val_loss")):
            hidden_losses.append(float(result["hidden_val_loss"]))
        if _is_number(result.get("public_val_loss")):
            public_losses.append(float(result["public_val_loss"]))

    if sorted(result_seeds) != sorted(seeds):
        errors.append("seed_results seeds must match seeds")
    if hidden_losses and not _almost_equal(statistics.median(hidden_losses), aggregate.get("hidden_val_loss")):
        errors.append("aggregate.hidden_val_loss must equal median seed hidden_val_loss")
    if public_losses and not _almost_equal(statistics.median(public_losses), aggregate.get("public_val_loss")):
        errors.append("aggregate.public_val_loss must equal median seed public_val_loss")

    replay_constraints = _require_object(record, "replay_constraints", errors)
    missing_constraints = _missing_fields(replay_constraints, REQUIRED_REPLAY_CONSTRAINTS)
    if missing_constraints:
        errors.append("replay_constraints missing fields: " + ", ".join(missing_constraints))
    if replay_constraints.get("clean_checkout") is not True:
        errors.append("replay_constraints.clean_checkout must be true")
    if replay_constraints.get("network_disabled") is not True:
        errors.append("replay_constraints.network_disabled must be true")
    if replay_constraints.get("candidate_selection_uses_hidden_data") is not False:
        errors.append("replay_constraints.candidate_selection_uses_hidden_data must be false")
    if replay_constraints.get("hidden_scores_returned_to_candidates") is not False:
        errors.append("replay_constraints.hidden_scores_returned_to_candidates must be false")

    promotion_use = _require_object(record, "promotion_use", errors)
    missing_promotion = _missing_fields(promotion_use, REQUIRED_PROMOTION_USE)
    if missing_promotion:
        errors.append("promotion_use missing fields: " + ", ".join(missing_promotion))
    promoted_min_seeds = contract_seed_policy.get("promoted_min_seeds") if isinstance(contract_seed_policy, dict) else None
    if promotion_use.get("minimum_promoted_seeds") != promoted_min_seeds:
        errors.append("promotion_use.minimum_promoted_seeds must match promoted_min_seeds")
    if promotion_use.get("comparison_metric") != contract.get("official_primary_metric"):
        errors.append("promotion_use.comparison_metric must match official primary metric")
    if promotion_use.get("direction") != contract.get("score_direction"):
        errors.append("promotion_use.direction must match score direction")
    if promotion_use.get("used_for_promoted_comparison") is True and record.get("baseline_status") != "frozen":
        errors.append("used_for_promoted_comparison requires baseline_status frozen")

    return errors
