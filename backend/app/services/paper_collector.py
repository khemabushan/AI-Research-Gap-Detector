"""
Orchestrates paper collection: calls both source clients concurrently,
deduplicates results, and persists them to the database against a Query.
"""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy.orm import Session

from app.models.db_models import Paper, PaperSource, Query, QueryStatus
from app.services.arxiv_client import ArxivClient
from app.services.semantic_scholar_client import SemanticScholarClient
from app.utils.dedup import deduplicate_papers
from app.utils.exceptions import NoPapersFoundError, PaperSourceError

logger = logging.getLogger(__name__)


class PaperCollectorService:
    def __init__(
        self,
        arxiv_client: ArxivClient | None = None,
        semantic_scholar_client: SemanticScholarClient | None = None,
    ):
        self.arxiv_client = arxiv_client or ArxivClient()
        self.semantic_scholar_client = semantic_scholar_client or SemanticScholarClient()

    async def collect(self, topic: str, max_results_per_source: int, db: Session) -> Query:
        """
        Creates a Query row, fetches papers from both sources (best-effort —
        one source failing does not abort the whole request), deduplicates,
        persists Paper rows, and returns the populated Query.
        """
        query = Query(topic=topic, status=QueryStatus.COLLECTING)
        db.add(query)
        db.commit()
        db.refresh(query)

        arxiv_results, s2_results = await self._fetch_all_sources(topic, max_results_per_source)
        combined = arxiv_results + s2_results

        if not combined:
            query.status = QueryStatus.FAILED
            db.commit()
            raise NoPapersFoundError(topic)

        deduped = deduplicate_papers(combined)

        for paper_dict in deduped:
            db.add(
                Paper(
                    query_id=query.id,
                    source=PaperSource(paper_dict["source"]),
                    external_id=paper_dict["external_id"] or paper_dict["title"][:100],
                    title=paper_dict["title"],
                    authors=paper_dict["authors"],
                    year=paper_dict["year"],
                    abstract=paper_dict["abstract"],
                    citation_count=paper_dict["citation_count"],
                    url=paper_dict["url"],
                )
            )

        query.status = QueryStatus.PENDING  # ready for /analyze
        db.commit()
        db.refresh(query)

        logger.info(
            "Collected %d unique papers for topic='%s' (arxiv=%d, semantic_scholar=%d)",
            len(deduped),
            topic,
            len(arxiv_results),
            len(s2_results),
        )
        return query

    async def _fetch_all_sources(
        self, topic: str, max_results: int
    ) -> tuple[list[dict], list[dict]]:
        """Fetch both sources concurrently; a failure in one does not sink the other."""
        results = await asyncio.gather(
            self._safe_fetch(self.arxiv_client.search, "arxiv", topic, max_results),
            self._safe_fetch(self.semantic_scholar_client.search, "semantic_scholar", topic, max_results),
        )
        return results[0], results[1]

    @staticmethod
    async def _safe_fetch(fetch_fn, source_name: str, topic: str, max_results: int) -> list[dict]:
        try:
            return await fetch_fn(topic, max_results)
        except PaperSourceError as exc:
            logger.warning("Source '%s' failed, continuing without it: %s", source_name, exc)
            return []
