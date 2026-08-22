import sys
import os
import json
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.device import Device
from app.models.child import Child
from app.models.location import Location
from app.models.safety_event import SafetyEvent

client = TestClient(app)

def get_sarah_token():
    """Sarah is caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]

def get_david_token():
    """David is caregiver, but NOT for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_openapi_separation_endpoints():
    """Verify separation endpoints appear in OpenAPI docs."""
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    assert "/api/v1/safety/separation/{child_id}" in paths
    assert "get" in paths["/api/v1/safety/separation/{child_id}"]

    assert "/api/v1/safety/separation/{child_id}/status" in paths
    assert "get" in paths["/api/v1/safety/separation/{child_id}/status"]

    assert "/api/v1/safety/separation/{child_id}/resolve" in paths
    assert "post" in paths["/api/v1/safety/separation/{child_id}/resolve"]

def test_connected_state_no_separation():
    """Test when band is connected and close by, no separation is detected."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Caregiver very close (within 10 meters)
    res = client.get(
        "/api/v1/safety/separation/child-leo-1?caregiver_lat=37.7750&caregiver_lon=-122.4195",
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["is_separated"] is False
    assert data["separation_reason"] is None
    assert data["severity"] == "normal"
    assert data["is_band_connected"] is True
    assert data["alert_created"] is False

def test_disconnected_band_trigger():
    """Test separation triggered when wearable band is disconnected."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Mark band as disconnected
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.connection_status = "disconnected"
        band.is_online = False
        db.commit()
    finally:
        db.close()

    res = client.get("/api/v1/safety/separation/child-leo-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_separated"] is True
    assert data["separation_reason"] == "band_disconnected"
    assert data["is_band_connected"] is False
    assert data["alert_created"] is True
    assert data["active_event_id"] is not None

    # Verify child status and event in DB
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        assert child.current_status == "separation_alert"

        event = db.query(SafetyEvent).filter(SafetyEvent.id == data["active_event_id"]).first()
        assert event is not None
        assert event.event_type == "separation_alert"
        assert event.is_acknowledged is False
    finally:
        db.close()

def test_heartbeat_timeout_trigger():
    """Test separation triggered when device heartbeat times out."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Set last_seen to 10 minutes ago
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.connection_status = "connected"
        band.is_online = True
        band.last_seen = datetime.now(timezone.utc) - timedelta(minutes=10)
        band.last_ping_at = band.last_seen
        db.commit()
    finally:
        db.close()

    res = client.get("/api/v1/safety/separation/child-leo-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_separated"] is True
    assert data["separation_reason"] == "heartbeat_timeout"
    assert data["severity"] == "critical"
    assert data["time_since_last_heartbeat_seconds"] > 120

def test_distance_threshold_trigger():
    """Test separation triggered when caregiver distance exceeds threshold."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Child location is 37.7750, -122.4195. Caregiver at 37.7850, -122.4195 (~1.1 km away)
    res = client.get(
        "/api/v1/safety/separation/child-leo-1?caregiver_lat=37.7850&caregiver_lon=-122.4195&threshold_meters=50",
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_separated"] is True
    assert data["separation_reason"] == "distance_exceeded"
    assert data["distance_meters"] > 50.0
    assert data["severity"] == "critical"

def test_last_known_location_saved_in_event():
    """Test last known location is captured in the separation event."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Disconnect band to create event
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.connection_status = "disconnected"
        band.is_online = False
        db.commit()
    finally:
        db.close()

    res = client.get("/api/v1/safety/separation/child-leo-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["last_known_location"] is not None
    assert "latitude" in data["last_known_location"]
    assert "longitude" in data["last_known_location"]
    assert "timestamp" in data["last_known_location"]

def test_resolution_resets_child_status_to_safe():
    """Test resolving separation events marks them acknowledged and restores status to safe."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger separation
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.connection_status = "disconnected"
        band.is_online = False
        db.commit()
    finally:
        db.close()

    client.get("/api/v1/safety/separation/child-leo-1", headers=headers)

    # Resolve separation
    resolve_res = client.post("/api/v1/safety/separation/child-leo-1/resolve", headers=headers)
    assert resolve_res.status_code == 200
    resolve_data = resolve_res.json()
    assert resolve_data["resolved"] is True
    assert resolve_data["current_status"] == "safe"
    assert resolve_data["resolved_events_count"] >= 1

    # Verify DB state
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        assert child.current_status == "safe"

        unack = (
            db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == "child-leo-1", SafetyEvent.is_acknowledged == False)
            .count()
        )
        assert unack == 0
    finally:
        db.close()

def test_separation_status_endpoint():
    """Test GET /api/v1/safety/separation/{child_id}/status."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/separation/child-leo-1/status", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert "is_separated" in data
    assert "current_status" in data
    assert "threshold_meters" in data

def test_unauthenticated_requests():
    """Test unauthenticated requests return 401 Unauthorized."""
    assert client.get("/api/v1/safety/separation/child-leo-1").status_code == 401
    assert client.get("/api/v1/safety/separation/child-leo-1/status").status_code == 401
    assert client.post("/api/v1/safety/separation/child-leo-1/resolve").status_code == 401

def test_unauthorized_caregiver_access():
    """Test David cannot evaluate or resolve separation for Sarah's child Leo (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    assert client.get("/api/v1/safety/separation/child-leo-1", headers=headers).status_code == 403
    assert client.get("/api/v1/safety/separation/child-leo-1/status", headers=headers).status_code == 403
    assert client.post("/api/v1/safety/separation/child-leo-1/resolve", headers=headers).status_code == 403

def test_non_existent_child_404():
    """Test non-existent child returns 404 Not Found."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/safety/separation/child-non-existent-999", headers=headers).status_code == 404
    assert client.get("/api/v1/safety/separation/child-non-existent-999/status", headers=headers).status_code == 404
    assert client.post("/api/v1/safety/separation/child-non-existent-999/resolve", headers=headers).status_code == 404
