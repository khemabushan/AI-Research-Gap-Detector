"""
FastAPI application entrypoint. Wires up middleware, routers, exception
handlers, and startup/shutdown events.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_analyze import router as analyze_router
from app.api.routes_directions import router as directions_router
from app.api.routes_gaps import router as gaps_router
from app.api.routes_queries import router as queries_router
from app.api.routes_search import router as search_router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.init_db import init_db
from app.utils.exceptions import ResearchGapDetectorError

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Research Gap Detector API (env=%s)...", settings.app_env)
    settings.ensure_data_dirs()
    init_db()
    yield
    logger.info("Shutting down AI Research Gap Detector API.")


app = FastAPI(
    title="AI Research Gap Detector API",
    description=(
        "Collects research paper abstracts, extracts structured fields, "
        "detects research gaps via embedding clustering, and generates "
        "future research directions and novel project ideas."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ResearchGapDetectorError)
async def domain_error_handler(request: Request, exc: ResearchGapDetectorError) -> JSONResponse:
    """Catch-all for any domain exception that a route didn't already translate."""
    logger.error("Unhandled domain error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=400, content={"error": exc.__class__.__name__, "detail": str(exc)})


app.include_router(search_router)
app.include_router(analyze_router)
app.include_router(gaps_router)
app.include_router(directions_router)
app.include_router(queries_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "env": settings.app_env}
