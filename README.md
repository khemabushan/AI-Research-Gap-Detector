# AI Research Gap Detector

Give it a research topic. It reads the literature, extracts structured
data from every paper, and reports exactly where the field has gaps —
each claim traceable back to the papers that support it.

```
"Brain Tumor Segmentation using Deep Learning"
        │
        ▼
  arXiv + Semantic Scholar  →  LLM extraction  →  embedding clusters
        │                          │                    │
        ▼                          ▼                    ▼
   10-30 papers          Problem / Dataset /      Thematic groups
                          Methodology / Model /
                          Limitations / Future Work
                                   │
                                   ▼
                    Research Gap Report + Novel Project Ideas
```

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind, hand-built shadcn-style components, React Query |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| AI | OpenAI (via LangChain, structured output), Sentence Transformers, FAISS, scikit-learn (KMeans clustering) |
| Data sources | arXiv API, Semantic Scholar API |
| Storage | SQLite |
| Deployment | Docker, Docker Compose, Render |

## Architecture

- **Backend** (`backend/`) — clean-architecture FastAPI service. Six
  endpoints: `POST /search → /analyze → /research-gaps → /future-directions`
  form the pipeline; `GET /queries/{id}` and `GET /health` are the read/
  status endpoints. See `backend/README.md` for the full endpoint reference
  and the AI reasoning design behind gap detection.
- **Frontend** (`frontend/`) — master-detail results view, a live pipeline
  stage tracker for the two sequential LLM calls, and an "evidence trail"
  UI motif — every gap/cluster shows citation chips back to source papers.
  See `frontend/README.md` for the integration details.

## Running locally

### Option A — Docker Compose (full stack, one command)

```bash
cp .env.example .env    # add your OPENAI_API_KEY
docker compose up --build
```

Frontend: http://localhost:3000 · Backend: http://localhost:8000/docs

### Option B — run each service directly

```bash
# Terminal 1 — backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend
npm install
cp .env.local.example .env.local   # defaults to http://localhost:8000
npm run dev
```

## Deploying

`render.yaml` is a Render Blueprint that provisions both services from
this repo (Docker runtime for each). After connecting the repo in Render:

1. Set `OPENAI_API_KEY` (and optionally `SEMANTIC_SCHOLAR_API_KEY`) on the
   backend service in the Render dashboard — these are marked `sync: false`
   in the blueprint so they're never committed.
2. Render assigns each service a URL like
   `https://research-gap-detector-backend.onrender.com`. If your actual
   assigned URLs differ from the ones pre-filled in `render.yaml`
   (`CORS_ORIGINS` on the backend, `NEXT_PUBLIC_API_BASE_URL` on the
   frontend), update both env vars to match and redeploy the frontend
   (`NEXT_PUBLIC_*` vars are baked in at build time, so this needs a
   rebuild, not just a restart).

## CI

`.github/workflows/ci.yml` runs on every push/PR to `main`: backend tests
via pytest, frontend typecheck + lint + production build via `next build`.

## Project structure

```
ai-research-gap-detector/
├── backend/          # FastAPI service — see backend/README.md
├── frontend/          # Next.js app — see frontend/README.md
├── docker-compose.yml
├── render.yaml
├── .env.example
└── .github/workflows/ci.yml
```

## Status / what's genuinely done vs. designed

- ✅ Backend: all 6 endpoints implemented, tested (11 passing tests),
  Dockerized.
- ✅ Frontend: all 3 pages implemented, fully wired to the backend,
  typechecked, production build verified.
- ✅ Integration: `GET /queries/{id}` makes the backend the single source
  of truth; the gap pipeline skips recomputation if a report already
  exists.
- 📝 Designed but not yet implemented in code: the six-signal gap-detection
  reasoning chain (code-based counting + two guarded LLM reasoning calls
  for "missing approaches" and "unsolved problems", plus a propose →
  self-critique loop for novel project ideas) — see the AI logic design
  doc for the full spec. The current `gap_detection.py` uses a simpler
  single-pass clustering + synthesis approach that works end-to-end today;
  the six-signal design is the natural next iteration for higher-precision
  gap detection.
