import pytest
from app.services.analytics import AnalyticsService
from app.services.data_store import DataStore
from app.database import init_db

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    yield

def test_accuracy_metrics_calculation(monkeypatch):
    store = DataStore()
    analytics = AnalyticsService(data_store=store)

    # Mock _collect_aligned_dataset to return known data points
    # Case: 4 hours
    # Actual:   [100, 200, 300, 400]
    # Forecast: [120, 190, 330, 360]
    # Error (F - A): [+20, -10, +30, -40]
    # Abs Error: [20, 10, 30, 40]
    # MAE = (20 + 10 + 30 + 40) / 4 = 100 / 4 = 25.0
    # MBE = (20 - 10 + 30 - 40) / 4 = 0 / 4 = 0.0
    # RMSE = sqrt((400 + 100 + 900 + 1600) / 4) = sqrt(3000 / 4) = sqrt(750) = 27.386... -> 27.39
    # Sum actual = 1000
    # WAPE = 100 / 1000 * 100 = 10.0%
    mock_points = [
        {"delivery_date": "2026-01-05", "hour": 0, "startTime": "2026-01-05T00:00:00Z", "actual": 100.0, "forecast": 120.0, "publish_time": "2026-01-04T10:30:00Z", "error": 20.0, "abs_error": 20.0},
        {"delivery_date": "2026-01-05", "hour": 1, "startTime": "2026-01-05T01:00:00Z", "actual": 200.0, "forecast": 190.0, "publish_time": "2026-01-04T10:30:00Z", "error": -10.0, "abs_error": 10.0},
        {"delivery_date": "2026-01-05", "hour": 2, "startTime": "2026-01-05T02:00:00Z", "actual": 300.0, "forecast": 330.0, "publish_time": "2026-01-04T10:30:00Z", "error": 30.0, "abs_error": 30.0},
        {"delivery_date": "2026-01-05", "hour": 3, "startTime": "2026-01-05T03:00:00Z", "actual": 400.0, "forecast": 360.0, "publish_time": "2026-01-04T10:30:00Z", "error": -40.0, "abs_error": 40.0},
    ]

    monkeypatch.setattr(analytics, "_collect_aligned_dataset", lambda *args, **kwargs: mock_points)

    res = analytics.compute_metrics_summary()

    assert res.mae == 25.0
    assert res.mbe == 0.0
    assert res.rmse == 27.39
    assert res.wape == 10.0
    assert res.accuracy_rate == 90.0
    assert res.max_over_forecast == 30.0
    assert res.max_under_forecast == -40.0
    assert res.total_observations == 4
    assert hasattr(res, "p10_error")
    assert hasattr(res, "p50_error")
    assert hasattr(res, "p90_error")
    assert hasattr(res, "p95_error")

def test_zero_generation_and_empty_dataset(monkeypatch):
    store = DataStore()
    analytics = AnalyticsService(data_store=store)

    # Test empty dataset
    monkeypatch.setattr(analytics, "_collect_aligned_dataset", lambda *args, **kwargs: [])
    empty_res = analytics.compute_metrics_summary()
    assert empty_res.total_observations == 0
    assert empty_res.mae == 0.0
    assert empty_res.wape == 0.0

    # Test zero actual generation (calm wind)
    zero_points = [
        {"delivery_date": "2026-01-05", "hour": 0, "startTime": "2026-01-05T00:00:00Z", "actual": 0.0, "forecast": 50.0, "publish_time": "2026-01-04T10:30:00Z", "error": 50.0, "abs_error": 50.0},
    ]
    monkeypatch.setattr(analytics, "_collect_aligned_dataset", lambda *args, **kwargs: zero_points)
    zero_res = analytics.compute_metrics_summary()
    # Must not raise ZeroDivisionError
    assert zero_res.mae == 50.0
    assert zero_res.mbe == 50.0
