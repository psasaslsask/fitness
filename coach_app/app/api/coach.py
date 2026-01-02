"""Coach endpoint for generating daily recommendations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from coach_app.app.core.llm_client import LLMClient
from coach_app.app.core.prompt_builder import PromptBuilder
from coach_app.app.db.session import get_session
from coach_app.app.db.models import DailyLog
from coach_app.app.schemas import CoachResponse, DailyInput

router = APIRouter(prefix="", tags=["coach"])


@router.post("/coach", response_model=CoachResponse)
async def coach(input: DailyInput, session: Session = Depends(get_session)) -> CoachResponse:
    builder = PromptBuilder(session)
    messages = builder.build_messages(today_inputs=input.dict(), today=input.log_date)

    client = LLMClient()
    try:
        llm_response = await client.chat(messages, temperature=0.25)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM call failed: {exc}",
        ) from exc

    log = DailyLog(
        log_date=input.log_date,
        weight=input.weight,
        activity=input.activity,
        hunger_level=input.hunger_level,
        food_eaten=input.food_eaten,
        planned_workout=input.planned_workout,
        recommendation=llm_response.get("recommendation"),
        reasoning=llm_response.get("reasoning"),
        calorie_estimate=llm_response.get("calorie_estimate"),
        next_steps=llm_response.get("next_steps"),
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    return CoachResponse(
        log_id=log.id,
        recommendation=log.recommendation or "",
        reasoning=log.reasoning or "",
        calorie_estimate=log.calorie_estimate or "",
        next_steps=log.next_steps or "",
    )
