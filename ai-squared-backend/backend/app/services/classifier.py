"""
classifier.py
=============
Rule-based (heuristic) prompt complexity classifier.

No ML model is trained here on purpose: the hackathon brief calls for
a heuristic classifier, and for a prompt-routing MVP, transparent rules
are also more explainable to judges than an opaque model would be.

The classifier scores a prompt on four independent signals:

1. Word count           -- longer prompts tend to need more reasoning.
2. Keyword matches       -- domain phrases that signal LOW/MEDIUM/HIGH intent.
3. Code detection        -- presence of code fences, keywords, or syntax.
4. Structural complexity -- multiple sub-questions, conjunctions, etc.

Each signal contributes points toward LOW / MEDIUM / HIGH; the tier with
the highest score wins, with MEDIUM as the tie-break default (a safe
middle ground if signals conflict).
"""

from __future__ import annotations

import logging
import re

from app.models.schemas import ClassificationResult
from app.utils.constants import (
    CODE_SIGNALS,
    HIGH_COMPLEXITY_KEYWORDS,
    LOW_COMPLEXITY_KEYWORDS,
    LOW_WORD_COUNT_MAX,
    MEDIUM_COMPLEXITY_KEYWORDS,
    MEDIUM_WORD_COUNT_MAX,
    ComplexityTier,
)

logger = logging.getLogger(__name__)

# Matches things like "1)", "2.", "- ", "* " at line starts, used as a
# signal for multi-part / structured requests (a HIGH-complexity hint).
_LIST_ITEM_PATTERN = re.compile(r"(?m)^\s*(?:[-*]|\d+[.)])\s+")


def _detect_code(prompt: str) -> bool:
    """Return True if the prompt looks like it contains or asks for code."""
    lowered = prompt.lower()
    return any(signal.lower() in lowered for signal in CODE_SIGNALS)


def _count_keyword_hits(lowered_prompt: str, keywords: list[str]) -> int:
    """Count how many keywords from a bank appear in the (lower-cased) prompt."""
    return sum(1 for kw in keywords if kw in lowered_prompt)


def _structural_complexity_score(prompt: str) -> int:
    """
    Estimate structural complexity from sentence/question count.

    Multiple '?' marks, list items, or long conjunction chains ("and",
    "then", "also") suggest a multi-part task, which pushes the
    classification toward MEDIUM/HIGH regardless of raw word count.
    """
    question_marks = prompt.count("?")
    list_items = len(_LIST_ITEM_PATTERN.findall(prompt))
    conjunctions = len(re.findall(r"\b(and then|also|additionally|furthermore)\b", prompt.lower()))
    return question_marks + list_items + conjunctions


def classify_prompt(prompt: str) -> ClassificationResult:
    """
    Classify a prompt into LOW / MEDIUM / HIGH complexity using heuristics.

    Args:
        prompt: The raw user prompt.

    Returns:
        A ClassificationResult with the chosen tier, a human-readable
        reason, the word count, and whether code was detected.
    """
    stripped = prompt.strip()
    word_count = len(stripped.split())
    lowered = stripped.lower()
    has_code = _detect_code(stripped)

    low_hits = _count_keyword_hits(lowered, LOW_COMPLEXITY_KEYWORDS)
    medium_hits = _count_keyword_hits(lowered, MEDIUM_COMPLEXITY_KEYWORDS)
    high_hits = _count_keyword_hits(lowered, HIGH_COMPLEXITY_KEYWORDS)
    structural_score = _structural_complexity_score(stripped)

    scores = {
        ComplexityTier.LOW.value: 0.0,
        ComplexityTier.MEDIUM.value: 0.0,
        ComplexityTier.HIGH.value: 0.0,
    }
    reasons: list[str] = []

    # --- Word count signal -------------------------------------------------
    if word_count <= 5:
        scores[ComplexityTier.LOW.value] += 2
        reasons.append(f"short prompt ({word_count} words)")
    elif word_count <= 8:
        scores[ComplexityTier.MEDIUM.value] += 2
        reasons.append(f"medium-length prompt ({word_count} words)")
    else:
        scores[ComplexityTier.HIGH.value] += 2
        reasons.append(f"long prompt ({word_count} words)")

    # --- Keyword signal ------------------------------------------------------
    if high_hits:
        scores[ComplexityTier.HIGH.value] += 3 * high_hits
        reasons.append(f"{high_hits} high-complexity keyword(s)")
    if medium_hits:
        scores[ComplexityTier.MEDIUM.value] += 2 * medium_hits
        reasons.append(f"{medium_hits} medium-complexity keyword(s)")
    if low_hits:
        scores[ComplexityTier.LOW.value] += 1.5 * low_hits
        reasons.append(f"{low_hits} low-complexity keyword(s)")

    # --- Code signal -----------------------------------------------------
    if has_code:
        scores[ComplexityTier.MEDIUM.value] += 2
        scores[ComplexityTier.HIGH.value] += 1
        reasons.append("code detected")

    # --- Structural signal -------------------------------------------------
    if structural_score >= 3:
        scores[ComplexityTier.HIGH.value] += 2
        reasons.append(f"multi-part structure (score={structural_score})")
    elif structural_score >= 1:
        scores[ComplexityTier.MEDIUM.value] += 1
        reasons.append(f"some structure (score={structural_score})")

    # --- Decide winner, MEDIUM as tie-break default -------------------------
    best_tier = max(scores, key=lambda tier: (scores[tier], tier == ComplexityTier.MEDIUM.value))
    reason_text = f"Classified as {best_tier} due to: " + "; ".join(reasons)

    logger.info(
        "Classified prompt (%d words) as %s | scores=%s",
        word_count,
        best_tier,
        scores,
    )

    return ClassificationResult(
        complexity=best_tier,
        reason=reason_text,
        word_count=word_count,
        has_code=has_code,
    )
