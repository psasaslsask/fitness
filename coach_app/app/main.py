"""FastAPI entrypoint for the local fitness/nutrition coaching engine."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from coach_app.app.api import coach, logs, profile
from coach_app.app.core.config import get_settings
from coach_app.app.db.session import get_session, init_db, seed_defaults

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


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


@app.get("/", include_in_schema=False)
def serve_dashboard():
    if not STATIC_DIR.exists():
        return {"message": "Static files not found"}
    return FileResponse(STATIC_DIR / "index.html")
