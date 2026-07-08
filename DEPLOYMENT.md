# Deploying to Render

Two ways to deploy: the Blueprint (`render.yaml`, one click, both services)
or manual dashboard setup (more control, useful if you want the services
under different names or in an existing Render project). Both produce the
same result — this doc covers both, plus the environment variable
reference and the gotchas specific to this stack (SQLite persistence,
FAISS index persistence, and Next.js build-time env vars).

---

## Option A — Blueprint deploy (recommended)

1. Push this repo to GitHub/GitLab.
2. In the Render dashboard: **New → Blueprint**, connect the repo. Render
   reads `render.yaml` and shows both services (`research-gap-detector-backend`,
   `research-gap-detector-frontend`) before creating anything.
3. Render will prompt for the env vars marked `sync: false` in `render.yaml`
   — enter your `OPENAI_API_KEY` (required) and `SEMANTIC_SCHOLAR_API_KEY`
   (optional but recommended — unauthenticated Semantic Scholar requests
   are heavily rate-limited).
4. Click **Apply**. Render builds both Docker images and deploys them.
5. **After first deploy**, check the actual assigned URLs (Render appends a
   suffix if the exact name is taken, e.g.
   `research-gap-detector-backend-a1b2.onrender.com`). If they differ from
   the ones pre-filled in `render.yaml`:
   - Update `CORS_ORIGINS` on the **backend** service to the real frontend URL.
   - Update `NEXT_PUBLIC_API_BASE_URL` on the **frontend** service to the
     real backend URL, then **trigger a manual redeploy** — this variable
     is baked into the JS bundle at build time, so just changing the env
     var and restarting the container does nothing; it requires a rebuild.

---

## Option B — Manual dashboard setup

### Backend service

1. **New → Web Service** → connect the repo.
2. **Root directory:** `backend`
3. **Runtime:** Docker (Render auto-detects the `Dockerfile`)
4. **Instance type:** Starter is enough for a resume project; the LLM calls
   are I/O-bound, not CPU-bound, so you don't need more compute — you'd
   scale up only if running embedding generation on much larger paper sets.
5. **Health check path:** `/health`
6. **Add a persistent disk** (Settings → Disks → Add Disk): mount path
   `/app/data`, 1GB is plenty. Without this, the SQLite database and FAISS
   indexes are wiped on every deploy and container restart — Render's
   filesystem is otherwise ephemeral.
7. **Environment variables:** see the reference table below.
8. Deploy. Note the assigned URL — you'll need it for the frontend.

### Frontend service

1. **New → Web Service** → same repo.
2. **Root directory:** `frontend`
3. **Runtime:** Docker
4. **Docker build arguments:** add `NEXT_PUBLIC_API_BASE_URL` set to the
   backend URL from the previous step. This must be set as a **build
   argument**, not just an environment variable — see the note below.
5. **Environment variables:** also set `NEXT_PUBLIC_API_BASE_URL` here
   (same value) so it's available if the app ever reads it at runtime too.
6. Deploy.
7. Go back to the **backend** service and set `CORS_ORIGINS` to this
   frontend's URL, then save (triggers a restart, not a rebuild — fine,
   since backend env vars are read at runtime, not build time).

---

## Environment variables reference

### Backend (`backend/.env.example`)

| Variable | Required | Notes |
|---|---|---|
| `APP_ENV` | No | Set to `production` on Render — reflected in `GET /health`'s response and used to quiet noisy third-party loggers (see `backend/app/core/logging_config.py`). |
| `OPENAI_API_KEY` | **Yes** | Set in Render dashboard, never commit. Used for all extraction/gap-synthesis LLM calls. |
| `OPENAI_MODEL` | No | Defaults to `gpt-4o-mini`. |
| `SEMANTIC_SCHOLAR_API_KEY` | No | Unauthenticated requests work but are rate-limited; recommended for production. |
| `CORS_ORIGINS` | **Yes** | Comma-separated. Must include the frontend's exact Render URL (`https://...`, not `http://`) or every frontend request will fail CORS. |
| `DATABASE_URL` | No | Defaults to `sqlite:////app/data/app.db` — matches the Dockerfile and the persistent disk mount path. Don't change this unless you also change the disk mount path. |
| `FAISS_INDEX_DIR` | No | Defaults to `/app/data/faiss_indexes` — same disk-persistence reasoning as above. |
| `PORT` | **Do not set manually** | Render injects this automatically at runtime; the Dockerfile's `CMD` reads it (`--port ${PORT:-8000}`). Setting it yourself in the dashboard can conflict with Render's own injection. |

### Frontend (`frontend/.env.local.example`)

| Variable | Required | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | **Yes** | The backend's public URL. **Must be set as a Docker build argument**, not only a runtime env var — Next.js inlines `NEXT_PUBLIC_*` variables into the client JavaScript bundle at `next build` time. Changing it later requires a rebuild, not just a restart. |

---

## Why the persistent disk matters

Without a mounted disk, every deploy (including auto-deploys on git push)
gets a fresh, empty filesystem. That means:
- The SQLite database resets — every past query, paper, extraction, and
  gap report is gone.
- The FAISS indexes on disk (`data/faiss_indexes/query_{id}.index`) are
  gone, so even a query that still has a database row referencing an old
  cluster analysis will error when `/research-gaps` tries to load an
  index that no longer exists.

The 1GB disk in `render.yaml` / dashboard step 6 above fixes both. For a
resume/demo project this is enough for hundreds of queries; if you outgrow
SQLite's single-writer model under real concurrent traffic, that's the
signal to migrate `DATABASE_URL` to a managed Postgres instance (Render
offers this too) — the SQLAlchemy layer in `backend/app/db/session.py` was
built to make that a one-line change.

## Verifying the deploy

```bash
curl https://<your-backend>.onrender.com/health
# {"status":"ok","env":"production"}

curl -X POST https://<your-backend>.onrender.com/search \
  -H "Content-Type: application/json" \
  -d '{"topic": "Brain Tumor Segmentation using Deep Learning"}'
# Should return a query_id and a list of papers within a few seconds.
```

Then open the frontend URL in a browser and confirm the header's
connection-status indicator shows "backend connected" (green dot) — that's
`useBackendHealth` polling `/health` in real time.
