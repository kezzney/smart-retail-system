"""API v1 Router."""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.products import router as products_router
from app.api.v1.stores import router as stores_router
from app.api.v1.forecasting import router as forecasting_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(analytics_router)
api_router.include_router(products_router)
api_router.include_router(stores_router)
api_router.include_router(forecasting_router)

__all__ = ["api_router"]
