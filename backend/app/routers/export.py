from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse
import io
import csv
from backend.app.services.analytics import AnalyticsService
from backend.app.config import DEFAULT_CUTOFF_TIME, ASSESSMENT_START_DATE, ASSESSMENT_END_DATE

router = APIRouter(prefix="/api/v1", tags=["export"])

@router.get("/export")
def export_csv(
    start_date: str = Query(ASSESSMENT_START_DATE, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(ASSESSMENT_END_DATE, description="End date (YYYY-MM-DD)"),
    cutoff_time: str = Query(DEFAULT_CUTOFF_TIME, description="Cutoff time (HH:MM)")
):
    service = AnalyticsService()
    points = service._collect_aligned_dataset(start_date, end_date, cutoff_time)

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "DeliveryDate",
        "HourOfDay",
        "TargetStartTime",
        "ActualGenerationMW",
        "ForecastGenerationMW",
        "ForecastPublishTime",
        "ErrorMW_ForecastMinusActual",
        "AbsoluteErrorMW",
        "PercentageError",
        "DecisionCutoffTime"
    ])

    for p in points:
        act = p["actual"]
        err = p["error"]
        abs_err = p["abs_error"]
        pct_err = round((abs_err / act * 100), 2) if act > 0 else 0.0

        writer.writerow([
            p["delivery_date"],
            f"{p['hour']:02d}:00",
            p["startTime"],
            act,
            p["forecast"],
            p["publish_time"],
            err,
            abs_err,
            pct_err,
            cutoff_time
        ])

    output.seek(0)
    filename = f"wind_forecast_vs_actual_{start_date}_to_{end_date}_{cutoff_time.replace(':', '')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
