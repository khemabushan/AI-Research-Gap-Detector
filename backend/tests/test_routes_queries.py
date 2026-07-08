"""
Tests for GET /queries/{query_id}. Uses a fresh in-memory SQLite DB per test
(via dependency override) so this doesn't touch the real data/app.db file
and stays isolated from the other test modules.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models.db_models import Base, Extraction, GapReport, Paper, PaperSource, Query, QueryStatus


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, TestingSessionLocal
    app.dependency_overrides.clear()


def test_get_query_not_found(client):
    test_client, _ = client
    response = test_client.get("/queries/999")
    assert response.status_code == 404


def test_get_query_returns_full_state(client):
    test_client, SessionLocal = client
    db = SessionLocal()

    query = Query(topic="Test Topic", status=QueryStatus.DONE)
    db.add(query)
    db.commit()
    db.refresh(query)
    query_id = query.id

    paper = Paper(
        query_id=query_id,
        source=PaperSource.ARXIV,
        external_id="1234.5678",
        title="A Test Paper",
        authors=["Alice"],
        year=2023,
        abstract="An abstract.",
        citation_count=5,
        url="http://example.com",
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    paper_id = paper.id

    db.add(
        Extraction(
            paper_id=paper_id,
            problem="P",
            methodology="M",
            dataset="D",
            model="Mo",
            limitations="L",
            future_work="F",
        )
    )
    db.add(
        GapReport(
            query_id=query_id,
            summary="Summary text",
            identified_gaps=["gap one"],
            cluster_summary=[{"cluster_id": 0, "paper_ids": [paper_id]}],
            future_directions=["direction one"],
            novel_project_ideas=[{"title": "Idea"}],
        )
    )
    db.commit()
    db.close()

    response = test_client.get(f"/queries/{query_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["query_id"] == query_id
    assert body["status"] == "done"
    assert body["total_papers"] == 1
    assert body["papers"][0]["title"] == "A Test Paper"
    assert body["extractions"][0]["problem"] == "P"
    assert body["gap_report"]["identified_gaps"] == ["gap one"]
    assert body["gap_report"]["novel_project_ideas"][0]["title"] == "Idea"


def test_get_query_without_analysis_has_empty_extractions_and_null_report(client):
    test_client, SessionLocal = client
    db = SessionLocal()

    query = Query(topic="Unanalyzed Topic", status=QueryStatus.PENDING)
    db.add(query)
    db.commit()
    db.refresh(query)
    query_id = query.id
    db.close()

    response = test_client.get(f"/queries/{query_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["extractions"] == []
    assert body["gap_report"] is None
