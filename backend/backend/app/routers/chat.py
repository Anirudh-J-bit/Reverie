from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.classifier import TaskClassifier
from app.services.model_router import ModelRouter
from app.services.energy_estimator import EnergyEstimator
from app.services.green_score import GreenScoreCalculator

router = APIRouter(prefix="/api", tags=["Chat & Optimization"])

@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
        
    classification = TaskClassifier.classify(request.prompt)
    complexity = classification["complexity"]

    inference_result = await ModelRouter.execute_inference(request.prompt, complexity)

    impact = EnergyEstimator.calculate_impact(
        execution_time_sec=inference_result["execution_time_sec"],
        power_watts=inference_result["est_power_watts"]
    )

    score = GreenScoreCalculator.calculate_score(complexity, impact["pct_compute_saved"])

    return ChatResponse(
        response=inference_result["response"],
        task_analysis={
            "complexity": complexity,
            "reasoning": classification["reason"],
            "word_count": classification["word_count"],
            "has_code": classification["has_code"]
        },
        model_details={
            "selected_model": inference_result["model_used"],
            "model_id": inference_result["model_id"],
            "execution_time_sec": inference_result["execution_time_sec"],
            "tokens_processed": inference_result["tokens_processed"]
        },
        sustainability_metrics={
            "energy_consumed_wh": impact["energy_consumed_wh"],
            "co2_emitted_g": impact["co2_emitted_g"],
            "baseline_energy_wh": impact["baseline_energy_wh"],
            "baseline_co2_g": impact["baseline_co2_g"],
            "energy_saved_wh": impact["energy_saved_wh"],
            "co2_saved_g": impact["co2_saved_g"],
            "pct_compute_saved": impact["pct_compute_saved"],
            "green_score": score
        }
    )