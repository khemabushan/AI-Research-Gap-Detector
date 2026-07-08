"""
POST /search — collects papers for a topic from arXiv + Semantic Scholar,
deduplicates, and persists them.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import PaperResponse, SearchRequest, SearchResponse
from app.services.paper_collector import PaperCollectorService
from app.utils.exceptions import NoPapersFoundError, PaperSourceError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_papers(
    request: SearchRequest,
    db: Session = Depends(get_db),
) -> SearchResponse:
    collector = PaperCollectorService()

    try:
        query = await collector.collect(
            topic=request.topic,
            max_results_per_source=request.max_results_per_source,
            db=db,
        )
    except NoPapersFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PaperSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return SearchResponse(
        query_id=query.id,
        topic=query.topic,
        total_papers=len(query.papers),
        papers=[PaperResponse.model_validate(p) for p in query.papers],
    )
