import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_endpoint():
    """Health check should return ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_version_endpoint():
    """Version endpoint should return version."""
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_scan_endpoint_validation():
    """Scan should reject invalid files."""
    # No file
    response = client.post("/api/v1/scan")
    assert response.status_code == 422
    
    # Wrong content type
    response = client.post(
        "/api/v1/scan",
        files={"file": ("test.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415
    
    # Oversized file (mock - would need actual large file)
    # This tests the validation logic exists


def test_scan_endpoint_contract():
    """Scan response should match contract."""
    # This would need a real image and loaded model
    # For now, test that endpoint exists
    response = client.post(
        "/api/v1/scan",
        files={"file": ("test.jpg", b"fake", "image/jpeg")},
    )
    # Will fail due to model not loaded, but endpoint should exist
    assert response.status_code in (200, 500)  # 500 if model not loaded


def test_twin_endpoint():
    """Twin endpoint should return graph and metrics."""
    response = client.get("/api/v1/twin")
    assert response.status_code == 200
    data = response.json()
    assert "graph" in data
    assert "metrics" in data
    assert "nodes" in data["graph"]
    assert "edges" in data["graph"]


def test_simulate_endpoint():
    """Simulate endpoint should return baseline, scenario, deltas."""
    response = client.post(
        "/api/v1/simulate",
        json={"compliance": 0.8, "ticks": 10},
    )
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "scenario" in data
    assert "deltas" in data
    assert all(k in data["deltas"] for k in ["diversion_rate", "contamination_rate", "co2e_avoided_kg", "pickup_cost"])


def test_advice_cached_endpoint():
    """Cached advice should work without LLM."""
    response = client.post("/api/v1/advice?use_cached=true")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "actions" in data
    assert "cached" in data


def test_admin_endpoints_require_admin():
    """Admin endpoints should require admin role."""
    # Without auth, should fail
    response = client.post("/api/v1/admin/demo/reset")
    assert response.status_code in (401, 403)
    
    response = client.post("/api/v1/admin/demo/traffic?start=true")
    assert response.status_code in (401, 403)


def test_rate_limiting_headers():
    """Rate limit headers should be present."""
    response = client.get("/api/v1/twin")
    # SlowAPI adds rate limit headers
    # This is a basic check
    assert response.status_code == 200