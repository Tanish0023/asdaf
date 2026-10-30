import pytest
from backend.app.services.data_store import DataStore
from backend.app.database import init_db, get_db_connection

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_wind.db")
    monkeypatch.setattr("backend.app.config.DB_PATH", test_db)
    init_db()
    yield test_db

def test_hourly_aggregation_two_half_hours():
    store = DataStore()
    # Insert two settlement periods for 2026-01-10 10:00 and 10:30
    records = [
        {
            "startTime": "2026-01-10T10:00:00Z",
            "publishTime": "2026-01-10T10:30:00Z",
            "settlementDate": "2026-01-10",
            "settlementPeriod": 21,
            "generation": 1000.0
        },
        {
            "startTime": "2026-01-10T10:30:00Z",
            "publishTime": "2026-01-10T11:00:00Z",
            "settlementDate": "2026-01-10",
            "settlementPeriod": 22,
            "generation": 1200.0
        }
    ]
    store.upsert_actuals(records)

    hourly = store.get_hourly_actuals_for_date("2026-01-10")
    target_hour = "2026-01-10T10:00:00Z"

    assert target_hour in hourly
    assert hourly[target_hour]["generation"] == 1100.0  # Average of 1000 and 1200
    assert hourly[target_hour]["settlementPeriods"] == [21, 22]

def test_hourly_aggregation_single_half_hour():
    store = DataStore()
    records = [
        {
            "startTime": "2026-01-10T14:30:00Z",
            "publishTime": "2026-01-10T15:00:00Z",
            "settlementDate": "2026-01-10",
            "settlementPeriod": 30,
            "generation": 850.0
        }
    ]
    store.upsert_actuals(records)

    hourly = store.get_hourly_actuals_for_date("2026-01-10")
    target_hour = "2026-01-10T14:00:00Z"

    assert hourly[target_hour]["generation"] == 850.0
    assert hourly[target_hour]["settlementPeriods"] == [30]

def test_hourly_aggregation_missing_data():
    store = DataStore()
    hourly = store.get_hourly_actuals_for_date("2026-01-10")
    target_hour = "2026-01-10T05:00:00Z"

    assert target_hour in hourly
    assert hourly[target_hour]["generation"] is None
