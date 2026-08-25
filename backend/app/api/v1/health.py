"""Health and Status Endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.connection import check_db_health
from app.schemas.health import HealthResponse, SystemStatusResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns service health status and database connectivity.",
)
def get_health():
    """Service health check endpoint."""
    db_healthy = check_db_health()
    db_status_str = "connected" if db_healthy else "disconnected"
    overall_status = "ok" if db_healthy else "degraded"

    response_data = HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status_str,
        timestamp=datetime.now(timezone.utc),
    )

    status_code = (
        status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(status_code=status_code, content=response_data.model_dump(mode="json"))


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Detailed System Status",
    description="Returns detailed system diagnostic status.",
)
def get_status():
    """System status and diagnostic information."""
    db_healthy = check_db_health()
    db_type = "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"

    return SystemStatusResponse(
        service_name=settings.PROJECT_NAME,
        status="ok" if db_healthy else "degraded",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database_connected=db_healthy,
        database_type=db_type,
        timestamp=datetime.now(timezone.utc),
    )
