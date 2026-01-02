"""SQLModel data models for persistent storage."""

from datetime import date, datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Timestamped(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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


class SystemPrompt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    version: str
    content: str


class DailyLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    log_date: date
    weight: Optional[float] = None
    activity: Optional[str] = None
    hunger_level: Optional[str] = None
    food_eaten: Optional[str] = None
    planned_workout: Optional[str] = None
    recommendation: Optional[str] = None
    reasoning: Optional[str] = None
    calorie_estimate: Optional[str] = None
    next_steps: Optional[str] = None


class Workout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    log_date: date
    focus_area: str
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class Meal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    log_date: date
    description: str
    calories: Optional[int] = None
    protein_grams: Optional[int] = None
    notes: Optional[str] = None
