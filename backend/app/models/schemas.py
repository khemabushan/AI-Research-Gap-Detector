"""
Pydantic schemas for API request/response validation. Kept separate from
SQLAlchemy models (app/models/db_models.py) so the API contract can evolve
independently of the storage schema.
"""
from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.db_models import PaperSource, QueryStatus

# ---------------------------------------------------------------------------
# /search
# ---------------------------------------------------------------------------


class SearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, examples=["Brain Tumor Segmentation using Deep Learning"])
    max_results_per_source: int = Field(default=15, ge=1, le=50)


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: PaperSource
    external_id: str
    title: str
    authors: list[str]
    year: int | None
    abstract: str
    citation_count: int | None
    url: str | None


class SearchResponse(BaseModel):
    query_id: int
    topic: str
    total_papers: int
    papers: list[PaperResponse]


# ---------------------------------------------------------------------------
# /analyze
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    query_id: int


class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    paper_id: int
    problem: str
    methodology: str
    dataset: str
    model: str
    limitations: str
    future_work: str


class AnalyzeResponse(BaseModel):
    query_id: int
    status: QueryStatus
    papers_processed: int
    papers_failed: int
    extractions: list[ExtractionResponse]


# ---------------------------------------------------------------------------
# /research-gaps
# ---------------------------------------------------------------------------


class ResearchGapsRequest(BaseModel):
    query_id: int
    num_clusters: int | None = Field(
        default=None,
        ge=2,
        le=15,
        description="Optional override; auto-estimated from paper count if omitted.",
    )


class ClusterSummary(BaseModel):
    cluster_id: int
    paper_ids: list[int]
    theme: str
    common_methods: list[str]
    common_datasets: list[str]


class ResearchGapsResponse(BaseModel):
    query_id: int
    topic: str
    summary: str
    identified_gaps: list[str]
    clusters: list[ClusterSummary]
    generated_at: datetime.datetime


# ---------------------------------------------------------------------------
# /future-directions
# ---------------------------------------------------------------------------


class FutureDirectionsRequest(BaseModel):
    query_id: int
    num_ideas: int = Field(default=5, ge=1, le=10)


class ProjectIdea(BaseModel):
    title: str
    description: str
    grounded_in_gap: str
    novelty_rationale: str
    suggested_approach: str


class FutureDirectionsResponse(BaseModel):
    query_id: int
    future_directions: list[str]
    novel_project_ideas: list[ProjectIdea]
    generated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Shared / error
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


# ---------------------------------------------------------------------------
# GET /queries/{query_id}
# ---------------------------------------------------------------------------


class GapReportSummary(BaseModel):
    """
    Read-only view of a persisted GapReport row. cluster_summary and
    novel_project_ideas are stored as raw JSON on the model (see
    GapReport in db_models.py), so they're typed loosely here — the
    frontend's TypeScript types give them concrete shape on that side.
    """

    model_config = ConfigDict(from_attributes=True)

    summary: str
    identified_gaps: list[str]
    cluster_summary: list[dict]
    future_directions: list[str]
    novel_project_ideas: list[dict]
    generated_at: datetime.datetime


class QueryDetailResponse(BaseModel):
    """
    Full state of a query: papers, extractions (if /analyze has run), and
    the gap report (if /research-gaps + /future-directions have run).
    This is what lets the frontend re-fetch a query's results on page load
    or refresh instead of relying on client-side state that only exists
    right after a POST call.
    """

    query_id: int
    topic: str
    status: QueryStatus
    created_at: datetime.datetime
    total_papers: int
    papers: list[PaperResponse]
    extractions: list[ExtractionResponse]
    gap_report: GapReportSummary | None

