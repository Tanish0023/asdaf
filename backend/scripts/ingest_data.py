import asyncio
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database import init_db
from app.services.elexon_client import ElexonClient
from app.services.data_store import DataStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ingest")

async def main():
    logger.info("Initializing Neon PostgreSQL database...")
    init_db()

    client = ElexonClient()
    store = DataStore()

    # Time range: Dec 31, 2025 to Feb 2, 2026
    start_dt = datetime(2025, 12, 31, 0, 0, 0)
    end_dt = datetime(2026, 2, 2, 0, 0, 0)

    logger.info(f"Ingesting FUELHH actuals from {start_dt} to {end_dt}...")
    try:
        fuel_records = await client.fetch_dataset_in_chunks("FUELHH", start_dt, end_dt, chunk_days=7)
        count_act = store.upsert_actuals(fuel_records)
        store.log_sync("FUELHH", count_act, "SUCCESS", f"Ingested {count_act} actual wind records")
        logger.info(f"Successfully ingested {count_act} actual wind records.")
    except Exception as e:
        logger.error(f"FUELHH ingestion failed: {e}")
        store.log_sync("FUELHH", 0, "FAILED", str(e))

    logger.info(f"Ingesting WINDFOR forecasts from {start_dt} to {end_dt}...")
    try:
        wind_records = await client.fetch_dataset_in_chunks("WINDFOR", start_dt, end_dt, chunk_days=5)
        count_for = store.upsert_forecasts(wind_records)
        store.log_sync("WINDFOR", count_for, "SUCCESS", f"Ingested {count_for} forecast records")
        logger.info(f"Successfully ingested {count_for} forecast records.")
    except Exception as e:
        logger.error(f"WINDFOR ingestion failed: {e}")
        store.log_sync("WINDFOR", 0, "FAILED", str(e))

    status = store.get_sync_status()
    logger.info(f"Ingestion complete! Final database totals: {status['actual_count']} actuals, {status['forecast_count']} forecasts.")

if __name__ == "__main__":
    asyncio.run(main())
