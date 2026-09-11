from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI(
    title="GreenAI Optimizer API",
    description="Backend API for Resource-Aware AI Orchestration and Sustainability Analytics.",
    version="1.0.0"
)

# Enable CORS for React/Next.js frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust during production deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "system": "GreenAI Optimizer Backend Service",
        "version": "1.0.0"
    }