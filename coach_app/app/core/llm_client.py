"""Thin LLM client wrapper using an OpenAI-style chat completion API."""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import ValidationError

from coach_app.app.schemas import RecommendationResponse

API_URL = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")


class LLMClient:
    def __init__(
        self,
        api_url: str = API_URL,
        api_key: Optional[str] = API_KEY,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

    async def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.2) -> Dict[str, Any]:
        if not self.api_key:
            return RecommendationResponse(
                recommendation="Strength train lower body today. Keep it to 90 minutes with controlled tempo squats and hip thrusts.",
                reasoning="Maintains focus on legs/glutes while respecting recovery windows.",
                calorie_estimate="Target ~1,950 kcal with 130g protein and front-load carbs pre-training.",
                next_steps="Warm up, lift, log meals, hydrate. If hunger spikes tonight, add 150-200 kcal protein snack early.",
            ).model_dump()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.api_url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = self._coerce_json(content)
                    validated = RecommendationResponse.model_validate(parsed)
                    return validated.model_dump()
            except (httpx.HTTPError, ValidationError, ValueError) as exc:  # pragma: no cover - defensive
                last_error = exc
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * attempt)
                    continue
                raise ValueError(f"LLM response failed after retries: {exc}") from exc
        raise ValueError("LLM response failed after retries") from last_error

    @staticmethod
    def _coerce_json(content: Any) -> Dict[str, Any]:
        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                raise ValueError("LLM did not return valid JSON") from exc
        raise ValueError("Unsupported LLM response type")
