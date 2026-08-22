import sys
import os
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.device import Device
from app.models.child import Child

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

def test_openapi_connection_endpoints():
    """Verify all 5 connection endpoints are registered in OpenAPI paths."""
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    assert "/api/v1/safety/bands/{band_id}/pair" in paths
    assert "post" in paths["/api/v1/safety/bands/{band_id}/pair"]

    assert "/api/v1/safety/bands/{band_id}/unpair" in paths
    assert "post" in paths["/api/v1/safety/bands/{band_id}/unpair"]

    assert "/api/v1/safety/bands/{band_id}/heartbeat" in paths
    assert "post" in paths["/api/v1/safety/bands/{band_id}/heartbeat"]

    assert "/api/v1/safety/bands/{band_id}/connection" in paths
    assert "get" in paths["/api/v1/safety/bands/{band_id}/connection"]

    assert "/api/v1/safety/bands/{band_id}/sync" in paths
    assert "post" in paths["/api/v1/safety/bands/{band_id}/sync"]

def test_pair_and_unpair_band_flow():
    """Test full pair and unpair workflow."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Register an unassigned band
    reg_res = client.post(
        "/api/v1/safety/bands",
        json={"device_identifier": "NIVARA-BAND-UNASSIGNED-1", "device_name": "Free Band"},
        headers=headers
    )
    assert reg_res.status_code == 201
    band_id = reg_res.json()["id"]

    # 2. First unpair existing seeded band dev-band-leo-1 from child-leo-1
    unpair_seeded = client.post("/api/v1/safety/bands/dev-band-leo-1/unpair", headers=headers)
    assert unpair_seeded.status_code == 200
    assert unpair_seeded.json()["is_paired"] is False
    assert unpair_seeded.json()["connection_status"] == "disconnected"

    # 3. Pair new band to child-leo-1
    pair_res = client.post(
        f"/api/v1/safety/bands/{band_id}/pair",
        json={"child_id": "child-leo-1"},
        headers=headers
    )
    assert pair_res.status_code == 200
    pair_data = pair_res.json()
    assert pair_data["band_id"] == band_id
    assert pair_data["child_id"] == "child-leo-1"
    assert pair_data["connection_status"] == "connected"
    assert pair_data["is_paired"] is True

    # 4. Check connection status
    conn_res = client.get(f"/api/v1/safety/bands/{band_id}/connection", headers=headers)
    assert conn_res.status_code == 200
    conn_data = conn_res.json()
    assert conn_data["is_paired"] is True
    assert conn_data["child_id"] == "child-leo-1"
    assert conn_data["connection_status"] == "connected"
    assert conn_data["is_stale"] is False

    # 5. Unpair band
    unpair_res = client.post(f"/api/v1/safety/bands/{band_id}/unpair", headers=headers)
    assert unpair_res.status_code == 200
    unpair_data = unpair_res.json()
    assert unpair_data["is_paired"] is False
    assert unpair_data["connection_status"] == "disconnected"

def test_prevent_duplicate_pairing():
    """Test duplicate pairing validation."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # dev-band-leo-1 is already paired to child-leo-1 by default
    res = client.post(
        "/api/v1/safety/bands/dev-band-leo-1/pair",
        json={"child_id": "child-leo-1"},
        headers=headers
    )
    assert res.status_code == 400
    assert "already paired" in res.json()["detail"].lower()

def test_heartbeat_updates_state_and_last_seen():
    """Test phone ↔ band heartbeat telemetry ping."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    heartbeat_payload = {
        "battery_level": 84,
        "connection_status": "connected",
        "is_online": True,
        "gps_status": "active",
        "rssi": -68,
        "firmware_version": "v1.3.0"
    }

    res = client.post(
        "/api/v1/safety/bands/dev-band-leo-1/heartbeat",
        json=heartbeat_payload,
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["band_id"] == "dev-band-leo-1"
    assert data["battery_level"] == 84
    assert data["connection_status"] == "connected"
    assert data["gps_status"] == "active"
    assert data["is_online"] is True
    assert data["is_stale"] is False
    assert "last_seen" in data

    # Verify directly in DB
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        assert band.battery_level == 84
        assert band.connection_status == "connected"
        assert band.firmware_version == "v1.3.0"
    finally:
        db.close()

def test_invalid_heartbeat_battery_bounds():
    """Test heartbeat with invalid battery levels returns 422."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Battery > 100
    res_high = client.post(
        "/api/v1/safety/bands/dev-band-leo-1/heartbeat",
        json={"battery_level": 105},
        headers=headers
    )
    assert res_high.status_code == 422

    # Battery < 0
    res_low = client.post(
        "/api/v1/safety/bands/dev-band-leo-1/heartbeat",
        json={"battery_level": -10},
        headers=headers
    )
    assert res_low.status_code == 422

def test_get_connection_status_and_stale_detection():
    """Test getting connection status and stale device detection."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Set last_seen to 10 minutes ago in DB
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.last_seen = datetime.now(timezone.utc) - timedelta(minutes=10)
        db.commit()
    finally:
        db.close()

    res = client.get("/api/v1/safety/bands/dev-band-leo-1/connection", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["band_id"] == "dev-band-leo-1"
    assert data["is_stale"] is True
    assert data["connection_status"] == "stale"

def test_sync_band_success():
    """Test POST /api/v1/safety/bands/{band_id}/sync."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    sync_payload = {
        "sync_mode": "full",
        "settings": {
            "tracking_interval_seconds": 15,
            "power_saving_mode": False
        }
    }

    res = client.post(
        "/api/v1/safety/bands/dev-band-leo-1/sync",
        json=sync_payload,
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["band_id"] == "dev-band-leo-1"
    assert data["synced"] is True
    assert data["settings"]["tracking_interval_seconds"] == 15
    assert "server_timestamp" in data

def test_unauthenticated_requests():
    """Test unauthenticated requests return 401 Unauthorized."""
    assert client.post("/api/v1/safety/bands/dev-band-leo-1/pair", json={"child_id": "child-leo-1"}).status_code == 401
    assert client.post("/api/v1/safety/bands/dev-band-leo-1/unpair").status_code == 401
    assert client.post("/api/v1/safety/bands/dev-band-leo-1/heartbeat", json={"battery_level": 50}).status_code == 401
    assert client.get("/api/v1/safety/bands/dev-band-leo-1/connection").status_code == 401
    assert client.post("/api/v1/safety/bands/dev-band-leo-1/sync", json={}).status_code == 401

def test_unauthorized_caregiver_access():
    """Test David cannot pair, unpair, heartbeat, or sync Sarah's child's band (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # Attempt to pair Sarah's child
    assert client.post(
        "/api/v1/safety/bands/dev-band-leo-1/pair",
        json={"child_id": "child-leo-1"},
        headers=headers
    ).status_code == 403

    # Attempt to unpair Leo's band
    assert client.post("/api/v1/safety/bands/dev-band-leo-1/unpair", headers=headers).status_code == 403

    # Attempt heartbeat on Leo's band
    assert client.post(
        "/api/v1/safety/bands/dev-band-leo-1/heartbeat",
        json={"battery_level": 50},
        headers=headers
    ).status_code == 403

    # Attempt connection check on Leo's band
    assert client.get("/api/v1/safety/bands/dev-band-leo-1/connection", headers=headers).status_code == 403

    # Attempt sync on Leo's band
    assert client.post("/api/v1/safety/bands/dev-band-leo-1/sync", json={}, headers=headers).status_code == 403

def test_invalid_band_404():
    """Test invalid band ID returns 404 Not Found."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/api/v1/safety/bands/dev-fake-999/pair", json={"child_id": "child-leo-1"}, headers=headers).status_code == 404
    assert client.post("/api/v1/safety/bands/dev-fake-999/unpair", headers=headers).status_code == 404
    assert client.post("/api/v1/safety/bands/dev-fake-999/heartbeat", json={"battery_level": 50}, headers=headers).status_code == 404
    assert client.get("/api/v1/safety/bands/dev-fake-999/connection", headers=headers).status_code == 404
    assert client.post("/api/v1/safety/bands/dev-fake-999/sync", json={}, headers=headers).status_code == 404
