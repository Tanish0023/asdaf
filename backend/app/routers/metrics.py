from fastapi import APIRouter, Query, HTTPException
from backend.app.schemas import (
    MetricsSummaryResponse, HourlyProfileResponse,
    DailyTimelineResponse, ErrorDistributionResponse,
    BalancingCalcRequest, BalancingCalcResponse
)
from backend.app.services.analytics import AnalyticsService
from backend.app.config import DEFAULT_CUTOFF_TIME, ASSESSMENT_START_DATE, ASSESSMENT_END_DATE

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

@router.get("/summary", response_model=MetricsSummaryResponse)
def get_metrics_summary(
    start_date: str = Query(ASSESSMENT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(ASSESSMENT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff_time: str = Query(DEFAULT_CUTOFF_TIME, description="Cutoff time (HH:MM)")
):
    try:
        service = AnalyticsService()
        return service.compute_metrics_summary(start_date, end_date, cutoff_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics summary: {str(e)}")

@router.get("/hourly-profile", response_model=HourlyProfileResponse)
def get_hourly_profile(
    start_date: str = Query(ASSESSMENT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(ASSESSMENT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff_time: str = Query(DEFAULT_CUTOFF_TIME, description="Cutoff time (HH:MM)")
):
    try:
        service = AnalyticsService()
        return service.compute_hourly_profile(start_date, end_date, cutoff_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute hourly profile: {str(e)}")

@router.get("/daily-timeline", response_model=DailyTimelineResponse)
def get_daily_timeline(
    start_date: str = Query(ASSESSMENT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(ASSESSMENT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff_time: str = Query(DEFAULT_CUTOFF_TIME, description="Cutoff time (HH:MM)")
):
    try:
        service = AnalyticsService()
        return service.compute_daily_timeline(start_date, end_date, cutoff_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute daily timeline: {str(e)}")

@router.get("/distribution", response_model=ErrorDistributionResponse)
def get_error_distribution(
    start_date: str = Query(ASSESSMENT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(ASSESSMENT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff_time: str = Query(DEFAULT_CUTOFF_TIME, description="Cutoff time (HH:MM)"),
    bins: int = Query(16, ge=6, le=50, description="Number of histogram bins")
):
    try:
        service = AnalyticsService()
        return service.compute_error_distribution(start_date, end_date, cutoff_time, bins)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute error distribution: {str(e)}")

@router.post("/balancing-calculator", response_model=BalancingCalcResponse)
def calculate_balancing(req: BalancingCalcRequest):
    try:
        service = AnalyticsService()
        return service.calculate_balancing_risk(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate balancing risk: {str(e)}")
