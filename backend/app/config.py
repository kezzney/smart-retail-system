"""Application Configuration."""

import os
from functools import lru_cache
from typing import List

# Base directory for the repository root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_FILE = os.path.join(BASE_DIR, "smart_retail.db").replace("\\", "/")


class Settings:
    """Application settings loaded from environment variables with sensible defaults."""

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Smart Retail Intelligence System")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database configuration
    # Defaults to canonical SQLite DB in repository root; can be overridden by PostgreSQL URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE}"
    )

    # External Raw Datasets Root
    SMART_RETAIL_DATA_ROOT: str = os.getenv(
        "SMART_RETAIL_DATA_ROOT",
        r"C:\Users\CHANDAN\Downloads\SmartRetailData",
    )

    # Repository Processed Data Directory
    PROCESSED_DATA_DIR: str = os.getenv(
        "PROCESSED_DATA_DIR",
        os.path.join(BASE_DIR, "data", "processed"),
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

    # Computer Vision / YOLO Configuration
    # Remote fine-tuned model URL (Hugging Face model repository)
    YOLO_MODEL_URL: str = os.getenv(
        "YOLO_MODEL_URL",
        "https://huggingface.co/Kezzney/smart-retail-yolov8/resolve/main/best.pt",
    )
    YOLO_MODEL_CACHE_DIR: str = os.getenv(
        "YOLO_MODEL_CACHE_DIR",
        os.path.join(BASE_DIR, "data", "models"),
    )
    # Local fine-tuned model path from training run
    _DEFAULT_LOCAL_MODEL_PATH: str = os.path.join(
        BASE_DIR, "runs", "detect", "runs", "detect", "sku110k_poc", "weights", "best.pt"
    )
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", _DEFAULT_LOCAL_MODEL_PATH)
    DEFAULT_CONFIDENCE_THRESHOLD: float = float(os.getenv("DEFAULT_CONFIDENCE_THRESHOLD", "0.25"))
    DEFAULT_IOU_THRESHOLD: float = float(os.getenv("DEFAULT_IOU_THRESHOLD", "0.45"))





@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
