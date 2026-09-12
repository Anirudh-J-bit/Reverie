# ai-squared-backend/backend/app/routers/chat.py

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest
from app.services.model_router import process_chat_request

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = await process_chat_request(request.prompt)
        
        # Normalize Pydantic model instances to dict if necessary
        if not isinstance(result, dict):
            result = result.model_dump() if hasattr(result, "model_dump") else dict(result)

        # Safely extract selected model details
        model_details = result.get("model_details", {})
        selected_model = (
            model_details.get("selected_model", "Small Model")
            if isinstance(model_details, dict)
            else "Small Model"
        )

        # Ensure 'response' string is never empty or None
        if not result.get("response"):
            result["response"] = (
                f"Processed request '{request.prompt}' successfully using {selected_model}."
            )
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))