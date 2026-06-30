from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.baseline_record_guard import load_json, validate_record


ROOT = Path(__file__).resolve().parents[1]


class BaselineRecordGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(ROOT / "verifier/replay-contract.json")
        self.record = load_json(ROOT / "verifier/baseline-record.example.json")

    def test_example_baseline_record_passes(self) -> None:
        self.assertEqual(validate_record(self.record, self.contract), [])

    def test_hidden_loss_must_be_median_of_seed_results(self) -> None:
        record = copy.deepcopy(self.record)
        record["aggregate"]["hidden_val_loss"] = 2.0
        errors = validate_record(record, self.contract)
        self.assertTrue(any("median seed hidden_val_loss" in error for error in errors))

    def test_seed_policy_must_match_contract(self) -> None:
        record = copy.deepcopy(self.record)
        record["seed_policy"]["promoted_min_seeds"] = 1
        errors = validate_record(record, self.contract)
        self.assertTrue(any("seed_policy" in error for error in errors))

    def test_promoted_comparison_requires_frozen_baseline(self) -> None:
        record = copy.deepcopy(self.record)
        record["promotion_use"]["used_for_promoted_comparison"] = True
        errors = validate_record(record, self.contract)
        self.assertTrue(any("baseline_status frozen" in error for error in errors))

    def test_hidden_scores_must_not_return_to_candidates(self) -> None:
        record = copy.deepcopy(self.record)
        record["replay_constraints"]["hidden_scores_returned_to_candidates"] = True
        errors = validate_record(record, self.contract)
        self.assertTrue(any("hidden_scores_returned_to_candidates" in error for error in errors))

    def test_cli_accepts_example_record(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_baseline_record.py",
                "--input",
                "verifier/baseline-record.example.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ok": true', result.stdout)

    def test_cli_rejects_bad_record(self) -> None:
        record = copy.deepcopy(self.record)
        record["replay_constraints"]["network_disabled"] = False
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_path = Path(temp_dir) / "bad-baseline-record.json"
            bad_path.write_text(json.dumps(record), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_baseline_record.py",
                    "--input",
                    str(bad_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("network_disabled", result.stdout)


if __name__ == "__main__":
    unittest.main()
