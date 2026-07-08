"""
POST /research-gaps — clusters analyzed papers by embedding similarity and
uses an LLM to synthesize an executive summary + list of identified gaps.
Requires /analyze to have been run first for the given query_id.
"""
import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Query
from app.models.schemas import ClusterSummary, ResearchGapsRequest, ResearchGapsResponse
from app.services.gap_detection import GapDetectionService
from app.services.report_generator import ReportGeneratorService
from app.utils.exceptions import InsufficientDataError, VectorStoreError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["research-gaps"])


@router.post("/research-gaps", response_model=ResearchGapsResponse)
async def detect_research_gaps(
    request: ResearchGapsRequest,
    db: Session = Depends(get_db),
) -> ResearchGapsResponse:
    query = db.get(Query, request.query_id)
    if query is None:
        raise HTTPException(status_code=404, detail=f"Query id={request.query_id} not found")

    papers_with_extractions = [p for p in query.papers if p.extraction is not None]

    gap_service = GapDetectionService()

    try:
        clusters = gap_service.cluster_papers(
            query_id=query.id,
            papers=papers_with_extractions,
            num_clusters=request.num_clusters,
        )
    except (InsufficientDataError, VectorStoreError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        synthesis = await gap_service.synthesize_gaps(topic=query.topic, clusters=clusters)
        clusters = [
    {
        **c,
        "theme": ", ".join(c["common_methods"][:3]) or "Mixed approaches",
    }
    for c in clusters
]
    except Exception as exc:
        logger.error("Gap synthesis LLM call failed for query_id=%s: %s", query.id, exc)
        raise HTTPException(status_code=502, detail=f"Gap synthesis failed: {exc}") from exc

    # Compute the display theme once and store it alongside each cluster, so
    # the persisted cluster_summary (read back later via GET /queries/{id})
    # has the exact same shape as this endpoint's response — no drift
    # between what a fresh call returns and what a reload sees.
    enriched_clusters = [
        {**c, "theme": ", ".join(c["common_methods"][:3]) or "Mixed approaches"} for c in clusters
    ]

    report = ReportGeneratorService.upsert_gap_report(
        db=db,
        query=query,
        summary=synthesis.summary,
        identified_gaps=synthesis.identified_gaps,
        cluster_summary=clusters,
    )

    return ResearchGapsResponse(
        query_id=query.id,
        topic=query.topic,
        summary=report.summary,
        identified_gaps=report.identified_gaps,
        clusters=[
            ClusterSummary(
                cluster_id=c["cluster_id"],
                paper_ids=c["paper_ids"],
                theme=c["theme"],
                common_methods=c["common_methods"],
                common_datasets=c["common_datasets"],
            )
            for c in enriched_clusters
        ],
        generated_at=report.generated_at or datetime.datetime.utcnow(),
    )
