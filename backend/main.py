
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.models.travel import TravelRequest
from backend.agents.travel_agent_7 import run_phase7_travel_agent
from backend.agents.mcp_travel_agent import plan_trip_via_mcp


app = FastAPI(
    title="Smart Flight + Hotel Agent API",
    description="API for planning flights and hotels using an AI travel agent.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class TravelPlanResponse(BaseModel):
    message: str
    travel_request: dict[str, Any]
    recommendation_count: int
    recommendations: list[dict[str, Any]]
    explanation: str


@app.get("/")
async def root():
    return {
        "message": "Smart Flight + Hotel Agent API is running."
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "smart-flight-hotel-agent-api",
    }


@app.post("/travel/validate")
async def validate_travel_request(request: TravelRequest):
    return {
        "message": "Travel request validated successfully.",
        "travel_request": request.model_dump(mode="json"),
    }


@app.post(
    "/travel/plan",
    response_model=TravelPlanResponse,
)
async def plan_travel(request: TravelRequest):
    try:
        # Get structured flight + hotel options from the Python planner.
        options = await plan_trip_via_mcp(request)

        # Get the natural-language explanation from the Phase 7 agent.
        explanation = await run_phase7_travel_agent(request)

        return TravelPlanResponse(
            message="Travel plan generated successfully.",
            travel_request=request.model_dump(mode="json"),
            recommendation_count=len(options),
            recommendations=options,
            explanation=explanation,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Travel planning failed.",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        ) from exc