"""Application configuration helpers."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Local Fitness Coach"
    api_prefix: str = ""
    database_url: str = "sqlite:///./fitness.db"
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]

    model_config = SettingsConfigDict(env_file=".env")


def get_settings() -> Settings:
    return Settings()
