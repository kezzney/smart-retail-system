"""Application Configuration."""

import os
from functools import lru_cache
from typing import List


class Settings:
    """Application settings loaded from environment variables with sensible defaults."""

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Smart Retail Intelligence System")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database configuration
    # Defaults to SQLite for local development; can be overridden by PostgreSQL URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./smart_retail.db"
    )

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
