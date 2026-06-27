from __future__ import annotations


def order_documents(documents: list[dict], config: dict) -> list[dict]:
    """Return the final training order for selected documents."""
    mode = str(config.get("curriculum", "short_to_long"))
    if mode == "long_to_short":
        return sorted(documents, key=lambda doc: (-len(str(doc.get("text", ""))), str(doc.get("id", ""))))
    if mode == "source_then_short":
        return sorted(documents, key=lambda doc: (str(doc.get("source", "")), len(str(doc.get("text", "")))))
    return sorted(documents, key=lambda doc: (len(str(doc.get("text", ""))), str(doc.get("id", ""))))
