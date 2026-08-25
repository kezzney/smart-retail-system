"""Tests for Health and System Status API Endpoints."""

from fastapi import status


def test_root_endpoint(client):
    """Test root endpoint returns 200 and expected metadata."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["health"] == "/api/v1/health"


def test_health_endpoint(client):
    """Test /api/v1/health endpoint returns 200 and valid schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert data["database"] == "connected"
    assert "timestamp" in data


def test_status_endpoint(client):
    """Test /api/v1/status endpoint returns 200 and system diagnostics."""
    response = client.get("/api/v1/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database_connected"] is True
    assert data["database_type"] in ["sqlite", "postgresql"]
    assert "service_name" in data
    assert "timestamp" in data
