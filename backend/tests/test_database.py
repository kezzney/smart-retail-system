"""Tests for Database Connection and Health Check."""

from sqlalchemy import text
from app.database.connection import check_db_health, engine, SessionLocal


def test_database_health_check():
    """Verify that database health check returns True."""
    assert check_db_health() is True


def test_database_session_execution():
    """Verify that database sessions can execute basic queries."""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1 as val")).scalar()
        assert result == 1
    finally:
        db.close()


def test_database_engine_connection():
    """Verify that the engine connects properly."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 42 as answer")).scalar()
        assert result == 42
