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
# Checkpoint Creation & Validation Tests
# ------------------------------------------------------------------------------

def test_checkpoint_creation_and_retrieval():
    """Test creating an NFC Checkpoint and retrieving by ID and NFC Tag."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Delete any existing test checkpoint to ensure fresh state
    db = SessionLocal()
    try:
        db.query(SafeZone).filter(SafeZone.nfc_tag_id == "NFC-LIBRARY-001").delete()
        db.commit()
    finally:
        db.close()

    payload = {
        "name": "Community Library Checkpoint",
        "nfc_tag_id": "NFC-LIBRARY-001",
        "latitude": 28.6150,
        "longitude": 77.2100,
        "radius": 120.0,
        "child_id": "child-leo-1",
        "status": "active",
        "address": "Central Library Safe Point"
    }

    res = client.post("/api/v1/safety/checkpoints", json=payload, headers=headers)
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["name"] == "Community Library Checkpoint"
    assert data["nfc_tag_id"] == "NFC-LIBRARY-001"
    assert data["latitude"] == 28.6150
    assert data["longitude"] == 77.2100
    assert data["radius"] == 120.0
    assert data["status"] == "active"
    assert "checkpoint_id" in data
    cp_id = data["checkpoint_id"]

    # Retrieve by checkpoint ID
    res_get = client.get(f"/api/v1/safety/checkpoints/{cp_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["nfc_tag_id"] == "NFC-LIBRARY-001"

    # Retrieve by NFC Tag ID
    res_nfc = client.get("/api/v1/safety/checkpoints/nfc/NFC-LIBRARY-001", headers=headers)
    assert res_nfc.status_code == 200
    assert res_nfc.json()["checkpoint_id"] == cp_id

def test_checkpoint_duplicate_nfc_rejection():
    """Test duplicate NFC tag ID rejection on checkpoint creation."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Duplicate School Gate",
        "nfc_tag_id": "NFC-SCHOOL-001",  # Seeded in main.py
        "latitude": 28.6139,
        "longitude": 77.2090,
        "radius": 100.0,
    }
    res = client.post("/api/v1/safety/checkpoints", json=payload, headers=headers)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()

def test_checkpoint_invalid_parameters():
    """Test latitude, longitude, and radius validation on checkpoint creation."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid latitude (> 90)
    res_lat = client.post(
        "/api/v1/safety/checkpoints",
        json={"name": "Bad Lat", "nfc_tag_id": "NFC-BAD-LAT", "latitude": 95.0, "longitude": 77.0, "radius": 50},
        headers=headers
    )
    assert res_lat.status_code == 422

    # Invalid radius (<= 0)
    res_rad = client.post(
        "/api/v1/safety/checkpoints",
        json={"name": "Bad Radius", "nfc_tag_id": "NFC-BAD-RAD", "latitude": 28.0, "longitude": 77.0, "radius": 0},
        headers=headers
    )
    assert res_rad.status_code == 422

# ------------------------------------------------------------------------------
# 1. Valid NFC + Valid GPS (Inside Checkpoint)
# ------------------------------------------------------------------------------
def test_1_valid_nfc_and_valid_gps_verification():
    """1. Valid NFC + valid GPS: Location matches checkpoint and device is online -> SAFE / VERIFIED."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure dev-band-leo-1 is online and assigned to child-leo-1 with full battery
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        if band:
            band.child_id = "child-leo-1"
            band.is_online = True
            band.connection_status = "online"
            band.battery_level = 92
            band.gps_enabled = True
            band.bluetooth_connected = True
            db.commit()
    finally:
        db.close()

    # School gate is at (28.6139, 77.2090) with radius 100m.
    # Coordinates (28.6140, 77.2091) is ~15m away, well inside the 100m radius.
    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6140,
        "longitude": 77.2091
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["verified"] is True
    assert data["status"] == "SAFE"
    assert data["verification_type"] == "NFC_GPS"
    assert data["checkpoint_id"] == "cp-school-1"
    assert data["checkpoint_name"] == "School Gate"
    assert data["child_id"] == "child-leo-1"
    assert data["child_name"] == "Leo Mitchell"
    assert data["band_id"] in ["dev-band-leo-1", "NIVARA-BAND-LEO-001"]
    assert data["distance_meters"] is not None
    assert data["distance_meters"] < 100.0
    assert data["device_connected"] is True
    assert data["battery_level"] == 92
    assert data["gps_enabled"] is True
    assert data["bluetooth_connected"] is True
    assert data["reason"] is None
    assert data["safety_event_id"] is not None

# ------------------------------------------------------------------------------
# 2. Valid NFC + GPS Outside Checkpoint (Location Mismatch)
# ------------------------------------------------------------------------------
def test_2_valid_nfc_and_gps_outside_checkpoint_mismatch():
    """2. Valid NFC + GPS outside checkpoint: 700m away -> LOCATION_MISMATCH."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Coordinates (28.6200, 77.2150) is ~900m away from (28.6139, 77.2090)
    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6200,
        "longitude": 77.2150
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "LOCATION_MISMATCH"
    assert "do not match" in data["reason"].lower()
    assert data["distance_meters"] > 100.0
    assert data["checkpoint_id"] == "cp-school-1"
    assert data["safety_event_id"] is not None

# ------------------------------------------------------------------------------
# 3. Invalid NFC Tag
# ------------------------------------------------------------------------------
def test_3_invalid_nfc_checkpoint():
    """3. Invalid NFC: Unregistered NFC tag -> UNKNOWN_NFC."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-UNREGISTERED-999",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "UNKNOWN_NFC"
    assert "not registered" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 4. NFC Belonging to Another Band (Not a Checkpoint)
# ------------------------------------------------------------------------------
def test_4_nfc_not_a_checkpoint():
    """4. NFC belonging to another entity / not registered as checkpoint -> UNKNOWN_NFC."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NV-NFC-OTHER-BAND-RANDOM",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "UNKNOWN_NFC"

# ------------------------------------------------------------------------------
# 5. Band Belonging to Another Child
# ------------------------------------------------------------------------------
def test_5_band_belonging_to_another_child():
    """5. Band belonging to another child: Prevent verifying child with a foreign band."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create a temporary band belonging to a different child
    db = SessionLocal()
    try:
        foreign_band = Device(
            id="dev-band-other-child",
            child_id="child-other-stranger",
            serial_number="FOREIGN-BAND-999",
            device_identifier="FOREIGN-BAND-999",
            is_active=True,
            is_online=True,
        )
        db.add(foreign_band)
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-other-child",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["verified"] is False
    assert data["status"] == "FAILED"
    assert "not belong" in data["reason"].lower() or "not assigned" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 6. Unauthorized Caregiver
# ------------------------------------------------------------------------------
def test_6_unauthorized_caregiver_rejection():
    """6. Unauthorized caregiver: David cannot perform safety verification for Sarah's child (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 403
    assert "unauthorized" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 7. Missing Child
# ------------------------------------------------------------------------------
def test_7_missing_child_404():
    """7. Missing child: Non-existent child returns 404."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-ghost-9999",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 8. Missing Checkpoint Lookup
# ------------------------------------------------------------------------------
def test_8_missing_checkpoint_404():
    """8. Missing checkpoint: GET /checkpoints/{id} returns 404 for non-existent checkpoint."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/checkpoints/cp-non-existent-999", headers=headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 9. Device Disconnected / Offline
# ------------------------------------------------------------------------------
def test_9_device_disconnected_offline():
    """9. Device disconnected: Wearable is offline -> DEVICE_OFFLINE (verified=False)."""
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
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "DEVICE_OFFLINE"
    assert data["device_connected"] is False
    assert "offline" in data["reason"].lower() or "disconnected" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 10. Low / Dead Battery
# ------------------------------------------------------------------------------
def test_10_dead_battery_handling():
    """10. Dead battery (0%): Device marked offline / not safely verifiable."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Set band to 0% battery
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.is_online = True
        band.connection_status = "online"
        band.battery_level = 0
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert data["status"] == "DEVICE_OFFLINE"
    assert data["battery_level"] == 0

# ------------------------------------------------------------------------------
# 11. Valid Verification Safety Event Logging
# ------------------------------------------------------------------------------
def test_11_valid_verification_safety_event():
    """11. Valid verification event: Persists NFC_GPS_VERIFIED in safety_events table."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Reset band to active and 90% battery
    db = SessionLocal()
    try:
        band = db.query(Device).filter(Device.id == "dev-band-leo-1").first()
        band.is_online = True
        band.connection_status = "online"
        band.battery_level = 90
        band.gps_enabled = True
        band.bluetooth_connected = True
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6139,
        "longitude": 77.2090
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    event_id = res.json()["safety_event_id"]

    # Verify event in SQLite DB
    db = SessionLocal()
    try:
        event = db.query(SafetyEvent).filter(SafetyEvent.id == event_id).first()
        assert event is not None
        assert event.event_type == "NFC_GPS_VERIFIED"
        assert event.severity == "info"
        assert event.child_id == "child-leo-1"
        assert "School Gate" in event.title
        assert event.latitude == 28.6139
        assert event.longitude == 77.2090
    finally:
        db.close()

# ------------------------------------------------------------------------------
# 12. Mismatch Safety Event Logging
# ------------------------------------------------------------------------------
def test_12_mismatch_safety_event():
    """12. Mismatch safety event: Persists NFC_GPS_MISMATCH in safety_events table."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "band_id": "dev-band-leo-1",
        "nfc_tag_id": "NFC-SCHOOL-001",
        "latitude": 28.6300,  # Far away
        "longitude": 77.2300
    }

    res = client.post("/api/v1/safety/verification/nfc-gps", json=payload, headers=headers)
    assert res.status_code == 200
    event_id = res.json()["safety_event_id"]

    # Verify event in SQLite DB
    db = SessionLocal()
    try:
        event = db.query(SafetyEvent).filter(SafetyEvent.id == event_id).first()
        assert event is not None
        assert event.event_type == "NFC_GPS_MISMATCH"
        assert event.severity == "warning"
        assert event.child_id == "child-leo-1"
        assert "Mismatch" in event.title
    finally:
        db.close()
