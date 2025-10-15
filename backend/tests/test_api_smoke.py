"""
Smoke tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_risk_endpoint():
    """Test risk assessment endpoint"""
    response = client.get("/risk?date=2024-01-15&bbox=-122,37,-121,38")
    assert response.status_code == 200
    
    data = response.json()
    assert "grid" in data
    assert "quality" in data
    assert "date" in data
    assert len(data["grid"]) > 0


def test_explain_endpoint():
    """Test explanation endpoint"""
    response = client.get("/explain?lat=37.5&lon=-122.0&date=2024-01-15")
    assert response.status_code == 200
    
    data = response.json()
    assert "probability" in data
    assert "local_shap" in data
    assert "interactions" in data
    assert "ood" in data


def test_counterfactual_endpoint():
    """Test counterfactual endpoint"""
    payload = {
        "lat": 37.5,
        "lon": -122.0,
        "date": "2024-01-15",
        "deltas": {
            "wind_speed_10m": 15.0,
            "rh": 30.0
        },
        "use_surrogate": True
    }
    
    response = client.post("/risk/counterfactual", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "probability" in data
    assert "delta" in data
    assert "used" in data


def test_frames_endpoint():
    """Test frames endpoint"""
    response = client.get("/frames?lat=37.5&lon=-122.0&date=2024-01-15")
    assert response.status_code == 200
    
    data = response.json()
    assert "times" in data
    assert "tiles" in data


def test_spread_endpoint():
    """Test spread simulation endpoint"""
    payload = {
        "lat": 37.5,
        "lon": -122.0,
        "date": "2024-01-15",
        "wind_speed_10m": 10.0,
        "wind_dir": 270.0,
        "duration_hours": 6,
        "steps": 12
    }
    
    response = client.post("/spread/run", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "footprint_geojson" in data
    assert "metrics" in data
