import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

import pytest

client = TestClient(app)

def test_unauthenticated_privacy_settings_denied():
    res = client.get("/api/v1/caregivers/me/privacy-settings")
    assert res.status_code == 401

def test_get_and_update_privacy_settings():
    # Login as Sarah (Verified Caregiver)
    login_res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch default privacy settings
    get_res = client.get("/api/v1/caregivers/me/privacy-settings", headers=headers)
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["profile_visibility"] == "Public"
    assert data["messaging_privacy"] == "Connections Only"
    assert data["group_privacy"] == "Active"
    assert data["notification_privacy"] == "All Alerts"

    # 2. Update privacy settings
    update_payload = {
        "profile_visibility": "Private",
        "messaging_privacy": "Disabled",
        "group_privacy": "Hidden",
        "notification_privacy": "Important Only",
    }
    patch_res = client.patch("/api/v1/caregivers/me/privacy-settings", json=update_payload, headers=headers)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["profile_visibility"] == "Private"
    assert updated["messaging_privacy"] == "Disabled"
    assert updated["group_privacy"] == "Hidden"
    assert updated["notification_privacy"] == "Important Only"

    # 3. Verify changes persist
    get_res2 = client.get("/api/v1/caregivers/me/privacy-settings", headers=headers)
    assert get_res2.status_code == 200
    assert get_res2.json()["profile_visibility"] == "Private"

def test_granular_privacy_toggles_and_archive():
    # Login as Sarah
    login_res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Update granular switches matching screenshot
    payload = {
        "public_profile": True,
        "show_location": False,
        "activity_status": True,
        "receive_direct_messages": True,
        "filter_unknown_senders": False,
        "read_receipts": True,
    }
    patch_res = client.patch("/api/v1/caregivers/me/privacy-settings", json=payload, headers=headers)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["public_profile"] is True
    assert data["show_location"] is False
    assert data["activity_status"] is True
    assert data["receive_direct_messages"] is True
    assert data["filter_unknown_senders"] is False
    assert data["read_receipts"] is True

    # 2. Test Request Data Archive
    archive_res = client.post("/api/v1/caregivers/me/request-archive", headers=headers)
    assert archive_res.status_code == 200
    arch_data = archive_res.json()
    assert arch_data["status"] == "processing"
    assert "archive request has been received" in arch_data["message"]

def test_update_caregiver_profile_bio_and_avatar():
    login_res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "bio": "Experienced Autism parent & advocate",
        "avatar_url": "https://example.com/avatar_sarah_updated.jpg"
    }
    patch_res = client.patch("/api/v1/caregivers/me/profile", json=profile_payload, headers=headers)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["bio"] == "Experienced Autism parent & advocate"
    assert data["avatar_url"] == "https://example.com/avatar_sarah_updated.jpg"

if __name__ == "__main__":
    test_unauthenticated_privacy_settings_denied()
    test_get_and_update_privacy_settings()
    test_granular_privacy_toggles_and_archive()
    test_update_caregiver_profile_bio_and_avatar()
    print("ALL PHASE 8 CAREGIVER PROFILE & PRIVACY TESTS PASSED PERFECTLY!")

