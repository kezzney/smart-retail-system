"""Forecasting and Restocking API Endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.schemas.forecasting import ForecastResponse, RestockingListResponse
from app.services.forecasting_service import forecast_item, get_available_items, FORECAST_HORIZON
from app.services.restocking_service import generate_restocking_recommendations

router = APIRouter(tags=["Forecasting"])


@router.get(
    "/restocking/recommendations",
    response_model=RestockingListResponse,
    summary="Restocking Recommendations",
    description=(
        "Returns prioritized restocking recommendations for all tracked SKUs. "
        "Items are ranked by urgency (CRITICAL > REORDER_SOON > MONITOR > ADEQUATE) "
        "then by recommended reorder quantity."
    ),
)
def get_restocking_recommendations(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of recommendations to return"),
    urgency: Optional[str] = Query(
        None,
        description="Filter by urgency level: CRITICAL, REORDER_SOON, MONITOR, or ADEQUATE",
    ),
):
    """Generate and return restocking recommendations."""
    return generate_restocking_recommendations(limit=limit, urgency_filter=urgency)


@router.get(
    "/forecast/{item_id}",
    response_model=ForecastResponse,
    summary="Item Demand Forecast",
    description=(
        "Returns historical demand and a forward-looking demand forecast for the given item_id. "
        "The item_id format is: CATEGORY_N_NNN (e.g. FOODS_1_001). "
        "Use the store_id query parameter to select a specific store (default: CA_1)."
    ),
)
def get_item_forecast(
    item_id: str,
    store_id: str = Query("CA_1", description="Store identifier (e.g. CA_1, TX_2)"),
    horizon: int = Query(
        FORECAST_HORIZON,
        ge=7,
        le=28,
        description=f"Forecast horizon in days (default: {FORECAST_HORIZON})",
    ),
):
    """Return demand forecast for a single SKU / store combination."""
    result = forecast_item(item_id=item_id, store_id=store_id, horizon=horizon)

    if result is None:
        # Try to suggest available items
        available = get_available_items()
        available_ids = sorted({i["item_id"] for i in available})[:10]
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"No forecasting data found for item_id='{item_id}', store_id='{store_id}'.",
                "hint": "The item_id or store_id combination was not found in the processed dataset.",
                "sample_item_ids": available_ids,
            },
        )

    return ForecastResponse(**result)


@router.get(
    "/forecast",
    summary="List Forecastable Items",
    description="Returns a list of all item/store combinations available in the forecasting dataset.",
)
def list_forecast_items(
    limit: int = Query(50, ge=1, le=500),
    category: Optional[str] = Query(None, description="Filter by category: FOODS, HOBBIES, HOUSEHOLD"),
):
    """List available forecastable item/store combinations."""
    items = get_available_items()
    if category:
        items = [i for i in items if i.get("category", "").upper() == category.upper()]
    return {"total": len(items), "items": items[:limit]}
