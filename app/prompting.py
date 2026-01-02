"""Prompt assembly utilities for the coaching agent."""

from datetime import date
from typing import List, Optional

from sqlmodel import Session, select

from .models import DailyLog, SystemPrompt, UserProfile


DEFAULT_SYSTEM_PROMPT = """You are a calm, supportive fitness and nutrition coach. You provide concise, structured guidance focusing on sustainable fat loss while maintaining muscle. Always consider menstrual cycle effects, under-fueling risks, and gym closures."""


class PromptBuilder:
    """Combines system prompt, user profile, and recent logs into a structured LLM payload."""

    def __init__(self, session: Session):
        self.session = session

    def load_profile(self) -> Optional[UserProfile]:
        return self.session.exec(select(UserProfile)).first()

    def load_system_prompt(self) -> str:
        prompt_row = self.session.exec(select(SystemPrompt).order_by(SystemPrompt.id.desc())).first()
        if prompt_row:
            return prompt_row.content
        return DEFAULT_SYSTEM_PROMPT

    def load_recent_logs(self, limit: int = 7) -> List[DailyLog]:
        return list(
            self.session.exec(select(DailyLog).order_by(DailyLog.log_date.desc()).limit(limit))
        )

    def build_messages(
        self,
        today_inputs: dict,
        today: Optional[date] = None,
    ) -> list:
        profile = self.load_profile()
        system_prompt = self.load_system_prompt()
        recent_logs = self.load_recent_logs()

        profile_block = {
            "sex": profile.sex if profile else "female",
            "height": profile.height if profile else "5'1\"",
            "weight_range": profile.weight_range if profile else "120-130 lbs",
            "goal": profile.goal if profile else "fat loss while maintaining muscle",
            "training_style": profile.training_style if profile else "weights 1.5-2h",
            "focus_areas": profile.focus_areas if profile else "legs, glutes, core",
            "gym_closures": profile.gym_closures if profile else "Sunday closures",
            "menstrual_cycle_notes": profile.menstrual_cycle_notes if profile else "regular cycle impacts energy and water",
            "fueling_sensitivity": profile.fueling_sensitivity if profile else "sensitive to under-fueling and late-night hunger",
            "reassurance_needs": profile.reassurance_needs if profile else "wants reassurance and clear decision support",
        }

        history_block = [
            {
                "date": log.log_date.isoformat(),
                "weight": log.weight,
                "activity": log.activity,
                "hunger": log.hunger_level,
                "food": log.food_eaten,
                "planned_workout": log.planned_workout,
                "recommendation": log.recommendation,
            }
            for log in recent_logs
        ]

        user_message = {
            "today": today.isoformat() if today else None,
            "inputs": today_inputs,
            "profile": profile_block,
            "recent_logs": history_block,
        }

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
