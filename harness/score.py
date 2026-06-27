#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.curation import public_score


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Limes DataForge public smoke scorer.")
    parser.add_argument("--config", default="configs/submission.json")
    parser.add_argument("--output", default="score.json")
    args = parser.parse_args()

    result = public_score(Path(args.config))
    output = Path(args.output)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
