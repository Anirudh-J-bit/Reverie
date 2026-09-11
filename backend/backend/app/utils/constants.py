import os

# Model Constants & Wattages
BASELINE_LARGE_MODEL_WATTS = float(os.getenv("BASELINE_LARGE_MODEL_WATTS", "350.0"))

MODEL_CONFIGS = {
    "LOW": {
        "model_name": os.getenv("SMALL_MODEL_ID", "llama3.2:1b"),
        "tier_label": "Small Model",
        "est_power_watts": 45.0,
        "quality_tier": 0.78
    },
    "MEDIUM": {
        "model_name": os.getenv("MEDIUM_MODEL_ID", "llama3.2:3b"),
        "tier_label": "Medium Model",
        "est_power_watts": 120.0,
        "quality_tier": 0.90
    },
    "HIGH": {
        "model_name": os.getenv("LARGE_MODEL_ID", "llama3:70b"),
        "tier_label": "Large Model",
        "est_power_watts": 350.0,
        "quality_tier": 0.96
    }
}

# Environmental Metrics (0.475 g CO2e per Wh / ~475 g per kWh)
DEFAULT_CARBON_INTENSITY = float(os.getenv("CARBON_INTENSITY_FACTOR", "0.475"))

# Classifier Heuristics
HIGH_COMPLEXITY_PATTERNS = [
    r"\banalyze\b", r"\bcompare\b", r"\bproof\b", r"\brefactor\b", 
    r"\barchitect\b", r"\bbenchmark\b", r"\bdataset\b", r"\bresearch paper\b",
    r"\boptimize\b", r"\bdesign pattern\b", r"\bsecurity audit\b"
]

MEDIUM_COMPLEXITY_PATTERNS = [
    r"\bexplain\b", r"\bhow to\b", r"\bsummarize\b", r"\bwrite a function\b",
    r"\bdebug\b", r"\bdifference between\b", r"\bexample of\b"
]