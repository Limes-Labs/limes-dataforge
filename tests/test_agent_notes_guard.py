from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.agent_notes_guard import load_json, validate_notes


ROOT = Path(__file__).resolve().parents[1]


class AgentNotesGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.notes = load_json(ROOT / "templates/agent-notes.example.json")

    def test_example_notes_pass(self) -> None:
        self.assertEqual(validate_notes(self.notes), [])

    def test_requires_exactly_one_selected_attempt(self) -> None:
        notes = copy.deepcopy(self.notes)
        notes["attempts"][0]["status"] = "selected"
        errors = validate_notes(notes)
        self.assertTrue(any("exactly one selected" in error for error in errors))

    def test_rejects_missing_negative_findings(self) -> None:
        notes = copy.deepcopy(self.notes)
        notes["negative_or_mixed_findings"] = []
        errors = validate_notes(notes)
        self.assertTrue(any("negative_or_mixed_findings" in error for error in errors))

    def test_rejects_unknown_selected_attempt_id(self) -> None:
        notes = copy.deepcopy(self.notes)
        notes["selection_summary"]["selected_attempt_id"] = "missing-attempt"
        errors = validate_notes(notes)
        self.assertTrue(any("selected_attempt_id" in error for error in errors))

    def test_cli_accepts_example_notes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_agent_notes.py",
                "--input",
                "templates/agent-notes.example.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"ok": true', result.stdout)

    def test_cli_rejects_bad_notes(self) -> None:
        notes = copy.deepcopy(self.notes)
        notes["attempts"][1]["public_score"].pop("public_proxy_loss")
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_path = Path(temp_dir) / "bad-agent-notes.json"
            bad_path.write_text(json.dumps(notes), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_agent_notes.py",
                    "--input",
                    str(bad_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public_score missing fields", result.stdout)


if __name__ == "__main__":
    unittest.main()
