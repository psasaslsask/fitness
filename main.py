"""FastAPI entrypoint for the local fitness/nutrition coaching engine."""

from datetime import date
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.database import get_session, init_db, seed_defaults
from app.llm_client import LLMClient
from app.models import DailyLog, SystemPrompt, UserProfile
from app.prompting import PromptBuilder
from app.schemas import CoachResponse, DailyInput, ProfilePayload, SystemPromptPayload

app = FastAPI(title="Local Fitness Coach", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_defaults()


@app.get("/profile", response_model=ProfilePayload)
def get_profile(session: Session = Depends(get_session)) -> ProfilePayload:
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not set")
    return ProfilePayload(**profile.dict())


@app.put("/profile", response_model=ProfilePayload)
def update_profile(payload: ProfilePayload, session: Session = Depends(get_session)) -> ProfilePayload:
    profile = session.exec(select(UserProfile)).first()
    if profile:
        for key, value in payload.dict().items():
            setattr(profile, key, value)
        session.add(profile)
    else:
        profile = UserProfile(**payload.dict())
        session.add(profile)
    session.commit()
    session.refresh(profile)
    return ProfilePayload(**profile.dict())


@app.get("/logs", response_model=List[CoachResponse])
def list_logs(limit: int = 10, session: Session = Depends(get_session)) -> List[CoachResponse]:
    logs = session.exec(select(DailyLog).order_by(DailyLog.log_date.desc()).limit(limit)).all()
    return [
        CoachResponse(
            log_id=log.id,
            recommendation=log.recommendation or "",
            reasoning=log.reasoning or "",
            calorie_estimate=log.calorie_estimate or "",
            next_steps=log.next_steps or "",
        )
        for log in logs
    ]


@app.post("/coach", response_model=CoachResponse)
async def coach(input: DailyInput, session: Session = Depends(get_session)) -> CoachResponse:
    builder = PromptBuilder(session)
    messages = builder.build_messages(today_inputs=input.dict(), today=input.log_date)

    client = LLMClient()
    llm_response = await client.chat(messages, temperature=0.25)

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


@app.get("/system-prompt", response_model=SystemPromptPayload)
def get_system_prompt(session: Session = Depends(get_session)) -> SystemPromptPayload:
    prompt_row = session.exec(select(SystemPrompt).order_by(SystemPrompt.id.desc())).first()
    if not prompt_row:
        raise HTTPException(status_code=404, detail="System prompt not set")
    return SystemPromptPayload(version=prompt_row.version, content=prompt_row.content)


@app.put("/system-prompt", response_model=SystemPromptPayload)
def update_system_prompt(payload: SystemPromptPayload, session: Session = Depends(get_session)) -> SystemPromptPayload:
    prompt_row = SystemPrompt(version=payload.version, content=payload.content)
    session.add(prompt_row)
    session.commit()
    session.refresh(prompt_row)
    return SystemPromptPayload(version=prompt_row.version, content=prompt_row.content)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}
