from fastapi import APIRouter, Query, HTTPException
from app.schemas import DayAheadResponse
from app.services.analytics import AnalyticsService
from app.config import DEFAULT_CUTOFF_TIME

router = APIRouter(prefix="/api/v1", tags=["day-ahead"])

@router.get("/day-ahead", response_model=DayAheadResponse)
def get_day_ahead_schedule(
    delivery_date: str = Query(..., description="Target delivery date in YYYY-MM-DD format (e.g. 2026-01-15)"),
    cutoff_time: str = Query(DEFAULT_CUTOFF_TIME, description="Cutoff time on D-1 in HH:MM format (e.g. 11:00)")
):
    try:
        service = AnalyticsService()
        return service.get_day_ahead_schedule(delivery_date, cutoff_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate day-ahead schedule: {str(e)}")
