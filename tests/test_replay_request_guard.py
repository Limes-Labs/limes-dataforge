from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from harness.replay_request_guard import load_json, validate_request


ROOT = Path(__file__).resolve().parents[1]


class ReplayRequestGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(ROOT / "verifier/replay-contract.json")

    def test_example_replay_request_validates(self) -> None:
        request = load_json(ROOT / "templates/replay-request.example.json")
        errors = validate_request(request, self.contract, verify_files=False)
        self.assertEqual(errors, [])

    def test_rejects_hidden_feedback_request(self) -> None:
        request = load_json(ROOT / "templates/replay-request.example.json")
        request["anti_probing"]["hidden_feedback_requested"] = True
        errors = validate_request(request, self.contract, verify_files=False)
        self.assertTrue(any("hidden_feedback_requested" in error for error in errors))

    def test_rejects_promotion_status_request(self) -> None:
        request = load_json(ROOT / "templates/replay-request.example.json")
        request["requested_status"] = "promoted"
        errors = validate_request(request, self.contract, verify_files=False)
        self.assertTrue(any("requested_status" in error for error in errors))

    def test_ready_request_requires_approval(self) -> None:
        request = load_json(ROOT / "templates/replay-request.example.json")
        request["source"] = "maintainer-review"
        request["replay_ready"] = True
        request["review"]["decision"] = "hold"
        errors = validate_request(request, self.contract, verify_files=False)
        self.assertTrue(any("review.decision" in error for error in errors))

    def test_rejects_replay_budget_over_quota(self) -> None:
        request = load_json(ROOT / "templates/replay-request.example.json")
        request["replay_budget"]["team_request_count_7_days"] = 3
        errors = validate_request(request, self.contract, verify_files=False)
        self.assertTrue(any("team_request_count_7_days" in error for error in errors))

    def test_cli_validates_example(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_replay_request.py",
                "--input",
                "templates/replay-request.example.json",
                "--schema-only",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ok": true', result.stdout)


if __name__ == "__main__":
    unittest.main()
