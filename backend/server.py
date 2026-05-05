"""
FastAPI server for ScreenTime AI backend.

Run with:
    uvicorn backend.server:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from main import analyze_user
from database import (
    get_or_create_user,
    save_analysis,
    get_user_history,
    get_all_users,
)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ScreenTime AI API",
    description="AI-powered screen time analyzer — brutally honest feedback on your phone habits.",
    version="1.0.0",
)

# Allow all origins so the Streamlit frontend (or any client) can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────

class AppUsage(BaseModel):
    name: str
    hours: float
    type: str


class AnalyzeRequest(BaseModel):
    user_name: str = Field(..., min_length=1, description="Name of the user")
    daily_usage_hours: float = Field(..., ge=0, description="Total daily screen time")
    apps: list[AppUsage] = Field(..., min_length=1, description="List of app usage entries")


class AnalyzeResponse(BaseModel):
    user_id: int
    summary: str
    insights: str
    is_addicted: str
    daily_usage_hours: float


class HistoryItem(BaseModel):
    daily_hours: float
    apps_json: str
    summary: Optional[str] = None
    insights: Optional[str] = None
    is_addicted: Optional[str] = None
    analyzed_at: str


class UserResponse(BaseModel):
    user_id: int
    name: str


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ScreenTime AI API"}


# ── Analysis ──────────────────────────────────────────────────────────────────

@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
def analyze(req: AnalyzeRequest):
    """Run the AI agent on the user's screen time data and save results."""

    # Validate 24h limit
    if req.daily_usage_hours > 24:
        raise HTTPException(
            status_code=400,
            detail=(
                f"A day only has 24 hours! "
                f"You entered {req.daily_usage_hours:.1f} hours — that is not possible."
            ),
        )

    # Get or create user
    user_id = get_or_create_user(req.user_name)

    # Build payload for the DSPy agent
    user_data_dict = {
        "user_id": str(user_id),
        "daily_usage_hours": req.daily_usage_hours,
        "apps": [a.model_dump() for a in req.apps],
    }

    try:
        analysis = analyze_user(user_data_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Save to database
    save_analysis(
        user_id=user_id,
        daily_hours=req.daily_usage_hours,
        apps=[a.model_dump() for a in req.apps],
        summary=str(analysis.summary),
        insights=str(analysis.insights),
        is_addicted=str(analysis.isAddicted),
    )

    return AnalyzeResponse(
        user_id=user_id,
        summary=str(analysis.summary),
        insights=str(analysis.insights),
        is_addicted=str(analysis.isAddicted),
        daily_usage_hours=req.daily_usage_hours,
    )


# ── Users ─────────────────────────────────────────────────────────────────────

@app.get("/users", response_model=list[str], tags=["Users"])
def list_users():
    """Return all registered user names."""
    return get_all_users()


@app.post("/users", response_model=UserResponse, tags=["Users"])
def create_user(name: str):
    """Get or create a user by name and return their ID."""
    uid = get_or_create_user(name)
    return UserResponse(user_id=uid, name=name.strip())


# ── History ───────────────────────────────────────────────────────────────────

@app.get("/history/{user_name}", response_model=list[HistoryItem], tags=["History"])
def user_history(user_name: str, limit: int = 5):
    """Return the last N analyses for a user."""
    uid = get_or_create_user(user_name)
    rows = get_user_history(uid, limit=limit)
    return [HistoryItem(**r) for r in rows]


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
