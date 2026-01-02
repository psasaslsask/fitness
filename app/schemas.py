"""Pydantic request/response schemas for API endpoints."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class DailyInput(BaseModel):
    log_date: date
    weight: Optional[float] = None
    activity: Optional[str] = None
    hunger_level: Optional[str] = Field(default=None, description="Low/Medium/High")
    food_eaten: Optional[str] = None
    planned_workout: Optional[str] = None


class RecommendationResponse(BaseModel):
    recommendation: str
    reasoning: str
    calorie_estimate: str
    next_steps: str


class CoachResponse(RecommendationResponse):
    log_id: int


class ProfilePayload(BaseModel):
    sex: str
    height: str
    weight_range: str
    goal: str
    training_style: str
    focus_areas: str
    gym_closures: str
    menstrual_cycle_notes: str
    fueling_sensitivity: str
    reassurance_needs: str
