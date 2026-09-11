"""
llm_service.py
===============
Thin async clients for the two free-tier LLM providers AI² uses:

- Google Gemini (generateContent REST API) -- free tier, used for LOW.
- Groq (OpenAI-compatible chat completions API) -- free tier, used for
  MEDIUM (Llama 3.1 8B) and HIGH (Llama 3.3 70B).

Both functions raise `LLMProviderError` on any failure (bad status
code, timeout, malformed response, missing API key) so that
`model_router.py` can catch a single exception type and decide whether
to fall back to another tier.

No SDK dependency is required -- both providers expose plain REST/HTTPS
JSON APIs, so a single `httpx.AsyncClient` covers everything, keeping
`requirements.txt` small for a hackathon.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass

import httpx

from app.utils.constants import DEFAULT_MAX_TOKENS, REQUEST_TIMEOUT_SEC

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GEMINI_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
)
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


class LLMProviderError(Exception):
    """Raised whenever a provider call fails for any reason (network, auth, parsing)."""

    def __init__(self, provider: str, detail: str) -> None:
        self.provider = provider
        self.detail = detail
        super().__init__(f"[{provider}] {detail}")


@dataclass
class LLMResult:
    """Normalized result shape returned by both provider functions."""

    text: str
    execution_time_sec: float
    prompt_tokens_est: int
    completion_tokens_est: int


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) used when a provider omits usage stats."""
    return max(1, len(text) // 4)


async def generate_with_gemini(prompt: str, model_id: str) -> LLMResult:
    """
    Generate a response using Google's Gemini free-tier REST API.

    Args:
        prompt: The user prompt to send.
        model_id: Gemini model identifier, e.g. "gemini-2.0-flash".

    Returns:
        An LLMResult with the generated text and timing/token info.

    Raises:
        LLMProviderError: If the API key is missing, the request fails,
            times out, or the response cannot be parsed.
    """
    if not GEMINI_API_KEY:
        raise LLMProviderError("gemini", "GEMINI_API_KEY is not set in the environment.")

    url = GEMINI_ENDPOINT_TEMPLATE.format(model_id=model_id)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": DEFAULT_MAX_TOKENS},
    }
    params = {"key": GEMINI_API_KEY}

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SEC) as client:
            resp = await client.post(url, params=params, json=payload)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise LLMProviderError("gemini", f"No candidates returned. Raw response: {data}")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise LLMProviderError("gemini", "Empty response text.")
    except httpx.TimeoutException as exc:
        raise LLMProviderError("gemini", f"Request timed out: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        raise LLMProviderError(
            "gemini", f"HTTP {exc.response.status_code}: {exc.response.text[:300]}"
        ) from exc
    except httpx.HTTPError as exc:
        raise LLMProviderError("gemini", f"Network error: {exc}") from exc
    except (KeyError, ValueError, TypeError) as exc:
        raise LLMProviderError("gemini", f"Malformed response: {exc}") from exc

    elapsed = time.perf_counter() - start
    usage = data.get("usageMetadata", {})
    prompt_tokens = usage.get("promptTokenCount") or _estimate_tokens(prompt)
    completion_tokens = usage.get("candidatesTokenCount") or _estimate_tokens(text)

    logger.info("Gemini (%s) responded in %.2fs", model_id, elapsed)
    return LLMResult(
        text=text,
        execution_time_sec=elapsed,
        prompt_tokens_est=prompt_tokens,
        completion_tokens_est=completion_tokens,
    )


async def generate_with_groq(prompt: str, model_id: str) -> LLMResult:
    """
    Generate a response using Groq's free-tier, OpenAI-compatible chat API.

    Args:
        prompt: The user prompt to send.
        model_id: Groq model identifier, e.g. "llama-3.1-8b-instant".

    Returns:
        An LLMResult with the generated text and timing/token info.

    Raises:
        LLMProviderError: If the API key is missing, the request fails,
            times out, or the response cannot be parsed.
    """
    if not GROQ_API_KEY:
        raise LLMProviderError("groq", "GROQ_API_KEY is not set in the environment.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": DEFAULT_MAX_TOKENS,
    }

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SEC) as client:
            resp = await client.post(GROQ_ENDPOINT, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise LLMProviderError("groq", f"No choices returned. Raw response: {data}")
        text = choices[0].get("message", {}).get("content", "").strip()
        if not text:
            raise LLMProviderError("groq", "Empty response text.")
    except httpx.TimeoutException as exc:
        raise LLMProviderError("groq", f"Request timed out: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        raise LLMProviderError(
            "groq", f"HTTP {exc.response.status_code}: {exc.response.text[:300]}"
        ) from exc
    except httpx.HTTPError as exc:
        raise LLMProviderError("groq", f"Network error: {exc}") from exc
    except (KeyError, ValueError, TypeError) as exc:
        raise LLMProviderError("groq", f"Malformed response: {exc}") from exc

    elapsed = time.perf_counter() - start
    usage = data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens") or _estimate_tokens(prompt)
    completion_tokens = usage.get("completion_tokens") or _estimate_tokens(text)

    logger.info("Groq (%s) responded in %.2fs", model_id, elapsed)
    return LLMResult(
        text=text,
        execution_time_sec=elapsed,
        prompt_tokens_est=prompt_tokens,
        completion_tokens_est=completion_tokens,
    )
