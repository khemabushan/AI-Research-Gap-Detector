# AI Research Gap Detector — Backend

FastAPI backend that collects research paper abstracts (arXiv + Semantic
Scholar), extracts structured fields via an LLM, embeds and clusters papers
with Sentence Transformers + FAISS, and synthesizes research-gap reports and
novel project ideas.

## Pipeline

```
POST /search            → collect + dedupe papers, store in SQLite
POST /analyze            → LLM structured extraction + build FAISS index
POST /research-gaps       → cluster papers, LLM gap synthesis
POST /future-directions   → LLM future directions + novel project ideas
```

Each step depends on the previous one having been run for the same
`query_id`. `/search` returns the `query_id` used by every subsequent call.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set OPENAI_API_KEY (and optionally SEMANTIC_SCHOLAR_API_KEY)

uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs` once running.

## Running with Docker

```bash
docker build -t research-gap-detector-backend .
docker run -p 8000:8000 --env-file .env research-gap-detector-backend
```

## Running tests

```bash
pytest tests/ -v
```

Tests for the arXiv and Semantic Scholar clients use `respx` to mock HTTP
calls, so they run fully offline. Dedup logic is tested directly. LLM/
embedding-dependent services (`extraction_service`, `gap_detection`,
`report_generator`) are best verified via a manual end-to-end run against a
real `OPENAI_API_KEY`, since mocking structured LLM output meaningfully
requires either a real key or a fairly elaborate fixture — left as a natural
next addition (see "Suggested Improvements" below).

## Example end-to-end flow

```bash
# 1. Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"topic": "Brain Tumor Segmentation using Deep Learning", "max_results_per_source": 15}'
# -> {"query_id": 1, ...}

# 2. Analyze (extraction + embeddings)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" -d '{"query_id": 1}'

# 3. Detect gaps
curl -X POST http://localhost:8000/research-gaps \
  -H "Content-Type: application/json" -d '{"query_id": 1}'

# 4. Generate future directions
curl -X POST http://localhost:8000/future-directions \
  -H "Content-Type: application/json" -d '{"query_id": 1, "num_ideas": 5}'
```

## Architecture notes

- **Clean separation**: `api/` (HTTP concerns only) → `services/` (business
  logic, framework-agnostic) → `models/` (DB + Pydantic schemas). Routes
  never touch FAISS/OpenAI directly; they call services.
- **Resilience**: `/search` fetches arXiv and Semantic Scholar concurrently;
  if one source fails, the other's results still get used (see
  `PaperCollectorService._safe_fetch`).
- **Grounded LLM calls**: gap synthesis and future-direction generation are
  prompted with pre-extracted structured fields and cluster summaries, not
  raw abstracts — this bounds token usage and keeps the LLM's reasoning
  anchored to verifiable extracted data rather than long free text.
- **FAISS**: one flat (exact, not approximate) inner-product index per
  `query_id`, persisted to `data/faiss_indexes/query_{id}.index`. Exact
  search is appropriate at this scale (tens of papers per query) and avoids
  the complexity of IVF/HNSW tuning.

## Suggested Improvements (good "what I'd do next" talking points)

- Add Alembic migrations instead of `create_all` for schema evolution.
- Move `/analyze` and later steps to a background task queue (Celery/RQ) so
  large topics don't block the HTTP request for the full extraction loop.
- Add a `respx`-free integration test that stubs `ChatOpenAI.ainvoke`
  directly to test `ExtractionService`/`GapDetectionService` logic without
  a real API key.
- Cache embeddings/extractions across queries when the same paper appears
  in multiple topic searches.
