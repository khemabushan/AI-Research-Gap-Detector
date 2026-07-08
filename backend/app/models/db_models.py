"""
SQLAlchemy ORM models. This is the single source of truth for the database
schema. Uses SQLAlchemy 2.0 declarative-typed style.
"""
from __future__ import annotations

import datetime
import enum

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class QueryStatus(str, enum.Enum):
    PENDING = "pending"
    COLLECTING = "collecting"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    DONE = "done"
    FAILED = "failed"


class PaperSource(str, enum.Enum):
    ARXIV = "arxiv"
    SEMANTIC_SCHOLAR = "semantic_scholar"


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    status: Mapped[QueryStatus] = mapped_column(
        Enum(QueryStatus), default=QueryStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    papers: Mapped[list["Paper"]] = relationship(
        back_populates="query", cascade="all, delete-orphan"
    )
    gap_report: Mapped["GapReport | None"] = relationship(
        back_populates="query", cascade="all, delete-orphan", uselist=False
    )


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (
        UniqueConstraint("query_id", "external_id", "source", name="uq_paper_per_query_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("queries.id", ondelete="CASCADE"))

    source: Mapped[PaperSource] = mapped_column(Enum(PaperSource), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list] = mapped_column(JSON, default=list)  # list[str]
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    abstract: Mapped[str] = mapped_column(Text, default="")
    citation_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    query: Mapped["Query"] = relationship(back_populates="papers")
    extraction: Mapped["Extraction | None"] = relationship(
        back_populates="paper", cascade="all, delete-orphan", uselist=False
    )
    embedding: Mapped["Embedding | None"] = relationship(
        back_populates="paper", cascade="all, delete-orphan", uselist=False
    )


class Extraction(Base):
    __tablename__ = "extractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), unique=True
    )

    problem: Mapped[str] = mapped_column(Text, default="")
    methodology: Mapped[str] = mapped_column(Text, default="")
    dataset: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[str] = mapped_column(Text, default="")
    limitations: Mapped[str] = mapped_column(Text, default="")
    future_work: Mapped[str] = mapped_column(Text, default="")
    extracted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    paper: Mapped["Paper"] = relationship(back_populates="extraction")


class Embedding(Base):
    """
    Stores metadata about a paper's embedding. The actual vector lives in the
    FAISS index on disk (one index per query_id); this row tracks the
    mapping from paper_id -> FAISS internal index position (faiss_index_pos)
    so we can translate similarity search results back to papers.
    """

    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), unique=True
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    faiss_index_pos: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    paper: Mapped["Paper"] = relationship(back_populates="embedding")


class GapReport(Base):
    __tablename__ = "gap_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_id: Mapped[int] = mapped_column(
        ForeignKey("queries.id", ondelete="CASCADE"), unique=True
    )

    summary: Mapped[str] = mapped_column(Text, default="")
    identified_gaps: Mapped[list] = mapped_column(JSON, default=list)
    future_directions: Mapped[list] = mapped_column(JSON, default=list)
    novel_project_ideas: Mapped[list] = mapped_column(JSON, default=list)
    cluster_summary: Mapped[list] = mapped_column(JSON, default=list)
    generated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    query: Mapped["Query"] = relationship(back_populates="gap_report")
