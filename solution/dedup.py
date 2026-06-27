from __future__ import annotations


def _fingerprint(document: dict) -> str:
    text = " ".join(str(document.get("text", "")).lower().split())
    return text


def deduplicate_documents(documents: list[dict], config: dict) -> list[dict]:
    """Return documents with exact normalized duplicate text removed."""
    seen: set[str] = set()
    result: list[dict] = []
    for document in documents:
        fingerprint = _fingerprint(document)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        result.append(document)
    return result
