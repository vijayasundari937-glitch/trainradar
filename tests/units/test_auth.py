"""
TrainRadar - Unit Tests for Authentication
-------------------------------------------
Tests that our API key auth correctly
allows and blocks requests.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

VALID_KEY   = "trainradar-secret-key-2026"
INVALID_KEY = "wrong-key-123"


@pytest.fixture(scope="module")
def client():
    """Create a fresh TestClient for each test module."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

VALID_KEY   = "trainradar-secret-key-2026"
INVALID_KEY = "wrong-key-123"


# ── Health Check (public) ─────────────────────────────────────────────────────

def test_health_no_key(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_with_key(client):
    response = client.get("/health", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200


def test_root_no_key(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


# ── Positions (protected) ─────────────────────────────────────────────────────

def test_positions_no_key(client):
    response = client.get("/positions")
    assert response.status_code == 403
    assert "Missing API key" in response.json()["detail"]


def test_positions_wrong_key(client):
    response = client.get("/positions", headers={"X-API-Key": INVALID_KEY})
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]


def test_positions_valid_key(client):
    response = client.get("/positions", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Delays (protected) ────────────────────────────────────────────────────────

def test_delays_no_key(client):
    response = client.get("/delays")
    assert response.status_code == 403


def test_delays_valid_key(client):
    response = client.get("/delays", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Alerts (protected) ────────────────────────────────────────────────────────

def test_alerts_no_key(client):
    response = client.get("/alerts")
    assert response.status_code == 403


def test_alerts_valid_key(client):
    response = client.get("/alerts", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Search (protected) ────────────────────────────────────────────────────────

def test_search_no_key(client):
    response = client.get("/search?q=IC123")
    assert response.status_code == 403


def test_search_valid_key(client):
    response = client.get("/search?q=IC123", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    assert "query" in response.json()
    assert "positions" in response.json()
    assert "delays" in response.json()
    assert "alerts" in response.json()


def test_search_missing_query(client):
    response = client.get("/search", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 422


# ── Stats (protected) ─────────────────────────────────────────────────────────

def test_stats_no_key(client):
    response = client.get("/stats")
    assert response.status_code == 403


def test_stats_valid_key(client):
    response = client.get("/stats", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    data = response.json()
    assert "total_trains" in data
    assert "total_positions" in data
    assert "total_delays" in data
    assert "total_alerts" in data
    assert "generated_at" in data


# ── Filter Tests ──────────────────────────────────────────────────────────────

def test_positions_filter_by_route(client):
    response = client.get("/positions?route_id=ROUTE_A", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    for position in response.json():
        assert position["route_id"] == "ROUTE_A"


def test_delays_filter_by_min_delay(client):
    response = client.get("/delays?min_delay=200", headers={"X-API-Key": VALID_KEY})
    assert response.status_code == 200
    for delay in response.json():
        assert delay["arrival_delay"] >= 200


def test_alerts_filter_by_effect(client):
    response = client.get(
        "/alerts?effect=DELAY&active_only=false",
        headers={"X-API-Key": VALID_KEY}
    )
    assert response.status_code == 200
    for alert in response.json():
        assert alert["effect"] == "DELAY"