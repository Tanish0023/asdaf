import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import math

from app.services.data_store import DataStore
from app.config import FIXED_DECISION_CUTOFF, ASSESSMENT_START_DATE, ASSESSMENT_END_DATE
from app.schemas import (
    HourlyDayAheadRecord, DayAheadSummary, DayAheadResponse,
    MetricsSummaryResponse, HourlyProfileItem, HourlyProfileResponse,
    DailyTimelineItem, DailyTimelineResponse,
    ErrorDistributionItem, ErrorDistributionResponse
)

_SCHEDULE_CACHE = {}
_DATASET_CACHE = {}

def clear_analytics_cache():
    _SCHEDULE_CACHE.clear()
    _DATASET_CACHE.clear()

class AnalyticsService:
    def __init__(self, data_store: Optional[DataStore] = None):
        self.data_store = data_store or DataStore()

    def get_day_ahead_schedule(self, delivery_date: str, cutoff_time: str = FIXED_DECISION_CUTOFF) -> DayAheadResponse:
        """
        Calculates day-ahead forecast vs actual generation for 24 hours of delivery_date.
        Cutoff is applied on day D-1 at cutoff_time (default 11:00 UTC).
        Cached in-memory so repeated day lookups respond in < 10ms.
        """
        import time as _time
        cache_key = f"{delivery_date}_{cutoff_time}"
        now = _time.time()
        if cache_key in _SCHEDULE_CACHE and (now - _SCHEDULE_CACHE[cache_key]["time"] < 300):
            return _SCHEDULE_CACHE[cache_key]["data"]

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            fut_act = executor.submit(self.data_store.get_hourly_actuals_for_date, delivery_date)
            fut_fc = executor.submit(self.data_store.get_day_ahead_forecasts, delivery_date, cutoff_time)
            hourly_actuals = fut_act.result()
            hourly_forecasts, cutoff_datetime, dec_date_str = fut_fc.result()

        records: List[HourlyDayAheadRecord] = []
        actual_vals = []
        forecast_vals = []
        errors = []
        abs_errors = []

        for h in range(24):
            hour_str = f"{h:02d}:00"
            hour_target = f"{delivery_date}T{h:02d}:00:00Z"
            
            act_info = hourly_actuals.get(hour_target, {})
            act_gen = act_info.get("generation")
            periods = act_info.get("settlementPeriods", [h * 2 + 1, h * 2 + 2])

            for_info = hourly_forecasts.get(hour_target, {})
            for_gen = for_info.get("generation")
            pub_time = for_info.get("publishTime")

            err = None
            abs_err = None
            pct_err = None

            if for_gen is not None and act_gen is not None:
                err = round(for_gen - act_gen, 2)
                abs_err = round(abs(err), 2)
                pct_err = round((abs_err / act_gen * 100), 2) if act_gen > 0 else 0.0

                actual_vals.append(act_gen)
                forecast_vals.append(for_gen)
                errors.append(err)
                abs_errors.append(abs_err)

            records.append(HourlyDayAheadRecord(
                hour=hour_str,
                startTime=hour_target,
                settlementPeriods=periods,
                forecast_generation=for_gen,
                actual_generation=act_gen,
                publish_time=pub_time,
                error_mw=err,
                abs_error_mw=abs_err,
                pct_error=pct_err
            ))

        # Day Summary
        summary = DayAheadSummary()
        if actual_vals and forecast_vals:
            summary.avg_actual_mw = round(float(np.mean(actual_vals)), 2)
            summary.avg_forecast_mw = round(float(np.mean(forecast_vals)), 2)
            summary.total_actual_mwh = round(float(np.sum(actual_vals)), 2)
            summary.total_forecast_mwh = round(float(np.sum(forecast_vals)), 2)
            summary.mae_mw = round(float(np.mean(abs_errors)), 2)
            summary.mbe_mw = round(float(np.mean(errors)), 2)
            tot_act = np.sum(actual_vals)
            summary.wape_pct = round(float(np.sum(abs_errors) / tot_act * 100), 2) if tot_act > 0 else 0.0
            summary.max_forecast_mw = round(float(np.max(forecast_vals)), 2)
            summary.min_forecast_mw = round(float(np.min(forecast_vals)), 2)

        res = DayAheadResponse(
            delivery_date=delivery_date,
            decision_date=dec_date_str,
            cutoff_time=cutoff_time,
            cutoff_datetime=cutoff_datetime,
            hourly_records=records,
            summary=summary
        )
        _SCHEDULE_CACHE[cache_key] = {"time": now, "data": res}
        return res

    def _collect_aligned_dataset(
        self,
        start_date: str = ASSESSMENT_START_DATE,
        end_date: str = ASSESSMENT_END_DATE,
        cutoff_time: str = FIXED_DECISION_CUTOFF
    ) -> List[Dict[str, Any]]:
        """
        HIGH-PERFORMANCE ALIGNMENT:
        Fetches all actuals and forecasts for the requested date range in 2 queries,
        then aligns all hours in-memory.
        Cached in-memory so subsequent concurrent metrics queries respond in 0ms.
        """
        import time as _time
        cache_key = f"{start_date}_{end_date}_{cutoff_time}"
        now = _time.time()

        if cache_key in _DATASET_CACHE and (now - _DATASET_CACHE[cache_key]["time"] < 300):
            return _DATASET_CACHE[cache_key]["data"]

        # 1. Fetch range data in 2 bulk queries
        act_rows, for_rows = self.data_store.get_bulk_range_data(start_date, end_date)

        # 2. Aggregate actuals by hour in-memory
        actuals_by_hour = defaultdict(list)
        for r in act_rows:
            st = r.start_time
            hour_key = st[:13] + ":00:00Z"
            actuals_by_hour[hour_key].append(r.generation)

        hourly_actuals = {
            h: sum(vals) / len(vals) for h, vals in actuals_by_hour.items() if vals
        }

        # 3. Organize forecasts by target hour sorted by publish_time DESC
        forecasts_by_start = defaultdict(list)
        for r in for_rows:
            forecasts_by_start[r.start_time].append((r.publish_time, r.generation))

        for st in forecasts_by_start:
            forecasts_by_start[st].sort(key=lambda x: x[0], reverse=True)

        # 4. Clean cutoff time format
        cutoff_clean = cutoff_time.strip()
        if len(cutoff_clean.split(":")) == 2:
            cutoff_clean = f"{cutoff_clean}:00Z"
        elif not cutoff_clean.endswith("Z"):
            cutoff_clean = f"{cutoff_clean}Z"

        # 5. In-memory alignment across days and hours
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        delta = (end_dt - start_dt).days + 1

        all_points = []
        for d in range(delta):
            curr_dt = start_dt + timedelta(days=d)
            curr_date = curr_dt.strftime("%Y-%m-%d")
            dec_date = (curr_dt - timedelta(days=1)).strftime("%Y-%m-%d")
            cutoff_datetime = f"{dec_date}T{cutoff_clean}"

            for h in range(24):
                hour_target = f"{curr_date}T{h:02d}:00:00Z"
                act_gen = hourly_actuals.get(hour_target)

                # Find latest forecast published <= cutoff_datetime
                candidates = forecasts_by_start.get(hour_target, [])
                for_gen = None
                pub_time = None
                for candidate_pub, candidate_gen in candidates:
                    if candidate_pub <= cutoff_datetime:
                        for_gen = candidate_gen
                        pub_time = candidate_pub
                        break

                if act_gen is not None and for_gen is not None:
                    err = round(for_gen - act_gen, 2)
                    all_points.append({
                        "delivery_date": curr_date,
                        "hour": h,
                        "startTime": hour_target,
                        "actual": round(act_gen, 2),
                        "forecast": round(for_gen, 2),
                        "publish_time": pub_time,
                        "error": err,
                        "abs_error": abs(err)
                    })

        _DATASET_CACHE[cache_key] = {"time": now, "data": all_points}
        return all_points

    def compute_metrics_summary(
        self,
        start_date: str = ASSESSMENT_START_DATE,
        end_date: str = ASSESSMENT_END_DATE,
        cutoff_time: str = FIXED_DECISION_CUTOFF
    ) -> MetricsSummaryResponse:
        points = self._collect_aligned_dataset(start_date, end_date, cutoff_time)

        if not points:
            return MetricsSummaryResponse(
                mae=0.0, rmse=0.0, mbe=0.0, wape=0.0, mape=0.0,
                accuracy_rate=0.0, p10_error=0.0, p50_error=0.0,
                p90_error=0.0, p95_error=0.0, max_over_forecast=0.0,
                max_under_forecast=0.0, total_observations=0,
                start_date=start_date, end_date=end_date, cutoff_time=cutoff_time
            )

        errors = np.array([p["error"] for p in points])
        abs_errors = np.array([p["abs_error"] for p in points])
        actuals = np.array([p["actual"] for p in points])

        mae = float(np.mean(abs_errors))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        mbe = float(np.mean(errors))
        
        sum_actuals = float(np.sum(actuals))
        wape = float((np.sum(abs_errors) / sum_actuals * 100)) if sum_actuals > 0 else 0.0

        # Safe MAPE: handle small actuals
        non_zero_mask = actuals > 10.0  # threshold at 10 MW to prevent extreme distortion
        if np.any(non_zero_mask):
            mape = float(np.mean(abs_errors[non_zero_mask] / actuals[non_zero_mask] * 100))
        else:
            mape = wape

        accuracy_rate = max(0.0, round(100.0 - wape, 2))

        p10 = float(np.percentile(errors, 10))
        p50 = float(np.percentile(errors, 50))
        p90 = float(np.percentile(errors, 90))
        p95 = float(np.percentile(errors, 95))

        return MetricsSummaryResponse(
            mae=round(mae, 2),
            rmse=round(rmse, 2),
            mbe=round(mbe, 2),
            wape=round(wape, 2),
            mape=round(mape, 2),
            accuracy_rate=accuracy_rate,
            p10_error=round(p10, 2),
            p50_error=round(p50, 2),
            p90_error=round(p90, 2),
            p95_error=round(p95, 2),
            max_over_forecast=round(float(np.max(errors)), 2),
            max_under_forecast=round(float(np.min(errors)), 2),
            total_observations=len(points),
            start_date=start_date,
            end_date=end_date,
            cutoff_time=cutoff_time
        )

    def compute_hourly_profile(
        self,
        start_date: str = ASSESSMENT_START_DATE,
        end_date: str = ASSESSMENT_END_DATE,
        cutoff_time: str = FIXED_DECISION_CUTOFF
    ) -> HourlyProfileResponse:
        points = self._collect_aligned_dataset(start_date, end_date, cutoff_time)
        df = pd.DataFrame(points)

        profiles = []
        for h in range(24):
            hour_label = f"{h:02d}:00 - {(h+1)%24:02d}:00"
            if not df.empty and not df[df["hour"] == h].empty:
                h_df = df[df["hour"] == h]
                profiles.append(HourlyProfileItem(
                    hour=h,
                    hour_label=hour_label,
                    avg_actual=round(float(h_df["actual"].mean()), 2),
                    avg_forecast=round(float(h_df["forecast"].mean()), 2),
                    mae=round(float(h_df["abs_error"].mean()), 2),
                    mbe=round(float(h_df["error"].mean()), 2),
                    sample_count=int(len(h_df))
                ))
            else:
                profiles.append(HourlyProfileItem(
                    hour=h,
                    hour_label=hour_label,
                    avg_actual=0.0,
                    avg_forecast=0.0,
                    mae=0.0,
                    mbe=0.0,
                    sample_count=0
                ))

        return HourlyProfileResponse(profiles=profiles, cutoff_time=cutoff_time)

    def compute_daily_timeline(
        self,
        start_date: str = ASSESSMENT_START_DATE,
        end_date: str = ASSESSMENT_END_DATE,
        cutoff_time: str = FIXED_DECISION_CUTOFF
    ) -> DailyTimelineResponse:
        points = self._collect_aligned_dataset(start_date, end_date, cutoff_time)
        if not points:
            return DailyTimelineResponse(timeline=[], cutoff_time=cutoff_time)

        df = pd.DataFrame(points)
        timeline = []
        for date_str, group in df.groupby("delivery_date"):
            mae = float(group["abs_error"].mean())
            rmse = float(np.sqrt((group["error"] ** 2).mean()))
            mbe = float(group["error"].mean())
            tot_act = float(group["actual"].sum())
            wape = float(group["abs_error"].sum() / tot_act * 100) if tot_act > 0 else 0.0

            timeline.append(DailyTimelineItem(
                date=str(date_str),
                mae=round(mae, 2),
                rmse=round(rmse, 2),
                mbe=round(mbe, 2),
                wape=round(wape, 2),
                total_actual_mwh=round(tot_act, 2),
                total_forecast_mwh=round(float(group["forecast"].sum()), 2),
                observation_count=int(len(group))
            ))

        timeline.sort(key=lambda x: x.date)
        return DailyTimelineResponse(timeline=timeline, cutoff_time=cutoff_time)

    def compute_error_distribution(
        self,
        start_date: str = ASSESSMENT_START_DATE,
        end_date: str = ASSESSMENT_END_DATE,
        cutoff_time: str = FIXED_DECISION_CUTOFF,
        num_bins: int = 16
    ) -> ErrorDistributionResponse:
        points = self._collect_aligned_dataset(start_date, end_date, cutoff_time)
        if not points:
            return ErrorDistributionResponse(
                distribution=[], total_count=0, mean_error=0.0, std_dev=0.0, cutoff_time=cutoff_time
            )

        errors = np.array([p["error"] for p in points])
        mean_err = float(np.mean(errors))
        std_err = float(np.std(errors))

        # Determine symmetric min/max for intuitive zero-centered histogram
        max_abs = max(abs(float(np.min(errors))), abs(float(np.max(errors))), 1000.0)
        # Round up to nearest 1000
        edge_limit = math.ceil(max_abs / 1000.0) * 1000.0
        bin_edges = np.linspace(-edge_limit, edge_limit, num_bins + 1)

        counts, edges = np.histogram(errors, bins=bin_edges)
        total = len(errors)

        distribution = []
        for i in range(len(counts)):
            b_start = round(float(edges[i]), 1)
            b_end = round(float(edges[i+1]), 1)
            label = f"{int(b_start)} to {int(b_end)}"
            cnt = int(counts[i])
            pct = round(cnt / total * 100.0, 2)
            distribution.append(ErrorDistributionItem(
                bin_start=b_start,
                bin_end=b_end,
                bin_label=label,
                count=cnt,
                percentage=pct
            ))

        return ErrorDistributionResponse(
            distribution=distribution,
            total_count=total,
            mean_error=round(mean_err, 2),
            std_dev=round(std_err, 2),
            cutoff_time=cutoff_time
        )
