import sys
import os
import json
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.config.database import SessionLocal
from app.models.child import Child
from app.models.device import Device
from app.models.location import Location
from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent
from app.models.emergency_contact import EmergencyContact

client = TestClient(app)

def get_sarah_token():
    """Sarah is the authorized caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def get_david_token():
    """David is an authorized caregiver, but NOT authorized for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

# ------------------------------------------------------------------------------
# 1. Valid NFC + Valid Wearable + Valid GPS -> Successful NFC SOS
# ------------------------------------------------------------------------------
def test_1_valid_nfc_and_valid_wearable_sos_trigger_success():
    """1. Valid NFC SOS: Generates active SOS with incident coordinates and NFC trigger source."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure dev-band-leo-1 is online and assigned to Leo
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = "child-leo-1"
            band.nfc_tag_id = "NV-NFC-001"
            band.is_online = True
            band.connection_status = "online"
            band.battery_level = 95
            band.is_active = True
            db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["triggered"] is True
    assert data["status"] == "SOS_ACTIVE"
    assert data["trigger_source"] == "NFC"
    assert data["child_id"] == "child-leo-1"
    assert data["device_verified"] is True
    assert data["latitude"] == 28.6139
    assert data["longitude"] == 77.2090
    assert data["location_available"] is True
    assert "timestamp" in data

    # Verify database updates
    db = SessionLocal()
    try:
        child = db.query(Child).filter(Child.id == "child-leo-1").first()
        assert child.current_status == "emergency"

        alert = db.query(EmergencyAlert).filter(EmergencyAlert.child_id == "child-leo-1", EmergencyAlert.status == "active").first()
        assert alert is not None
        assert alert.triggered_by == "nfc_emergency"
        assert alert.latitude == 28.6139
        assert alert.longitude == 77.2090
    finally:
        db.close()

# ------------------------------------------------------------------------------
# 2. Caregiver Alert & Emergency Contacts Integration
# ------------------------------------------------------------------------------
def test_2_caregiver_alert_and_emergency_contacts_integration():
    """2. Caregiver & Emergency Contacts: Verify that emergency alert pipeline triggers for registered contacts."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure emergency contact exists for Sarah & Leo
    db = SessionLocal()
    try:
        contact = db.query(EmergencyContact).filter(EmergencyContact.child_id == "child-leo-1").first()
        if not contact:
            contact = EmergencyContact(
                id="contact-leo-emg-1",
                user_id="user-verified-sarah",
                child_id="child-leo-1",
                name="Dr. Emily Watson",
                relationship_type="Specialist",
                phone_number="+1-555-0199",
                priority_order=1,
                notify_via_sms=True,
                notify_via_call=True
            )
            db.add(contact)
            db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "SOS_ACTIVE"

# ------------------------------------------------------------------------------
# 3. Duplicate SOS Protection
# ------------------------------------------------------------------------------
def test_3_duplicate_sos_protection():
    """3. Duplicate SOS protection: Repeated triggers maintain SOS_ACTIVE without creating multiple active emergencies."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    # First trigger
    res1 = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["status"] == "SOS_ACTIVE"

    # Second trigger
    res2 = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "SOS_ACTIVE"

    # Verify only ONE active EmergencyAlert exists for the child
    db = SessionLocal()
    try:
        active_alerts = db.query(EmergencyAlert).filter(
            EmergencyAlert.child_id == "child-leo-1",
            EmergencyAlert.status == "active"
        ).all()
        assert len(active_alerts) == 1
    finally:
        db.close()

# ------------------------------------------------------------------------------
# 4. NFC Belonging to Another Child (DEVICE_NOT_ASSOCIATED)
# ------------------------------------------------------------------------------
def test_4_nfc_belonging_to_another_child():
    """4. NFC belonging to another child: Reject with DEVICE_NOT_ASSOCIATED."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Register an NFC tag assigned to another child/wearable
    db = SessionLocal()
    try:
        other_band = db.query(Device).filter(Device.nfc_tag_id == "NV-NFC-OTHER-999").first()
        if not other_band:
            other_band = Device(
                id="dev-band-other-999",
                serial_number="NV-BAND-OTHER-999",
                child_id="child-maya-1",
                nfc_tag_id="NV-NFC-OTHER-999",
                is_active=True,
                is_online=True,
                battery_level=100
            )
            db.add(other_band)
            db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-OTHER-999",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["triggered"] is False
    assert data["status"] == "DEVICE_NOT_ASSOCIATED"
    assert "another child" in data["reason"].lower() or "not associated" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 5. Missing Wearable (DEVICE_NOT_ASSOCIATED)
# ------------------------------------------------------------------------------
def test_5_missing_wearable():
    """5. Missing wearable: Child has no assigned wearable -> DEVICE_NOT_ASSOCIATED."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Temporarily remove Leo's band assignment
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = None
            db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["triggered"] is False
    assert data["status"] == "DEVICE_NOT_ASSOCIATED"

    # Restore Leo's band assignment
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = "child-leo-1"
            db.commit()
    finally:
        db.close()

# ------------------------------------------------------------------------------
# 6. Unauthorized Request (403 Forbidden)
# ------------------------------------------------------------------------------
def test_6_unauthorized_request():
    """6. Unauthorized request: David cannot trigger SOS for Sarah's child (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 403
    assert "unauthorized" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 7. Offline Device (DEVICE_OFFLINE)
# ------------------------------------------------------------------------------
def test_7_offline_device():
    """7. Offline device: Wearable is offline or battery depleted -> DEVICE_OFFLINE."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Set band to offline
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = "child-leo-1"
            band.is_online = False
            band.connection_status = "offline"
            db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["triggered"] is False
    assert data["status"] == "DEVICE_OFFLINE"
    assert "offline" in data["reason"].lower() or "disconnected" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 8. Invalid NFC Identifier (NFC_INVALID)
# ------------------------------------------------------------------------------
def test_8_invalid_nfc_identifier():
    """8. Invalid NFC: Unregistered/mismatched NFC tag returns NFC_INVALID."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Reset band to online
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = "child-leo-1"
            band.nfc_tag_id = "NV-NFC-001"
            band.is_online = True
            band.connection_status = "online"
            band.battery_level = 90
            db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-RANDOM-INVALID",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["triggered"] is False
    assert data["status"] == "NFC_INVALID"

# ------------------------------------------------------------------------------
# 9. Missing Child (404 Not Found)
# ------------------------------------------------------------------------------
def test_9_missing_child():
    """9. Missing child: Non-existent child returns 404 Not Found."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-non-existent-9999",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 10. Missing Location Fallback to Last-Known Location
# ------------------------------------------------------------------------------
def test_10_missing_location_fallback_to_last_known():
    """10. Missing location: When coordinates are omitted, system falls back to child's last known location."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure device is online and seed a last-known location
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = "child-leo-1"
            band.nfc_tag_id = "NV-NFC-001"
            band.is_online = True
            band.connection_status = "online"
            band.battery_level = 95
            band.is_active = True
            db.commit()

        loc = Location(
            id="loc-test-fallback-1",
            child_id="child-leo-1",
            device_id="dev-band-leo-1",
            latitude=37.7749,
            longitude=-122.4194,
            accuracy=5.0,
            battery_level=90.0,
            address="San Francisco, CA"
        )
        db.add(loc)
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001"
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["triggered"] is True
    assert data["status"] == "SOS_ACTIVE"
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["location_available"] is True

# ------------------------------------------------------------------------------
# 11. Safety Events Linked to Incident
# ------------------------------------------------------------------------------
def test_11_safety_events_linked_to_incident():
    """11. Safety event linkage: Verify that NFC_SOS_TRIGGERED contains emergency_id, coordinates, and trigger_source."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "NV-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/emergency/nfc-trigger", json=payload, headers=headers)
    assert res.status_code == 200

    db = SessionLocal()
    try:
        events = db.query(SafetyEvent).filter(
            SafetyEvent.child_id == "child-leo-1",
            SafetyEvent.event_type == "NFC_SOS_TRIGGERED"
        ).all()
        assert len(events) > 0
        ev = events[-1]
        assert ev.severity == "critical"
        assert ev.latitude == 28.6139
        assert ev.longitude == 77.2090

        meta = json.loads(ev.metadata_json)
        assert meta["trigger_source"] == "NFC"
        assert meta["emergency_id"] is not None
    finally:
        db.close()
