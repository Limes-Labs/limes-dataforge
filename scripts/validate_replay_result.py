#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.replay_result_guard import load_json, validate_result


ROOT = Path(__file__).resolve().parents[1]


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Limes DataForge trusted replay result.")
    parser.add_argument("--input", required=True, help="Replay result JSON.")
    parser.add_argument(
        "--contract",
        default="verifier/replay-contract.json",
        help="Verifier replay contract JSON.",
    )
    args = parser.parse_args()

    result_path = resolve(args.input)
    contract_path = resolve(args.contract)
    payload = load_json(result_path)
    contract = load_json(contract_path)
    errors = validate_result(payload, contract)
    report = {
        "ok": not errors,
        "challenge": contract.get("challenge"),
        "input": str(result_path),
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
