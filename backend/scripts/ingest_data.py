import asyncio
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add backend directory and project root to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import init_db
from app.services.ingest_service import ensure_data_ingested

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ingest")

async def main():
    logger.info("Initializing Neon PostgreSQL database schema...")
    init_db()

    logger.info("Running data ingestion pipeline...")
    status = await ensure_data_ingested(force=True)
    logger.info(f"Ingestion complete! Final database totals: {status['actual_count']} actuals, {status['forecast_count']} forecasts.")

if __name__ == "__main__":
    asyncio.run(main())
