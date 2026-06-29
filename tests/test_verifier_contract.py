from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VerifierContractTests(unittest.TestCase):
    def load_contract(self) -> dict:
        return json.loads((ROOT / "verifier/replay-contract.json").read_text(encoding="utf-8"))

    def test_contract_pins_hidden_primary_metric_and_status_gates(self) -> None:
        contract = self.load_contract()
        self.assertEqual(contract["challenge"], "limes-dataforge")
        self.assertFalse(contract["hidden_verifier_ready"])
        self.assertEqual(contract["official_primary_metric"], "hidden_val_loss")
        self.assertEqual(contract["score_direction"], "minimize")
        for status in ["candidate", "verified", "promoted", "replicated", "scaled"]:
            self.assertIn(status, contract["promotion_gates"])
            self.assertGreater(len(contract["promotion_gates"][status]), 0)

    def test_contract_keeps_hidden_data_private_and_no_network(self) -> None:
        contract = self.load_contract()
        self.assertFalse(contract["hidden_data_policy"]["hidden_data_bundled"])
        self.assertFalse(contract["hidden_data_policy"]["candidate_selection_uses_hidden_data"])
        self.assertEqual(contract["trusted_runner"]["network"], "disabled during official scoring")
        self.assertTrue(contract["trusted_runner"]["clean_checkout"])

    def test_contract_lists_official_result_fields(self) -> None:
        metrics = set(self.load_contract()["official_result_schema"]["metrics"])
        for required in {
            "hidden_val_loss",
            "public_val_loss",
            "downstream_mini_eval",
            "dataset_hash",
            "selection_hash",
            "baseline_hidden_val_loss",
        }:
            self.assertIn(required, metrics)

    def test_verify_hidden_prints_contract(self) -> None:
        result = subprocess.run(
            [sys.executable, "harness/verify_hidden.py", "--public-contract-only"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["challenge"], "limes-dataforge")
        self.assertEqual(payload["official_primary_metric"], "hidden_val_loss")


if __name__ == "__main__":
    unittest.main()
