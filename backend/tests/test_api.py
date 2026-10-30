import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data

def test_dates_endpoint():
    response = client.get("/api/v1/dates")
    assert response.status_code == 200
    data = response.json()
    assert "delivery_dates" in data
    assert "decision_dates" in data
    assert "cutoff_options" in data
    assert len(data["cutoff_options"]) >= 4

def test_day_ahead_endpoint():
    response = client.get("/api/v1/day-ahead?delivery_date=2026-01-15&cutoff_time=11:00")
    assert response.status_code == 200
    data = response.json()
    assert data["delivery_date"] == "2026-01-15"
    assert data["cutoff_time"] == "11:00"
    assert len(data["hourly_records"]) == 24
    assert "summary" in data

def test_metrics_summary_endpoint():
    response = client.get("/api/v1/metrics/summary?start_date=2026-01-01&end_date=2026-01-31&cutoff_time=11:00")
    assert response.status_code == 200
    data = response.json()
    assert "mae" in data
    assert "rmse" in data
    assert "mbe" in data
    assert "wape" in data
    assert "accuracy_rate" in data

def test_hourly_profile_endpoint():
    response = client.get("/api/v1/metrics/hourly-profile?start_date=2026-01-01&end_date=2026-01-31&cutoff_time=11:00")
    assert response.status_code == 200
    data = response.json()
    assert "profiles" in data
    assert len(data["profiles"]) == 24

def test_distribution_endpoint():
    response = client.get("/api/v1/metrics/distribution?start_date=2026-01-01&end_date=2026-01-31&cutoff_time=11:00")
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert "total_count" in data

def test_export_endpoint():
    response = client.get("/api/v1/export?start_date=2026-01-01&end_date=2026-01-02&cutoff_time=11:00")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "DeliveryDate" in response.text
