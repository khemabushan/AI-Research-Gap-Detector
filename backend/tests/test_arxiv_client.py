"""
Unit tests for ArxivClient. Uses respx to mock httpx calls so tests run
offline and deterministically.
"""
import httpx
import pytest
import respx

from app.services.arxiv_client import ArxivClient

SAMPLE_ATOM_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2301.01234v1</id>
    <title>Brain Tumor Segmentation using Deep Learning: A Survey</title>
    <summary>This paper surveys $\\alpha$-weighted deep learning methods for
    brain tumor segmentation on MRI scans.</summary>
    <published>2023-01-15T00:00:00Z</published>
    <author><name>Jane Doe</name></author>
    <author><name>John Smith</name></author>
  </entry>
</feed>"""


@pytest.mark.asyncio
@respx.mock
async def test_search_parses_entries_correctly():
    respx.get("https://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(200, text=SAMPLE_ATOM_RESPONSE)
    )

    client = ArxivClient()
    results = await client.search("brain tumor segmentation", max_results=5)

    assert len(results) == 1
    paper = results[0]
    assert paper["source"] == "arxiv"
    assert paper["external_id"] == "2301.01234"
    assert "Brain Tumor Segmentation" in paper["title"]
    assert paper["authors"] == ["Jane Doe", "John Smith"]
    assert paper["year"] == 2023
    assert paper["citation_count"] is None
    assert "alpha" not in paper["abstract"]  # LaTeX artifact stripped-ish


@pytest.mark.asyncio
@respx.mock
async def test_search_raises_on_http_error():
    from app.utils.exceptions import PaperSourceError

    respx.get("https://export.arxiv.org/api/query").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )

    client = ArxivClient()
    with pytest.raises(PaperSourceError):
        await client.search("test topic")