"""Tests for ETL Data Cleaning and Transformation Functions."""

import pandas as pd
from app.services.grocery_etl import (
    clean_price_value,
    clean_rating_value,
    clean_discount_value,
    clean_text_field,
)


def test_clean_price_value():
    """Test price parsing from various raw string formats."""
    assert clean_price_value("$56.99 ") == 56.99
    assert clean_price_value("1,249.50") == 1249.50
    assert clean_price_value("$9.99") == 9.99
    assert clean_price_value(None) == 0.0
    assert clean_price_value(float("nan")) == 0.0


def test_clean_rating_value():
    """Test rating extraction from descriptive strings."""
    assert clean_rating_value("Rated 4.3 out of 5 stars based on 265 reviews.") == 4.3
    assert clean_rating_value("4.8") == 4.8
    assert clean_rating_value(None) is None


def test_clean_discount_value():
    """Test discount percentage parsing."""
    assert clean_discount_value("20% off") == 20.0
    assert clean_discount_value("$5.00 off") == 5.0
    assert clean_discount_value("No Discount") == 0.0
    assert clean_discount_value(None) == 0.0


def test_clean_text_field():
    """Test text whitespace normalization."""
    raw = "  Product   Title\nWith  Linebreaks  "
    cleaned = clean_text_field(raw)
    assert cleaned == "Product Title With Linebreaks"
    assert clean_text_field(None, default="Default") == "Default"
