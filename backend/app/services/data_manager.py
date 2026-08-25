"""Unified Data Manager and Pipeline Runner.

Coordinates dataset loading, preprocessing, and database ingestion across all retail datasets.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

# Ensure backend root is on sys.path when executed directly
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal, engine
from app.database.base import Base
from app.services.grocery_etl import ingest_grocery_catalog
from app.services.rossmann_etl import ingest_rossmann_analytics
from app.services.m5_etl import prepare_m5_forecasting_subset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_all_etl(
    db: Optional[Session] = None,
    data_root: Optional[str] = None,
    sample_stores: Optional[int] = None,
    top_m5_skus: int = 50,
) -> Dict[str, Any]:
    """Execute complete ETL pipelines for Grocery, Rossmann, and M5 datasets."""
    # Ensure all tables exist
    Base.metadata.create_all(bind=engine)

    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    results = {}
    try:
        logger.info("Starting Grocery Catalog ETL...")
        products_ingested = ingest_grocery_catalog(db, data_root=data_root)
        results["grocery"] = {"products_ingested": products_ingested}

        logger.info("Starting Rossmann Analytics ETL...")
        rossmann_res = ingest_rossmann_analytics(db, data_root=data_root, sample_stores=sample_stores)
        results["rossmann"] = rossmann_res

        logger.info("Starting M5 Forecasting Subset ETL...")
        m5_res = prepare_m5_forecasting_subset(data_root=data_root, top_n_skus=top_m5_skus)
        results["m5"] = m5_res

        logger.info("Data Pipeline ETL completed successfully: %s", results)
        return results

    finally:
        if owns_session:
            db.close()


if __name__ == "__main__":
    print("Running Smart Retail System ETL Pipelines...")
    res = run_all_etl()
    print("ETL Ingestion Complete:", res)
