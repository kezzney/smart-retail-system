"""Demand Forecasting and Restocking Pydantic Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    """Single time-series data point."""

    date: str = Field(..., description="Date string YYYY-MM-DD")
    actual: Optional[float] = Field(None, description="Actual demand (None for future forecast)")
    predicted: float = Field(..., description="Model predicted demand")


class ForecastResponse(BaseModel):
    """Full forecast response for a single item."""

    item_id: str = Field(..., description="SKU / item identifier")
    store_id: str = Field(..., description="Store identifier")
    category: str = Field(..., description="Item category (FOODS, HOBBIES, HOUSEHOLD)")
    model_name: str = Field(..., description="Forecasting model/approach used")
    forecast_horizon_days: int = Field(..., description="Number of days forecast into the future")
    mae: Optional[float] = Field(None, description="Mean Absolute Error on validation split (if available)")
    rmse: Optional[float] = Field(None, description="Root Mean Squared Error on validation split")
    history: List[ForecastPoint] = Field(default_factory=list, description="Historical demand points")
    forecast: List[ForecastPoint] = Field(default_factory=list, description="Predicted future demand")


class RestockingRecommendation(BaseModel):
    """Single SKU restocking recommendation."""

    item_id: str = Field(..., description="SKU / item identifier")
    store_id: str = Field(..., description="Store identifier")
    category: str = Field(..., description="Product category")
    avg_recent_demand: float = Field(..., description="Average daily demand in the recent observation window")
    avg_forecast_demand: float = Field(..., description="Average daily forecast demand over horizon")
    demand_trend_pct: float = Field(..., description="Percentage change: forecast vs recent demand")
    recommended_reorder_qty: int = Field(..., description="Recommended units to reorder")
    urgency: str = Field(..., description="Urgency status: CRITICAL | REORDER_SOON | MONITOR | ADEQUATE")
    reason: str = Field(..., description="Human-readable explanation of the recommendation")
    forecast_horizon_days: int = Field(..., description="Horizon used for forecast demand calculation")


class RestockingListResponse(BaseModel):
    """Paginated restocking recommendations list."""

    total: int
    limit: int
    items: List[RestockingRecommendation]


class ForecastCatalogItem(BaseModel):
    """Lightweight item summary used in the forecast catalog listing."""

    item_id: str
    store_id: str
    category: str
    avg_daily_demand: float
    peak_daily_demand: float
