"""Restocking Recommendation Service.

Converts demand forecasts into actionable inventory reorder recommendations
using transparent, documented business rules.

Restocking Rules (in priority order):
---------------------------------------
Given:
  D_recent  = average daily demand over the last 14 days (observation window)
  D_forecast = average daily forecast demand over the next 14 days (horizon)
  trend_pct  = (D_forecast - D_recent) / max(D_recent, 0.1) * 100

  reorder_qty = ceil( D_forecast * LEAD_TIME_DAYS * (1 + SAFETY_BUFFER_PCT) )
              where LEAD_TIME_DAYS = 7, SAFETY_BUFFER_PCT = 0.25 (25%)

Urgency Assignment:
  CRITICAL     — D_recent >= 5 AND trend_pct >= 20  (demand spiking)
  CRITICAL     — D_recent >= 10 (high volume, near zero safe stock)
  REORDER_SOON — D_forecast >= 3 AND trend_pct >= 5  (moderate rising demand)
  REORDER_SOON — D_recent >= 2 AND D_forecast >= D_recent (stable high mover)
  MONITOR      — D_forecast >= 1 AND D_forecast < 3 (low but non-zero)
  ADEQUATE     — All other cases (low demand, stable)
"""

import math
import logging
from typing import List, Optional

from app.services.forecasting_service import (
    load_forecasting_data,
    get_available_items,
    forecast_item,
    FORECAST_HORIZON,
)
from app.schemas.forecasting import RestockingRecommendation, RestockingListResponse

logger = logging.getLogger(__name__)

# Business rule constants — documented and centralized
LEAD_TIME_DAYS = 7
SAFETY_BUFFER_PCT = 0.25
RECENT_WINDOW_DAYS = 14


def _urgency_and_reason(
    d_recent: float,
    d_forecast: float,
    trend_pct: float,
    reorder_qty: int,
) -> tuple[str, str]:
    """Assign urgency label and human-readable reason based on business rules."""

    if d_recent >= 5 and trend_pct >= 20:
        return (
            "CRITICAL",
            f"Demand spiking: forecast is {trend_pct:+.1f}% above recent average "
            f"({d_recent:.1f} → {d_forecast:.1f} units/day). Immediate reorder of {reorder_qty} units advised.",
        )
    if d_recent >= 10:
        return (
            "CRITICAL",
            f"High-velocity SKU ({d_recent:.1f} units/day avg). "
            f"Reorder {reorder_qty} units to cover {LEAD_TIME_DAYS}-day lead time with {int(SAFETY_BUFFER_PCT*100)}% safety buffer.",
        )
    if d_forecast >= 3 and trend_pct >= 5:
        return (
            "REORDER_SOON",
            f"Forecast demand rising ({trend_pct:+.1f}%). Expected {d_forecast:.1f} units/day. "
            f"Reorder {reorder_qty} units within the week.",
        )
    if d_recent >= 2 and d_forecast >= d_recent:
        return (
            "REORDER_SOON",
            f"Stable high-mover: {d_recent:.1f} units/day recent, {d_forecast:.1f} units/day forecast. "
            f"Recommended reorder: {reorder_qty} units.",
        )
    if 1.0 <= d_forecast < 3:
        return (
            "MONITOR",
            f"Low but consistent demand ({d_forecast:.1f} units/day forecast). "
            f"Monitor inventory levels; reorder {reorder_qty} units if stock depletes.",
        )
    return (
        "ADEQUATE",
        f"Low forecast demand ({d_forecast:.1f} units/day). No immediate reorder action required.",
    )


def compute_reorder_qty(d_forecast: float) -> int:
    """Calculate recommended reorder quantity using lead time and safety buffer."""
    raw = d_forecast * LEAD_TIME_DAYS * (1 + SAFETY_BUFFER_PCT)
    return max(1, math.ceil(raw))


def generate_restocking_recommendations(
    limit: int = 50,
    urgency_filter: Optional[str] = None,
) -> RestockingListResponse:
    """Generate restocking recommendations for all tracked items.

    Process:
    1. Load available items from the cached M5 subset.
    2. For each item, compute recent demand (last 14-day rolling average).
    3. Run the lightweight forecasting model to get the 14-day ahead demand.
    4. Apply business rules to assign urgency and compute reorder quantity.
    5. Sort by urgency priority (CRITICAL first) then by reorder_qty descending.
    """
    df = load_forecasting_data()
    items = get_available_items()

    recommendations: List[RestockingRecommendation] = []

    for item in items:
        item_id = item["item_id"]
        store_id = item["store_id"]
        category = item["category"]

        # Recent demand: last RECENT_WINDOW_DAYS from historical data
        mask = (df["item_id"] == item_id) & (df["store_id"] == store_id)
        df_item = df[mask].sort_values("date")

        if df_item.empty:
            continue

        recent_series = df_item["sales_units"].iloc[-RECENT_WINDOW_DAYS:]
        d_recent = float(recent_series.mean()) if len(recent_series) > 0 else 0.0

        # Forecast demand
        fc_result = forecast_item(item_id, store_id, horizon=FORECAST_HORIZON)
        if fc_result is None:
            continue

        forecast_vals = [p["predicted"] for p in fc_result["forecast"]]
        d_forecast = float(sum(forecast_vals) / len(forecast_vals)) if forecast_vals else d_recent

        trend_pct = ((d_forecast - d_recent) / max(d_recent, 0.1)) * 100
        reorder_qty = compute_reorder_qty(d_forecast)

        urgency, reason = _urgency_and_reason(d_recent, d_forecast, trend_pct, reorder_qty)

        if urgency_filter and urgency != urgency_filter.upper():
            continue

        recommendations.append(
            RestockingRecommendation(
                item_id=item_id,
                store_id=store_id,
                category=category,
                avg_recent_demand=round(d_recent, 2),
                avg_forecast_demand=round(d_forecast, 2),
                demand_trend_pct=round(trend_pct, 1),
                recommended_reorder_qty=reorder_qty,
                urgency=urgency,
                reason=reason,
                forecast_horizon_days=FORECAST_HORIZON,
            )
        )

    # Sort: CRITICAL > REORDER_SOON > MONITOR > ADEQUATE, then by reorder qty desc
    urgency_rank = {"CRITICAL": 0, "REORDER_SOON": 1, "MONITOR": 2, "ADEQUATE": 3}
    recommendations.sort(key=lambda r: (urgency_rank.get(r.urgency, 9), -r.recommended_reorder_qty))

    total = len(recommendations)
    limited = recommendations[:limit]

    return RestockingListResponse(total=total, limit=limit, items=limited)
