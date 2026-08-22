import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.child import Child
from app.models.location import Location
from app.models.emergency import EmergencyAlert
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

# 1. SOS Trigger
def test_sos_trigger_success():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "message": "Immediate SOS button activated",
        "triggered_by": "sos_button"
    }
    res = client.post("/api/v1/safety/emergency/sos", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["status"] == "active"
    assert data["severity"] == "critical"
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["location_available"] is True
    assert "id" in data

# 2. Authentication Required
def test_unauthenticated_requests():
    assert client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}).status_code == 401
    assert client.get("/api/v1/safety/emergency/child-leo-1").status_code == 401
    assert client.get("/api/v1/safety/emergency/emg-fake/details").status_code == 401
    assert client.post("/api/v1/safety/emergency/emg-fake/resolve").status_code == 401

# 3. Authorized Caregiver SOS Access
def test_authorized_caregiver_access():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201
    emg_id = res.json()["id"]

    # Caregiver can view details
    details_res = client.get(f"/api/v1/safety/emergency/{emg_id}/details", headers=headers)
    assert details_res.status_code == 200
    assert details_res.json()["id"] == emg_id

# 4. Unauthorized Caregiver Access (403)
def test_unauthorized_caregiver_access():
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # David tries to trigger SOS on Sarah's child Leo
    assert client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers).status_code == 403

    # David tries to get emergency status of Leo
    assert client.get("/api/v1/safety/emergency/child-leo-1", headers=headers).status_code == 403

# 5. Non-existent Child (404)
def test_non_existent_child_404():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-non-existent-999"}, headers=headers).status_code == 404
    assert client.get("/api/v1/safety/emergency/child-non-existent-999", headers=headers).status_code == 404

# 6. Current Location Captured from Request
def test_current_location_captured():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "latitude": 37.7812,
        "longitude": -122.4001,
        "message": "SOS with exact live coords"
    }
    res = client.post("/api/v1/safety/emergency/sos", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["latitude"] == 37.7812
    assert data["longitude"] == -122.4001
    assert data["location_available"] is True

# 7. Last Known Location Fallback
def test_last_known_location_fallback():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Child has location in database (seeded: 37.7750, -122.4195)
    # Trigger SOS without coordinates in payload
    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["latitude"] is not None
    assert data["longitude"] is not None
    assert data["location_available"] is True

# 8. No Location Available (Graceful None Handling)
def test_no_location_available_handling():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Delete all locations for child-leo-1 from DB
    db = SessionLocal()
    try:
        db.query(Location).filter(Location.child_id == "child-leo-1").delete()
        db.commit()
    finally:
        db.close()

    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["latitude"] is None
    assert data["longitude"] is None
    assert data["location_available"] is False
    assert "Location Unavailable" in data["message"]

# 9. Emergency Event Creation in DB
def test_emergency_event_creation():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201

    db = SessionLocal()
    try:
        event = (
            db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == "child-leo-1", SafetyEvent.event_type.in_(["SOS", "sos_triggered"]))
            .order_by(SafetyEvent.created_at.desc())
            .first()
        )
        assert event is not None
        assert event.severity == "critical"
        assert event.is_acknowledged is False
    finally:
        db.close()

# 10. Emergency Alert Creation in DB
def test_emergency_alert_creation():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201
    emg_id = res.json()["id"]

    db = SessionLocal()
    try:
        alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == emg_id).first()
        assert alert is not None
        assert alert.status == "active"
        assert alert.severity == "critical"
    finally:
        db.close()

# 11. Active Emergency Retrieval
def test_active_emergency_retrieval():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201
    emg_id = res.json()["id"]

    status_res = client.get("/api/v1/safety/emergency/child-leo-1", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["id"] == emg_id
    assert status_res.json()["status"] == "active"

# 12. Duplicate Active SOS Prevention (409 Conflict)
def test_duplicate_active_sos_prevention():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First SOS succeeds
    res1 = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res1.status_code == 201

    # Second SOS while first is active returns 409 Conflict
    res2 = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res2.status_code == 409
    assert "already has an active emergency" in res2.json()["detail"].lower()

# 13. Emergency Details Endpoint
def test_emergency_details():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1", "message": "Help needed immediately"}, headers=headers)
    assert res.status_code == 201
    emg_id = res.json()["id"]

    details_res = client.get(f"/api/v1/safety/emergency/{emg_id}/details", headers=headers)
    assert details_res.status_code == 200
    detail_data = details_res.json()
    assert detail_data["id"] == emg_id
    assert detail_data["child_id"] == "child-leo-1"
    assert detail_data["status"] == "active"
    assert "message" in detail_data

# 14. Emergency Resolution
def test_emergency_resolution():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger SOS
    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201
    emg_id = res.json()["id"]

    # Verify child status is emergency
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        assert child.current_status == "emergency"
    finally:
        db.close()

    # Resolve emergency
    resolve_res = client.post(
        f"/api/v1/safety/emergency/{emg_id}/resolve",
        json={"status": "resolved", "resolution_notes": "Child found safe with teacher."},
        headers=headers
    )
    assert resolve_res.status_code == 200
    resolve_data = resolve_res.json()
    assert resolve_data["status"] == "resolved"
    assert resolve_data["resolved_at"] is not None

    # Verify child status restored to safe in DB
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        assert child.current_status == "safe"
    finally:
        db.close()

# 15. Already Resolved Emergency (400 Bad Request)
def test_already_resolved_emergency_rejection():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger & resolve
    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert res.status_code == 201
    emg_id = res.json()["id"]

    res_resolve1 = client.post(f"/api/v1/safety/emergency/{emg_id}/resolve", json={}, headers=headers)
    assert res_resolve1.status_code == 200

    # Attempt resolving again -> returns 400
    res_resolve2 = client.post(f"/api/v1/safety/emergency/{emg_id}/resolve", json={}, headers=headers)
    assert res_resolve2.status_code == 400
    assert "already resolved" in res_resolve2.json()["detail"].lower()

# 16. Non-existent Emergency (404 Not Found)
def test_non_existent_emergency_404():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/safety/emergency/emg-non-existent-999/details", headers=headers).status_code == 404
    assert client.post("/api/v1/safety/emergency/emg-non-existent-999/resolve", json={}, headers=headers).status_code == 404
