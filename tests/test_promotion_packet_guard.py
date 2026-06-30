from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.promotion_packet_guard import load_json, validate_packet


ROOT = Path(__file__).resolve().parents[1]


class PromotionPacketGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(ROOT / "verifier/replay-contract.json")
        self.packet = load_json(ROOT / "templates/promotion-packet.example.json")

    def test_example_promotion_packet_passes(self) -> None:
        self.assertEqual(validate_packet(self.packet, self.contract), [])

    def test_example_packet_must_not_claim_promotion_ready(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["promotion_ready"] = True
        errors = validate_packet(packet, self.contract)
        self.assertTrue(any("schema-only example" in error for error in errors))

    def test_promoted_packet_requires_clean_gates_and_review_approval(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["source"] = "trusted-runner"
        packet["requested_status"] = "promoted"
        packet["promotion_ready"] = True
        packet["evidence"]["result_card_present"] = True
        packet["evidence"]["downstream_non_regression"] = True
        errors = validate_packet(packet, self.contract)
        self.assertTrue(any("failed or blocked gates" in error for error in errors))
        self.assertTrue(any("review.decision must be approve" in error for error in errors))

    def test_promoted_packet_can_pass_when_all_gates_are_bound(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["source"] = "trusted-runner"
        packet.pop("disclaimer", None)
        packet["requested_status"] = "promoted"
        packet["promotion_ready"] = True
        packet["evidence"]["result_card_present"] = True
        packet["evidence"]["seed_count"] = 3
        packet["evidence"]["downstream_non_regression"] = True
        packet["gates"]["passed"] = ["trusted replay", "baseline comparison", "downstream non-regression"]
        packet["gates"]["failed"] = []
        packet["gates"]["blocked"] = []
        packet["review"]["decision"] = "approve"
        errors = validate_packet(packet, self.contract)
        self.assertEqual(errors, [])

    def test_artifacts_must_be_validated(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["artifacts"]["replay_result"]["validated"] = False
        errors = validate_packet(packet, self.contract)
        self.assertTrue(any("artifacts.replay_result.validated" in error for error in errors))

    def test_cli_accepts_example_packet(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_promotion_packet.py",
                "--input",
                "templates/promotion-packet.example.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ok": true', result.stdout)

    def test_cli_rejects_bad_packet(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["evidence"]["network_disabled"] = False
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_path = Path(temp_dir) / "bad-promotion-packet.json"
            bad_path.write_text(json.dumps(packet), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_promotion_packet.py",
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
