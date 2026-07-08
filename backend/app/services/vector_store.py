"""
Manages a FAISS index per query_id, persisted to disk under
FAISS_INDEX_DIR/{query_id}.index. Uses IndexFlatIP (inner product) over
L2-normalized vectors, which is mathematically equivalent to cosine
similarity search and is exact (no approximation) — appropriate at the
small scale (tens of papers) this project operates at.
"""
from __future__ import annotations

import logging
from pathlib import Path

import faiss
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db_models import Embedding, Paper
from app.services.embedding_service import EmbeddingService
from app.utils.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self, embedding_service: EmbeddingService | None = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.index_dir = Path(settings.faiss_index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def _index_path(self, query_id: int) -> Path:
        return self.index_dir / f"query_{query_id}.index"

    def build_index_for_query(
        self, query_id: int, papers: list[Paper], db: Session
    ) -> faiss.Index:
        """
        Embeds every paper's text (title + abstract + methodology if
        available), builds a fresh FAISS index, persists it to disk, and
        writes Embedding rows mapping paper_id -> position in the index.
        """
        if not papers:
            raise VectorStoreError("Cannot build an index with zero papers")

        texts = [
            self.embedding_service.build_paper_text(
                title=paper.title,
                abstract=paper.abstract,
                methodology=paper.extraction.methodology if paper.extraction else "",
            )
            for paper in papers
        ]
        vectors = self.embedding_service.embed_texts(texts)

        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, str(self._index_path(query_id)))

        # Clear any stale embedding rows for this query, then write fresh ones.
        for paper in papers:
            if paper.embedding is not None:
                db.delete(paper.embedding)
        db.flush()

        for position, paper in enumerate(papers):
            db.add(
                Embedding(
                    paper_id=paper.id,
                    model_name=self.embedding_service.model_name,
                    faiss_index_pos=position,
                )
            )
        db.commit()

        logger.info("Built FAISS index for query_id=%s with %d vectors", query_id, len(papers))
        return index

    def load_index_for_query(self, query_id: int) -> faiss.Index:
        path = self._index_path(query_id)
        if not path.exists():
            raise VectorStoreError(f"No FAISS index found for query_id={query_id}")
        return faiss.read_index(str(path))

    def similarity_matrix(self, query_id: int) -> np.ndarray:
        """
        Returns the full NxN cosine-similarity matrix for a query's papers,
        used by the gap-detection clustering step.
        """
        index = self.load_index_for_query(query_id)
        n = index.ntotal
        vectors = index.reconstruct_n(0, n)
        return vectors @ vectors.T
