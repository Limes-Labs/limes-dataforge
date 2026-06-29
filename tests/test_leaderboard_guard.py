from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.leaderboard_guard import load_json, validate_payload


ROOT = Path(__file__).resolve().parents[1]


class LeaderboardGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(ROOT / "verifier/replay-contract.json")
        self.payload = load_json(ROOT / "examples/limeslabs/leaderboard.example.json")

    def test_example_fixture_passes(self) -> None:
        self.assertEqual(validate_payload(self.payload, self.contract), [])

    def test_candidate_hidden_metric_must_be_null(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["entries"][0]["score"]["hidden_val_loss"] = 2.0
        errors = validate_payload(payload, self.contract)
        self.assertTrue(any("must be null" in error for error in errors))

    def test_promoted_entry_requires_trusted_runner_and_result_card(self) -> None:
        payload = copy.deepcopy(self.payload)
        entry = payload["entries"][0]
        entry["status"] = "promoted"
        entry["score"]["hidden_val_loss"] = 2.9
        entry["replay"]["trusted_runner"] = None
        entry["links"]["result_card"] = None
        errors = validate_payload(payload, self.contract)
        self.assertTrue(any("trusted_runner" in error for error in errors))
        self.assertTrue(any("result_card" in error for error in errors))

    def test_replicated_entry_requires_numeric_seed_count(self) -> None:
        payload = copy.deepcopy(self.payload)
        entry = payload["entries"][0]
        entry["status"] = "replicated"
        entry["score"]["hidden_val_loss"] = 2.9
        entry["replay"]["trusted_runner"] = "runner-1"
        entry["replay"]["seed_count"] = "many"
        errors = validate_payload(payload, self.contract)
        self.assertTrue(any("seed_count" in error for error in errors))

    def test_cli_accepts_example_fixture(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_leaderboard.py",
                "--input",
                "examples/limeslabs/leaderboard.example.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ok": true', result.stdout)

    def test_cli_rejects_bad_payload(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["entries"][0]["score"]["hidden_val_loss"] = 1.0
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_path = Path(temp_dir) / "bad-leaderboard.json"
            bad_path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_leaderboard.py",
                    "--input",
                    str(bad_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be null", result.stdout)


if __name__ == "__main__":
    unittest.main()
