"""Tests for Business Analytics API Endpoints."""

from fastapi import status


def test_analytics_overview_endpoint(client):
    """Test /api/v1/analytics/overview returns valid KPIs and schema."""
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "total_sales" in data
    assert "total_customers" in data
    assert "number_of_stores" in data
    assert "number_of_products" in data
    assert "average_daily_sales" in data
    assert "promo_sales_lift_pct" in data
    assert "top_performing_store" in data
    assert isinstance(data["top_categories"], list)
    assert data["total_sales"] >= 0.0
    assert data["number_of_stores"] >= 0


def test_analytics_sales_trend_endpoint(client):
    """Test /api/v1/analytics/sales returns time series data."""
    response = client.get("/api/v1/analytics/sales?limit=30")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "start_date" in data
    assert "end_date" in data
    assert "total_points" in data
    assert "data" in data
    assert isinstance(data["data"], list)

    if data["total_points"] > 0:
        first_point = data["data"][0]
        assert "date" in first_point
        assert "sales" in first_point
        assert "customers" in first_point
        assert "open_stores" in first_point
        assert "avg_sales_per_store" in first_point
