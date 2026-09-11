"""
green_score.py
===============
Computes a single 0-100 "Green Score" summarizing how sustainably a
request was handled.

The score rewards two things:

1. Compute saved (`pct_compute_saved`) relative to the always-use-the-
   biggest-model baseline -- this is the dominant factor (70% weight).
2. Routing to a genuinely smaller tier (LOW/MEDIUM) rather than HIGH --
   a smaller bonus (30% weight) that rewards the classifier for
   correctly recognizing simple requests, even in cases where the
   percentage-saved math alone might understate it.

A request that had to go to HIGH because it genuinely needed the
largest model still scores reasonably (it saved 0% compute but wasn't
mis-routed), while a request served entirely by the baseline-sized
model due to a fallback failure scores lowest.
"""

from __future__ import annotations

import logging

from app.models.schemas import SustainabilityMetrics
from app.utils.constants import ComplexityTier

logger = logging.getLogger(__name__)

# Weight given to compute-saved percentage vs. tier bonus.
_COMPUTE_WEIGHT = 0.70
_TIER_BONUS_WEIGHT = 0.30

# Bonus points (0-100 scale, pre-weighting) awarded purely for which
# tier ultimately served the request.
_TIER_BONUS: dict[str, float] = {
    ComplexityTier.LOW.value: 100.0,
    ComplexityTier.MEDIUM.value: 65.0,
    ComplexityTier.HIGH.value: 30.0,
}


def compute_green_score(
    metrics: SustainabilityMetrics, complexity: str
) -> float:
    """
    Compute the 0-100 Green Score for a single request.

    Args:
        metrics: Sustainability metrics already computed for this request
            (uses `pct_compute_saved`).
        complexity: The tier that actually served the request ("LOW",
            "MEDIUM", or "HIGH"), used for the routing-quality bonus.

    Returns:
        A float in [0, 100].
    """
    compute_component = max(0.0, min(100.0, metrics.pct_compute_saved))
    tier_component = _TIER_BONUS.get(complexity, _TIER_BONUS[ComplexityTier.HIGH.value])

    score = (compute_component * _COMPUTE_WEIGHT) + (tier_component * _TIER_BONUS_WEIGHT)
    score = round(max(0.0, min(100.0, score)), 1)

    logger.info(
        "Green score=%.1f (compute_component=%.1f, tier_component=%.1f, tier=%s)",
        score, compute_component, tier_component, complexity,
    )
    return score
