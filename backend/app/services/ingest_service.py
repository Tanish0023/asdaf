import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Tuple

from app.services.elexon_client import ElexonClient, ElexonConnectionError
from app.services.data_store import DataStore

logger = logging.getLogger("gridbricks.ingest")

async def fetch_from_elexon(
    client: ElexonClient,
    store: DataStore,
    start_dt: datetime = datetime(2025, 12, 31, 0, 0, 0),
    end_dt: datetime = datetime(2026, 2, 2, 0, 0, 0)
) -> Tuple[int, int]:
    """
    Fetches FUELHH actuals and WINDFOR forecasts from Elexon BMRS in parallel.
    """
    logger.info("Fetching January 2026 wind actuals and forecasts from Elexon BMRS...")
    fuel_task = client.fetch_dataset_in_chunks("FUELHH", start_dt, end_dt, chunk_days=7)
    wind_task = client.fetch_dataset_in_chunks("WINDFOR", start_dt, end_dt, chunk_days=5)

    fuel_records, wind_records = await asyncio.gather(fuel_task, wind_task)

    count_act = store.upsert_actuals(fuel_records, batch_size=1000)
    count_for = store.upsert_forecasts(wind_records, batch_size=1500)
    logger.info(f"Ingested from Elexon BMRS: {count_act} actuals, {count_for} forecasts.")
    return count_act, count_for

async def ensure_data_ingested(force: bool = False) -> Dict[str, Any]:
    """
    Checks if database contains data. If records are missing (or force=True),
    automatically fetches live from Elexon BMRS (FUELHH actuals & WINDFOR forecasts).
    """
    store = DataStore()
    status = store.get_sync_status()

    if not force and status.get("actual_count", 0) > 0 and status.get("forecast_count", 0) > 0:
        return status

    client = ElexonClient()
    try:
        await fetch_from_elexon(client, store)
    except (ElexonConnectionError, Exception) as e:
        logger.error(f"Elexon BMRS fetch failed: {e}")
        raise e

    store.invalidate_cache()
    return store.get_sync_status()
