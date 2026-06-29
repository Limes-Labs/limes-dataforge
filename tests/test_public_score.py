from __future__ import annotations

import unittest

from harness.curation import load_documents, public_score


class PublicScoreTests(unittest.TestCase):
    def test_loads_smoke_documents(self) -> None:
        documents = load_documents()
        self.assertGreaterEqual(len(documents), 4)
        self.assertTrue(all("id" in doc and "text" in doc for doc in documents))

    def test_public_score_has_required_fields(self) -> None:
        score = public_score()
        for field in [
            "public_proxy_loss",
            "baseline_public_proxy_loss",
            "public_proxy_delta",
            "public_proxy_improvement",
            "kept_ratio",
            "dedup_rate",
            "selected_document_count",
            "selected_byte_count",
            "selection_hash",
            "baseline_name",
            "baseline_document_count",
            "baseline_selection_hash",
            "runtime_seconds",
            "dataset_hash",
        ]:
            self.assertIn(field, score)
        self.assertGreater(score["public_proxy_loss"], 0.0)
        self.assertGreater(score["baseline_public_proxy_loss"], 0.0)
        self.assertAlmostEqual(
            score["public_proxy_delta"],
            score["public_proxy_loss"] - score["baseline_public_proxy_loss"],
        )
        self.assertAlmostEqual(
            score["public_proxy_improvement"],
            score["baseline_public_proxy_loss"] - score["public_proxy_loss"],
        )
        self.assertGreaterEqual(score["kept_ratio"], 0.0)
        self.assertLessEqual(score["kept_ratio"], 1.0)
        self.assertGreaterEqual(score["selected_document_count"], 0)
        self.assertEqual(len(score["selection_hash"]), 64)
        self.assertEqual(len(score["baseline_selection_hash"]), 64)

    def test_public_score_does_not_publish_hidden_metrics(self) -> None:
        score = public_score()
        self.assertNotIn("hidden_val_loss", score)
        self.assertNotIn("public_val_loss", score)


if __name__ == "__main__":
    unittest.main()
