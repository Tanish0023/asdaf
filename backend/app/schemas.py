from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CutoffOption(BaseModel):
    value: str
    label: str
    description: str

class DateOptionsResponse(BaseModel):
    decision_dates: List[str]
    delivery_dates: List[str]
    default_delivery_date: str
    default_decision_date: str
    cutoff_options: List[CutoffOption]
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
    p90_shortfall: float
    p95_shortfall: float
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

class BalancingHourlyItem(BaseModel):
    hour: str
    startTime: str
    demand_mw: float
    forecast_wind_mw: float
    actual_wind_mw: Optional[float]
    base_thermal_required_mw: float
    reserve_buffer_mw: float
    total_thermal_procured_mw: float
    net_position_with_actual_mw: Optional[float]

class BalancingCalcRequest(BaseModel):
    customer_demand_mw: float = Field(25000.0, ge=100.0, le=100000.0)
    delivery_date: str
    cutoff_time: str = "11:00"
    confidence_level: float = Field(0.90, ge=0.50, le=0.99)

class BalancingCalcResponse(BaseModel):
    delivery_date: str
    decision_date: str
    cutoff_time: str
    customer_demand_mw: float
    confidence_level: float
    avg_forecast_wind_mw: float
    min_forecast_wind_mw: float
    max_forecast_wind_mw: float
    expected_base_thermal_mw: float
    recommended_reserve_buffer_mw: float
    total_thermal_procurement_mw: float
    hourly_breakdown: List[BalancingHourlyItem]

class SyncResponse(BaseModel):
    status: str
    actuals_synced: int
    forecasts_synced: int
    message: str
    synced_at: str
