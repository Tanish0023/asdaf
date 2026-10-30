import pytest
from backend.app.services.data_store import DataStore
from backend.app.database import init_db, get_db
from backend.app.models import ActualWind

TEST_DATE = "2099-01-10"

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    with get_db() as session:
        session.query(ActualWind).filter(ActualWind.settlement_date == TEST_DATE).delete()
        session.commit()
    yield
    with get_db() as session:
        session.query(ActualWind).filter(ActualWind.settlement_date == TEST_DATE).delete()
        session.commit()

def test_hourly_aggregation_two_half_hours():
    store = DataStore()
    records = [
        {
            "startTime": f"{TEST_DATE}T10:00:00Z",
            "publishTime": f"{TEST_DATE}T10:30:00Z",
            "settlementDate": TEST_DATE,
            "settlementPeriod": 21,
            "generation": 1000.0
        },
        {
            "startTime": f"{TEST_DATE}T10:30:00Z",
            "publishTime": f"{TEST_DATE}T11:00:00Z",
            "settlementDate": TEST_DATE,
            "settlementPeriod": 22,
            "generation": 1200.0
        }
    ]
    store.upsert_actuals(records)

    hourly = store.get_hourly_actuals_for_date(TEST_DATE)
    target_hour = f"{TEST_DATE}T10:00:00Z"

    assert target_hour in hourly
    assert hourly[target_hour]["generation"] == 1100.0  # Average of 1000 and 1200
    assert hourly[target_hour]["settlementPeriods"] == [21, 22]

def test_hourly_aggregation_single_half_hour():
    store = DataStore()
    records = [
        {
            "startTime": f"{TEST_DATE}T14:30:00Z",
            "publishTime": f"{TEST_DATE}T15:00:00Z",
            "settlementDate": TEST_DATE,
            "settlementPeriod": 30,
            "generation": 850.0
        }
    ]
    store.upsert_actuals(records)

    hourly = store.get_hourly_actuals_for_date(TEST_DATE)
    target_hour = f"{TEST_DATE}T14:00:00Z"

    assert hourly[target_hour]["generation"] == 850.0
    assert hourly[target_hour]["settlementPeriods"] == [30]

def test_hourly_aggregation_missing_data():
    store = DataStore()
    hourly = store.get_hourly_actuals_for_date(TEST_DATE)
    target_hour = f"{TEST_DATE}T05:00:00Z"

    assert target_hour in hourly
    assert hourly[target_hour]["generation"] is None
