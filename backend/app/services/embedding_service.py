"""
Wraps Sentence Transformers to produce embeddings for papers. The model is
loaded once per process (module-level cache) since loading it is expensive.
"""
from __future__ import annotations

import logging

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

_model_cache: dict[str, SentenceTransformer] = {}


def get_embedding_model(model_name: str | None = None) -> SentenceTransformer:
    name = model_name or settings.embedding_model_name
    if name not in _model_cache:
        logger.info("Loading Sentence Transformers model '%s'...", name)
        _model_cache[name] = SentenceTransformer(name)
    return _model_cache[name]


class EmbeddingService:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model_name
        self.model = get_embedding_model(self.model_name)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Returns an (n, dim) float32 array of L2-normalized embeddings."""
        if not texts:
            return np.empty((0, settings.embedding_dimension), dtype="float32")
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.astype("float32")

    @staticmethod
    def build_paper_text(title: str, abstract: str, methodology: str = "") -> str:
        """
        Composes the text used for embedding a paper. Including methodology
        (when available from extraction) sharpens clustering by technical
        approach rather than just topical similarity from the abstract alone.
        """
        parts = [title, abstract]
        if methodology:
            parts.append(methodology)
        return " ".join(p for p in parts if p)
