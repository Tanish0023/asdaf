from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
from app.schemas import SyncResponse
from app.services.elexon_client import ElexonClient, ElexonConnectionError
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/v1", tags=["sync"])
logger = logging.getLogger(__name__)

async def run_sync_task():
    client = ElexonClient()
    store = DataStore()
    
    start_dt = datetime(2025, 12, 31, 0, 0, 0)
    end_dt = datetime(2026, 2, 1, 23, 59, 59)

    logger.info("Starting background synchronization with Elexon BMRS API...")
    try:
        fuel_records = await client.fetch_dataset_in_chunks("FUELHH", start_dt, end_dt, chunk_days=7)
        actuals_count = store.upsert_actuals(fuel_records)
        store.log_sync("FUELHH", actuals_count, "SUCCESS", f"Synced {actuals_count} wind records")
    except ElexonConnectionError as e:
        logger.warning(f"Elexon connection error during FUELHH sync: {e}")
        store.log_sync("FUELHH", 0, "FAILED", str(e))
        raise e
    except Exception as e:
        logger.error(f"Failed to sync FUELHH: {e}")
        store.log_sync("FUELHH", 0, "FAILED", str(e))
        raise e

    try:
        wind_records = await client.fetch_dataset_in_chunks("WINDFOR", start_dt, end_dt, chunk_days=5)
        forecasts_count = store.upsert_forecasts(wind_records)
        store.log_sync("WINDFOR", forecasts_count, "SUCCESS", f"Synced {forecasts_count} forecast records")
    except ElexonConnectionError as e:
        logger.warning(f"Elexon connection error during WINDFOR sync: {e}")
        store.log_sync("WINDFOR", 0, "FAILED", str(e))
        raise e
    except Exception as e:
        logger.error(f"Failed to sync WINDFOR: {e}")
        store.log_sync("WINDFOR", 0, "FAILED", str(e))
        raise e

    logger.info("Synchronization completed successfully.")
    return actuals_count, forecasts_count

@router.post("/sync", response_model=SyncResponse)
async def sync_elexon_data():
    try:
        actuals_synced, forecasts_synced = await run_sync_task()
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return SyncResponse(
            status="SUCCESS",
            actuals_synced=actuals_synced,
            forecasts_synced=forecasts_synced,
            message="Successfully synchronized January 2026 datasets from Elexon BMRS into Neon PostgreSQL.",
            synced_at=now_str
        )
    except ElexonConnectionError as e:
        # Graceful HTTP 503 informing user that cached data remains available
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Elexon BMRS API is currently unreachable from this environment (DNS/Network resolution failure for data.elexon.co.uk). "
                "The platform continues to operate without interruption using the pre-cached January 2026 dataset in Neon PostgreSQL."
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synchronization failed: {str(e)}"
        )
