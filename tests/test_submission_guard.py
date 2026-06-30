from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.submission_guard import (
    REQUIRED_PUBLIC_SCORE_FIELDS,
    classify_changed_paths,
    load_json,
    validate_manifest,
    validate_submission,
)


ROOT = Path(__file__).resolve().parents[1]


def valid_manifest() -> dict:
    public_score = {field: 1 for field in REQUIRED_PUBLIC_SCORE_FIELDS}
    public_score.update(
        {
            "selection_hash": "a" * 64,
            "baseline_selection_hash": "b" * 64,
            "baseline_name": "public_smoke_all_nonempty_dedup_short_to_long",
            "dataset_hash": "c" * 64,
        }
    )
    return {
        "challenge": "limes-dataforge",
        "status": "candidate",
        "commit": "0123456789abcdef0123456789abcdef01234567",
        "changed_files": ["solution/filter.py"],
        "public_score": public_score,
        "hardware": "local test machine",
        "seeds": [1],
        "selection_trials": 1,
        "method_summary": "Keep documents that satisfy a stricter source and length rule.",
        "expected_failure_modes": ["May over-prefer short technical public-smoke text."],
        "agent_notes": "tests only",
    }


class SubmissionGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(ROOT / "challenge.json")

    def test_classifies_editable_forbidden_and_unknown_paths(self) -> None:
        classified = classify_changed_paths(
            ["solution/filter.py", "harness/score.py", "verifier/task-spec.json", "README.md"],
            self.contract,
        )
        self.assertEqual(classified["editable"], ["solution/filter.py"])
        self.assertEqual(classified["forbidden"], ["harness/score.py", "verifier/task-spec.json"])
        self.assertEqual(classified["unknown"], ["README.md"])

    def test_valid_manifest_passes(self) -> None:
        errors = validate_manifest(valid_manifest(), self.contract)
        self.assertEqual(errors, [])

    def test_forbidden_changed_file_fails(self) -> None:
        manifest = valid_manifest()
        manifest["changed_files"] = ["harness/curation.py"]
        errors = validate_manifest(manifest, self.contract)
        self.assertTrue(any("forbidden files changed" in error for error in errors))

    def test_checked_diff_must_match_manifest(self) -> None:
        errors = validate_submission(
            valid_manifest(),
            self.contract,
            ["solution/filter.py", "solution/rank_documents.py"],
        )
        self.assertTrue(any("exactly match" in error for error in errors))

    def test_cli_accepts_explicit_changed_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "submission.json"
            manifest_path.write_text(json.dumps(valid_manifest()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/check_submission.py",
                    "--manifest",
                    str(manifest_path),
                    "--changed-file",
                    "solution/filter.py",
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
