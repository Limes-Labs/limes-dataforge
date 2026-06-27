from __future__ import annotations


def keep_document(document: dict, config: dict) -> bool:
    """Return True when a document should stay in the selected training mix."""
    text = str(document.get("text", "")).strip()
    source = str(document.get("source", ""))
    min_chars = int(config.get("min_chars", 0))
    max_chars = int(config.get("max_chars", 10_000_000))
    preferred_sources = set(config.get("preferred_sources", []))

    if len(text) < min_chars or len(text) > max_chars:
        return False
    if preferred_sources and source not in preferred_sources:
        return False
    return True
