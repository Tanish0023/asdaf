import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from backend.app.config import ELEXON_BASE_URL

logger = logging.getLogger(__name__)

class ElexonClient:
    def __init__(self, base_url: str = ELEXON_BASE_URL, timeout: float = 45.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def fetch_fuelhh_stream(
        self,
        publish_from: str,
        publish_to: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch FUELHH actual generation stream and filter for WIND.
        Returns list of wind records with:
        startTime, publishTime, settlementDate, settlementPeriod, generation
        """
        url = f"{self.base_url}/datasets/FUELHH/stream"
        params = {
            "publishDateTimeFrom": publish_from,
            "publishDateTimeTo": publish_to
        }
        headers = {"User-Agent": "GridBricks-WindPulse/1.0 (Energy Procurement)"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            raw_data = resp.json()

        wind_records = []
        for item in raw_data:
            if item.get("fuelType") == "WIND":
                gen = item.get("generation")
                # Handle possible null or missing generation
                gen_val = float(gen) if gen is not None else 0.0
                wind_records.append({
                    "startTime": item.get("startTime"),
                    "publishTime": item.get("publishTime"),
                    "settlementDate": item.get("settlementDate"),
                    "settlementPeriod": item.get("settlementPeriod"),
                    "generation": gen_val
                })

        logger.info(f"Fetched {len(wind_records)} WIND records from FUELHH ({publish_from} to {publish_to})")
        return wind_records

    async def fetch_windfor_stream(
        self,
        publish_from: str,
        publish_to: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch WINDFOR wind forecasts stream.
        Returns list of records with:
        publishTime, startTime, generation
        """
        url = f"{self.base_url}/datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": publish_from,
            "publishDateTimeTo": publish_to
        }
        headers = {"User-Agent": "GridBricks-WindPulse/1.0 (Energy Procurement)"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            raw_data = resp.json()

        forecast_records = []
        for item in raw_data:
            gen = item.get("generation")
            gen_val = float(gen) if gen is not None else 0.0
            start_time = item.get("startTime")
            pub_time = item.get("publishTime")
            if start_time and pub_time:
                forecast_records.append({
                    "publishTime": pub_time,
                    "startTime": start_time,
                    "generation": gen_val
                })

        logger.info(f"Fetched {len(forecast_records)} WINDFOR forecast records ({publish_from} to {publish_to})")
        return forecast_records

    async def fetch_dataset_in_chunks(
        self,
        dataset: str,
        start_date: datetime,
        end_date: datetime,
        chunk_days: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetches data in chunk_days windows to avoid large responses and timeouts.
        """
        current_start = start_date
        all_records = []

        while current_start < end_date:
            current_end = min(current_start + timedelta(days=chunk_days), end_date)
            from_str = current_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            to_str = current_end.strftime("%Y-%m-%dT%H:%M:%SZ")

            try:
                if dataset == "FUELHH":
                    records = await self.fetch_fuelhh_stream(from_str, to_str)
                elif dataset == "WINDFOR":
                    records = await self.fetch_windfor_stream(from_str, to_str)
                else:
                    raise ValueError(f"Unknown dataset: {dataset}")
                all_records.extend(records)
            except Exception as e:
                logger.error(f"Error fetching {dataset} for {from_str} to {to_str}: {e}")
                # continue to next chunk or re-raise if fatal
                raise e

            current_start = current_end

        return all_records
