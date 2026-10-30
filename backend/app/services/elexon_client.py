import httpx
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.config import ELEXON_BASE_URL

logger = logging.getLogger(__name__)

class ElexonConnectionError(Exception):
    """Raised when Elexon BMRS API cannot be reached due to DNS or network errors."""
    pass

class ElexonClient:
    def __init__(self, base_url: str = ELEXON_BASE_URL, timeout: float = 30.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    async def _get_with_retry(self, url: str, params: dict, headers: dict) -> dict:
        """
        Executes HTTP GET with retries and exponential backoff to handle transient DNS or connection drops.
        """
        last_error = None
        transport = httpx.AsyncHTTPTransport(retries=self.max_retries)
        
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, transport=transport) as client:
                    resp = await client.get(url, params=params, headers=headers)
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.ConnectError, httpx.NetworkError) as e:
                last_error = e
                logger.warning(f"Connection attempt {attempt}/{self.max_retries} to {url} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(1.5 * attempt)
            except Exception as e:
                logger.error(f"Unexpected HTTP error for {url}: {e}")
                raise e

        # If all retries exhausted
        err_msg = (
            f"Unable to reach Elexon BMRS API at {self.base_url}. "
            f"DNS or network resolution failed: {str(last_error)}. "
            "Please check internet connectivity and DNS configuration."
        )
        logger.error(err_msg)
        raise ElexonConnectionError(err_msg)

    async def fetch_fuelhh_stream(
        self,
        publish_from: str,
        publish_to: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch FUELHH actual generation stream and filter for WIND.
        """
        url = f"{self.base_url}/datasets/FUELHH/stream"
        params = {
            "publishDateTimeFrom": publish_from,
            "publishDateTimeTo": publish_to
        }
        headers = {"User-Agent": "GridBricks-WindPulse/1.0 (Energy Procurement)"}

        raw_data = await self._get_with_retry(url, params, headers)

        wind_records = []
        for item in raw_data:
            if item.get("fuelType") == "WIND":
                gen = item.get("generation")
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
        """
        url = f"{self.base_url}/datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": publish_from,
            "publishDateTimeTo": publish_to
        }
        headers = {"User-Agent": "GridBricks-WindPulse/1.0 (Energy Procurement)"}

        raw_data = await self._get_with_retry(url, params, headers)

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

            if dataset == "FUELHH":
                records = await self.fetch_fuelhh_stream(from_str, to_str)
            elif dataset == "WINDFOR":
                records = await self.fetch_windfor_stream(from_str, to_str)
            else:
                raise ValueError(f"Unknown dataset: {dataset}")
            all_records.extend(records)

            current_start = current_end

        return all_records
