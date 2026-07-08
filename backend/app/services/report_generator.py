"""
Generates future research directions and novel project ideas grounded in
previously identified gaps, and persists the final GapReport row.
"""
from __future__ import annotations

import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db_models import GapReport, Query
from app.prompts.gap_synthesis_prompt import (
    FUTURE_DIRECTIONS_SYSTEM_PROMPT,
    FUTURE_DIRECTIONS_USER_TEMPLATE,
)
from app.utils.exceptions import InsufficientDataError

logger = logging.getLogger(__name__)


class ProjectIdeaResult(BaseModel):
    title: str
    description: str
    grounded_in_gap: str
    novelty_rationale: str
    suggested_approach: str


class FutureDirectionsResult(BaseModel):
    future_directions: list[str] = Field(description="List of future research direction statements")
    novel_project_ideas: list[ProjectIdeaResult]


class ReportGeneratorService:
    def __init__(self, model_name: str | None = None):
        self.llm = ChatOpenAI(
            model=model_name or settings.openai_model,
            temperature=0.5,
            api_key=settings.openai_api_key,
        )
        self.structured_llm = self.llm.with_structured_output(FutureDirectionsResult)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", FUTURE_DIRECTIONS_SYSTEM_PROMPT),
                ("human", FUTURE_DIRECTIONS_USER_TEMPLATE),
            ]
        )

    async def generate_future_directions(
        self, topic: str, identified_gaps: list[str], num_ideas: int = 5
    ) -> FutureDirectionsResult:
        if not identified_gaps:
            raise InsufficientDataError(
                "No identified gaps available — run /research-gaps before /future-directions."
            )

        chain = self.prompt | self.structured_llm
        result: FutureDirectionsResult = await chain.ainvoke(
            {
                "topic": topic,
                "gaps_json": json.dumps(identified_gaps, indent=2),
                "num_ideas": num_ideas,
            }
        )
        return result

    @staticmethod
    def upsert_gap_report(
        db: Session,
        query: Query,
        summary: str | None = None,
        identified_gaps: list[str] | None = None,
        cluster_summary: list[dict] | None = None,
        future_directions: list[str] | None = None,
        novel_project_ideas: list[dict] | None = None,
    ) -> GapReport:
        """
        Creates the GapReport row if absent, otherwise updates only the
        fields provided — /research-gaps and /future-directions populate
        this incrementally.
        """
        report = query.gap_report
        if report is None:
            report = GapReport(query_id=query.id)
            db.add(report)

        if summary is not None:
            report.summary = summary
        if identified_gaps is not None:
            report.identified_gaps = identified_gaps
        if cluster_summary is not None:
            report.cluster_summary = cluster_summary
        if future_directions is not None:
            report.future_directions = future_directions
        if novel_project_ideas is not None:
            report.novel_project_ideas = novel_project_ideas

        db.commit()
        db.refresh(report)
        return report
