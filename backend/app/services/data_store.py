from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import logging

from sqlalchemy import select, func, desc, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.app.database import get_db
from backend.app.models import ActualWind, ForecastWind, SyncLog

logger = logging.getLogger(__name__)

class DataStore:
    def upsert_actuals(self, records: List[Dict[str, Any]], batch_size: int = 500) -> int:
        """
        Idempotent PostgreSQL upsert for actual wind generation records (FUELHH).
        """
        if not records:
            return 0

        # Transform keys to match ActualWind column names
        mapped_records = []
        for r in records:
            mapped_records.append({
                "start_time": r.get("startTime") or r.get("start_time"),
                "publish_time": r.get("publishTime") or r.get("publish_time"),
                "settlement_date": r.get("settlementDate") or r.get("settlement_date"),
                "settlement_period": r.get("settlementPeriod") or r.get("settlement_period"),
                "generation": float(r.get("generation", 0.0)),
            })

        total_upserted = 0
        with get_db() as session:
            for i in range(0, len(mapped_records), batch_size):
                batch = mapped_records[i:i + batch_size]
                stmt = pg_insert(ActualWind).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[ActualWind.start_time],
                    set_={
                        "publish_time": stmt.excluded.publish_time,
                        "settlement_date": stmt.excluded.settlement_date,
                        "settlement_period": stmt.excluded.settlement_period,
                        "generation": stmt.excluded.generation,
                    }
                )
                session.execute(stmt)
                total_upserted += len(batch)
            session.commit()

        return total_upserted

    def upsert_forecasts(self, records: List[Dict[str, Any]], batch_size: int = 500) -> int:
        """
        Idempotent PostgreSQL upsert for wind forecast records (WINDFOR).
        """
        if not records:
            return 0

        mapped_records = []
        for r in records:
            mapped_records.append({
                "publish_time": r.get("publishTime") or r.get("publish_time"),
                "start_time": r.get("startTime") or r.get("start_time"),
                "generation": float(r.get("generation", 0.0)),
            })

        total_upserted = 0
        with get_db() as session:
            for i in range(0, len(mapped_records), batch_size):
                batch = mapped_records[i:i + batch_size]
                stmt = pg_insert(ForecastWind).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[ForecastWind.publish_time, ForecastWind.start_time],
                    set_={"generation": stmt.excluded.generation}
                )
                session.execute(stmt)
                total_upserted += len(batch)
            session.commit()

        return total_upserted

    def log_sync(self, dataset: str, count: int, status: str, details: str = ""):
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        with get_db() as session:
            log_entry = SyncLog(
                dataset=dataset,
                synced_at=now_str,
                records_count=count,
                status=status,
                details=details
            )
            session.add(log_entry)
            session.commit()

    def get_sync_status(self) -> Dict[str, Any]:
        with get_db() as session:
            latest_sync = session.query(func.max(SyncLog.synced_at)).filter(SyncLog.status == "SUCCESS").scalar()
            actual_count = session.query(func.count(ActualWind.start_time)).scalar() or 0
            forecast_count = session.query(func.count(ForecastWind.publish_time)).scalar() or 0

            return {
                "latest_sync": latest_sync,
                "actual_count": actual_count,
                "forecast_count": forecast_count
            }

    def get_available_dates(self) -> Dict[str, Any]:
        with get_db() as session:
            rows = session.query(
                func.substr(ActualWind.start_time, 1, 10).label("date_str")
            ).filter(
                ActualWind.start_time >= "2026-01-01T00:00:00Z",
                ActualWind.start_time <= "2026-01-31T23:59:59Z"
            ).distinct().order_by("date_str").all()

            dates = [r.date_str for r in rows]

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
        """
        start_bound = f"{delivery_date}T00:00:00Z"
        end_bound = f"{delivery_date}T23:59:59Z"

        with get_db() as session:
            rows = session.query(
                ActualWind.start_time,
                ActualWind.settlement_period,
                ActualWind.generation
            ).filter(
                ActualWind.start_time >= start_bound,
                ActualWind.start_time <= end_bound
            ).order_by(ActualWind.start_time.asc()).all()

        hourly_buckets = defaultdict(lambda: {"gens": [], "periods": []})
        for row in rows:
            st = row.start_time
            hour_key = st[:13] + ":00:00Z"
            hourly_buckets[hour_key]["gens"].append(row.generation)
            if row.settlement_period is not None:
                hourly_buckets[hour_key]["periods"].append(row.settlement_period)

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
    ) -> Tuple[Dict[str, Dict[str, Any]], str, str]:
        """
        Day-Ahead Decision Alignment in PostgreSQL:
        For delivery date D, decision cutoff datetime C is (D-1) at cutoff_time.
        For each delivery hour h on day D, selects latest published forecast at or before C.
        Strictly excludes any forecast published after C.
        """
        deliv_dt = datetime.strptime(delivery_date, "%Y-%m-%d")
        decision_dt = deliv_dt - timedelta(days=1)
        dec_date_str = decision_dt.strftime("%Y-%m-%d")

        cutoff_clean = cutoff_time.strip()
        if len(cutoff_clean.split(":")) == 2:
            cutoff_clean = f"{cutoff_clean}:00Z"
        elif not cutoff_clean.endswith("Z"):
            cutoff_clean = f"{cutoff_clean}Z"

        cutoff_datetime = f"{dec_date_str}T{cutoff_clean}"

        with get_db() as session:
            hourly_forecasts = {}
            for h in range(24):
                hour_target = f"{delivery_date}T{h:02d}:00:00Z"
                row = session.query(
                    ForecastWind.publish_time,
                    ForecastWind.generation
                ).filter(
                    ForecastWind.start_time == hour_target,
                    ForecastWind.publish_time <= cutoff_datetime
                ).order_by(ForecastWind.publish_time.desc()).first()

                if row:
                    hourly_forecasts[hour_target] = {
                        "generation": round(row.generation, 2),
                        "publishTime": row.publish_time
                    }
                else:
                    hourly_forecasts[hour_target] = {
                        "generation": None,
                        "publishTime": None
                    }

        return hourly_forecasts, cutoff_datetime, dec_date_str
