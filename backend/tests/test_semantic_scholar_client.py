"""
Unit tests for SemanticScholarClient using respx-mocked HTTP responses.
"""
import httpx
import pytest
import respx

from app.services.semantic_scholar_client import SemanticScholarClient

SAMPLE_JSON_RESPONSE = {
    "data": [
        {
            "paperId": "abc123",
            "title": "Deep Learning for Brain Tumor Segmentation",
            "abstract": "We propose a U-Net based approach for segmenting brain tumors.",
            "year": 2022,
            "citationCount": 57,
            "authors": [{"name": "Alice Zhang"}, {"name": "Bob Lee"}],
            "externalIds": {"DOI": "10.1234/abcd"},
            "url": "https://www.semanticscholar.org/paper/abc123",
        },
        {
            # Paper with no abstract should be filtered out.
            "paperId": "def456",
            "title": "A Paper With No Abstract",
            "abstract": None,
            "year": 2021,
            "citationCount": 3,
            "authors": [],
            "externalIds": {},
            "url": None,
        },
    ]
}


@pytest.mark.asyncio
@respx.mock
async def test_search_normalizes_and_filters_results():
    respx.get("https://api.semanticscholar.org/graph/v1/paper/search").mock(
        return_value=httpx.Response(200, json=SAMPLE_JSON_RESPONSE)
    )

    client = SemanticScholarClient()
    results = await client.search("brain tumor segmentation", max_results=10)

    assert len(results) == 1  # paper without abstract filtered out
    paper = results[0]
    assert paper["source"] == "semantic_scholar"
    assert paper["external_id"] == "10.1234/abcd"
    assert paper["citation_count"] == 57
    assert paper["authors"] == ["Alice Zhang", "Bob Lee"]


@pytest.mark.asyncio
@respx.mock
async def test_search_raises_on_http_error():
    from app.utils.exceptions import PaperSourceError

    respx.get("https://api.semanticscholar.org/graph/v1/paper/search").mock(
        return_value=httpx.Response(429, text="Too Many Requests")
    )

    client = SemanticScholarClient()
    with pytest.raises(PaperSourceError):
        await client.search("test topic")
