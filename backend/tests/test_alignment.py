import pytest
from app.services.data_store import DataStore
from app.database import init_db, get_db
from app.models import ForecastWind

TEST_DELIVERY_DATE = "2099-01-15"
TEST_DECISION_DATE = "2099-01-14"

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    with get_db() as session:
        session.query(ForecastWind).filter(ForecastWind.start_time.like(f"{TEST_DELIVERY_DATE}T%")).delete()
        session.commit()
    yield
    with get_db() as session:
        session.query(ForecastWind).filter(ForecastWind.start_time.like(f"{TEST_DELIVERY_DATE}T%")).delete()
        session.commit()

def test_forecast_alignment_selects_latest_before_cutoff():
    store = DataStore()
    target_hour = f"{TEST_DELIVERY_DATE}T14:00:00Z"

    # Insert three forecasts for target_hour:
    # 1. Published 2099-01-14T06:00:00Z (before cutoff, early) -> gen = 5000
    # 2. Published 2099-01-14T10:30:00Z (before cutoff, latest valid) -> gen = 5500
    # 3. Published 2099-01-14T11:30:00Z (AFTER cutoff!) -> gen = 6000
    # 4. Published 2099-01-15T08:00:00Z (Day-of, intra-day) -> gen = 6500
    forecasts = [
        {"publishTime": f"{TEST_DECISION_DATE}T06:00:00Z", "startTime": target_hour, "generation": 5000.0},
        {"publishTime": f"{TEST_DECISION_DATE}T10:30:00Z", "startTime": target_hour, "generation": 5500.0},
        {"publishTime": f"{TEST_DECISION_DATE}T11:30:00Z", "startTime": target_hour, "generation": 6000.0},
        {"publishTime": f"{TEST_DELIVERY_DATE}T08:00:00Z", "startTime": target_hour, "generation": 6500.0},
    ]
    store.upsert_forecasts(forecasts)

    # Query with default 11:00 cutoff
    hourly_forecasts, cutoff_dt, dec_date = store.get_day_ahead_forecasts(TEST_DELIVERY_DATE, "11:00")

    assert dec_date == TEST_DECISION_DATE
    assert cutoff_dt == f"{TEST_DECISION_DATE}T11:00:00Z"
    
    selected = hourly_forecasts[target_hour]
    # Must select 10:30 forecast (5500 MW), NEVER 11:30 (6000 MW) or 08:00 (6500 MW)
    assert selected["generation"] == 5500.0
    assert selected["publishTime"] == f"{TEST_DECISION_DATE}T10:30:00Z"

def test_forecast_alignment_with_later_cutoff():
    store = DataStore()
    target_hour = f"{TEST_DELIVERY_DATE}T14:00:00Z"

    forecasts = [
        {"publishTime": f"{TEST_DECISION_DATE}T10:30:00Z", "startTime": target_hour, "generation": 5500.0},
        {"publishTime": f"{TEST_DECISION_DATE}T11:30:00Z", "startTime": target_hour, "generation": 6000.0},
    ]
    store.upsert_forecasts(forecasts)

    # If trader uses 12:00 cutoff, 11:30 forecast becomes available
    hourly_forecasts, cutoff_dt, _ = store.get_day_ahead_forecasts(TEST_DELIVERY_DATE, "12:00")
    assert cutoff_dt == f"{TEST_DECISION_DATE}T12:00:00Z"
    assert hourly_forecasts[target_hour]["generation"] == 6000.0
    assert hourly_forecasts[target_hour]["publishTime"] == f"{TEST_DECISION_DATE}T11:30:00Z"

def test_forecast_alignment_strictly_excludes_future_forecasts():
    store = DataStore()
    target_hour = f"{TEST_DELIVERY_DATE}T14:00:00Z"

    # Only a forecast published AFTER cutoff exists
    forecasts = [
        {"publishTime": f"{TEST_DECISION_DATE}T15:00:00Z", "startTime": target_hour, "generation": 7000.0},
    ]
    store.upsert_forecasts(forecasts)

    hourly_forecasts, _, _ = store.get_day_ahead_forecasts(TEST_DELIVERY_DATE, "11:00")
    assert hourly_forecasts[target_hour]["generation"] is None
    assert hourly_forecasts[target_hour]["publishTime"] is None
