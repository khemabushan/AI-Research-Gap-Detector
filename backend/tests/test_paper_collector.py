"""
Unit tests for the deduplication utility used by PaperCollectorService.
These test the pure dedup logic directly rather than the full async
collector, which requires a live DB session (see integration tests / manual
testing notes in README for full-flow verification).
"""
from app.utils.dedup import deduplicate_papers


def test_deduplicate_exact_title_match_keeps_richer_record():
    papers = [
        {
            "source": "arxiv",
            "title": "Brain Tumor Segmentation using Deep Learning",
            "abstract": "Short abstract.",
            "citation_count": None,
        },
        {
            "source": "semantic_scholar",
            "title": "Brain Tumor Segmentation using Deep Learning",
            "abstract": "A much longer and more detailed abstract describing the full methodology.",
            "citation_count": 42,
        },
    ]

    result = deduplicate_papers(papers)

    assert len(result) == 1
    assert result[0]["source"] == "semantic_scholar"  # longer abstract wins
    assert result[0]["citation_count"] == 42


def test_deduplicate_fuzzy_title_match():
    papers = [
        {"source": "arxiv", "title": "Brain Tumor Segmentation Using Deep Learning", "abstract": "A"},
        {"source": "semantic_scholar", "title": "Brain tumor segmentation using deep learning.", "abstract": "B longer"},
    ]

    result = deduplicate_papers(papers)
    assert len(result) == 1


def test_deduplicate_distinct_titles_kept_separate():
    papers = [
        {"source": "arxiv", "title": "Brain Tumor Segmentation using Deep Learning", "abstract": "A"},
        {"source": "arxiv", "title": "Lung Cancer Detection using CNNs", "abstract": "B"},
    ]

    result = deduplicate_papers(papers)
    assert len(result) == 2


def test_deduplicate_handles_empty_list():
    assert deduplicate_papers([]) == []
