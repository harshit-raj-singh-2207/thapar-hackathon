import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.device import Device
from app.models.child import Child

client = TestClient(app)

def get_sarah_token():
    """Sarah is the caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def get_david_token():
    """David is a verified caregiver, but NOT caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def test_openapi_docs_band_registration():
    """Verify that all GPS band endpoints appear in OpenAPI docs."""
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    assert "/api/v1/safety/bands" in paths, "POST /api/v1/safety/bands is not in OpenAPI"
    assert "post" in paths["/api/v1/safety/bands"], "POST method missing on /api/v1/safety/bands"

    assert "/api/v1/safety/bands/{identifier}" in paths, "GET /api/v1/safety/bands/{identifier} is not in OpenAPI"
    assert "get" in paths["/api/v1/safety/bands/{identifier}"], "GET method missing on /api/v1/safety/bands/{identifier}"

    assert "/api/v1/safety/bands/{band_id}" in paths, "PATCH/DELETE /api/v1/safety/bands/{band_id} is not in OpenAPI"
    assert "patch" in paths["/api/v1/safety/bands/{band_id}"], "PATCH method missing on /api/v1/safety/bands/{band_id}"
    assert "delete" in paths["/api/v1/safety/bands/{band_id}"], "DELETE method missing on /api/v1/safety/bands/{band_id}"

    assert "/api/v1/safety/bands/{band_id}/status" in paths, "GET /api/v1/safety/bands/{band_id}/status is not in OpenAPI"
    assert "get" in paths["/api/v1/safety/bands/{band_id}/status"], "GET method missing on /api/v1/safety/bands/{band_id}/status"

def test_register_band_success():
    """Test registering a new GPS band for a child with full attributes."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "device_identifier": "NIVARA-BAND-NEW-001",
        "device_name": "Leo Smart SafeBand V2",
        "device_type": "gps_band",
        "child_id": "child-leo-1",
        "battery_level": 95,
        "connection_status": "online",
        "gps_status": "active",
        "firmware_version": "v2.0.1"
    }

    # First delete seeded band if child-leo-1 already has dev-band-leo-1
    db = SessionLocal()
    try:
        db.query(Device).filter(Device.child_id == "child-leo-1").delete()
        db.commit()
    finally:
        db.close()

    res = client.post("/api/v1/safety/bands", json=payload, headers=headers)
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}: {res.text}"

    data = res.json()
    assert data["device_identifier"] == "NIVARA-BAND-NEW-001"
    assert data["serial_number"] == "NIVARA-BAND-NEW-001"
    assert data["child_id"] == "child-leo-1"
    assert data["battery_level"] == 95
    assert data["connection_status"] == "online"
    assert data["gps_status"] == "active"
    assert data["is_online"] is True
    assert "id" in data
    assert "last_seen" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify persistence directly in database
    db = SessionLocal()
    try:
        saved = db.query(Device).filter(Device.id == data["id"]).first()
        assert saved is not None
        assert saved.device_identifier == "NIVARA-BAND-NEW-001"
        assert saved.battery_level == 95
        assert saved.child_id == "child-leo-1"
    finally:
        db.close()

def test_prevent_duplicate_device_identifier():
    """Test duplicate device identifier / serial number is rejected with 400."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # The seeded band has serial_number 'NIVARA-BAND-LEO-001'
    payload = {
        "device_identifier": "NIVARA-BAND-LEO-001",
        "device_name": "Duplicate Band",
    }
    res = client.post("/api/v1/safety/bands", json=payload, headers=headers)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()

def test_prevent_duplicate_band_assignment_to_child():
    """Test assigning a second active band to the same child is rejected with 400."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Leo already has dev-band-leo-1 seeded
    payload = {
        "device_identifier": "NIVARA-BAND-ANOTHER-002",
        "device_name": "Another Band",
        "child_id": "child-leo-1",
    }
    res = client.post("/api/v1/safety/bands", json=payload, headers=headers)
    assert res.status_code == 400
    assert "already has" in res.json()["detail"].lower()

def test_get_child_band():
    """Test fetching child's band using GET /api/v1/safety/bands/{child_id}."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/bands/child-leo-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["id"] == "dev-band-leo-1"
    assert data["device_identifier"] == "NIVARA-BAND-LEO-001"
    assert data["battery_level"] == 92
    assert data["connection_status"] == "online"
    assert data["gps_status"] == "active"

def test_get_band_by_band_id():
    """Test fetching band details using GET /api/v1/safety/bands/{band_id}."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/bands/dev-band-leo-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "dev-band-leo-1"
    assert data["device_name"] == "NIVARA Smart SafeBand"
    assert data["serial_number"] == "NIVARA-BAND-LEO-001"
    assert data["is_online"] is True

def test_get_band_status():
    """Test GET /api/v1/safety/bands/{band_id}/status."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/bands/dev-band-leo-1/status", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["band_id"] == "dev-band-leo-1"
    assert data["device_identifier"] == "NIVARA-BAND-LEO-001"
    assert data["child_id"] == "child-leo-1"
    assert data["connection_status"] == "online"
    assert data["is_online"] is True
    assert data["battery_level"] == 92
    assert data["gps_status"] == "active"
    assert "last_seen" in data

def test_update_band_patch():
    """Test PATCH /api/v1/safety/bands/{band_id}."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "battery_level": 78,
        "connection_status": "offline",
        "gps_status": "standby",
        "device_name": "Updated SafeBand"
    }

    res = client.patch("/api/v1/safety/bands/dev-band-leo-1", json=update_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["battery_level"] == 78
    assert data["connection_status"] == "offline"
    assert data["is_online"] is False
    assert data["gps_status"] == "standby"
    assert data["device_name"] == "Updated SafeBand"

    # Verify directly in DB
    db = SessionLocal()
    try:
        saved = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        assert saved.battery_level == 78
        assert saved.connection_status == "offline"
        assert saved.is_online is False
        assert saved.gps_status == "standby"
    finally:
        db.close()

def test_remove_band_delete():
    """Test DELETE /api/v1/safety/bands/{band_id}."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.delete("/api/v1/safety/bands/dev-band-leo-1", headers=headers)
    assert res.status_code == 200
    assert "removed successfully" in res.json()["message"]

    # Verify deleted from DB
    db = SessionLocal()
    try:
        saved = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        assert saved is None
    finally:
        db.close()

    # GET after delete should return 404
    get_res = client.get("/api/v1/safety/bands/dev-band-leo-1", headers=headers)
    assert get_res.status_code == 404

def test_unauthenticated_requests():
    """Test requests without token return 401 Unauthorized."""
    assert client.post("/api/v1/safety/bands", json={"device_identifier": "TEST-1"}).status_code == 401
    assert client.get("/api/v1/safety/bands/child-leo-1").status_code == 401
    assert client.get("/api/v1/safety/bands/dev-band-leo-1").status_code == 401
    assert client.get("/api/v1/safety/bands/dev-band-leo-1/status").status_code == 401
    assert client.patch("/api/v1/safety/bands/dev-band-leo-1", json={"battery_level": 50}).status_code == 401
    assert client.delete("/api/v1/safety/bands/dev-band-leo-1").status_code == 401

def test_unauthorized_caregiver_access():
    """Test David cannot view, update, or remove Sarah's child's band (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # Attempt to view Leo's band
    res_get = client.get("/api/v1/safety/bands/child-leo-1", headers=headers)
    assert res_get.status_code == 403

    # Attempt to view Leo's band status
    res_status = client.get("/api/v1/safety/bands/dev-band-leo-1/status", headers=headers)
    assert res_status.status_code == 403

    # Attempt to update Leo's band
    res_patch = client.patch("/api/v1/safety/bands/dev-band-leo-1", json={"battery_level": 20}, headers=headers)
    assert res_patch.status_code == 403

    # Attempt to delete Leo's band
    res_del = client.delete("/api/v1/safety/bands/dev-band-leo-1", headers=headers)
    assert res_del.status_code == 403

    # Attempt to assign Leo to a new band
    res_reg = client.post(
        "/api/v1/safety/bands",
        json={"device_identifier": "DAVID-HACK-001", "child_id": "child-leo-1"},
        headers=headers
    )
    assert res_reg.status_code == 403

def test_invalid_band_or_child_id():
    """Test non-existent band ID and child ID return 404."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/safety/bands/non-existent-id", headers=headers).status_code == 404
    assert client.get("/api/v1/safety/bands/non-existent-id/status", headers=headers).status_code == 404
    assert client.patch("/api/v1/safety/bands/non-existent-id", json={"battery_level": 50}, headers=headers).status_code == 404
    assert client.delete("/api/v1/safety/bands/non-existent-id", headers=headers).status_code == 404
