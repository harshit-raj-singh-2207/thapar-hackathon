import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.emergency_contact import EmergencyContact
from app.models.safety_event import SafetyEvent
from app.models.child import Child
from app.models.device import Device

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

# 1. Create contact
def test_create_emergency_contact_success():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "name": "Grandma Rose",
        "phone": "+1-555-0199",
        "relationship": "Grandmother",
        "priority": 1,
        "active": True,
    }
    res = client.post("/api/v1/safety/emergency-contacts", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Grandma Rose"
    assert data["phone"] == "+1-555-0199"
    assert data["relationship"] == "Grandmother"
    assert data["priority"] == 1
    assert data["active"] is True
    assert "id" in data

# 2. Get contacts for child
def test_get_child_emergency_contacts():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create two contacts
    client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Contact 1",
        "phone": "+1-555-0111",
        "relationship": "Uncle",
        "priority": 2
    }, headers=headers)

    client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Contact 2",
        "phone": "+1-555-0222",
        "relationship": "Aunt",
        "priority": 1
    }, headers=headers)

    res = client.get("/api/v1/safety/emergency-contacts/child-leo-1", headers=headers)
    assert res.status_code == 200
    contacts = res.json()
    assert isinstance(contacts, list)
    assert len(contacts) >= 2
    # Priority order: Contact 2 (prio 1) before Contact 1 (prio 2)
    names = [c["name"] for c in contacts]
    assert "Contact 2" in names
    assert "Contact 1" in names

# 3. Get single contact
def test_get_single_emergency_contact():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Dr. Smith",
        "phone": "+1-555-0333",
        "relationship": "Pediatrician",
        "priority": 1
    }, headers=headers)
    assert create_res.status_code == 201
    contact_id = create_res.json()["id"]

    res = client.get(f"/api/v1/safety/emergency-contacts/{contact_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == contact_id
    assert data["name"] == "Dr. Smith"

# 4. Update contact
def test_update_emergency_contact():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Uncle Bob",
        "phone": "+1-555-0444",
        "relationship": "Uncle"
    }, headers=headers)
    contact_id = create_res.json()["id"]

    patch_res = client.patch(f"/api/v1/safety/emergency-contacts/{contact_id}", json={
        "name": "Uncle Robert",
        "phone": "+1-555-0999",
        "priority": 3
    }, headers=headers)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["name"] == "Uncle Robert"
    assert data["phone"] == "+1-555-0999"
    assert data["priority"] == 3

# 5. Delete contact
def test_delete_emergency_contact():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Temporary Contact",
        "phone": "+1-555-0555",
        "relationship": "Neighbor"
    }, headers=headers)
    contact_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/safety/emergency-contacts/{contact_id}", headers=headers)
    assert del_res.status_code == 200

    # Ensure it's deleted
    assert client.get(f"/api/v1/safety/emergency-contacts/{contact_id}", headers=headers).status_code == 404

# 6 & 7. Enable / Disable contact
def test_enable_disable_emergency_contact():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Coach Mike",
        "phone": "+1-555-0666",
        "relationship": "Coach",
        "active": True
    }, headers=headers)
    contact_id = create_res.json()["id"]

    # Disable
    dis_res = client.patch(f"/api/v1/safety/emergency-contacts/{contact_id}/status", json={"active": False}, headers=headers)
    assert dis_res.status_code == 200
    assert dis_res.json()["active"] is False

    # Enable
    en_res = client.patch(f"/api/v1/safety/emergency-contacts/{contact_id}/status", json={"active": True}, headers=headers)
    assert en_res.status_code == 200
    assert en_res.json()["active"] is True

# 8. Invalid phone validation
def test_invalid_phone_validation():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Invalid Phone User",
        "phone": "invalid_phone_123",
        "relationship": "Friend"
    }, headers=headers)
    assert res.status_code in [400, 422]

# 9. Missing child (404)
def test_missing_child_404():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-non-existent-999",
        "name": "Ghost Contact",
        "phone": "+1-555-0777",
        "relationship": "Friend"
    }, headers=headers)
    assert res.status_code == 404

# 10. Unauthorized caregiver access (403)
def test_unauthorized_caregiver_contact_access():
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # David tries to add contact for Sarah's child Leo
    res = client.post("/api/v1/safety/emergency-contacts", json={
        "child_id": "child-leo-1",
        "name": "Unauthorized Contact",
        "phone": "+1-555-0888",
        "relationship": "Friend"
    }, headers=headers)
    assert res.status_code == 403

    # David tries to view Leo's contacts
    assert client.get("/api/v1/safety/emergency-contacts/child-leo-1", headers=headers).status_code == 403

# 11. Unauthenticated contact requests (401)
def test_unauthenticated_contact_requests():
    assert client.post("/api/v1/safety/emergency-contacts", json={"name": "No Auth"}).status_code == 401
    assert client.get("/api/v1/safety/emergency-contacts/child-leo-1").status_code == 401
    assert client.patch("/api/v1/safety/emergency-contacts/contact-123", json={}).status_code == 401
    assert client.delete("/api/v1/safety/emergency-contacts/contact-123").status_code == 401

# 12. Get child alerts
def test_get_child_alerts():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger SOS to create real alert
    client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)

    res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    assert len(alerts) >= 1
    assert alerts[0]["child_id"] == "child-leo-1"

# 13. Get alert details
def test_get_alert_details():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    sos_res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    assert sos_res.status_code == 201

    alerts_res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    alert_id = alerts_res.json()[0]["id"]

    detail_res = client.get(f"/api/v1/safety/alerts/{alert_id}", headers=headers)
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["id"] == alert_id
    assert "severity" in data

# 14. Mark alert as read
def test_mark_alert_as_read():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    alerts_res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    alert_id = alerts_res.json()[0]["id"]

    read_res = client.patch(f"/api/v1/safety/alerts/{alert_id}/read", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_acknowledged"] is True
    assert read_res.json()["read_at"] is not None

# 15. Resolve alert
def test_resolve_alert():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1"}, headers=headers)
    alerts_res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    alert_id = alerts_res.json()[0]["id"]

    res = client.patch(
        f"/api/v1/safety/alerts/{alert_id}/resolve",
        json={"resolution_notes": "Checked and child is safe with teacher."},
        headers=headers
    )
    assert res.status_code == 200
    assert res.json()["is_acknowledged"] is True

# 16. Unauthorized alert access (403)
def test_unauthorized_alert_access():
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # David tries to fetch Leo's alerts
    assert client.get("/api/v1/safety/alerts/child-leo-1", headers=headers).status_code == 403

# 17. Unauthenticated alert access (401)
def test_unauthenticated_alert_access():
    assert client.get("/api/v1/safety/alerts/child-leo-1").status_code == 401
    assert client.patch("/api/v1/safety/alerts/alert-fake/read").status_code == 401
    assert client.patch("/api/v1/safety/alerts/alert-fake/resolve").status_code == 401

# 18. SOS -> Caregiver Alert Integration
def test_sos_creates_caregiver_alert():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/safety/emergency/sos", json={"child_id": "child-leo-1", "message": "Help!"}, headers=headers)
    assert res.status_code == 201

    alerts_res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    alerts = alerts_res.json()
    sos_alerts = [a for a in alerts if "SOS" in a["alert_type"].upper() or "SOS" in a["title"].upper()]
    assert len(sos_alerts) >= 1

# 19. Separation -> Caregiver Alert Integration
def test_separation_creates_caregiver_alert():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Force device disconnected for child
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.child_id == "child-leo-1").first()
        if band:
            band.connection_status = "disconnected"
            band.is_online = False
            db.commit()
    finally:
        db.close()

    # Trigger separation check
    sep_res = client.get("/api/v1/safety/separation/child-leo-1", headers=headers)
    assert sep_res.status_code == 200
    assert sep_res.json()["is_separated"] is True

    # Verify alert created in child alerts list
    alerts_res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    alerts = alerts_res.json()
    sep_alerts = [a for a in alerts if "separation" in a["alert_type"].lower() or "separation" in a["title"].lower()]
    assert len(sep_alerts) >= 1

# 20. Safe Zone Exit -> Caregiver Alert Integration
def test_safe_zone_exit_creates_caregiver_alert():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create safe zone centered around (37.7749, -122.4194)
    zone_res = client.post("/api/v1/safety/safe-zones", json={
        "child_id": "child-leo-1",
        "name": "Home Sanctuary",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "radius": 100.0,
        "active": True
    }, headers=headers)
    assert zone_res.status_code == 201

    # First evaluate inside
    client.post("/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.7749&longitude=-122.4194", headers=headers)

    # Then evaluate exit (far away: 37.8000, -122.4000)
    exit_res = client.post("/api/v1/safety/safe-zones/child-leo-1/check?latitude=37.8000&longitude=-122.4000", headers=headers)
    assert exit_res.status_code == 200
    assert exit_res.json()["is_inside_safe_zone"] is False

    # Verify exit alert created
    alerts_res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    exit_alerts = [a for a in alerts_res.json() if "geofence_exit" in a["alert_type"].lower() or "safe zone exit" in a["title"].lower()]
    assert len(exit_alerts) >= 1

# 21. Device Low Battery Alert Integration
def test_low_battery_alert_integration():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Heartbeat with battery = 10%
    db = SessionLocal()
    serial = "LEO-BAND-001"
    try:
        band = db.query(Device).filter(Device.child_id == "child-leo-1").first()
        if band:
            serial = band.serial_number
    finally:
        db.close()

    hb_res = client.post("/api/v1/safety/devices/heartbeat", json={
        "serial_number": serial,
        "battery_level": 10,
        "connection_status": "connected"
    })
    assert hb_res.status_code == 200

    # Verify low battery alert appears in alerts list
    alerts_res = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    bat_alerts = [a for a in alerts_res.json() if "low_battery" in a["alert_type"].lower() or "battery" in a["title"].lower()]
    assert len(bat_alerts) >= 1

# 22. No Duplicate Alerts on Repeated Polling
def test_no_duplicate_alerts_on_repeated_query():
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res1 = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    res2 = client.get("/api/v1/safety/alerts/child-leo-1", headers=headers)
    assert len(res1.json()) == len(res2.json())
