"""Business Analytics API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.analytics import AnalyticsOverviewResponse, SalesTrendResponse
from app.services.analytics_service import get_analytics_overview, get_sales_trend

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Executive Dashboard Overview KPIs",
    description="Returns aggregate retail KPIs including total sales, footfall, active stores, and promo performance.",
)
def get_overview(db: Session = Depends(get_db)):
    """Retrieve executive retail overview metrics."""
    return get_analytics_overview(db)


@router.get(
    "/sales",
    response_model=SalesTrendResponse,
    summary="Historical Sales and Traffic Trends",
    description="Returns daily sales time series with customer traffic and store open counts.",
)
def get_sales(
    start_date: Optional[str] = Query(None, description="Filter start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter end date (YYYY-MM-DD)"),
    limit: int = Query(60, description="Max time-series points to return (default: 60)", le=365, ge=1),
    db: Session = Depends(get_db),
):
    """Retrieve time-series sales trend metrics."""
    return get_sales_trend(db, start_date=start_date, end_date=end_date, limit=limit)
