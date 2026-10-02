"""
Centralized application configuration.
Reads values from environment variables / .env file — nothing is hardcoded.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/chatarchive"

    # Redis / Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Vector DB
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_API_KEY: str | None = None

    # CORS
    CORS_ORIGINS: str = "*"

    # App
    PROJECT_NAME: str = "ChatArchive"

    class Config:
        env_file = ".env"


settings = Settings()