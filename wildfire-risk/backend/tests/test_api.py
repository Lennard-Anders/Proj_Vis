from datetime import date

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_risk_endpoint() -> None:
    params = {"date": date.today().isoformat(), "bbox": "-120.5,35.0,-120.0,35.5"}
    response = client.get("/api/risk", params=params)
    assert response.status_code == 200
    payload = response.json()
    assert "grid" in payload
    assert len(payload["grid"]) > 0
