import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.child import Child
from app.models.safe_zone import SafeZone
from app.models.safety_event import SafetyEvent
from app.models.emergency import EmergencyAlert

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

# 1. Create Safe Zone
def test_create_safe_zone_success():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "name": "Leo's Park Safe Zone",
        "latitude": 37.7760,
        "longitude": -122.4180,
        "radius": 200.0,
        "active": True
    }
    res = client.post("/api/v1/safety/safe-zones", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Leo's Park Safe Zone"
    assert data["child_id"] == "child-leo-1"
    assert data["latitude"] == 37.7760
    assert data["longitude"] == -122.4180
    assert data["radius"] == 200.0
    assert data["active"] is True
    assert "id" in data

# 2. Get Child's Safe Zones
def test_get_child_safe_zones():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve all safe zones for child-leo-1
    res = client.get("/api/v1/safety/safe-zones/child-leo-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(z["id"] == "sz-home-1" for z in data)

# 3. Get Single Safe Zone
def test_get_single_safe_zone():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/safe-zones/sz-home-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "sz-home-1"
    assert "Home" in data["name"]
    assert data["child_id"] == "child-leo-1"

# 4. Update Safe Zone (PATCH)
def test_update_safe_zone_patch():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "name": "Home Sanctuary V2",
        "radius": 180.0,
        "active": True
    }
    res = client.patch("/api/v1/safety/safe-zones/sz-home-1", json=update_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "sz-home-1"
    assert data["name"] == "Home Sanctuary V2"
    assert data["radius"] == 180.0

# 5. Delete Safe Zone
def test_delete_safe_zone():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create temporary zone
    create_res = client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "Temp Zone", "latitude": 37.7750, "longitude": -122.4195, "radius": 50.0},
        headers=headers
    )
    assert create_res.status_code == 201
    temp_id = create_res.json()["id"]

    # Delete temporary zone
    del_res = client.delete(f"/api/v1/safety/safe-zones/{temp_id}", headers=headers)
    assert del_res.status_code == 200

    # Ensure it's deleted
    get_res = client.get(f"/api/v1/safety/safe-zones/{temp_id}", headers=headers)
    assert get_res.status_code == 404

# 6. Invalid Latitude (< -90 or > 90)
def test_invalid_latitude():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res_high = client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "Bad Lat", "latitude": 95.0, "longitude": -122.4195, "radius": 100.0},
        headers=headers
    )
    assert res_high.status_code == 422

    res_low = client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "Bad Lat", "latitude": -95.0, "longitude": -122.4195, "radius": 100.0},
        headers=headers
    )
    assert res_low.status_code == 422

# 7. Invalid Longitude (< -180 or > 180)
def test_invalid_longitude():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res_high = client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "Bad Lon", "latitude": 37.7750, "longitude": 185.0, "radius": 100.0},
        headers=headers
    )
    assert res_high.status_code == 422

    res_low = client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "Bad Lon", "latitude": 37.7750, "longitude": -185.0, "radius": 100.0},
        headers=headers
    )
    assert res_low.status_code == 422

# 8. Invalid Radius (<= 0)
def test_invalid_radius():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res_zero = client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "Zero Radius", "latitude": 37.7750, "longitude": -122.4195, "radius": 0.0},
        headers=headers
    )
    assert res_zero.status_code == 422

    res_neg = client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "Neg Radius", "latitude": 37.7750, "longitude": -122.4195, "radius": -50.0},
        headers=headers
    )
    assert res_neg.status_code == 422

# 9. Child inside safe zone
def test_child_inside_safe_zone():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # sz-home-1 is at 37.774929, -122.419416 with radius 150m
    # Testing location very close to center (approx 5m away)
    res = client.get(
        "/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.774930&longitude=-122.419418",
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_inside_safe_zone"] is True
    assert data["is_inside"] is True
    assert data["active_zone_id"] == "sz-home-1"
    assert data["status"] == "safe"

# 10. Child outside safe zone
def test_child_outside_safe_zone():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Testing location far away (> 1km away)
    res = client.get(
        "/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.7950&longitude=-122.419416",
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_inside_safe_zone"] is False
    assert data["is_inside"] is False
    assert data["active_zone_id"] is None
    assert data["status"] == "out_of_bounds"

# 11. Outside → Inside entry detection
def test_entry_detection_outside_to_inside():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Set child status to out_of_bounds
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        child.current_status = "out_of_bounds"
        db.commit()
    finally:
        db.close()

    # Step 2: Check inside coordinate -> triggers entry event
    res = client.get(
        "/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.774929&longitude=-122.419416&create_events=true",
        headers=headers
    )
    assert res.status_code == 200
    assert res.json()["is_inside"] is True
    assert res.json()["status"] == "safe"

    # Verify geofence_entry event created
    db = SessionLocal()
    try:
        event = (
            db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == "child-leo-1", SafetyEvent.event_type == "geofence_entry")
            .order_by(SafetyEvent.created_at.desc())
            .first()
        )
        assert event is not None
        assert event.severity == "info"
        assert "Safe Zone Return" in event.title
    finally:
        db.close()

# 12. Inside → Outside exit detection
def test_exit_detection_inside_to_outside():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Set child status to safe
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        child.current_status = "safe"
        db.commit()
    finally:
        db.close()

    # Step 2: Check outside coordinate -> triggers exit event
    res = client.get(
        "/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.7950&longitude=-122.419416&create_events=true",
        headers=headers
    )
    assert res.status_code == 200
    assert res.json()["is_inside"] is False
    assert res.json()["status"] == "out_of_bounds"

    # Verify geofence_exit event created
    db = SessionLocal()
    try:
        event = (
            db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == "child-leo-1", SafetyEvent.event_type == "geofence_exit")
            .order_by(SafetyEvent.created_at.desc())
            .first()
        )
        assert event is not None
        assert event.severity == "critical"
        assert "Geofence Exit" in event.title or "Geofence Breach" in event.title
    finally:
        db.close()

# 13. Safety event creation check
def test_safety_event_details():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger exit event
    client.get(
        "/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.7950&longitude=-122.419416&create_events=true",
        headers=headers
    )

    db = SessionLocal()
    try:
        event = (
            db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == "child-leo-1", SafetyEvent.event_type == "geofence_exit")
            .order_by(SafetyEvent.created_at.desc())
            .first()
        )
        assert event is not None
        assert event.latitude == 37.7950
        assert event.longitude == -122.419416
        assert event.is_acknowledged is False
    finally:
        db.close()

# 14. Caregiver alert creation check
def test_caregiver_alert_creation():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Reset child status to safe
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        child.current_status = "safe"
        db.commit()
    finally:
        db.close()

    # Trigger exit event
    client.get(
        "/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.7950&longitude=-122.419416&create_events=true",
        headers=headers
    )

    db = SessionLocal()
    try:
        alert = (
            db.query(EmergencyAlert)
            .filter(EmergencyAlert.child_id == "child-leo-1")
            .order_by(EmergencyAlert.created_at.desc())
            .first()
        )
        assert alert is not None
        assert alert.triggered_by == "geofence_breach"
        assert "GEOFENCE" in alert.message.upper()
    finally:
        db.close()

# 15. Unauthorized caregiver (403 Forbidden)
def test_unauthorized_caregiver_access():
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # David tries to create safe zone for Leo
    assert client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-leo-1", "name": "David's zone", "latitude": 37.7750, "longitude": -122.4195, "radius": 100.0},
        headers=headers
    ).status_code == 403

    # David tries to get Leo's safe zones
    assert client.get("/api/v1/safety/safe-zones/child-leo-1", headers=headers).status_code == 403

    # David tries to get sz-home-1 (belongs to Leo)
    assert client.get("/api/v1/safety/safe-zones/sz-home-1", headers=headers).status_code == 403

    # David tries to update sz-home-1
    assert client.patch(
        "/api/v1/safety/safe-zones/sz-home-1",
        json={"name": "Hacked Zone"},
        headers=headers
    ).status_code == 403

    # David tries to delete sz-home-1
    assert client.delete("/api/v1/safety/safe-zones/sz-home-1", headers=headers).status_code == 403

# 16. Unauthenticated request (401 Unauthorized)
def test_unauthenticated_requests():
    assert client.post("/api/v1/safety/safe-zones", json={"child_id": "child-leo-1", "name": "No Auth", "latitude": 37.7750, "longitude": -122.4195, "radius": 100.0}).status_code == 401
    assert client.get("/api/v1/safety/safe-zones/child-leo-1").status_code == 401
    assert client.get("/api/v1/safety/safe-zones/sz-home-1").status_code == 401
    assert client.patch("/api/v1/safety/safe-zones/sz-home-1", json={"name": "No Auth"}).status_code == 401
    assert client.delete("/api/v1/safety/safe-zones/sz-home-1").status_code == 401

# 17. Non-existent child (404 Not Found)
def test_non_existent_child_404():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post(
        "/api/v1/safety/safe-zones",
        json={"child_id": "child-non-existent-999", "name": "Fake Child Zone", "latitude": 37.7750, "longitude": -122.4195, "radius": 100.0},
        headers=headers
    ).status_code == 404

    assert client.get("/api/v1/safety/safe-zones/child-non-existent-999", headers=headers).status_code == 404

# 18. Non-existent safe zone (404 Not Found)
def test_non_existent_safe_zone_404():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/safety/safe-zones/sz-non-existent-999", headers=headers).status_code == 404
    assert client.patch("/api/v1/safety/safe-zones/sz-non-existent-999", json={"name": "Fake Zone"}, headers=headers).status_code == 404
    assert client.delete("/api/v1/safety/safe-zones/sz-non-existent-999", headers=headers).status_code == 404
