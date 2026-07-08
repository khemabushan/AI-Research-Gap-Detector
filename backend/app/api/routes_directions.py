"""
POST /future-directions — generates future research directions and novel,
concrete project ideas grounded in the gaps previously identified via
/research-gaps. Requires /research-gaps to have been run first.
"""
import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Query
from app.models.schemas import FutureDirectionsRequest, FutureDirectionsResponse, ProjectIdea
from app.services.report_generator import ReportGeneratorService
from app.utils.exceptions import InsufficientDataError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["future-directions"])


@router.post("/future-directions", response_model=FutureDirectionsResponse)
async def generate_future_directions(
    request: FutureDirectionsRequest,
    db: Session = Depends(get_db),
) -> FutureDirectionsResponse:
    query = db.get(Query, request.query_id)
    if query is None:
        raise HTTPException(status_code=404, detail=f"Query id={request.query_id} not found")

    if query.gap_report is None or not query.gap_report.identified_gaps:
        raise HTTPException(
            status_code=400,
            detail="No identified gaps found — call /research-gaps for this query_id first.",
        )

    report_service = ReportGeneratorService()

    try:
        result = await report_service.generate_future_directions(
            topic=query.topic,
            identified_gaps=query.gap_report.identified_gaps,
            num_ideas=request.num_ideas,
        )
    except InsufficientDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Future-directions LLM call failed for query_id=%s: %s", query.id, exc)
        raise HTTPException(status_code=502, detail=f"Future-direction generation failed: {exc}") from exc

    ideas_as_dicts = [idea.model_dump() for idea in result.novel_project_ideas]

    report = ReportGeneratorService.upsert_gap_report(
        db=db,
        query=query,
        future_directions=result.future_directions,
        novel_project_ideas=ideas_as_dicts,
    )

    return FutureDirectionsResponse(
        query_id=query.id,
        future_directions=report.future_directions,
        novel_project_ideas=[ProjectIdea(**idea) for idea in report.novel_project_ideas],
        generated_at=report.generated_at or datetime.datetime.utcnow(),
    )
