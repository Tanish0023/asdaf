from fastapi import APIRouter
from app.schemas import DateOptionsResponse
from app.services.data_store import DataStore
from app.config import FIXED_DECISION_CUTOFF

router = APIRouter(prefix="/api/v1", tags=["dates"])

@router.get("/dates", response_model=DateOptionsResponse)
def get_available_dates():
    store = DataStore()
    date_info = store.get_available_dates()
    status = store.get_data_status()

    return DateOptionsResponse(
        decision_dates=date_info["decision_dates"],
        delivery_dates=date_info["delivery_dates"],
        default_delivery_date=date_info["default_delivery_date"],
        default_decision_date=date_info["default_decision_date"],
        decision_cutoff=FIXED_DECISION_CUTOFF,
        total_actual_records=status["actual_count"],
        total_forecast_records=status["forecast_count"]
    )
