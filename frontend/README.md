# AI Research Gap Detector — Frontend

Next.js 14 (App Router) + TypeScript + Tailwind + a hand-built shadcn-style
component set, fully wired to the FastAPI backend at
`NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000`).

## Integration overview

| Backend endpoint | Hook | Used by |
|---|---|---|
| `POST /search` | `useSearchPapers` | Home page — kicks off a query, redirects to `/results/{id}` |
| `GET /queries/{id}` | `useQueryDetail` | Results & gap-report pages — **the source of truth** for a query's current state |
| `POST /analyze` | `useAnalyzePapers` | Results page — extraction, then invalidates the `useQueryDetail` cache |
| `POST /research-gaps` → `POST /future-directions` | `useGapPipeline` | Gap-report page — runs both in sequence, skips them if `GET /queries/{id}` already shows a persisted report |
| `GET /health` | `useBackendHealth` | Header — live connection indicator, polled every 30s |

All requests go through `lib/api-client.ts`, a single typed `fetch` wrapper
(`get`/`post` over a shared `request` function) that turns non-2xx
responses and network failures into a single `ApiRequestError` — every
hook and component handles errors through that one type, so error UI is
consistent everywhere.

### Why `GET /queries/{id}` matters

Earlier iterations of this frontend patched around the backend only having
POST endpoints by mirroring responses into `sessionStorage`. That's gone
now — the backend gained a real `GET /queries/{id}` endpoint (see
`backend/app/api/routes_queries.py`), so the frontend fetches fresh from
the database on every page load via React Query, with the query's SQLite
row as the single source of truth. Refreshing `/results/42` or
`/research-gaps/42` re-fetches and just works, including resuming a gap
report that's already been generated instead of re-running LLM calls.

## Loading & error handling patterns

- **Skeletons**, not spinners, for anything with known shape —
  `components/shared/loading-skeletons.tsx` (paper list, gap report,
  project ideas).
- **`ErrorBanner`** (`components/shared/error-banner.tsx`) is the one error
  UI used everywhere a request can fail, always with a "Try again" action
  wired to the query/mutation's own retry.
- **404 vs. other errors are handled differently** — a missing `query_id`
  shows an `EmptyState` pointing back to a new search; any other failure
  (backend down, 500, etc.) shows `ErrorBanner` with retry.
- **The gap-detection pipeline** shows granular stage progress
  (`components/shared/stage-progress.tsx`) across its two sequential LLM
  calls, rather than one opaque spinner — each stage is independently
  markable as done/current/failed.
- **Connection status** in the header polls `/health` so backend
  unreachability is visible before someone tries to search, not just
  discovered when a request fails.

## Folder structure

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                          # Home
│   ├── results/[queryId]/page.tsx        # Papers + comparison table
│   └── research-gaps/[queryId]/page.tsx  # Gap report shell (loads query, delegates to GapReportContent)
├── components/
│   ├── ui/        # button, card, input, badge, tabs, tooltip, separator, scroll-area, progress, skeleton
│   ├── home/       # search-hero, how-it-works
│   ├── results/     # paper-card, paper-list, abstract-viewer, comparison-table, analyze-panel
│   ├── gaps/         # gap-card, cluster-card, evidence-trail, project-idea-card,
│   │                 # future-direction-list, gap-report-content (owns useGapPipeline)
│   └── shared/        # header, connection-status, stage-progress, empty-state,
│                       # error-banner, loading-skeletons, theme/query providers
├── hooks/
│   ├── use-search-papers.ts     # POST /search
│   ├── use-analyze.ts            # POST /analyze
│   ├── use-query-detail.ts        # GET /queries/{id} — primary data source
│   ├── use-backend-health.ts       # GET /health
│   └── use-pipeline.ts              # orchestrates /research-gaps + /future-directions
├── lib/
│   ├── api-client.ts   # typed fetch wrapper (get/post + ApiRequestError)
│   ├── types.ts          # mirrors backend Pydantic schemas exactly
│   ├── constants.ts
│   └── utils.ts
```

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local   # already defaults to http://localhost:8000
npm run dev
```

Start the backend first (see `backend/README.md`) — CORS on the backend
defaults to allowing `http://localhost:3000`, matching Next's dev server.

## Scripts

```bash
npm run dev         # local dev server
npm run build         # production build
npm run typecheck      # tsc --noEmit
npm run lint             # next lint
```
