"""Health and System Status Schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Structured response schema for service health status."""

    status: str = Field(..., description="Overall health status", examples=["ok"])
    version: str = Field(..., description="Application version", examples=["0.1.0"])
    environment: str = Field(..., description="Current environment mode", examples=["development"])
    database: str = Field(..., description="Database connection status", examples=["connected"])
    timestamp: datetime = Field(..., description="UTC timestamp of the health check")


class SystemStatusResponse(BaseModel):
    """Detailed system diagnostic status schema."""

    service_name: str
    status: str
    version: str
    environment: str
    database_connected: bool
    database_type: str
    timestamp: datetime
