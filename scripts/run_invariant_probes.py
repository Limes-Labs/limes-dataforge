#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.invariant_probes import dumps_report, run_invariant_probes


ROOT = Path(__file__).resolve().parents[1]


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DataForge public invariant probes.")
    parser.add_argument("--config", default="configs/submission.json")
    args = parser.parse_args()
    report = run_invariant_probes(resolve(args.config))
    print(dumps_report(report), end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
