"""
energy_estimator.py
====================
Estimates energy consumption and CO2 emissions for:

1. The ACTUAL request (using the model that really served it), and
2. A BASELINE hypothetical where the request had instead been sent to
   the largest model tier (`BASELINE_TIER`, i.e. what most naive AI
   systems do today: send everything to the biggest model).

The delta between these two is the whole point of AI² -- it's the
"sustainability benefit" of resource-aware routing.

All figures are heuristic, order-of-magnitude estimates suitable for a
hackathon demo, not a certified energy audit. See the note at the top
of `constants.py`.
"""

from __future__ import annotations

import logging

from app.models.schemas import ModelRoutingResult, SustainabilityMetrics
from app.utils.constants import BASELINE_TIER, CARBON_INTENSITY_G_PER_KWH, MODEL_CONFIG

logger = logging.getLogger(__name__)


def _watt_seconds_to_wh(power_watts: float, seconds: float) -> float:
    """Convert power (W) x time (s) into energy (Wh)."""
    return (power_watts * seconds) / 3600.0


def _wh_to_co2_grams(energy_wh: float) -> float:
    """Convert energy (Wh) into estimated CO2 emissions (g) via grid intensity."""
    energy_kwh = energy_wh / 1000.0
    return energy_kwh * CARBON_INTENSITY_G_PER_KWH


def estimate_sustainability(routing_result: ModelRoutingResult) -> SustainabilityMetrics:
    """
    Compute actual vs. baseline energy/CO2 for a completed request.

    Args:
        routing_result: The result returned by `model_router.route_request`,
            containing the actual model used, its power draw, and the
            measured execution time / token count.

    Returns:
        A SustainabilityMetrics object with actual, baseline, and
        saved energy/CO2 figures plus the percentage of compute saved.
        (The green_score field is left at 0 here -- it's filled in by
        `green_score.py`, which needs this object as input.)
    """
    # --- Actual run ----------------------------------------------------
    energy_consumed_wh = _watt_seconds_to_wh(
        routing_result.est_power_watts, routing_result.execution_time_sec
    )
    co2_emitted_g = _wh_to_co2_grams(energy_consumed_wh)

    # --- Hypothetical baseline: same token count, but on the biggest model --
    baseline_config = MODEL_CONFIG[BASELINE_TIER]
    baseline_power_watts = float(baseline_config["avg_power_watts"])
    baseline_sec_per_token = float(baseline_config["sec_per_token"])
    baseline_time_sec = routing_result.tokens_processed * baseline_sec_per_token

    # If the actual request *was* already served by the baseline tier,
    # baseline == actual (no hypothetical difference to report).
    if routing_result.model_id == baseline_config["model_id"]:
        baseline_time_sec = routing_result.execution_time_sec
        baseline_power_watts = routing_result.est_power_watts

    baseline_energy_wh = _watt_seconds_to_wh(baseline_power_watts, baseline_time_sec)
    baseline_co2_g = _wh_to_co2_grams(baseline_energy_wh)

    # --- Savings ---------------------------------------------------------
    energy_saved_wh = max(0.0, baseline_energy_wh - energy_consumed_wh)
    co2_saved_g = max(0.0, baseline_co2_g - co2_emitted_g)
    pct_compute_saved = (
        (energy_saved_wh / baseline_energy_wh) * 100.0 if baseline_energy_wh > 0 else 0.0
    )

    logger.info(
        "Sustainability: actual=%.5fWh baseline=%.5fWh saved=%.1f%%",
        energy_consumed_wh, baseline_energy_wh, pct_compute_saved,
    )

    return SustainabilityMetrics(
        energy_consumed_wh=round(energy_consumed_wh, 6),
        co2_emitted_g=round(co2_emitted_g, 6),
        baseline_energy_wh=round(baseline_energy_wh, 6),
        baseline_co2_g=round(baseline_co2_g, 6),
        energy_saved_wh=round(energy_saved_wh, 6),
        co2_saved_g=round(co2_saved_g, 6),
        pct_compute_saved=round(pct_compute_saved, 2),
        green_score=0.0,  # populated by green_score.compute_green_score()
    )
