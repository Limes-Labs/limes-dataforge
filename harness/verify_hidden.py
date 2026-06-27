#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


CONTRACT = {
    "hidden_verifier_ready": False,
    "mode": "public-contract-only",
    "official_primary_metric": "hidden_val_loss",
    "requires": [
        "hidden shard generation and hashes",
        "fixed tokenizer, model, optimizer, schedule, seeds, and token budget",
        "trusted runner with no network during scoring",
        "repeated-seed promotion gate",
        "downstream mini-eval non-regression",
        "larger-budget scaling audit for scaled status"
    ]
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Describe the DataForge hidden verifier contract.")
    parser.add_argument("--public-contract-only", action="store_true")
    args = parser.parse_args()
    if not args.public_contract_only:
        raise SystemExit("hidden verifier data is not bundled; use --public-contract-only")
    print(json.dumps(CONTRACT, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
