"""
chat.py
=======
The single public endpoint for AI²: POST /api/chat.

Wires together the full pipeline in order:

    ChatRequest
      -> classify_prompt()          (classifier.py)
      -> route_request()            (model_router.py -> llm_service.py)
      -> estimate_sustainability()  (energy_estimator.py)
      -> compute_green_score()      (green_score.py)
      -> ChatResponse
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ChatRequest, ChatResponse
from app.services.classifier import classify_prompt
from app.services.energy_estimator import estimate_sustainability
from app.services.green_score import compute_green_score
from app.services.model_router import RoutingError, route_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Classify, route, answer, and score a prompt for sustainability",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Run a prompt through the full AI² pipeline.

    1. Classify the prompt's complexity (LOW/MEDIUM/HIGH) via heuristics.
    2. Route it to the smallest suitable free-tier model, with fallback.
    3. Estimate energy consumption and CO2 emissions for that run.
    4. Compute a 0-100 Green Score summarizing the sustainability win.

    Raises:
        HTTPException(422): Empty/invalid prompt (handled by Pydantic).
        HTTPException(502): Every LLM provider failed (primary + fallbacks).
        HTTPException(500): Any other unexpected server-side error.
    """
    logger.info("Received prompt (%d chars)", len(request.prompt))

    try:
        classification = classify_prompt(request.prompt)
    except Exception as exc:  # noqa: BLE001 - classifier is pure logic; any failure is a bug
        logger.exception("Classifier failed unexpectedly.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {exc}",
        ) from exc

    try:
        routing = await route_request(request.prompt, classification.complexity)
    except RoutingError as exc:
        logger.error("All providers failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "All configured LLM providers failed for this request. "
                "Check that GEMINI_API_KEY / GROQ_API_KEY are set and valid, "
                f"and that you haven't hit a free-tier rate limit. Detail: {exc}"
            ),
        ) from exc

    try:
        sustainability = estimate_sustainability(routing)
        sustainability.green_score = compute_green_score(sustainability, classification.complexity)
    except Exception as exc:  # noqa: BLE001 - pure arithmetic; any failure is a bug
        logger.exception("Sustainability estimation failed unexpectedly.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sustainability estimation failed: {exc}",
        ) from exc

    logger.info(
        "Served via %s | green_score=%.1f | saved=%.1f%%",
        routing.model_used, sustainability.green_score, sustainability.pct_compute_saved,
    )

    return ChatResponse(
        classification=classification,
        routing=routing,
        sustainability=sustainability,
    )
