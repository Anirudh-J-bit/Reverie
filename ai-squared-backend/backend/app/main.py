"""
main.py
=======
AI² (AI Squared) -- Resource-Aware AI Orchestration for Sustainable Computing.

FastAPI application entrypoint. Configures logging, CORS, exception
handling, and mounts the chat router.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Then open http://127.0.0.1:8000/docs for interactive Swagger UI.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import HealthResponse
from app.routers import chat

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ai_squared")

APP_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Lifespan Context Manager (Modern FastAPI Startup / Shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Log a friendly banner on boot when server starts."""
    logger.info("=" * 60)
    logger.info("AI² (AI Squared) backend starting -- v%s", APP_VERSION)
    logger.info("Docs available at http://127.0.0.1:8000/docs")
    logger.info("=" * 60)
    yield
    logger.info("AI² (AI Squared) backend shutting down.")


app = FastAPI(
    title="AI² API(AI Squared)",
    description="Resource-Aware AI Orchestration for Sustainable Computing.",
    version=APP_VERSION,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS Configuration -- Permits cross-origin calls from React Vite dev server
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers -- Mount under both root and /api for route compatibility
# ---------------------------------------------------------------------------
app.include_router(chat.router)
app.include_router(chat.router, prefix="/api")


# ---------------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler so unexpected errors return formatted JSON."""
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected server error occurred.",
            "error": str(exc),
        },
    )


# ---------------------------------------------------------------------------
# Health / Root Endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_model=HealthResponse, tags=["health"])
async def root() -> HealthResponse:
    """Basic liveness check."""
    return HealthResponse(status="ok", service="AI² (AI Squared)", version=APP_VERSION)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    """Alias for `/`."""
    return HealthResponse(status="ok", service="AI² (AI Squared)", version=APP_VERSION)