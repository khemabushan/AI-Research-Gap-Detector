"""
GET /queries/{query_id} — returns the full current state of a query:
papers, extractions (if analyzed), and the gap report (if generated).

This is the read counterpart to the write-oriented /search, /analyze,
/research-gaps, /future-directions endpoints — it's what lets a client
reload or deep-link into a query's results instead of only being able to
see them once, immediately after each POST call.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Query
from app.models.schemas import (
    ExtractionResponse,
    GapReportSummary,
    PaperResponse,
    QueryDetailResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["queries"])


@router.get("/queries/{query_id}", response_model=QueryDetailResponse)
async def get_query(query_id: int, db: Session = Depends(get_db)) -> QueryDetailResponse:
    query = db.get(Query, query_id)
    if query is None:
        raise HTTPException(status_code=404, detail=f"Query id={query_id} not found")

    gap_report = None
    if query.gap_report is not None:
        gap_report = GapReportSummary.model_validate(query.gap_report)

    return QueryDetailResponse(
        query_id=query.id,
        topic=query.topic,
        status=query.status,
        created_at=query.created_at,
        total_papers=len(query.papers),
        papers=[PaperResponse.model_validate(p) for p in query.papers],
        extractions=[
            ExtractionResponse.model_validate(p.extraction) for p in query.papers if p.extraction
        ],
        gap_report=gap_report,
    )
