"""
model_router.py
================
Routes a classified prompt to the smallest suitable model, calls the
appropriate provider function from `llm_service.py`, and normalizes the
result into a `ModelRoutingResult`.

If the primary provider for a tier fails (rate limit, network error,
missing key, etc.), the router walks a predefined fallback chain
(`FALLBACK_CHAIN` in constants.py) and retries with the next tier's
model before giving up entirely.
"""

from __future__ import annotations

import logging

from app.models.schemas import ModelRoutingResult
from app.services.llm_service import LLMProviderError, LLMResult, generate_with_gemini, generate_with_groq
from app.utils.constants import FALLBACK_CHAIN, MODEL_CONFIG, Provider

logger = logging.getLogger(__name__)


class RoutingError(Exception):
    """Raised when every provider in the fallback chain has failed."""


async def _call_provider(prompt: str, tier: str) -> LLMResult:
    """Dispatch to the correct provider function for a given tier."""
    config = MODEL_CONFIG[tier]
    provider = config["provider"]
    model_id = str(config["model_id"])

    if provider == Provider.GEMINI.value:
        return await generate_with_gemini(prompt, model_id)
    if provider == Provider.GROQ.value:
        return await generate_with_groq(prompt, model_id)
    raise RoutingError(f"Unknown provider '{provider}' configured for tier '{tier}'.")


async def route_request(prompt: str, complexity: str) -> ModelRoutingResult:
    """
    Route a prompt to the model matching its complexity tier, with fallback.

    Args:
        prompt: The user's raw prompt.
        complexity: One of "LOW", "MEDIUM", "HIGH" (from the classifier).

    Returns:
        A ModelRoutingResult describing which model actually served the
        request, the generated text, and timing/power/token metadata.

    Raises:
        RoutingError: If the primary tier and every tier in its fallback
            chain fail.
    """
    if complexity not in MODEL_CONFIG:
        logger.warning("Unknown complexity '%s'; defaulting to MEDIUM.", complexity)
        complexity = "MEDIUM"

    tiers_to_try = [complexity, *FALLBACK_CHAIN.get(complexity, [])]
    last_error: Exception | None = None

    for attempt_index, tier in enumerate(tiers_to_try):
        config = MODEL_CONFIG[tier]
        try:
            result = await _call_provider(prompt, tier)
            fallback_used = attempt_index > 0
            if fallback_used:
                logger.warning(
                    "Primary tier '%s' failed; served by fallback tier '%s' (%s).",
                    complexity, tier, config["display_name"],
                )
            tokens_processed = result.prompt_tokens_est + result.completion_tokens_est
            return ModelRoutingResult(
                response=result.text,
                model_used=str(config["display_name"]),
                model_id=str(config["model_id"]),
                provider=str(config["provider"]),
                execution_time_sec=round(result.execution_time_sec, 4),
                tokens_processed=tokens_processed,
                est_power_watts=float(config["avg_power_watts"]),
                fallback_used=fallback_used,
            )
        except LLMProviderError as exc:
            logger.error("Provider failed for tier '%s': %s", tier, exc)
            last_error = exc
            continue

    raise RoutingError(
        f"All providers failed for complexity '{complexity}'. Last error: {last_error}"
    )
