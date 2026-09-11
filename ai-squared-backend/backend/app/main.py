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

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import HealthResponse
from app.routers import chat

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ai_squared")

APP_VERSION = "1.0.0"

app = FastAPI(
    title="AI² (AI Squared)",
    description="Resource-Aware AI Orchestration for Sustainable Computing.",
    version=APP_VERSION,
)

# ---------------------------------------------------------------------------
# CORS -- wide open for hackathon demo purposes (tighten for production).
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(chat.router)


# ---------------------------------------------------------------------------
# Global exception handler -- guarantees a clean JSON error body instead of
# an unhandled-exception traceback leaking to the client.
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler so unexpected errors never crash the process or leak tracebacks."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred.", "error": str(exc)},
    )


# ---------------------------------------------------------------------------
# Health / root endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_model=HealthResponse, tags=["health"])
async def root() -> HealthResponse:
    """Basic liveness check -- also useful as the hackathon demo's first curl."""
    return HealthResponse(status="ok", service="AI² (AI Squared)", version=APP_VERSION)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    """Alias for `/` -- some deployment platforms probe `/health` specifically."""
    return HealthResponse(status="ok", service="AI² (AI Squared)", version=APP_VERSION)


@app.on_event("startup")
async def on_startup() -> None:
    """Log a friendly banner on boot -- useful when judges watch the terminal."""
    logger.info("=" * 60)
    logger.info("AI² (AI Squared) backend starting -- v%s", APP_VERSION)
    logger.info("Docs available at /docs")
    logger.info("=" * 60)
