"""Database setup utilities for the local coaching app."""

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./fitness.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create all tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Yield a SQLModel session for FastAPI dependencies."""
    with Session(engine) as session:
        yield session
