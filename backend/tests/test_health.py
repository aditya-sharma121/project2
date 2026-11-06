import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AFTERFLOW" in data["service"]
    assert "disclaimer" in data
    assert "decision-support" in data["disclaimer"].lower()


def test_error_response_format_404():
    response = client.get("/api/v1/non-existent-route-404")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]


def test_api_v1_subroutes_exist():
    # Test auth (returns 401 unauthorized without token, confirming auth guard works)
    assert client.get("/api/v1/auth/me").status_code == 401
    # Test incidents
    assert client.get("/api/v1/incidents").status_code == 200
    # Test evidence
    assert client.get("/api/v1/evidence").status_code == 200
    # Test AI
    assert client.get("/api/v1/ai/status").status_code == 200
    # Test Geo
    assert client.get("/api/v1/geo/incidents").status_code == 200
    # Test Routes
    assert client.get("/api/v1/routes/status").status_code == 200
    # Test Dashboard
    assert client.get("/api/v1/dashboard/kpis").status_code == 200
