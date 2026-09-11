"""
schemas.py
==========
Pydantic v2 request/response models shared across routers and services.

Every service function returns one of these typed models rather than a
raw dict, so FastAPI can validate + document the API automatically via
Swagger/OpenAPI, and so every downstream consumer gets IDE autocomplete
and type checking instead of guessing dict keys.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Incoming request body for POST /api/chat."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="The user's natural-language prompt to classify, route, and answer.",
        examples=["Explain the difference between TCP and UDP in two sentences."],
    )


class ClassificationResult(BaseModel):
    """Output of the heuristic complexity classifier."""

    complexity: str = Field(..., description="One of LOW, MEDIUM, HIGH.")
    reason: str = Field(..., description="Human-readable explanation of why this tier was chosen.")
    word_count: int = Field(..., ge=0, description="Word count of the raw prompt.")
    has_code: bool = Field(..., description="Whether the prompt appears to contain or request code.")


class ModelRoutingResult(BaseModel):
    """Output of the model router + LLM generation step."""

    model_config = ConfigDict(protected_namespaces=())

    response: str = Field(..., description="The generated answer text.")
    model_used: str = Field(..., description="Human-readable name of the model that actually served the request.")
    model_id: str = Field(..., description="Provider-specific model identifier that actually served the request.")
    provider: str = Field(..., description="Provider that actually served the request (gemini or groq).")
    execution_time_sec: float = Field(..., ge=0, description="Wall-clock time taken to generate the response.")
    tokens_processed: int = Field(..., ge=0, description="Estimated total tokens (prompt + completion).")
    est_power_watts: float = Field(..., ge=0, description="Assumed average inference power draw for this model class.")
    fallback_used: bool = Field(False, description="True if the primary provider failed and a fallback tier was used.")


class SustainabilityMetrics(BaseModel):
    """Output of the energy/carbon/green-score pipeline."""

    energy_consumed_wh: float = Field(..., ge=0, description="Estimated energy actually used, in watt-hours.")
    co2_emitted_g: float = Field(..., ge=0, description="Estimated CO2 emitted for the actual run, in grams.")
    baseline_energy_wh: float = Field(..., ge=0, description="Estimated energy if the largest model had handled this request.")
    baseline_co2_g: float = Field(..., ge=0, description="Estimated CO2 if the largest model had handled this request.")
    energy_saved_wh: float = Field(..., description="baseline_energy_wh - energy_consumed_wh.")
    co2_saved_g: float = Field(..., description="baseline_co2_g - co2_emitted_g.")
    pct_compute_saved: float = Field(..., description="Percentage energy saved relative to the baseline run.")
    green_score: float = Field(..., ge=0, le=100, description="0-100 sustainability score for this request.")


class ChatResponse(BaseModel):
    """Full response body for POST /api/chat, combining every pipeline stage."""

    classification: ClassificationResult
    routing: ModelRoutingResult
    sustainability: SustainabilityMetrics


class HealthResponse(BaseModel):
    """Simple health-check payload."""

    status: str
    service: str
    version: str
