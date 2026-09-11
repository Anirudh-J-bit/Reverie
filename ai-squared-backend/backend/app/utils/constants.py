"""
constants.py
============
Central configuration for the AI² (AI Squared) backend.

This module holds every "magic number" used elsewhere in the app:
model routing table, heuristic classifier keyword banks, and the
sustainability estimation constants (power draw, grid carbon
intensity, per-token latency assumptions).

Keeping these in one place means the classifier, router, and
sustainability services never hard-code values themselves — they
import from here. For a hackathon, this also makes the numbers easy
to tune live during a demo without touching business logic.

NOTE ON THE NUMBERS: The power-draw and time-per-token figures below
are *heuristic estimates* for demo purposes, loosely informed by
public disclosures on datacenter inference power draw (e.g. small
quantized models running on efficient accelerators vs. large
70B-class models). They are NOT vendor-measured values. Say so
plainly if asked during judging — the point of AI² is the
*architecture* for resource-aware routing, not a certified carbon
audit.
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class ComplexityTier(str, Enum):
    """The three complexity buckets a prompt can be classified into."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Provider(str, Enum):
    """Supported free-tier LLM providers."""

    GEMINI = "gemini"
    GROQ = "groq"


# ---------------------------------------------------------------------------
# Model routing table
# ---------------------------------------------------------------------------
# Each tier maps to a (provider, model_id, display_name, avg_power_watts,
# sec_per_token) tuple. avg_power_watts is the assumed *average inference
# power draw* for a request served by that model class. sec_per_token is
# the assumed average generation latency, used only as a fallback when we
# want to estimate a hypothetical (non-executed) baseline run.
MODEL_CONFIG: Final[dict[str, dict[str, object]]] = {
    ComplexityTier.LOW.value: {
        "provider": Provider.GROQ.value,
        "model_id": "openai/gpt-oss-20b",
        "display_name": "GPT OSS 20B",
        "avg_power_watts": 12.0,
        "sec_per_token": 0.010,
    },
    ComplexityTier.MEDIUM.value: {
        "provider": Provider.GROQ.value,
        "model_id": "openai/gpt-oss-20b",
        "display_name": "GPT OSS 20B",
        "avg_power_watts": 28.0,
        "sec_per_token": 0.006,  # Groq's LPU inference is very fast
    },
    ComplexityTier.HIGH.value: {
        "provider": Provider.GROQ.value,
        "model_id": "openai/gpt-oss-120b",
        "display_name": "GPT OSS 120B",
        "avg_power_watts": 70.0,
        "sec_per_token": 0.009,
    },
}

# Fallback chain: if the primary provider for a tier fails, try these
# tiers in order (first one that succeeds wins). HIGH is the ultimate
# safety net since Groq's 70B model is the most likely to be available.
FALLBACK_CHAIN: Final[dict[str, list[str]]] = {
    ComplexityTier.LOW.value: [ComplexityTier.MEDIUM.value, ComplexityTier.HIGH.value],
    ComplexityTier.MEDIUM.value: [ComplexityTier.HIGH.value, ComplexityTier.LOW.value],
    ComplexityTier.HIGH.value: [ComplexityTier.MEDIUM.value, ComplexityTier.LOW.value],
}

# The tier used as the sustainability "baseline" -- i.e. what would have
# happened if every single request (regardless of true complexity) had
# been sent to the biggest model, which is the status-quo behavior AI²
# is designed to avoid.
BASELINE_TIER: Final[str] = ComplexityTier.HIGH.value

# ---------------------------------------------------------------------------
# Sustainability constants
# ---------------------------------------------------------------------------
# Global average grid carbon intensity, grams CO2 per kWh. Source: rough
# global average cited across IEA/Ember grid-mix summaries. Swap for a
# region-specific figure if you want a sharper story for judges.
CARBON_INTENSITY_G_PER_KWH: Final[float] = 475.0

# Rough characters-per-token ratio used when we only have text, not a
# real tokenizer, on hand -- fine for an order-of-magnitude estimate.
CHARS_PER_TOKEN: Final[float] = 4.0

# ---------------------------------------------------------------------------
# Classifier heuristics
# ---------------------------------------------------------------------------
# Keyword banks are lower-cased and matched as substrings against the
# lower-cased prompt. They are intentionally short and demo-tunable
# rather than exhaustive.
HIGH_COMPLEXITY_KEYWORDS: Final[list[str]] = [
    "architecture", "design a system", "design an algorithm", "prove",
    "proof", "optimize", "optimization", "algorithm", "complexity analysis",
    "big o", "research", "compare and contrast", "in-depth", "in depth",
    "analyze", "analysis", "trade-off", "tradeoff", "distributed system",
    "microservice", "refactor the entire", "multi-step", "dissertation",
    "thesis", "derive", "theorem", "simulate", "benchmark", "whitepaper",
]

MEDIUM_COMPLEXITY_KEYWORDS: Final[list[str]] = [
    "explain", "summarize", "summarise", "write a function", "debug",
    "translate", "compare", "pros and cons", "outline", "how does",
    "how do", "write a script", "convert this code", "review this code",
    "write an essay", "step by step", "step-by-step",
]

LOW_COMPLEXITY_KEYWORDS: Final[list[str]] = [
    "what is", "define", "capital of", "convert", "spell", "translate word",
    "what time", "who is", "what year", "synonym", "antonym", "meaning of",
]

# Code-detection signals: presence of any of these strongly suggests the
# prompt involves reading or producing source code.
CODE_SIGNALS: Final[list[str]] = [
    "```", "def ", "class ", "import ", "function(", "=>", "{", "}",
    "SELECT ", "console.log", "public static", "#include", "std::",
]

# Word-count thresholds used as a coarse first signal before keyword and
# code-detection adjustments are applied.
LOW_WORD_COUNT_MAX: Final[int] = 12
MEDIUM_WORD_COUNT_MAX: Final[int] = 40

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT_SEC: Final[float] = 30.0
DEFAULT_MAX_TOKENS: Final[int] = 1024
