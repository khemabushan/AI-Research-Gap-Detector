"""
Domain-specific exceptions. Kept separate from framework exceptions so
services stay decoupled from FastAPI; routes translate these into HTTP
responses via the handlers registered in main.py.
"""


class ResearchGapDetectorError(Exception):
    """Base class for all application-specific errors."""


class PaperSourceError(ResearchGapDetectorError):
    """Raised when an external paper source (arXiv, Semantic Scholar) fails."""

    def __init__(self, source: str, message: str):
        self.source = source
        self.message = message
        super().__init__(f"[{source}] {message}")


class QueryNotFoundError(ResearchGapDetectorError):
    """Raised when a requested query_id does not exist in the database."""

    def __init__(self, query_id: int):
        self.query_id = query_id
        super().__init__(f"Query with id={query_id} was not found")


class NoPapersFoundError(ResearchGapDetectorError):
    """Raised when a search returns zero papers from all sources."""

    def __init__(self, topic: str):
        self.topic = topic
        super().__init__(f"No papers found for topic: '{topic}'")


class InsufficientDataError(ResearchGapDetectorError):
    """Raised when downstream analysis lacks enough extracted data to run."""


class ExtractionError(ResearchGapDetectorError):
    """Raised when LLM-based structured extraction fails for a paper."""

    def __init__(self, paper_id: int, message: str):
        self.paper_id = paper_id
        super().__init__(f"Extraction failed for paper_id={paper_id}: {message}")


class VectorStoreError(ResearchGapDetectorError):
    """Raised when FAISS index operations fail."""
