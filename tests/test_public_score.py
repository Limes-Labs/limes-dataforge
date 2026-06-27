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
        for field in ["public_proxy_loss", "kept_ratio", "dedup_rate", "runtime_seconds", "dataset_hash"]:
            self.assertIn(field, score)
        self.assertGreater(score["public_proxy_loss"], 0.0)
        self.assertGreaterEqual(score["kept_ratio"], 0.0)
        self.assertLessEqual(score["kept_ratio"], 1.0)


if __name__ == "__main__":
    unittest.main()
