import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.ingest_service import ensure_data_ingested

@pytest.mark.asyncio
async def test_ensure_data_ingested_skips_when_populated():
    with patch("app.services.ingest_service.DataStore") as mock_ds_cls:
        mock_store = MagicMock()
        mock_store.get_data_status.return_value = {
            "actual_count": 1585,
            "forecast_count": 19272,
            "min_actual_date": "2025-12-30",
            "max_actual_date": "2026-02-01",
            "is_complete": True
        }
        mock_ds_cls.return_value = mock_store

        with patch("app.services.ingest_service.fetch_from_elexon", new_callable=AsyncMock) as mock_fetch:
            status = await ensure_data_ingested(force=False)
            assert status["actual_count"] == 1585
            assert not mock_fetch.called

@pytest.mark.asyncio
async def test_ensure_data_ingested_triggers_when_empty():
    with patch("app.services.ingest_service.DataStore") as mock_ds_cls:
        mock_store = MagicMock()
        # First call: incomplete DB, Second call: complete
        mock_store.get_data_status.side_effect = [
            {"actual_count": 0, "forecast_count": 0, "is_complete": False},
            {"actual_count": 1585, "forecast_count": 19272, "is_complete": True}
        ]
        mock_ds_cls.return_value = mock_store

        with patch("app.services.ingest_service.fetch_from_elexon", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (1585, 19272)
            status = await ensure_data_ingested(force=False)
            assert mock_fetch.called
            assert mock_store.invalidate_cache.called
            assert status["actual_count"] == 1585

@pytest.mark.asyncio
async def test_ensure_data_ingested_graceful_on_elexon_failure():
    with patch("app.services.ingest_service.DataStore") as mock_ds_cls:
        mock_store = MagicMock()
        mock_store.get_data_status.return_value = {
            "actual_count": 0,
            "forecast_count": 0,
            "is_complete": False
        }
        mock_ds_cls.return_value = mock_store

        with patch("app.services.ingest_service.fetch_from_elexon", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Elexon DNS resolution failed")
            # When Elexon fails, logs warning and returns current status instead of raising
            status = await ensure_data_ingested(force=False)
            assert mock_fetch.called
            assert status["actual_count"] == 0
