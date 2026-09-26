from __future__ import annotations

import re

from langchain_core.documents import Document


STOP_WORDS = {
    "a", "about", "after", "all", "an", "and", "any", "are", "as", "at", "be", "before", "but",
    "can", "could", "do", "does", "for", "from", "get", "how", "i", "in", "is", "it", "me", "my",
    "of", "on", "or", "the", "their", "there", "this", "to", "up", "use", "vidzy", "what", "when",
    "where", "which", "while", "will", "with", "work", "would", "you", "your",
}


def _terms(text: str) -> set[str]:
    terms: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if token in STOP_WORDS or len(token) < 3:
            continue
        for suffix in ("ing", "ed", "es", "s"):
            if token.endswith(suffix) and len(token) - len(suffix) >= 4:
                token = token[: -len(suffix)]
                break
        terms.add(token)
    return terms


def has_lexical_support(query: str, document: Document) -> bool:
    """Reject semantic neighbors that share only generic product wording."""
    return bool(_terms(query).intersection(_terms(document.page_content)))


def classify_confidence(
    query: str,
    results,
    *,
    direct_threshold: float,
    related_threshold: float,
    ambiguity_margin: float,
) -> str:
    if not results:
        return "no_reliable_answer"
    top = results[0]
    if top.score < related_threshold or not has_lexical_support(query, top.document):
        return "no_reliable_answer"
    second_score = results[1].score if len(results) > 1 else 0.0
    if top.score < direct_threshold or top.score - second_score < ambiguity_margin:
        return "related_results"
    return "direct_answer"
