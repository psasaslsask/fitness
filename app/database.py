"""Database setup utilities for the local coaching app."""

from sqlmodel import SQLModel, create_engine, Session, select

from .models import SystemPrompt, UserProfile

DATABASE_URL = "sqlite:///./fitness.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create all tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def seed_defaults() -> None:
    """Ensure a baseline profile and system prompt exist for consistent behavior."""
    with Session(engine) as session:
        if not session.exec(select(UserProfile)).first():
            session.add(
                UserProfile(
                    sex="female",
                    height="5'1\"",
                    weight_range="120–130 lbs",
                    goal="fat loss while maintaining muscle",
                    training_style="weights 1.5–2h per session",
                    focus_areas="legs, glutes, core",
                    gym_closures="gym closed on Sundays",
                    menstrual_cycle_notes="regular cycle affects energy and water retention",
                    fueling_sensitivity="sensitive to under-fueling and late-night hunger",
                    reassurance_needs="wants reassurance and clear decision support",
                )
            )

        if not session.exec(select(SystemPrompt)).first():
            session.add(
                SystemPrompt(
                    version="v1",
                    content=(
                        "You are a calm, supportive, opinionated fitness and nutrition coach. "
                        "You serve one user: female, 5'1\", 120–130 lbs, training legs/glutes/core with 1.5–2h weight sessions. "
                        "Goal: fat loss while maintaining muscle. The gym is closed Sundays. The menstrual cycle impacts energy and water retention. "
                        "The user is sensitive to under-fueling and late-night hunger and wants reassurance plus clear decision support. "
                        "Always provide concise, structured guidance that includes: recommendation, reasoning, calorie estimate, and next steps. "
                        "Respect recovery, warn against under-fueling, and keep a warm, steady tone."
                    ),
                )
            )

        session.commit()


def get_session() -> Session:
    """Yield a SQLModel session for FastAPI dependencies."""
    with Session(engine) as session:
        yield session
