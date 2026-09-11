from typing import Dict, Any

class EnergyEstimator:
    """
    Estimates electricity usage (Wh) and carbon footprint (g CO2e).
    """

    # Average global carbon intensity factor: ~475 g CO2e / kWh = 0.475 g CO2e / Wh
    CARBON_INTENSITY_FACTOR = 0.475  

    # Baseline: High-performance Large Model parameters (350W average power draw)
    BASELINE_LARGE_MODEL_WATTS = 350.0

    @classmethod
    def calculate_impact(cls, execution_time_sec: float, power_watts: float) -> Dict[str, Any]:
        # Energy = (Power in Watts * Time in seconds) / 3600 -> Watt-hours (Wh)
        energy_wh = (power_watts * execution_time_sec) / 3600.0
        co2_grams = energy_wh * cls.CARBON_INTENSITY_FACTOR

        # Baseline Calculation (assuming task was forced through Large Model)
        baseline_energy_wh = (cls.BASELINE_LARGE_MODEL_WATTS * execution_time_sec) / 3600.0
        baseline_co2_grams = baseline_energy_wh * cls.CARBON_INTENSITY_FACTOR

        # Savings calculation
        energy_saved_wh = max(0.0, baseline_energy_wh - energy_wh)
        co2_saved_grams = max(0.0, baseline_co2_grams - co2_grams)
        pct_compute_saved = round(((cls.BASELINE_LARGE_MODEL_WATTS - power_watts) / cls.BASELINE_LARGE_MODEL_WATTS) * 100, 2)

        return {
            "energy_consumed_wh": round(energy_wh, 4),
            "co2_emitted_g": round(co2_grams, 4),
            "baseline_energy_wh": round(baseline_energy_wh, 4),
            "baseline_co2_g": round(baseline_co2_grams, 4),
            "energy_saved_wh": round(energy_saved_wh, 4),
            "co2_saved_g": round(co2_saved_grams, 4),
            "pct_compute_saved": max(0.0, pct_compute_saved)
        }
        