# app/routers/posts.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.harvesting_agent import analyze_feasibility
from app.agents.cost_agent import analyze_cost_and_schemes

router = APIRouter(prefix="/api", tags=["posts"])

# ---- Feature 1: Feasibility ----
class FeasibilityIn(BaseModel):
    name: str
    location: str
    roof_area: float
    open_space: float

@router.post("/feasibility")
async def check_feasibility(data: FeasibilityIn):
    try:
        # Call your Gemini agent
        result = analyze_feasibility(
            location=data.location,
            roof_area=data.roof_area,
            open_space=data.open_space
        )
        # ✅ return structured JSON, not just message
        return {
            "feasible": result["can_build"],
            "harvesting_type": result["harvesting_type"],
            "reason": result["reason"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Feature 2: Cost Estimation ----
class CostIn(BaseModel):
    type: str
    location: str

@router.post("/cost")
async def estimate_cost(data: CostIn):
    try:
        # Call your Gemini agent
        result = analyze_cost_and_schemes(
            harvesting_type=data.type,
            location=data.location
        )
        return {
            "estimate": result["estimated_cost"],
            "schemes": [s.strip() for s in result["govt_schemes"].split(",") if s.strip()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
