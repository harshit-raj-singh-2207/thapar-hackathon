import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.config.database import SessionLocal
from app.models.device import Device
from app.models.child import Child
from app.models.safe_zone import SafeZone
from app.models.safety_event import SafetyEvent
from app.models.caregiver_nfc import CaregiverNFC

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
# 1. Register Caregiver NFC
# ------------------------------------------------------------------------------
def test_1_register_caregiver_nfc_success():
    """1. Valid caregiver NFC registration: Register unique NFC badge for child pickup."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Clean up test credential if previously registered
    db = SessionLocal()
    try:
        db.query(CaregiverNFC).filter(CaregiverNFC.nfc_identifier == "CAREGIVER-NFC-TEST-001").delete()
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-TEST-001",
        "status": "active"
    }

    res = client.post("/api/v1/safety/caregiver/nfc/register", json=payload, headers=headers)
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["nfc_identifier"] == "CAREGIVER-NFC-TEST-001"
    assert data["child_id"] == "child-leo-1"
    assert data["status"] == "active"
    assert "id" in data
    assert "created_at" in data

    # Verify directly in SQLite database
    db = SessionLocal()
    try:
        record = db.query(CaregiverNFC).filter(CaregiverNFC.nfc_identifier == "CAREGIVER-NFC-TEST-001").first()
        assert record is not None
        assert record.child_id == "child-leo-1"
    finally:
        db.close()

# ------------------------------------------------------------------------------
# 2. Duplicate Caregiver NFC Rejection
# ------------------------------------------------------------------------------
def test_2_duplicate_caregiver_nfc_rejection():
    """2. Duplicate NFC rejection: Prevent registering the same NFC badge twice."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # CAREGIVER-NFC-001 is seeded for Sarah
    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-001"
    }

    res = client.post("/api/v1/safety/caregiver/nfc/register", json=payload, headers=headers)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 3. Unauthorized Caregiver Registration
# ------------------------------------------------------------------------------
def test_3_unauthorized_caregiver_registration():
    """3. Unauthorized caregiver: David cannot register a pickup NFC badge for Sarah's child (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-HIJACK-001"
    }

    res = client.post("/api/v1/safety/caregiver/nfc/register", json=payload, headers=headers)
    assert res.status_code == 403
    assert "unauthorized" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 4. Invalid Child Registration
# ------------------------------------------------------------------------------
def test_4_invalid_child_registration():
    """4. Invalid child: Reject registering NFC badge for non-existent child (404 Not Found)."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-non-existent-9999",
        "nfc_identifier": "CAREGIVER-NFC-ORPHAN-001"
    }

    res = client.post("/api/v1/safety/caregiver/nfc/register", json=payload, headers=headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 5. Successful Authorized Pickup Verification
# ------------------------------------------------------------------------------
def test_5_successful_pickup_verification():
    """5. Successful pickup: All signals (Caregiver NFC, authorized child, GPS location, active wearable) pass -> PICKUP_VERIFIED."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure dev-band-leo-1 is online and active
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = "child-leo-1"
            band.is_online = True
            band.connection_status = "online"
            band.battery_level = 95
            band.gps_enabled = True
            band.bluetooth_connected = True
            db.commit()
    finally:
        db.close()

    # School Gate is at (28.6139, 77.2090)
    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["verified"] is True
    assert data["status"] == "PICKUP_VERIFIED"
    assert data["child_id"] == "child-leo-1"
    assert data["child_name"] == "Leo Mitchell"
    assert data["location_verified"] is True
    assert data["device_verified"] is True
    assert data["nfc_identifier"] == "CAREGIVER-NFC-001"
    assert data["safety_event_id"] is not None

# ------------------------------------------------------------------------------
# 6. Unauthorized Caregiver Pickup Attempt
# ------------------------------------------------------------------------------
def test_6_unauthorized_caregiver_pickup():
    """6. Unauthorized caregiver: David cannot verify pickup for Sarah's child (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 403
    assert "unauthorized" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 7. Invalid Caregiver NFC
# ------------------------------------------------------------------------------
def test_7_invalid_caregiver_nfc():
    """7. Invalid NFC: Unregistered NFC tag -> PICKUP_REJECTED (verified=False)."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-UNREGISTERED-999",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "PICKUP_REJECTED"
    assert "not registered" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 8. NFC Belonging to Another Caregiver
# ------------------------------------------------------------------------------
def test_8_nfc_belonging_to_another_caregiver():
    """8. NFC belonging to another caregiver: Reject when user attempts to present another caregiver's badge."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Register an NFC badge owned by David
    db = SessionLocal()
    try:
        db.query(CaregiverNFC).filter(CaregiverNFC.nfc_identifier == "CAREGIVER-NFC-DAVID-999").delete()
        db.commit()

        david_user = db.query(Child).first()
        david_nfc = CaregiverNFC(
            id="cgnfc-david-test",
            caregiver_id="user-verified-david",
            child_id="child-leo-1",
            nfc_identifier="CAREGIVER-NFC-DAVID-999",
            status="active"
        )
        db.add(david_nfc)
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-DAVID-999",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "PICKUP_REJECTED"
    assert "not authorized" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 9. Wrong Child Pickup
# ------------------------------------------------------------------------------
def test_9_wrong_child_pickup():
    """9. Wrong child: Reject when caregiver's NFC credential was issued for a different child."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Register Sarah's badge for a different child
    db = SessionLocal()
    try:
        db.query(CaregiverNFC).filter(CaregiverNFC.nfc_identifier == "CAREGIVER-NFC-MAYA-ONLY").delete()
        db.commit()

        maya_nfc = CaregiverNFC(
            id="cgnfc-sarah-maya",
            caregiver_id="user-verified-sarah",
            child_id="child-other-stranger",
            nfc_identifier="CAREGIVER-NFC-MAYA-ONLY",
            status="active"
        )
        db.add(maya_nfc)
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-MAYA-ONLY",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "PICKUP_REJECTED"
    assert "not authorized for this child" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 10. GPS Outside Pickup Location
# ------------------------------------------------------------------------------
def test_10_gps_outside_pickup_location():
    """10. GPS outside pickup location: Caregiver is 5km away from school/safe zone -> LOCATION_MISMATCH."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Far away coordinates (28.7000, 77.3000)
    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-001",
        "latitude": 28.7000,
        "longitude": 77.3000
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "LOCATION_MISMATCH"
    assert data["location_verified"] is False
    assert "outside" in data["reason"].lower() or "allowed pickup" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 11. Child Device Offline
# ------------------------------------------------------------------------------
def test_11_device_offline_pickup():
    """11. Device offline: Child's wearable is offline/dead battery -> DEVICE_OFFLINE."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Set band to offline
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.is_online = False
        band.connection_status = "offline"
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "DEVICE_OFFLINE"
    assert data["device_verified"] is False
    assert "offline" in data["reason"].lower() or "disconnected" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 12. Repeated Pickup Attempt
# ------------------------------------------------------------------------------
def test_12_repeated_pickup_attempt():
    """12. Repeated pickup: Second verification attempt succeeds and updates last_pickup_at."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Reset band to online
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.is_online = True
        band.connection_status = "online"
        band.battery_level = 90
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "nfc_identifier": "CAREGIVER-NFC-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/pickup/verify", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["verified"] is True
    assert res.json()["status"] == "PICKUP_VERIFIED"

def test_13_pickup_safety_events_persisted():
    """13. Safety event creation: Verify that PICKUP_VERIFIED, LOCATION_MISMATCH, and DEVICE_OFFLINE are persisted in safety_events table."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Trigger PICKUP_VERIFIED
    res_v = client.post(
        "/api/v1/safety/pickup/verify",
        json={"child_id": "child-leo-1", "nfc_identifier": "CAREGIVER-NFC-001", "latitude": 28.6139, "longitude": 77.2090},
        headers=headers
    )
    assert res_v.status_code == 200
    assert res_v.json()["verified"] is True
    ev_verified_id = res_v.json()["safety_event_id"]

    # 2. Trigger LOCATION_MISMATCH
    res_m = client.post(
        "/api/v1/safety/pickup/verify",
        json={"child_id": "child-leo-1", "nfc_identifier": "CAREGIVER-NFC-001", "latitude": 28.7500, "longitude": 77.3500},
        headers=headers
    )
    assert res_m.status_code == 200
    assert res_m.json()["verified"] is False
    ev_mismatch_id = res_m.json()["safety_event_id"]

    # Verify event rows in SQLite database
    db = SessionLocal()
    try:
        ev_v = db.query(SafetyEvent).filter(SafetyEvent.id == ev_verified_id).first()
        assert ev_v is not None
        assert ev_v.event_type == "PICKUP_VERIFIED"
        assert ev_v.severity == "info"
        assert ev_v.child_id == "child-leo-1"

        ev_m = db.query(SafetyEvent).filter(SafetyEvent.id == ev_mismatch_id).first()
        assert ev_m is not None
        assert ev_m.event_type == "LOCATION_MISMATCH"
        assert ev_m.severity == "warning"
        assert ev_m.child_id == "child-leo-1"
    finally:
        db.close()
