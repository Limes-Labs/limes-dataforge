from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from harness.invariant_probes import run_invariant_probes


ROOT = Path(__file__).resolve().parents[1]


class InvariantProbeTests(unittest.TestCase):
    def test_default_solution_passes_public_invariant_probes(self) -> None:
        report = run_invariant_probes()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["probe_count"], 4)
        self.assertEqual(
            {
                "deterministic_public_selection",
                "public_id_remap_stability",
                "input_documents_are_not_mutated",
                "synthetic_documents_do_not_crash",
            },
            {probe["name"] for probe in report["probes"]},
        )

    def test_cli_accepts_default_solution(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/run_invariant_probes.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ok": true', result.stdout)


if __name__ == "__main__":
    unittest.main()
