import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from backend.app.database import get_db_connection

logger = logging.getLogger(__name__)

class DataStore:
    def upsert_actuals(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO actual_wind 
                (startTime, publishTime, settlementDate, settlementPeriod, generation)
                VALUES (:startTime, :publishTime, :settlementDate, :settlementPeriod, :generation)
            """, records)
            conn.commit()
            return len(records)

    def upsert_forecasts(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO forecast_wind 
                (publishTime, startTime, generation)
                VALUES (:publishTime, :startTime, :generation)
            """, records)
            conn.commit()
            return len(records)

    def log_sync(self, dataset: str, count: int, status: str, details: str = ""):
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sync_log (dataset, synced_at, records_count, status, details)
                VALUES (?, ?, ?, ?, ?)
            """, (dataset, now, count, status, details))
            conn.commit()

    def get_sync_status(self) -> Dict[str, Any]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(synced_at) as latest_sync FROM sync_log WHERE status = 'SUCCESS'")
            row = cursor.fetchone()
            latest_sync = row["latest_sync"] if row and row["latest_sync"] else None

            cursor.execute("SELECT COUNT(*) as count FROM actual_wind")
            actual_count = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM forecast_wind")
            forecast_count = cursor.fetchone()["count"]

            return {
                "latest_sync": latest_sync,
                "actual_count": actual_count,
                "forecast_count": forecast_count
            }

    def get_available_dates(self) -> Dict[str, Any]:
        """
        Derives available delivery dates and decision dates.
        Delivery dates in January 2026: 2026-01-01 through 2026-01-31.
        Decision date is delivery_date - 1 day.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT SUBSTR(startTime, 1, 10) as date_str 
                FROM actual_wind 
                WHERE startTime >= '2026-01-01T00:00:00Z' AND startTime <= '2026-01-31T23:59:59Z'
                ORDER BY date_str ASC
            """)
            dates = [row["date_str"] for row in cursor.fetchall()]

        # If DB not yet fully populated, default to standard Jan 2026 dates
        if not dates:
            start = datetime(2026, 1, 1)
            dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(31)]

        delivery_dates = sorted(dates)
        decision_dates = []
        for d_str in delivery_dates:
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            dec_dt = dt - timedelta(days=1)
            decision_dates.append(dec_dt.strftime("%Y-%m-%d"))

        return {
            "delivery_dates": delivery_dates,
            "decision_dates": sorted(list(set(decision_dates))),
            "default_delivery_date": "2026-01-15" if "2026-01-15" in delivery_dates else delivery_dates[0],
            "default_decision_date": "2026-01-14"
        }

    def get_hourly_actuals_for_date(self, delivery_date: str) -> Dict[str, Dict[str, Any]]:
        """
        Fetches half-hourly actuals for delivery_date and aggregates into 24 hourly averages.
        Returns dict keyed by hour string ('YYYY-MM-DDTHH:00:00Z').
        """
        # Range covers 00:00:00Z through 23:59:59Z
        start_bound = f"{delivery_date}T00:00:00Z"
        end_bound = f"{delivery_date}T23:59:59Z"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT startTime, settlementPeriod, generation
                FROM actual_wind
                WHERE startTime >= ? AND startTime <= ?
                ORDER BY startTime ASC
            """, (start_bound, end_bound))
            rows = cursor.fetchall()

        hourly_buckets = defaultdict(lambda: {"gens": [], "periods": []})
        for row in rows:
            st = row["startTime"]
            # e.g. 2026-01-15T14:30:00Z -> 2026-01-15T14:00:00Z
            hour_key = st[:13] + ":00:00Z"
            hourly_buckets[hour_key]["gens"].append(row["generation"])
            if row["settlementPeriod"] is not None:
                hourly_buckets[hour_key]["periods"].append(row["settlementPeriod"])

        hourly_actuals = {}
        for h in range(24):
            hour_str = f"{delivery_date}T{h:02d}:00:00Z"
            bucket = hourly_buckets.get(hour_str)
            if bucket and bucket["gens"]:
                avg_gen = sum(bucket["gens"]) / len(bucket["gens"])
                hourly_actuals[hour_str] = {
                    "generation": round(avg_gen, 2),
                    "settlementPeriods": sorted(bucket["periods"])
                }
            else:
                hourly_actuals[hour_str] = {
                    "generation": None,
                    "settlementPeriods": [h * 2 + 1, h * 2 + 2]
                }

        return hourly_actuals

    def get_day_ahead_forecasts(
        self,
        delivery_date: str,
        cutoff_time: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Day-Ahead Decision Alignment:
        For delivery date D, decision is made on D-1.
        Cutoff datetime C is: (delivery_date - 1 day) + cutoff_time.
        For each delivery hour h on day D:
            Find forecasts for startTime == h with publishTime <= C.
            Pick the one with MAX(publishTime).
        Strictly excludes any forecast with publishTime > C.
        """
        deliv_dt = datetime.strptime(delivery_date, "%Y-%m-%d")
        decision_dt = deliv_dt - timedelta(days=1)
        dec_date_str = decision_dt.strftime("%Y-%m-%d")

        # Normalize cutoff_time e.g. "11:00" -> "11:00:00Z"
        cutoff_clean = cutoff_time.strip()
        if len(cutoff_clean.split(":")) == 2:
            cutoff_clean = f"{cutoff_clean}:00Z"
        elif not cutoff_clean.endswith("Z"):
            cutoff_clean = f"{cutoff_clean}Z"

        cutoff_datetime = f"{dec_date_str}T{cutoff_clean}"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            hourly_forecasts = {}
            for h in range(24):
                hour_target = f"{delivery_date}T{h:02d}:00:00Z"
                cursor.execute("""
                    SELECT publishTime, generation
                    FROM forecast_wind
                    WHERE startTime = ? AND publishTime <= ?
                    ORDER BY publishTime DESC
                    LIMIT 1
                """, (hour_target, cutoff_datetime))
                row = cursor.fetchone()
                if row:
                    hourly_forecasts[hour_target] = {
                        "generation": round(row["generation"], 2),
                        "publishTime": row["publishTime"]
                    }
                else:
                    hourly_forecasts[hour_target] = {
                        "generation": None,
                        "publishTime": None
                    }

        return hourly_forecasts, cutoff_datetime, dec_date_str
