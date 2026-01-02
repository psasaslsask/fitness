"""FastAPI entrypoint for the local fitness/nutrition coaching engine."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from coach_app.app.api import coach, logs, profile
from coach_app.app.core.config import get_settings
from coach_app.app.db.session import get_session, init_db, seed_defaults

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_defaults()


app.include_router(profile.router)
app.include_router(coach.router)
app.include_router(logs.router)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}
