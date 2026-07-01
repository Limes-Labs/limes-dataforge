from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
CHALLENGE = "limes-dataforge"
MANIFEST_KIND = "trusted-hidden-shard-manifest"
HASH_ALGORITHM = "sha256"
SHARD_ROLES = {"train", "validation", "downstream_eval", "contamination_probe"}
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "challenge",
    "manifest_kind",
    "source",
    "hidden_manifest_ready",
    "hash_algorithm",
    "shard_policy",
    "shards",
    "seed_policy",
    "contamination_checks",
}
REQUIRED_SHARD_POLICY = {
    "candidate_selection_uses_hidden_data",
    "hidden_shards_disclosed_to_candidates",
    "public_or_hidden_contamination_check_required",
}
REQUIRED_SHARD = {
    "id",
    "role",
    "split",
    "path",
    "sha256",
    "document_count",
    "byte_count",
    "token_estimate",
    "disclosed_to_candidates",
}
REQUIRED_SEED_POLICY = {"verified_min_seeds", "promoted_min_seeds", "replicated_min_seeds"}
REQUIRED_CONTAMINATION = {
    "public_smoke_overlap_check",
    "heldout_overlap_check",
    "external_benchmark_overlap_check",
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _is_example(payload: dict[str, Any]) -> bool:
    return payload.get("source") == "example-schema-only"


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _looks_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value.lower()
    )


def _missing(payload: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in payload)


def _validate_seed_policy(seed_policy: Any, replay_contract: dict[str, Any]) -> list[str]:
    if not isinstance(seed_policy, dict):
        return ["seed_policy must be an object"]
    errors: list[str] = []
    missing = _missing(seed_policy, REQUIRED_SEED_POLICY)
    if missing:
        errors.append("seed_policy missing fields: " + ", ".join(missing))
        return errors
    for field in sorted(REQUIRED_SEED_POLICY):
        if not isinstance(seed_policy.get(field), int) or seed_policy[field] <= 0:
            errors.append(f"seed_policy.{field} must be a positive integer")
    expected = replay_contract.get("training_protocol", {}).get("seed_policy", {})
    if isinstance(expected, dict):
        for field in sorted(REQUIRED_SEED_POLICY):
            if field in expected and seed_policy.get(field) != expected.get(field):
                errors.append(f"seed_policy.{field} must match replay contract")
    return errors


def _validate_shard_policy(policy: Any) -> list[str]:
    if not isinstance(policy, dict):
        return ["shard_policy must be an object"]
    errors: list[str] = []
    missing = _missing(policy, REQUIRED_SHARD_POLICY)
    if missing:
        errors.append("shard_policy missing fields: " + ", ".join(missing))
        return errors
    if policy.get("candidate_selection_uses_hidden_data") is not False:
        errors.append("shard_policy.candidate_selection_uses_hidden_data must be false")
    if policy.get("hidden_shards_disclosed_to_candidates") is not False:
        errors.append("shard_policy.hidden_shards_disclosed_to_candidates must be false")
    if policy.get("public_or_hidden_contamination_check_required") is not True:
        errors.append("shard_policy.public_or_hidden_contamination_check_required must be true")
    return errors


def _validate_shards(shards: Any, example: bool) -> list[str]:
    if not isinstance(shards, list) or not shards:
        return ["shards must be a non-empty list"]
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, shard in enumerate(shards):
        prefix = f"shards[{index}]"
        if not isinstance(shard, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = _missing(shard, REQUIRED_SHARD)
        if missing:
            errors.append(f"{prefix} missing fields: " + ", ".join(missing))
            continue
        shard_id = shard.get("id")
        if not _non_empty_string(shard_id):
            errors.append(f"{prefix}.id must be a non-empty string")
        elif shard_id in seen_ids:
            errors.append(f"{prefix}.id duplicates an earlier shard")
        else:
            seen_ids.add(shard_id)
        if shard.get("role") not in SHARD_ROLES:
            errors.append(f"{prefix}.role must be one of {sorted(SHARD_ROLES)}")
        for field in ["split", "path"]:
            if not _non_empty_string(shard.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if example:
            if not _non_empty_string(shard.get("sha256")):
                errors.append(f"{prefix}.sha256 must be a non-empty string")
        elif not _looks_sha256(shard.get("sha256")):
            errors.append(f"{prefix}.sha256 must be a sha256 hex string")
        for field in ["document_count", "byte_count", "token_estimate"]:
            if example:
                if not isinstance(shard.get(field), int) or shard[field] < 0:
                    errors.append(f"{prefix}.{field} must be a non-negative integer")
            elif not isinstance(shard.get(field), int) or shard[field] <= 0:
                errors.append(f"{prefix}.{field} must be a positive integer")
        if shard.get("disclosed_to_candidates") is not False:
            errors.append(f"{prefix}.disclosed_to_candidates must be false")
    roles = {shard.get("role") for shard in shards if isinstance(shard, dict)}
    for required_role in ["train", "validation"]:
        if required_role not in roles:
            errors.append(f"shards must include at least one {required_role} shard")
    return errors


def _validate_contamination(checks: Any, require_passed: bool) -> list[str]:
    if not isinstance(checks, dict):
        return ["contamination_checks must be an object"]
    errors: list[str] = []
    missing = _missing(checks, REQUIRED_CONTAMINATION)
    if missing:
        errors.append("contamination_checks missing fields: " + ", ".join(missing))
        return errors
    for field in sorted(REQUIRED_CONTAMINATION):
        if not isinstance(checks.get(field), bool):
            errors.append(f"contamination_checks.{field} must be boolean")
        elif require_passed and checks[field] is not True:
            errors.append(f"contamination_checks.{field} must be true for ready hidden manifests")
    return errors


def validate_hidden_manifest(manifest: dict[str, Any], replay_contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = _missing(manifest, REQUIRED_TOP_LEVEL)
    if missing:
        errors.append("hidden manifest missing fields: " + ", ".join(missing))
        return errors
    example = _is_example(manifest)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("challenge") != CHALLENGE or manifest.get("challenge") != replay_contract.get("challenge"):
        errors.append(f"challenge must be {CHALLENGE}")
    if manifest.get("manifest_kind") != MANIFEST_KIND:
        errors.append(f"manifest_kind must be {MANIFEST_KIND}")
    if manifest.get("hash_algorithm") != HASH_ALGORITHM:
        errors.append(f"hash_algorithm must be {HASH_ALGORITHM}")
    if not isinstance(manifest.get("hidden_manifest_ready"), bool):
        errors.append("hidden_manifest_ready must be boolean")
    if example:
        disclaimer = str(manifest.get("disclaimer", "")).lower()
        if "not a real hidden manifest" not in disclaimer:
            errors.append("schema-only hidden manifest must say it is not a real hidden manifest")
        if manifest.get("hidden_manifest_ready") is not False:
            errors.append("schema-only hidden manifest must not be ready")

    errors.extend(_validate_shard_policy(manifest.get("shard_policy")))
    errors.extend(_validate_shards(manifest.get("shards"), example))
    errors.extend(_validate_seed_policy(manifest.get("seed_policy"), replay_contract))
    errors.extend(
        _validate_contamination(
            manifest.get("contamination_checks"),
            require_passed=not example and manifest.get("hidden_manifest_ready") is True,
        )
    )
    return errors
