"""Main FastAPI Application Entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import settings
from app.database.connection import engine, SessionLocal
from app.database.base import Base
# Import models to ensure they are registered with Base metadata
import app.models  # noqa: F401

import logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory for Smart Retail Intelligence System."""
    # Ensure database schema tables exist
    Base.metadata.create_all(bind=engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # noqa: ARG001
        """Application lifespan — seeds the database at startup if tables are empty."""
        from app.services.seed_service import seed_database_if_empty
        db = SessionLocal()
        try:
            result = seed_database_if_empty(db)
            seeded = {k: v for k, v in result.items() if v > 0}
            if seeded:
                logger.info("Startup seed complete: %s", seeded)
            else:
                logger.info("Startup seed: all tables already populated, no seeding needed")
        except Exception as exc:
            logger.error("Startup seed error (non-fatal): %s", exc)
        finally:
            db.close()
        yield  # application runs here

    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    application.include_router(api_router, prefix=settings.API_V1_STR)

    @application.get("/", tags=["Root"])
    def root():
        """Root endpoint returning basic service metadata."""
        return {
            "message": "Welcome to Smart Retail Intelligence System API",
            "version": settings.VERSION,
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health",
        }

    return application


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
