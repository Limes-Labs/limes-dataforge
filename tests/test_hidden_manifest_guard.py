from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from harness.hidden_manifest_guard import load_json, validate_hidden_manifest


ROOT = Path(__file__).resolve().parents[1]


class HiddenManifestGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(ROOT / "verifier/replay-contract.json")

    def test_example_hidden_manifest_validates(self) -> None:
        manifest = load_json(ROOT / "verifier/hidden-manifest.example.json")
        errors = validate_hidden_manifest(manifest, self.contract)
        self.assertEqual(errors, [])

    def test_rejects_candidate_disclosure(self) -> None:
        manifest = load_json(ROOT / "verifier/hidden-manifest.example.json")
        manifest["shards"][0]["disclosed_to_candidates"] = True
        errors = validate_hidden_manifest(manifest, self.contract)
        self.assertTrue(any("disclosed_to_candidates" in error for error in errors))

    def test_rejects_seed_policy_drift(self) -> None:
        manifest = load_json(ROOT / "verifier/hidden-manifest.example.json")
        manifest["seed_policy"]["promoted_min_seeds"] = 1
        errors = validate_hidden_manifest(manifest, self.contract)
        self.assertTrue(any("promoted_min_seeds" in error for error in errors))

    def test_rejects_placeholder_hash_for_real_manifest(self) -> None:
        manifest = load_json(ROOT / "verifier/hidden-manifest.example.json")
        manifest["source"] = "trusted-runner-local"
        manifest["hidden_manifest_ready"] = True
        errors = validate_hidden_manifest(manifest, self.contract)
        self.assertTrue(any("sha256" in error for error in errors))

    def test_accepts_real_manifest_shape(self) -> None:
        manifest = load_json(ROOT / "verifier/hidden-manifest.example.json")
        manifest["source"] = "trusted-runner-local"
        manifest["hidden_manifest_ready"] = True
        for index, shard in enumerate(manifest["shards"]):
            shard["sha256"] = f"{index + 1:064x}"
            shard["document_count"] = 10 + index
            shard["byte_count"] = 1000 + index
            shard["token_estimate"] = 500 + index
        for field in manifest["contamination_checks"]:
            manifest["contamination_checks"][field] = True
        errors = validate_hidden_manifest(manifest, self.contract)
        self.assertEqual(errors, [])

    def test_cli_validates_example(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_hidden_manifest.py",
                "--input",
                "verifier/hidden-manifest.example.json",
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
