from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.runner_manifest_guard import load_json, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class RunnerManifestGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(ROOT / "verifier/replay-contract.json")
        self.manifest = load_json(ROOT / "verifier/trusted-runner-manifest.example.json")

    def test_example_manifest_passes(self) -> None:
        self.assertEqual(validate_manifest(self.manifest, self.contract), [])

    def test_network_must_be_disabled(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["network_disabled"] = False
        manifest["anti_cheat"]["network_disabled_during_scoring"] = False
        errors = validate_manifest(manifest, self.contract)
        self.assertTrue(any("network_disabled" in error for error in errors))

    def test_hidden_manifest_path_must_match_contract(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["hidden_data_manifest"]["path"] = "other/manifest.json"
        errors = validate_manifest(manifest, self.contract)
        self.assertTrue(any("hidden_data_manifest.path" in error for error in errors))

    def test_hidden_data_must_not_be_bundled(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["hidden_data_manifest"]["hidden_data_bundled"] = True
        errors = validate_manifest(manifest, self.contract)
        self.assertTrue(any("hidden_data_bundled" in error for error in errors))

    def test_seed_policy_must_match_contract(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["seed_policy"]["promoted_min_seeds"] = 1
        errors = validate_manifest(manifest, self.contract)
        self.assertTrue(any("seed_policy" in error for error in errors))

    def test_cli_accepts_example_manifest(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_runner_manifest.py",
                "--input",
                "verifier/trusted-runner-manifest.example.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ok": true', result.stdout)

    def test_cli_rejects_bad_manifest(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["anti_cheat"]["hidden_scores_returned_to_candidates"] = True
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_path = Path(temp_dir) / "bad-runner-manifest.json"
            bad_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_runner_manifest.py",
                    "--input",
                    str(bad_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hidden_scores_returned_to_candidates", result.stdout)


if __name__ == "__main__":
    unittest.main()
