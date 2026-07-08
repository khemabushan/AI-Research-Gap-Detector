"""
Client for the Semantic Scholar Graph API
(https://api.semanticscholar.org/graph/v1).

Works without an API key at a low rate limit; set SEMANTIC_SCHOLAR_API_KEY
in .env for higher limits.
"""
from __future__ import annotations

import logging

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.utils.exceptions import PaperSourceError
from app.utils.text_cleaning import normalize_whitespace

logger = logging.getLogger(__name__)

_FIELDS = "title,authors,year,abstract,citationCount,externalIds,url"


class SemanticScholarClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: float = 20.0):
        self.base_url = base_url or settings.semantic_scholar_base_url
        self.api_key = api_key if api_key is not None else settings.semantic_scholar_api_key
        self.timeout = timeout

    def _headers(self) -> dict:
        return {"x-api-key": self.api_key} if self.api_key else {}

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    async def search(self, topic: str, max_results: int = 15) -> list[dict]:
        """
        Search Semantic Scholar for a topic and return normalized paper dicts:
        {source, external_id, title, authors, year, abstract, citation_count, url}
        """
        params = {
            "query": topic,
            "limit": max_results,
            "fields": _FIELDS,
        }

        try:
            async with httpx.AsyncClient(
    timeout=self.timeout,
    follow_redirects=True,
) as client:
                response = await client.get(
                    f"{self.base_url}/paper/search",
                    params=params,
                    headers=self._headers(),
                )
                if response.status_code == 429:
                    logger.warning("Semantic Scholar rate limit reached.")
                    raise PaperSourceError(
                        "semantic_scholar",
                        "Semantic Scholar rate limit reached."
                    )

                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Semantic Scholar request failed: %s", exc)
            raise PaperSourceError("semantic_scholar", str(exc)) from exc

        payload = response.json()
        return [self._normalize(item) for item in payload.get("data", []) if item.get("abstract")]

    @staticmethod
    def _normalize(item: dict) -> dict:
        authors = [
            normalize_whitespace(author.get("name", ""))
            for author in item.get("authors", [])
            if author.get("name")
        ]

        external_ids = item.get("externalIds") or {}
        external_id = (
            external_ids.get("DOI")
            or external_ids.get("ArXiv")
            or item.get("paperId")
            or ""
        )

        return {
            "source": "semantic_scholar",
            "external_id": str(external_id),
            "title": normalize_whitespace(item.get("title", "")),
            "authors": authors,
            "year": item.get("year"),
            "abstract": normalize_whitespace(item.get("abstract") or ""),
            "citation_count": item.get("citationCount"),
            "url": item.get("url"),
        }
