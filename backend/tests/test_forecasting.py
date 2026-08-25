"""Tests for Demand Forecasting and Restocking APIs."""

import pytest
import numpy as np
import pandas as pd
from fastapi import status

from app.services.restocking_service import compute_reorder_qty, _urgency_and_reason, LEAD_TIME_DAYS, SAFETY_BUFFER_PCT
from app.services.forecasting_service import _build_features, _rolling_mean_forecast, FORECAST_HORIZON


# ─── Synthetic fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def synthetic_item_df():
    """Small synthetic time-series for unit-testing without the full dataset."""
    dates = pd.date_range("2015-01-01", periods=90, freq="D")
    np.random.seed(42)
    sales = np.maximum(0, np.random.poisson(lam=5, size=90).astype(float))
    return pd.DataFrame({
        "date": dates,
        "sales_units": sales,
        "event_name_1": [None] * 90,
        "sell_price": [2.99] * 90,
    })


# ─── Feature Engineering Tests ────────────────────────────────────────────────

def test_build_features_adds_lag_columns(synthetic_item_df):
    """_build_features should add lag_7, lag_14, rolling_7_mean, rolling_14_mean."""
    result = _build_features(synthetic_item_df)
    for col in ["lag_7", "lag_14", "rolling_7_mean", "rolling_14_mean", "has_event", "day_of_week", "month"]:
        assert col in result.columns, f"Missing column: {col}"


def test_build_features_no_nans(synthetic_item_df):
    """All feature columns should be filled — no NaN values in lag columns."""
    result = _build_features(synthetic_item_df)
    assert result["lag_7"].isna().sum() == 0
    assert result["lag_14"].isna().sum() == 0


def test_build_features_length_preserved(synthetic_item_df):
    """Feature engineering should not change the number of rows."""
    result = _build_features(synthetic_item_df)
    assert len(result) == len(synthetic_item_df)


# ─── Rolling Mean Forecast Tests ──────────────────────────────────────────────

def test_rolling_mean_returns_correct_horizon():
    """Rolling mean should return exactly `horizon` predictions."""
    series = pd.Series([3.0, 4.0, 5.0, 2.0, 3.0, 4.0, 2.0, 3.0])
    preds, _ = _rolling_mean_forecast(series, horizon=7)
    assert len(preds) == 7


def test_rolling_mean_no_negative_values():
    """Rolling mean predictions should never be negative."""
    series = pd.Series([0.0] * 10)
    preds, _ = _rolling_mean_forecast(series, horizon=10)
    assert all(p >= 0 for p in preds)


def test_rolling_mean_constant_series():
    """For a constant series, rolling mean should equal that constant."""
    series = pd.Series([4.0] * 20)
    preds, _ = _rolling_mean_forecast(series, horizon=7, window=14)
    assert all(abs(p - 4.0) < 1e-6 for p in preds)


# ─── Restocking Business Rules Tests ─────────────────────────────────────────

def test_compute_reorder_qty_formula():
    """Reorder qty should be ceil(forecast * lead_time * (1 + safety_buffer))."""
    d_forecast = 10.0
    expected = int(np.ceil(d_forecast * LEAD_TIME_DAYS * (1 + SAFETY_BUFFER_PCT)))
    assert compute_reorder_qty(d_forecast) == expected


def test_compute_reorder_qty_minimum_one():
    """Even for zero forecast, reorder qty should be at least 1."""
    assert compute_reorder_qty(0.0) == 1


def test_urgency_critical_high_velocity():
    """High-velocity SKU (>=10 units/day) should be CRITICAL."""
    urgency, reason = _urgency_and_reason(d_recent=15.0, d_forecast=16.0, trend_pct=5.0, reorder_qty=140)
    assert urgency == "CRITICAL"
    assert "High-velocity" in reason


def test_urgency_critical_spiking():
    """Demand spike (>=5 units/day, >=20% increase) should be CRITICAL."""
    urgency, reason = _urgency_and_reason(d_recent=5.0, d_forecast=7.0, trend_pct=40.0, reorder_qty=62)
    assert urgency == "CRITICAL"
    assert "spike" in reason.lower() or "spiking" in reason.lower()


def test_urgency_reorder_soon_rising():
    """Moderate rising demand should trigger REORDER_SOON."""
    urgency, _ = _urgency_and_reason(d_recent=2.0, d_forecast=4.0, trend_pct=100.0, reorder_qty=35)
    assert urgency == "REORDER_SOON"


def test_urgency_monitor_low_steady():
    """Low but non-zero demand should be MONITOR."""
    urgency, _ = _urgency_and_reason(d_recent=1.5, d_forecast=2.0, trend_pct=10.0, reorder_qty=18)
    assert urgency == "MONITOR"


def test_urgency_adequate_minimal():
    """Very low demand should be ADEQUATE."""
    urgency, _ = _urgency_and_reason(d_recent=0.2, d_forecast=0.3, trend_pct=5.0, reorder_qty=3)
    assert urgency == "ADEQUATE"


# ─── API Endpoint Tests ───────────────────────────────────────────────────────

def test_restocking_recommendations_returns_200(client):
    """GET /api/v1/restocking/recommendations should return 200 and valid schema."""
    response = client.get("/api/v1/restocking/recommendations?limit=5")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "total" in data
    assert "limit" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_restocking_recommendations_schema(client):
    """Each recommendation should have required fields with correct types."""
    response = client.get("/api/v1/restocking/recommendations?limit=3")
    assert response.status_code == status.HTTP_200_OK
    items = response.json()["items"]

    if items:
        rec = items[0]
        assert "item_id" in rec
        assert "store_id" in rec
        assert "category" in rec
        assert "urgency" in rec
        assert rec["urgency"] in {"CRITICAL", "REORDER_SOON", "MONITOR", "ADEQUATE"}
        assert "recommended_reorder_qty" in rec
        assert rec["recommended_reorder_qty"] >= 1
        assert "reason" in rec
        assert "avg_recent_demand" in rec
        assert "avg_forecast_demand" in rec


def test_restocking_recommendations_urgency_filter(client):
    """Urgency filter should return only items matching that urgency level."""
    for level in ["CRITICAL", "REORDER_SOON", "MONITOR", "ADEQUATE"]:
        response = client.get(f"/api/v1/restocking/recommendations?urgency={level}&limit=20")
        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        for rec in items:
            assert rec["urgency"] == level


def test_forecast_list_endpoint(client):
    """GET /api/v1/forecast should list available forecastable items."""
    response = client.get("/api/v1/forecast?limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] > 0


def test_forecast_item_not_found(client):
    """GET /api/v1/forecast/{item_id} with invalid ID should return 404."""
    response = client.get("/api/v1/forecast/INVALID_ITEM_XYZ?store_id=CA_1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data


def test_forecast_item_valid(client):
    """GET /api/v1/forecast/{item_id} with a valid item should return full schema."""
    # Get a valid item from the list endpoint first
    list_resp = client.get("/api/v1/forecast?limit=1")
    assert list_resp.status_code == status.HTTP_200_OK
    items = list_resp.json()["items"]
    if not items:
        pytest.skip("No forecasting items available in the dataset")

    item_id = items[0]["item_id"]
    store_id = items[0]["store_id"]

    response = client.get(f"/api/v1/forecast/{item_id}?store_id={store_id}&horizon=14")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["item_id"] == item_id
    assert data["store_id"] == store_id
    assert "model_name" in data
    assert "forecast_horizon_days" in data
    assert "history" in data and isinstance(data["history"], list)
    assert "forecast" in data and isinstance(data["forecast"], list)
    assert len(data["forecast"]) == 14

    # Each forecast point should have date and predicted
    for pt in data["forecast"]:
        assert "date" in pt
        assert "predicted" in pt
        assert pt["predicted"] >= 0
