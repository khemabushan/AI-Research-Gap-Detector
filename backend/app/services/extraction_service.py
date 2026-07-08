"""
Uses LangChain + OpenAI structured output to extract Problem / Methodology /
Dataset / Model / Limitations / Future Work from each paper's abstract.
"""
from __future__ import annotations

import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db_models import Extraction, Paper
from app.prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE
from app.utils.exceptions import ExtractionError
from app.utils.text_cleaning import truncate

logger = logging.getLogger(__name__)


class ExtractedFields(BaseModel):
    """Structured output schema — LangChain binds this to the LLM call so the
    response is guaranteed to be parseable, rather than hoping the model
    returns well-formed JSON."""

    problem: str = Field(description="The specific problem or research question addressed")
    methodology: str = Field(description="The core technical approach or method used")
    dataset: str = Field(description="Dataset(s) used, or 'Not specified'")
    model: str = Field(description="Model/architecture name, or 'Not specified'")
    limitations: str = Field(description="Stated limitations, or 'Not specified'")
    future_work: str = Field(description="Stated future work, or 'Not specified'")


class ExtractionService:
    def __init__(self, model_name: str | None = None, temperature: float = 0.0):
        self.llm = ChatOpenAI(
            model=model_name or settings.openai_model,
            temperature=temperature,
            api_key=settings.openai_api_key,
        )
        self.structured_llm = self.llm.with_structured_output(ExtractedFields)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EXTRACTION_SYSTEM_PROMPT),
                ("human", EXTRACTION_USER_TEMPLATE),
            ]
        )

    async def extract_one(self, paper: Paper) -> ExtractedFields:
        chain = self.prompt | self.structured_llm
        try:
            result: ExtractedFields = await chain.ainvoke(
                {"title": paper.title, "abstract": truncate(paper.abstract, 3000)}
            )
            return result
        except Exception as exc:  # LangChain/OpenAI can raise various error types
            logger.error("Extraction failed for paper_id=%s: %s", paper.id, exc)
            raise ExtractionError(paper.id, str(exc)) from exc

    async def extract_and_persist_all(
        self, papers: list[Paper], db: Session
    ) -> tuple[list[Extraction], list[int]]:
        """
        Runs extraction sequentially (kept simple/predictable for a resume
        project; swap to asyncio.gather with a semaphore if throughput
        becomes a concern) and persists successful results.

        Returns (extractions, failed_paper_ids).
        """
        extractions: list[Extraction] = []
        failed_ids: list[int] = []

        for paper in papers:
            try:
                fields = await self.extract_one(paper)
            except ExtractionError:
                failed_ids.append(paper.id)
                continue

            extraction = Extraction(
                paper_id=paper.id,
                problem=fields.problem,
                methodology=fields.methodology,
                dataset=fields.dataset,
                model=fields.model,
                limitations=fields.limitations,
                future_work=fields.future_work,
            )
            db.add(extraction)
            extractions.append(extraction)

        db.commit()
        for extraction in extractions:
            db.refresh(extraction)

        return extractions, failed_ids
