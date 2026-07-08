"""
Client for the arXiv API (http://export.arxiv.org/api/query).

arXiv returns Atom XML, not JSON, and has an informal rate limit of
~1 request per 3 seconds per the API terms of use — we respect that via
a delay in the collector layer, not here, so this client stays stateless
and testable in isolation.
"""
from __future__ import annotations

import logging
from xml.etree import ElementTree as ET

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.utils.exceptions import PaperSourceError
from app.utils.text_cleaning import normalize_whitespace, strip_latex_artifacts

logger = logging.getLogger(__name__)

_ATOM_NS = "{http://www.w3.org/2005/Atom}"
_ARXIV_NS = "{http://arxiv.org/schemas/atom}"


class ArxivClient:
    def __init__(self, base_url: str | None = None, timeout: float = 20.0):
        self.base_url = base_url or settings.arxiv_base_url
        self.timeout = timeout

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def search(self, topic: str, max_results: int = 15) -> list[dict]:
        """
        Search arXiv for a topic and return a list of normalized paper dicts:
        {source, external_id, title, authors, year, abstract, citation_count, url}

        arXiv does not expose citation counts, so citation_count is always None.
        """
        params = {
            "search_query": f"all:{topic}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("arXiv request failed: %s", exc)
            raise PaperSourceError("arxiv", str(exc)) from exc

        return self._parse_feed(response.text)

    def _parse_feed(self, xml_text: str) -> list[dict]:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise PaperSourceError("arxiv", f"Failed to parse Atom response: {exc}") from exc

        papers: list[dict] = []
        for entry in root.findall(f"{_ATOM_NS}entry"):
            papers.append(self._parse_entry(entry))
        return papers

    def _parse_entry(self, entry: ET.Element) -> dict:
        raw_id = self._text(entry, f"{_ATOM_NS}id")
        # e.g. http://arxiv.org/abs/2301.01234v1 -> 2301.01234
        external_id = raw_id.rsplit("/", 1)[-1].split("v")[0] if raw_id else ""

        title = normalize_whitespace(self._text(entry, f"{_ATOM_NS}title"))
        abstract = strip_latex_artifacts(self._text(entry, f"{_ATOM_NS}summary"))

        authors = [
            normalize_whitespace(self._text(author, f"{_ATOM_NS}name"))
            for author in entry.findall(f"{_ATOM_NS}author")
        ]

        published = self._text(entry, f"{_ATOM_NS}published")
        year = int(published[:4]) if published[:4].isdigit() else None

        return {
            "source": "arxiv",
            "external_id": external_id,
            "title": title,
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "citation_count": None,
            "url": raw_id,
        }

    @staticmethod
    def _text(element: ET.Element, tag: str) -> str:
        node = element.find(tag)
        return node.text.strip() if node is not None and node.text else ""
