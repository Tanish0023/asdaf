from pydantic import BaseModel
from typing import List, Optional

class DateOptionsResponse(BaseModel):
    decision_dates: List[str]
    delivery_dates: List[str]
    default_delivery_date: str
    default_decision_date: str
    decision_cutoff: str = "11:00"
    latest_sync_time: Optional[str] = None
    total_actual_records: int
    total_forecast_records: int

class HourlyDayAheadRecord(BaseModel):
    hour: str
    startTime: str
    settlementPeriods: List[int]
    forecast_generation: Optional[float] = None
    actual_generation: Optional[float] = None
    publish_time: Optional[str] = None
    error_mw: Optional[float] = None  # forecast - actual (positive = over-forecast)
    abs_error_mw: Optional[float] = None
    pct_error: Optional[float] = None

class DayAheadSummary(BaseModel):
    avg_actual_mw: Optional[float] = None
    avg_forecast_mw: Optional[float] = None
    total_actual_mwh: Optional[float] = None
    total_forecast_mwh: Optional[float] = None
    mae_mw: Optional[float] = None
    mbe_mw: Optional[float] = None
    wape_pct: Optional[float] = None
    max_forecast_mw: Optional[float] = None
    min_forecast_mw: Optional[float] = None

class DayAheadResponse(BaseModel):
    delivery_date: str
    decision_date: str
    cutoff_time: str
    cutoff_datetime: str
    hourly_records: List[HourlyDayAheadRecord]
    summary: DayAheadSummary

class MetricsSummaryResponse(BaseModel):
    mae: float
    rmse: float
    mbe: float
    wape: float
    mape: float
    accuracy_rate: float
    p10_error: float
    p50_error: float
    p90_error: float
    p95_error: float
    max_over_forecast: float
    max_under_forecast: float
    total_observations: int
    start_date: str
    end_date: str
    cutoff_time: str

class HourlyProfileItem(BaseModel):
    hour: int
    hour_label: str
    avg_actual: float
    avg_forecast: float
    mae: float
    mbe: float
    sample_count: int

class HourlyProfileResponse(BaseModel):
    profiles: List[HourlyProfileItem]
    cutoff_time: str

class DailyTimelineItem(BaseModel):
    date: str
    mae: float
    rmse: float
    mbe: float
    wape: float
    total_actual_mwh: float
    total_forecast_mwh: float
    observation_count: int

class DailyTimelineResponse(BaseModel):
    timeline: List[DailyTimelineItem]
    cutoff_time: str

class ErrorDistributionItem(BaseModel):
    bin_start: float
    bin_end: float
    bin_label: str
    count: int
    percentage: float

class ErrorDistributionResponse(BaseModel):
    distribution: List[ErrorDistributionItem]
    total_count: int
    mean_error: float
    std_dev: float
    cutoff_time: str
