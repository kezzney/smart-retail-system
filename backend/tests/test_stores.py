"""Tests for Stores API Endpoints."""

from fastapi import status


def test_list_stores_endpoint(client):
    """Test /api/v1/stores returns store list."""
    response = client.get("/api/v1/stores?limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)

    if data["total"] > 0:
        store = data["items"][0]
        assert "id" in store
        assert "store_type" in store
        assert "total_sales" in store
        assert "total_customers" in store
        assert "avg_daily_sales" in store


def test_get_single_store_not_found(client):
    """Test 404 response for non-existent store."""
    response = client.get("/api/v1/stores/9999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
