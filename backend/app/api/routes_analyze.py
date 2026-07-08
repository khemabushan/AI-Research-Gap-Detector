"""
POST /analyze — runs structured extraction (Problem/Methodology/Dataset/
Model/Limitations/Future Work) on every paper for a query, then builds the
FAISS embedding index for that query.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Query, QueryStatus
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, ExtractionResponse
from app.services.extraction_service import ExtractionService
from app.services.vector_store import VectorStoreService
from app.utils.exceptions import QueryNotFoundError, VectorStoreError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_papers(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    query = db.get(Query, request.query_id)
    if query is None:
        raise HTTPException(status_code=404, detail=f"Query id={request.query_id} not found")
    if not query.papers:
        raise HTTPException(status_code=400, detail="Query has no papers to analyze")

    query.status = QueryStatus.EXTRACTING
    db.commit()

    extraction_service = ExtractionService()
    extractions, failed_ids = await extraction_service.extract_and_persist_all(query.papers, db)

    if not extractions:
        query.status = QueryStatus.FAILED
        db.commit()
        raise HTTPException(
            status_code=502,
            detail="Extraction failed for all papers — check OPENAI_API_KEY and try again.",
        )

    # Refresh papers so paper.extraction relationships are populated before indexing.
    db.refresh(query)
    papers_with_extractions = [p for p in query.papers if p.extraction is not None]

    try:
        vector_store = VectorStoreService()
        vector_store.build_index_for_query(query.id, papers_with_extractions, db)
    except VectorStoreError as exc:
        logger.error("Vector index build failed for query_id=%s: %s", query.id, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    query.status = QueryStatus.DONE
    db.commit()

    return AnalyzeResponse(
        query_id=query.id,
        status=query.status,
        papers_processed=len(extractions),
        papers_failed=len(failed_ids),
        extractions=[ExtractionResponse.model_validate(e) for e in extractions],
    )
