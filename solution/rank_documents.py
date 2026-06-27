from __future__ import annotations


def score_document(document: dict, config: dict) -> float:
    """Return a ranking score. Higher-ranked documents are selected first."""
    text = str(document.get("text", ""))
    words = text.lower().split()
    keywords = set(str(item).lower() for item in config.get("keywords", []))
    keyword_hits = sum(1 for word in words if word.strip(".,:;!?()[]") in keywords)
    length_weight = float(config.get("rank_length_weight", 0.0))
    keyword_weight = float(config.get("rank_keyword_weight", 1.0))
    return keyword_weight * keyword_hits + length_weight * min(len(text), 1000) / 100.0
