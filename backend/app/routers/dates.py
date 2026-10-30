from fastapi import APIRouter
from app.schemas import DateOptionsResponse, CutoffOption
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/v1", tags=["dates"])

@router.get("/dates", response_model=DateOptionsResponse)
def get_available_dates():
    store = DataStore()
    date_info = store.get_available_dates()
    status = store.get_sync_status()

    cutoff_options = [
        CutoffOption(
            value="09:30",
            label="09:30 UTC (Early Morning Bid Prep)",
            description="Early forecast run before internal trading desk valuation."
        ),
        CutoffOption(
            value="11:00",
            label="11:00 UTC (GB Day-Ahead Auction Close - Default)",
            description="Official EPEX SPOT & Nord Pool GB Day-Ahead wholesale auction gate closure."
        ),
        CutoffOption(
            value="12:00",
            label="12:00 UTC (Midday Cutoff)",
            description="Post-auction adjustments & secondary market bidding."
        ),
        CutoffOption(
            value="15:30",
            label="15:30 UTC (Afternoon Update)",
            description="Afternoon National Grid forecast release."
        ),
        CutoffOption(
            value="17:00",
            label="17:00 UTC (Close of Day-Ahead Window)",
            description="Final bilateral schedule notification deadline."
        )
    ]

    return DateOptionsResponse(
        decision_dates=date_info["decision_dates"],
        delivery_dates=date_info["delivery_dates"],
        default_delivery_date=date_info["default_delivery_date"],
        default_decision_date=date_info["default_decision_date"],
        cutoff_options=cutoff_options,
        latest_sync_time=status["latest_sync"],
        total_actual_records=status["actual_count"],
        total_forecast_records=status["forecast_count"]
    )
