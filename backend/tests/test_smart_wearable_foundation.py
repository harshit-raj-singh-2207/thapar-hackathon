import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.config.database import SessionLocal
from app.models.device import Device
from app.models.child import Child

client = TestClient(app)

def get_sarah_token():
    """Sarah is the caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def get_david_token():
    """David is a caregiver, but NOT authorized for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

# ------------------------------------------------------------------------------
# 1. Register Smart Wearable
# ------------------------------------------------------------------------------
def test_1_register_smart_wearable():
    """1. Register wearable: Create smart wearable with NFC ID, semiconductor status, battery and child association."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Delete existing band for child-leo-1 so we can register a fresh unified wearable
    db = SessionLocal()
    try:
        db.query(Device).filter(Device.child_id == "child-leo-1").delete()
        db.commit()
    finally:
        db.close()

    payload = {
        "child_id": "child-leo-1",
        "band_id": "NIVARA-BAND-001",
        "nfc_tag_id": "NIVARA-NFC-001",
        "device_name": "Leo's Smart Safety Wearable",
        "battery_level": 98,
        "gps_enabled": True,
        "gps_status": "active",
        "bluetooth_connected": True,
        "connection_status": "online",
        "status": "active",
        "firmware_version": "v2.0.0"
    }

    res = client.post("/api/v1/safety/bands", json=payload, headers=headers)
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["band_id"] == "NIVARA-BAND-001"
    assert data["nfc_tag_id"] == "NIVARA-NFC-001"
    assert data["child_id"] == "child-leo-1"
    assert data["status"] == "active"
    assert data["battery_level"] == 98
    assert data["battery"] == 98
    assert data["gps_enabled"] is True
    assert data["gps_status"] == "active"
    assert data["bluetooth_connected"] is True
    assert "last_seen_at" in data
    assert "created_at" in data

    # Verify directly in SQLite DB
    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.serial_number == "NIVARA-BAND-001").first()
        assert device is not None
        assert device.nfc_tag_id == "NIVARA-NFC-001"
        assert device.child_id == "child-leo-1"
        assert device.battery_level == 98
        assert device.gps_enabled is True
        assert device.bluetooth_connected is True
        assert device.status == "active"
    finally:
        db.close()

# ------------------------------------------------------------------------------
# 2. Duplicate Band Rejection
# ------------------------------------------------------------------------------
def test_2_duplicate_band_rejection():
    """2. Duplicate band rejection: Prevent registering a device with an existing band ID."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Seeded band is NIVARA-BAND-LEO-001
    payload = {
        "band_id": "NIVARA-BAND-LEO-001",
        "nfc_tag_id": "NV-NFC-NEW-999",
        "device_name": "Duplicate Band",
    }

    res = client.post("/api/v1/safety/bands", json=payload, headers=headers)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 3. Duplicate NFC Rejection
# ------------------------------------------------------------------------------
def test_3_duplicate_nfc_rejection():
    """3. Duplicate NFC rejection: Prevent registering another device with an existing NFC ID."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Seeded band has nfc_tag_id="NV-NFC-001"
    payload = {
        "band_id": "NV-BAND-NEW-777",
        "nfc_tag_id": "NV-NFC-001",
        "device_name": "Duplicate NFC Band",
    }

    res = client.post("/api/v1/safety/bands", json=payload, headers=headers)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 4. Invalid Child Rejection
# ------------------------------------------------------------------------------
def test_4_invalid_child_rejection():
    """4. Invalid child: Reject assignment to non-existent child ID with 404."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-non-existent-9999",
        "band_id": "NV-BAND-ORPHAN-001",
        "nfc_tag_id": "NV-NFC-ORPHAN-001",
    }

    res = client.post("/api/v1/safety/bands", json=payload, headers=headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

# ------------------------------------------------------------------------------
# 5. Unauthorized Caregiver
# ------------------------------------------------------------------------------
def test_5_unauthorized_caregiver():
    """5. Unauthorized caregiver: David cannot register, view, or verify Sarah's child's wearable (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # David attempts to register wearable for Sarah's child (child-leo-1)
    res_reg = client.post(
        "/api/v1/safety/bands",
        json={"child_id": "child-leo-1", "band_id": "NV-BAND-HIJACK-001", "nfc_tag_id": "NV-NFC-HIJACK-001"},
        headers=headers
    )
    assert res_reg.status_code == 403

    # David attempts to view Leo's wearable
    res_get = client.get("/api/v1/safety/bands/NIVARA-BAND-LEO-001", headers=headers)
    assert res_get.status_code == 403

    # David attempts to verify NFC tag belonging to Leo's wearable
    res_verify = client.post(
        "/api/v1/safety/bands/verify-nfc",
        json={"nfc_tag_id": "NV-NFC-001"},
        headers=headers
    )
    assert res_verify.status_code == 403

# ------------------------------------------------------------------------------
# 6. Get Wearable
# ------------------------------------------------------------------------------
def test_6_get_wearable():
    """6. Get wearable: Retrieve child, band ID, NFC ID, status, battery, GPS, BLE, and last seen."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/bands/NIVARA-BAND-LEO-001", headers=headers)
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["band_id"] == "NIVARA-BAND-LEO-001"
    assert data["nfc_tag_id"] == "NV-NFC-001"
    assert data["child_id"] == "child-leo-1"
    assert data["status"] == "active"
    assert data["device_status"] == "active"
    assert data["battery_level"] == 92
    assert data["battery"] == 92
    assert data["gps_enabled"] is True
    assert data["gps_status"] == "active"
    assert data["bluetooth_connected"] is True
    assert "last_seen_at" in data
    assert "child" in data or "child_name" in data

# ------------------------------------------------------------------------------
# 7. Valid NFC Verification
# ------------------------------------------------------------------------------
def test_7_valid_nfc_verification():
    """7. Valid NFC verification: POST /verify-nfc returns verified=True, band_id, child_id, status."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/safety/bands/verify-nfc",
        json={"nfc_tag_id": "NV-NFC-001"},
        headers=headers
    )
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["verified"] is True
    assert data["band_id"] == "NIVARA-BAND-LEO-001"
    assert data["child_id"] == "child-leo-1"
    assert data["status"] == "active"
    assert data["child_name"] == "Leo Mitchell"
    assert data["battery_level"] == 92
    assert data["gps_enabled"] is True
    assert data["bluetooth_connected"] is True
    assert "verified_at" in data

# ------------------------------------------------------------------------------
# 8. Invalid NFC Verification
# ------------------------------------------------------------------------------
def test_8_invalid_nfc_verification():
    """8. Invalid NFC verification: Unknown NFC tag returns verified=False and reason."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/safety/bands/verify-nfc",
        json={"nfc_tag_id": "UNKNOWN-NFC-9999"},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is False
    assert "nfc tag not registered" in data["reason"].lower()

# ------------------------------------------------------------------------------
# 9. Battery Validation
# ------------------------------------------------------------------------------
def test_9_battery_validation():
    """9. Battery validation: Enforce battery level between 0 and 100."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Battery > 100 on creation
    res_high = client.post(
        "/api/v1/safety/bands",
        json={"band_id": "NV-BAND-OVERLOAD", "battery_level": 150},
        headers=headers
    )
    assert res_high.status_code == 422

    # Battery < 0 on creation
    res_low = client.post(
        "/api/v1/safety/bands",
        json={"band_id": "NV-BAND-UNDERLOAD", "battery_level": -10},
        headers=headers
    )
    assert res_low.status_code == 422

    # Battery > 100 on update
    res_update_high = client.patch(
        "/api/v1/safety/bands/dev-band-leo-1",
        json={"battery_level": 120},
        headers=headers
    )
    assert res_update_high.status_code == 422

    # Battery < 0 on update
    res_update_low = client.patch(
        "/api/v1/safety/bands/dev-band-leo-1",
        json={"battery_level": -5},
        headers=headers
    )
    assert res_update_low.status_code == 422

# ------------------------------------------------------------------------------
# 10. Device Status Update
# ------------------------------------------------------------------------------
def test_10_device_status_update():
    """10. Device status update: Update battery, GPS status, BLE status, last seen, and device status."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Update via PATCH /api/v1/safety/bands/{band_id}
    patch_res = client.patch(
        "/api/v1/safety/bands/dev-band-leo-1",
        json={
            "battery_level": 75,
            "gps_enabled": False,
            "gps_status": "standby",
            "bluetooth_connected": True,
            "status": "maintenance"
        },
        headers=headers
    )
    assert patch_res.status_code == 200, f"Expected 200 OK, got {patch_res.status_code}: {patch_res.text}"
    data = patch_res.json()

    assert data["battery_level"] == 75
    assert data["battery"] == 75
    assert data["gps_enabled"] is False
    assert data["gps_status"] == "standby"
    assert data["bluetooth_connected"] is True
    assert data["status"] == "maintenance"
    assert data["device_status"] == "maintenance"
    assert "last_seen_at" in data

    # Update via Heartbeat API POST /api/v1/safety/bands/{band_id}/heartbeat
    heartbeat_res = client.post(
        "/api/v1/safety/bands/dev-band-leo-1/heartbeat",
        json={
            "battery_level": 88,
            "connection_status": "connected",
            "gps_enabled": True,
            "gps_status": "active",
            "bluetooth_connected": True,
            "status": "active"
        },
        headers=headers
    )
    assert heartbeat_res.status_code == 200
    hb_data = heartbeat_res.json()
    assert hb_data["battery_level"] == 88
    assert hb_data["gps_enabled"] is True
    assert hb_data["bluetooth_connected"] is True
    assert hb_data["status"] == "active"
    assert "last_seen_at" in hb_data
