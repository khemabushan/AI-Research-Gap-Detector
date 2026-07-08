"""
Detects research gaps by:
1. Clustering papers using their FAISS embeddings (KMeans over the vectors
   reconstructed from the index).
2. Summarizing each cluster's common methods/datasets/limitations from the
   structured extractions.
3. Feeding cluster summaries (not raw abstracts) to an LLM to synthesize an
   executive summary and a list of concrete identified gaps.

Cluster summaries are used as the LLM input (rather than raw text) to keep
token usage bounded and to ground the LLM's reasoning in already-extracted,
verifiable structured fields.
"""
from __future__ import annotations

import json
import logging
import math

import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from sklearn.cluster import KMeans
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db_models import Paper
from app.prompts.gap_synthesis_prompt import (
    GAP_SYNTHESIS_SYSTEM_PROMPT,
    GAP_SYNTHESIS_USER_TEMPLATE,
)
from app.services.vector_store import VectorStoreService
from app.utils.exceptions import InsufficientDataError

logger = logging.getLogger(__name__)

MIN_PAPERS_FOR_ANALYSIS = 3


class GapSynthesisResult(BaseModel):
    summary: str = Field(description="Executive summary of the research landscape")
    identified_gaps: list[str] = Field(description="List of concrete, specific research gaps")


class GapDetectionService:
    def __init__(
        self,
        vector_store: VectorStoreService | None = None,
        model_name: str | None = None,
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.llm = ChatOpenAI(
            model=model_name or settings.openai_model,
            temperature=0.3,
            api_key=settings.openai_api_key,
        )
        self.structured_llm = self.llm.with_structured_output(GapSynthesisResult)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", GAP_SYNTHESIS_SYSTEM_PROMPT),
                ("human", GAP_SYNTHESIS_USER_TEMPLATE),
            ]
        )

    def cluster_papers(
        self, query_id: int, papers: list[Paper], num_clusters: int | None = None
    ) -> list[dict]:
        """
        Clusters papers by embedding similarity and returns a list of cluster
        summary dicts: {cluster_id, paper_ids, common_methods, common_datasets,
        limitations}.
        """
        if len(papers) < MIN_PAPERS_FOR_ANALYSIS:
            raise InsufficientDataError(
                f"Need at least {MIN_PAPERS_FOR_ANALYSIS} papers with extractions to detect gaps, "
                f"got {len(papers)}."
            )

        index = self.vector_store.load_index_for_query(query_id)
        vectors = index.reconstruct_n(0, index.ntotal)

        k = num_clusters or self._estimate_k(len(papers))
        k = min(k, len(papers))

        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(vectors)

        clusters: list[dict] = []
        for cluster_id in sorted(set(labels)):
            member_indices = [i for i, label in enumerate(labels) if label == cluster_id]
            member_papers = [papers[i] for i in member_indices]
            clusters.append(self._summarize_cluster(cluster_id, member_papers))

        return clusters

    @staticmethod
    def _estimate_k(num_papers: int) -> int:
        """Heuristic: roughly sqrt(n/2) clusters, bounded to [2, 8]."""
        estimate = max(2, round(math.sqrt(num_papers / 2)))
        return min(estimate, 8)

    @staticmethod
    def _summarize_cluster(cluster_id: int, papers: list[Paper]) -> dict:
        methods = [p.extraction.model for p in papers if p.extraction and p.extraction.model]
        datasets = [p.extraction.dataset for p in papers if p.extraction and p.extraction.dataset]
        limitations = [
            p.extraction.limitations for p in papers if p.extraction and p.extraction.limitations
        ]

        return {
            "cluster_id": int(cluster_id),
            "paper_ids": [p.id for p in papers],
            "paper_titles": [p.title for p in papers],
            "common_methods": sorted(set(m for m in methods if m.lower() != "not specified")),
            "common_datasets": sorted(set(d for d in datasets if d.lower() != "not specified")),
            "limitations": limitations,
        }

    async def synthesize_gaps(self, topic: str, clusters: list[dict]) -> GapSynthesisResult:
        """Calls the LLM with cluster summaries to produce the gap narrative."""
        chain = self.prompt | self.structured_llm

        # Trim paper_ids/titles from the LLM payload — it only needs the
        # thematic content to reason about gaps.
        llm_clusters = [
            {
                "cluster_id": c["cluster_id"],
                "common_methods": c["common_methods"],
                "common_datasets": c["common_datasets"],
                "limitations": c["limitations"][:5],  # cap to avoid token bloat
            }
            for c in clusters
        ]

        result: GapSynthesisResult = await chain.ainvoke(
            {
                "topic": topic,
                "clusters_json": json.dumps(llm_clusters, indent=2),
            }
        )
        return result
