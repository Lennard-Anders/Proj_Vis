import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data


def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_risk():
    """Test risk prediction endpoint"""
    request_data = {
        "latitude": 35.0,
        "longitude": -120.0,
        "temperature": 32.0,
        "humidity": 25.0,
        "wind_speed": 15.0,
        "precipitation": 0.0,
        "vegetation_index": 0.6,
        "fuel_moisture": 8.0
    }
    response = client.post("/risk/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert "confidence" in data
    assert "calibrated_score" in data
    assert data["risk_level"] in ["low", "moderate", "high", "critical"]


def test_counterfactual():
    """Test counterfactual endpoint"""
    request_data = {
        "latitude": 35.0,
        "longitude": -120.0,
        "temperature": 32.0,
        "humidity": 25.0,
        "wind_speed": 15.0,
        "precipitation": 0.0,
        "vegetation_index": 0.6,
        "fuel_moisture": 8.0,
        "target_risk": 0.3
    }
    response = client.post("/risk/counterfactual", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "original_risk" in data
    assert "target_risk" in data
    assert "suggested_changes" in data
    assert "feasibility" in data


def test_explain():
    """Test explanation endpoint"""
    request_data = {
        "latitude": 35.0,
        "longitude": -120.0,
        "temperature": 32.0,
        "humidity": 25.0,
        "wind_speed": 15.0,
        "precipitation": 0.0,
        "vegetation_index": 0.6,
        "fuel_moisture": 8.0
    }
    response = client.post("/explain/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "base_value" in data
    assert "predicted_value" in data
    assert "feature_importances" in data
    assert len(data["feature_importances"]) > 0
    
    # Check feature importance structure
    importance = data["feature_importances"][0]
    assert "feature" in importance
    assert "importance" in importance
    assert "direction" in importance


def test_frames():
    """Test frames endpoint"""
    request_data = {
        "start_latitude": 35.0,
        "start_longitude": -120.0,
        "end_latitude": 36.0,
        "end_longitude": -119.0,
        "start_time": "2023-07-01T12:00:00",
        "duration_hours": 24,
        "interval_hours": 6
    }
    response = client.post("/frames/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "frames" in data
    assert "total_frames" in data
    assert "spatial_resolution" in data
    assert data["total_frames"] > 0


def test_spread():
    """Test spread prediction endpoint"""
    request_data = {
        "ignition_latitude": 35.0,
        "ignition_longitude": -120.0,
        "temperature": 32.0,
        "humidity": 25.0,
        "wind_speed": 15.0,
        "wind_direction": 45.0,
        "fuel_type": "grass",
        "simulation_hours": 24
    }
    response = client.post("/spread/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "ignition_point" in data
    assert "spread_points" in data
    assert "total_area_km2" in data
    assert "max_distance_km" in data
