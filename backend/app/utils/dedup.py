"""
Deduplicates papers collected from multiple sources (arXiv + Semantic
Scholar) using normalized-title exact matching plus a fuzzy fallback via
difflib, which is stdlib-only and avoids adding another dependency.
"""
from __future__ import annotations

from difflib import SequenceMatcher

from app.utils.text_cleaning import normalize_title_for_dedup

FUZZY_MATCH_THRESHOLD = 0.92


def _titles_similar(a: str, b: str) -> bool:
    if not a or not b:
        return False
    return SequenceMatcher(None, a, b).ratio() >= FUZZY_MATCH_THRESHOLD


def deduplicate_papers(papers: list[dict]) -> list[dict]:
    """
    Deduplicate a list of paper dicts (each must have a 'title' key).
    When two papers are judged duplicates, the one with a longer abstract
    (usually the richer / more complete record) is kept, and its
    citation_count is upgraded from the other if higher.
    """
    deduped: list[dict] = []
    normalized_seen: list[str] = []

    for paper in papers:
        norm_title = normalize_title_for_dedup(paper.get("title", ""))
        if not norm_title:
            continue

        match_index = None
        for idx, seen_title in enumerate(normalized_seen):
            if norm_title == seen_title or _titles_similar(norm_title, seen_title):
                match_index = idx
                break

        if match_index is None:
            deduped.append(paper)
            normalized_seen.append(norm_title)
        else:
            existing = deduped[match_index]
            existing_abstract_len = len(existing.get("abstract") or "")
            new_abstract_len = len(paper.get("abstract") or "")

            merged = existing if existing_abstract_len >= new_abstract_len else paper
            # Keep whichever citation count is higher/known.
            merged["citation_count"] = max(
                existing.get("citation_count") or 0,
                paper.get("citation_count") or 0,
            )
            deduped[match_index] = merged

    return deduped
