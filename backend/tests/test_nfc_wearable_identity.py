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
    """David is a verified caregiver, but NOT caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def test_1_valid_wearable_registration_with_nfc():
    """1. Valid wearable registration: Register band with unique NFC/RFID identifier."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Delete seeded band for child-leo-1 to register a new one
    db = SessionLocal()
    try:
        db.query(Device).filter(Device.child_id == "child-leo-1").delete()
        db.commit()
    finally:
        db.close()

    payload = {
        "nfc_tag_id": "NV-NFC-LEO-001",
        "band_id": "NV-BAND-LEO-001",
        "device_name": "Leo's Nivara SafeBand",
        "device_type": "nfc_wearable",
        "child_id": "child-leo-1",
        "battery_level": 98,
        "connection_status": "online",
        "gps_status": "active",
        "firmware_version": "v1.2.0"
    }

    res = client.post("/api/v1/safety/bands/nfc/register", json=payload, headers=headers)
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}: {res.text}"
    data = res.json()

    assert data["nfc_tag_id"] == "NV-NFC-LEO-001"
    assert data["device_identifier"] == "NV-BAND-LEO-001"
    assert data["child_id"] == "child-leo-1"
    assert data["battery_level"] == 98
    assert data["connection_status"] == "online"
    assert "id" in data

    # Verify persistence directly in SQLite database
    db = SessionLocal()
    try:
        saved = db.query(Device).filter(Device.nfc_tag_id == "NV-NFC-LEO-001").first()
        assert saved is not None
        assert saved.nfc_tag_id == "NV-NFC-LEO-001"
        assert saved.child_id == "child-leo-1"
        assert saved.serial_number == "NV-BAND-LEO-001"
    finally:
        db.close()

def test_2_valid_nfc_id_retrieval():
    """2. Valid NFC ID: Retrieve wearable info using NFC tag ID (seeded NV-NFC-001)."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve via dedicated NFC endpoint
    res = client.get("/api/v1/safety/bands/nfc/NV-NFC-001", headers=headers)
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["nfc_tag_id"] == "NV-NFC-001"
    assert data["child_id"] == "child-leo-1"
    assert data["device_identifier"] == "NIVARA-BAND-LEO-001"

    # Retrieve via general identifier endpoint
    res_gen = client.get("/api/v1/safety/bands/NV-NFC-001", headers=headers)
    assert res_gen.status_code == 200
    assert res_gen.json()["nfc_tag_id"] == "NV-NFC-001"

def test_3_duplicate_nfc_id_prevention():
    """3. Duplicate NFC ID: Prevent registering another device with same NFC ID."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    duplicate_payload = {
        "nfc_tag_id": "NV-NFC-001",  # already in use by seeded dev-band-leo-1
        "band_id": "NV-BAND-DUP-999",
        "device_name": "Duplicate NFC Band",
    }

    # Attempt via NFC register endpoint
    res = client.post("/api/v1/safety/bands/nfc/register", json=duplicate_payload, headers=headers)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()

    # Attempt via general band register endpoint
    res_gen = client.post(
        "/api/v1/safety/bands",
        json={
            "device_identifier": "NV-BAND-DUP-888",
            "nfc_tag_id": "NV-NFC-001",
        },
        headers=headers
    )
    assert res_gen.status_code == 400
    assert "already registered" in res_gen.json()["detail"].lower()

def test_4_invalid_child_rejection():
    """4. Invalid child: Reject assignment to non-existent child ID with 404."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "nfc_tag_id": "NV-NFC-GHOST-001",
        "band_id": "NV-BAND-GHOST-001",
        "child_id": "child-non-existent-9999",
    }

    res = client.post("/api/v1/safety/bands/nfc/register", json=payload, headers=headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_5_invalid_wearable_rejection():
    """5. Invalid wearable: Non-existent NFC tag or band ID returns 404."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Lookup non-existent NFC
    res_get = client.get("/api/v1/safety/bands/nfc/NV-NFC-NON-EXISTENT", headers=headers)
    assert res_get.status_code == 404

    # Update non-existent band NFC
    res_patch = client.patch(
        "/api/v1/safety/bands/dev-non-existent/nfc",
        json={"nfc_tag_id": "NV-NFC-NEW-999"},
        headers=headers
    )
    assert res_patch.status_code == 404

def test_6_unauthorized_caregiver_rejection():
    """6. Unauthorized caregiver: David cannot access or modify Sarah's child's wearable (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # David attempts to assign wearable to Sarah's child (child-leo-1)
    res_assign = client.post(
        "/api/v1/safety/bands/nfc/register",
        json={"nfc_tag_id": "NV-NFC-HACK-001", "child_id": "child-leo-1"},
        headers=headers
    )
    assert res_assign.status_code == 403

    # David attempts to view Leo's wearable by NFC tag
    res_view = client.get("/api/v1/safety/bands/nfc/NV-NFC-001", headers=headers)
    assert res_view.status_code == 403

    # David attempts to update NFC tag on Leo's band
    res_update = client.patch(
        "/api/v1/safety/bands/dev-band-leo-1/nfc",
        json={"nfc_tag_id": "NV-NFC-HIJACK-001"},
        headers=headers
    )
    assert res_update.status_code == 403

def test_7_nfc_verification_endpoints():
    """7. NFC verification: Verify NFC tag returns active child & wearable metadata."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # POST verify
    res_post = client.post(
        "/api/v1/safety/bands/nfc/verify",
        json={"nfc_tag_id": "NV-NFC-001"},
        headers=headers
    )
    assert res_post.status_code == 200, f"Expected 200 OK, got {res_post.status_code}: {res_post.text}"
    data_post = res_post.json()
    assert data_post["is_valid"] is True
    assert data_post["nfc_tag_id"] == "NV-NFC-001"
    assert data_post["child_id"] == "child-leo-1"
    assert data_post["child_name"] == "Leo Mitchell"
    assert data_post["status"] == "active"
    assert "verified_at" in data_post

    # GET verify
    res_get = client.get("/api/v1/safety/bands/nfc/verify/NV-NFC-001", headers=headers)
    assert res_get.status_code == 200
    data_get = res_get.json()
    assert data_get["is_valid"] is True
    assert data_get["nfc_tag_id"] == "NV-NFC-001"
    assert data_get["child_name"] == "Leo Mitchell"

    # Non-existent NFC verify -> 404
    res_invalid = client.post(
        "/api/v1/safety/bands/nfc/verify",
        json={"nfc_tag_id": "NV-NFC-UNKNOWN-999"},
        headers=headers
    )
    assert res_invalid.status_code == 404

def test_8_missing_nfc_id_validation():
    """8. Missing NFC ID: Reject registration or verification when NFC ID is missing/empty."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Empty NFC ID in registration
    res_empty_reg = client.post(
        "/api/v1/safety/bands/nfc/register",
        json={"nfc_tag_id": "   ", "child_id": "child-leo-1"},
        headers=headers
    )
    assert res_empty_reg.status_code in [400, 422]

    # Empty NFC ID in verify
    res_empty_verify = client.post(
        "/api/v1/safety/bands/nfc/verify",
        json={"nfc_tag_id": ""},
        headers=headers
    )
    assert res_empty_verify.status_code in [400, 422]

def test_9_authentication_failure():
    """9. Authentication failure: Reject requests without token or with invalid token (401)."""
    # No auth header
    assert client.post("/api/v1/safety/bands/nfc/register", json={"nfc_tag_id": "NV-NFC-TEST"}).status_code == 401
    assert client.get("/api/v1/safety/bands/nfc/NV-NFC-001").status_code == 401
    assert client.post("/api/v1/safety/bands/nfc/verify", json={"nfc_tag_id": "NV-NFC-001"}).status_code == 401
    assert client.get("/api/v1/safety/bands/nfc/verify/NV-NFC-001").status_code == 401
    assert client.patch("/api/v1/safety/bands/dev-band-leo-1/nfc", json={"nfc_tag_id": "NV-NFC-2"}).status_code == 401

    # Invalid token
    bad_headers = {"Authorization": "Bearer invalid.token.value"}
    assert client.post("/api/v1/safety/bands/nfc/register", json={"nfc_tag_id": "NV-NFC-TEST"}, headers=bad_headers).status_code == 401

def test_10_update_nfc_identifier():
    """10. Update NFC identifier: Update NFC tag on existing wearable band."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Update Leo's band NFC tag to a new value via PATCH /nfc
    update_res = client.patch(
        "/api/v1/safety/bands/dev-band-leo-1/nfc",
        json={"nfc_tag_id": "NV-NFC-LEO-UPDATED-002"},
        headers=headers
    )
    assert update_res.status_code == 200, f"Expected 200, got {update_res.status_code}: {update_res.text}"
    assert update_res.json()["nfc_tag_id"] == "NV-NFC-LEO-UPDATED-002"

    # Verify old NFC tag is no longer found
    assert client.get("/api/v1/safety/bands/nfc/NV-NFC-001", headers=headers).status_code == 404

    # Verify new NFC tag resolves
    new_get = client.get("/api/v1/safety/bands/nfc/NV-NFC-LEO-UPDATED-002", headers=headers)
    assert new_get.status_code == 200
    assert new_get.json()["nfc_tag_id"] == "NV-NFC-LEO-UPDATED-002"

    # Also test updating via general PATCH /bands/{band_id}
    patch_gen = client.patch(
        "/api/v1/safety/bands/dev-band-leo-1",
        json={"nfc_tag_id": "NV-NFC-001"},
        headers=headers
    )
    assert patch_gen.status_code == 200
    assert patch_gen.json()["nfc_tag_id"] == "NV-NFC-001"
