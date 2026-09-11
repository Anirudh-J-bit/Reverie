from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    prompt: str = Field(..., example="Explain TCP congestion control with an example.")

class TaskAnalysis(BaseModel):
    complexity: str
    reasoning: str
    word_count: int
    has_code: bool

class ModelDetails(BaseModel):
    selected_model: str
    model_id: str
    execution_time_sec: float
    tokens_processed: int

class SustainabilityMetrics(BaseModel):
    energy_consumed_wh: float
    co2_emitted_g: float
    baseline_energy_wh: float
    baseline_co2_g: float
    energy_saved_wh: float
    co2_saved_g: float
    pct_compute_saved: float
    green_score: int

class ChatResponse(BaseModel):
    response: str
    task_analysis: TaskAnalysis
    model_details: ModelDetails
    sustainability_metrics: SustainabilityMetrics