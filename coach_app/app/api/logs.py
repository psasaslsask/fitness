"""Endpoints for retrieving coaching logs."""

from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from coach_app.app.db.models import DailyLog
from coach_app.app.db.session import get_session
from coach_app.app.schemas import CoachResponse

router = APIRouter(prefix="", tags=["logs"])


@router.get("/logs", response_model=List[CoachResponse])
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
