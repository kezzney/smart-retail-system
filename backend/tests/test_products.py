"""Tests for Products Catalog API Endpoints."""

from fastapi import status


def test_list_products_endpoint(client):
    """Test /api/v1/products returns paginated products."""
    response = client.get("/api/v1/products?limit=10&skip=0")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "items" in data
    assert data["limit"] == 10
    assert isinstance(data["items"], list)

    if data["total"] > 0:
        item = data["items"][0]
        assert "id" in item
        assert "title" in item
        assert "sub_category" in item
        assert "price" in item
        assert isinstance(item["price"], (int, float))


def test_filter_products_by_category(client):
    """Test filtering products by category."""
    response = client.get("/api/v1/products?category=Bakery")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data["items"], list)
    for p in data["items"]:
        assert "bakery" in p["sub_category"].lower()


def test_get_single_product_not_found(client):
    """Test 404 response for non-existent product."""
    response = client.get("/api/v1/products/9999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
