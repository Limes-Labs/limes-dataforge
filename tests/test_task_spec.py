from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TaskSpecTests(unittest.TestCase):
    def setUp(self) -> None:
        self.challenge = json.loads((ROOT / "challenge.json").read_text(encoding="utf-8"))
        self.contract = json.loads((ROOT / "verifier/replay-contract.json").read_text(encoding="utf-8"))
        self.spec = json.loads((ROOT / self.contract["task_spec_path"]).read_text(encoding="utf-8"))

    def test_task_spec_matches_challenge(self) -> None:
        self.assertEqual(self.spec["challenge"], self.challenge["id"])
        self.assertTrue(self.spec["public_surface"]["candidate_only"])
        self.assertEqual(self.spec["public_surface"]["official_metric"], self.challenge["score"]["primaryMetric"])

    def test_every_hook_points_to_editable_file_and_declares_hidden_axes(self) -> None:
        editable = set(self.challenge["editablePaths"])
        hook_ids = {hook["id"] for hook in self.spec["curation_hooks"]}
        self.assertEqual(hook_ids, {"filter", "rank_documents", "dedup", "curriculum"})
        for hook in self.spec["curation_hooks"]:
            with self.subTest(hook=hook["id"]):
                self.assertIn(hook["editable_file"], editable)
                self.assertTrue((ROOT / hook["editable_file"]).exists())
                self.assertGreaterEqual(len(hook["research_questions"]), 2)
                self.assertGreaterEqual(len(hook["hidden_replay_axes"]), 3)
                self.assertGreaterEqual(len(hook["invalid_patterns"]), 2)

    def test_official_replay_axes_record_hashes_and_failures(self) -> None:
        axes = {axis["id"]: axis for axis in self.spec["official_replay_axes"]}
        self.assertIn("hidden-shard-replay", axes)
        self.assertIn("repeated-seed-promotion", axes)
        self.assertIn("scaling-audit", axes)
        self.assertIn("dataset_hash", axes["hidden-shard-replay"]["must_record"])
        self.assertIn("selection_hash", axes["hidden-shard-replay"]["must_record"])
        self.assertIn("failure_modes", axes["scaling-audit"]["must_record"])


if __name__ == "__main__":
    unittest.main()
