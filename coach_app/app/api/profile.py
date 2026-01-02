"""Profile and system prompt management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from coach_app.app.db.models import SystemPrompt, UserProfile
from coach_app.app.db.session import get_session
from coach_app.app.schemas import ProfilePayload, SystemPromptPayload

router = APIRouter(prefix="", tags=["profile"])


@router.get("/profile", response_model=ProfilePayload)
def get_profile(session: Session = Depends(get_session)) -> ProfilePayload:
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not set")
    return ProfilePayload(**profile.model_dump())


@router.put("/profile", response_model=ProfilePayload)
def update_profile(payload: ProfilePayload, session: Session = Depends(get_session)) -> ProfilePayload:
    profile = session.exec(select(UserProfile)).first()
    if profile:
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)
        session.add(profile)
    else:
        profile = UserProfile(**payload.model_dump())
        session.add(profile)
    session.commit()
    session.refresh(profile)
    return ProfilePayload(**profile.model_dump())


@router.get("/system-prompt", response_model=SystemPromptPayload)
def get_system_prompt(session: Session = Depends(get_session)) -> SystemPromptPayload:
    prompt_row = session.exec(select(SystemPrompt).order_by(SystemPrompt.id.desc())).first()
    if not prompt_row:
        raise HTTPException(status_code=404, detail="System prompt not set")
    return SystemPromptPayload(version=prompt_row.version, content=prompt_row.content)


@router.put("/system-prompt", response_model=SystemPromptPayload)
def update_system_prompt(payload: SystemPromptPayload, session: Session = Depends(get_session)) -> SystemPromptPayload:
    prompt_row = SystemPrompt(version=payload.version, content=payload.content)
    session.add(prompt_row)
    session.commit()
    session.refresh(prompt_row)
    return SystemPromptPayload(version=prompt_row.version, content=prompt_row.content)
