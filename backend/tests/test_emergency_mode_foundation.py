import os
import sys
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences

client = TestClient(app)

def get_sarah_token():
    """Sarah is caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def get_david_token():
    """David is a caregiver, but NOT for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


# ==============================================================================
# 1. Create Emergency Mode Tests
# ==============================================================================

def test_create_emergency_mode_default():
    token = get_sarah_token()
    payload = {
        "child_id": "child-leo-1",
        "duration_days": 90,
        "reason": "Worldwide Pandemic Emergency - Physical Gathering Restrictions",
        "preferences": {
            "communication_enabled": True,
            "learning_enabled": True,
            "emotional_support_enabled": True,
            "games_enabled": True,
            "safety_monitoring_enabled": True,
            "caregiver_notifications_enabled": True
        }
    }
    res = client.post("/api/v1/emergency/mode", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["caregiver_id"] == "user-verified-sarah"
    assert data["is_active"] is True
    assert data["is_expired"] is False
    assert data["duration_days"] == 90
    assert data["days_remaining"] >= 89
    assert data["reason"] == "Worldwide Pandemic Emergency - Physical Gathering Restrictions"
    assert data["preferences"]["communication_enabled"] is True
    assert data["preferences"]["learning_enabled"] is True
    assert data["preferences"]["safety_monitoring_enabled"] is True


def test_create_emergency_mode_custom_dates():
    token = get_sarah_token()
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=60)
    payload = {
        "child_id": "child-leo-1",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "reason": "Regional 60-Day Health Advisory Lockdown",
    }
    res = client.post("/api/v1/emergency/mode", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["duration_days"] == 60
    assert data["days_remaining"] >= 59
    assert data["reason"] == "Regional 60-Day Health Advisory Lockdown"


# ==============================================================================
# 2. Get Emergency Mode Tests
# ==============================================================================

def test_get_emergency_mode_success():
    token = get_sarah_token()
    # Ensure mode exists
    client.post("/api/v1/emergency/mode", json={"child_id": "child-leo-1", "duration_days": 90}, headers={"Authorization": f"Bearer {token}"})

    res = client.get("/api/v1/emergency/mode/child-leo-1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["is_active"] is True
    assert "preferences" in data
    assert data["preferences"]["communication_enabled"] is True


# ==============================================================================
# 3. Update Emergency Mode Tests (PATCH)
# ==============================================================================

def test_update_emergency_mode():
    token = get_sarah_token()
    # Create mode
    client.post("/api/v1/emergency/mode", json={"child_id": "child-leo-1", "duration_days": 90}, headers={"Authorization": f"Bearer {token}"})

    # Update preferences and reason
    patch_payload = {
        "reason": "Extended Quarantine Protocols",
        "preferences": {
            "games_enabled": False,
            "emotional_support_enabled": True
        }
    }
    res = client.patch("/api/v1/emergency/mode/child-leo-1", json=patch_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["reason"] == "Extended Quarantine Protocols"
    assert data["preferences"]["games_enabled"] is False
    assert data["preferences"]["emotional_support_enabled"] is True

    # Test toggling is_active
    res2 = client.patch("/api/v1/emergency/mode/child-leo-1", json={"is_active": False}, headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    assert res2.json()["is_active"] is False


# ==============================================================================
# 4. Unauthorized Caregiver Tests (403 Forbidden)
# ==============================================================================

def test_unauthorized_caregiver_access():
    david_token = get_david_token()
    sarah_token = get_sarah_token()

    # Sarah creates emergency mode
    client.post("/api/v1/emergency/mode", json={"child_id": "child-leo-1", "duration_days": 90}, headers={"Authorization": f"Bearer {sarah_token}"})

    # David tries to get Sarah's child emergency mode
    res_get = client.get("/api/v1/emergency/mode/child-leo-1", headers={"Authorization": f"Bearer {david_token}"})
    assert res_get.status_code == 403, res_get.text
    assert "Unauthorized" in res_get.json()["detail"]

    # David tries to patch Sarah's child emergency mode
    res_patch = client.patch("/api/v1/emergency/mode/child-leo-1", json={"is_active": False}, headers={"Authorization": f"Bearer {david_token}"})
    assert res_patch.status_code == 403, res_patch.text

    # David tries to create/overwrite Sarah's child emergency mode
    res_post = client.post("/api/v1/emergency/mode", json={"child_id": "child-leo-1", "duration_days": 30}, headers={"Authorization": f"Bearer {david_token}"})
    assert res_post.status_code == 403, res_post.text

    # David tries to view Sarah's child emergency dashboard
    res_dash = client.get("/api/v1/emergency/dashboard/child-leo-1", headers={"Authorization": f"Bearer {david_token}"})
    assert res_dash.status_code == 403, res_dash.text


# ==============================================================================
# 5. Non-Existent Child Tests (404 Not Found)
# ==============================================================================

def test_non_existent_child():
    token = get_sarah_token()
    res = client.get("/api/v1/emergency/mode/child-nonexistent-999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404, res.text
    assert "not found" in res.json()["detail"].lower()

    res_post = client.post("/api/v1/emergency/mode", json={"child_id": "child-nonexistent-999", "duration_days": 90}, headers={"Authorization": f"Bearer {token}"})
    assert res_post.status_code == 404, res_post.text

    res_dash = client.get("/api/v1/emergency/dashboard/child-nonexistent-999", headers={"Authorization": f"Bearer {token}"})
    assert res_dash.status_code == 404, res_dash.text


# ==============================================================================
# 6. Invalid Dates & Validation (400 Bad Request)
# ==============================================================================

def test_invalid_dates_and_duration():
    token = get_sarah_token()
    start = datetime.now(timezone.utc)
    invalid_end = start - timedelta(days=10)

    # End date before start date
    payload_invalid_dates = {
        "child_id": "child-leo-1",
        "start_date": start.isoformat(),
        "end_date": invalid_end.isoformat(),
    }
    res = client.post("/api/v1/emergency/mode", json=payload_invalid_dates, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400, res.text
    assert "cannot be earlier" in res.json()["detail"]

    # Invalid duration_days <= 0
    payload_invalid_dur = {
        "child_id": "child-leo-1",
        "duration_days": 0,
    }
    res_dur = client.post("/api/v1/emergency/mode", json=payload_invalid_dur, headers={"Authorization": f"Bearer {token}"})
    assert res_dur.status_code in [400, 422], res_dur.text


# ==============================================================================
# 7. Expired Emergency Mode Test
# ==============================================================================

def test_expired_emergency_mode():
    token = get_sarah_token()
    past_start = datetime.now(timezone.utc) - timedelta(days=120)
    past_end = datetime.now(timezone.utc) - timedelta(days=30)

    payload = {
        "child_id": "child-leo-1",
        "start_date": past_start.isoformat(),
        "end_date": past_end.isoformat(),
        "reason": "Past emergency period",
    }
    res = client.post("/api/v1/emergency/mode", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["is_expired"] is True
    assert data["is_active"] is False
    assert data["days_remaining"] == 0


# ==============================================================================
# 8. Support Preferences Tests
# ==============================================================================

def test_support_preferences_toggle():
    token = get_sarah_token()
    # Create with specific preferences
    payload = {
        "child_id": "child-leo-1",
        "duration_days": 90,
        "preferences": {
            "communication_enabled": True,
            "learning_enabled": False,
            "emotional_support_enabled": True,
            "games_enabled": False,
            "safety_monitoring_enabled": True,
            "caregiver_notifications_enabled": True
        }
    }
    res = client.post("/api/v1/emergency/mode", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    pref = res.json()["preferences"]
    assert pref["communication_enabled"] is True
    assert pref["learning_enabled"] is False
    assert pref["games_enabled"] is False
    assert pref["safety_monitoring_enabled"] is True

    # Patch preferences
    patch_res = client.patch(
        "/api/v1/emergency/mode/child-leo-1",
        json={"preferences": {"learning_enabled": True, "games_enabled": True}},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert patch_res.status_code == 200
    updated_pref = patch_res.json()["preferences"]
    assert updated_pref["learning_enabled"] is True
    assert updated_pref["games_enabled"] is True


# ==============================================================================
# 9. Emergency Dashboard Summary Test
# ==============================================================================

def test_emergency_dashboard_summary():
    token = get_sarah_token()
    # Activate emergency mode
    client.post("/api/v1/emergency/mode", json={"child_id": "child-leo-1", "duration_days": 90}, headers={"Authorization": f"Bearer {token}"})

    res = client.get("/api/v1/emergency/dashboard/child-leo-1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["child_id"] == "child-leo-1"
    assert data["child_name"] == "Leo Mitchell"
    assert data["is_emergency_mode_active"] is True
    assert data["emergency_mode"]["duration_days"] == 90

    # Verify 4 Core pillars + Caregiver Coordination
    assert data["communication_support"]["status"] == "ACTIVE"
    assert data["communication_support"]["enabled"] is True
    assert len(data["communication_support"]["available_tools"]) >= 3

    assert data["learning_support"]["status"] == "ACTIVE"
    assert data["learning_support"]["enabled"] is True

    assert data["emotional_support"]["status"] == "ACTIVE"
    assert data["emotional_support"]["enabled"] is True

    assert data["safety_support"]["status"] == "ACTIVE"
    assert data["safety_support"]["enabled"] is True

    assert data["caregiver_coordination"]["status"] == "CONNECTED"
    assert data["caregiver_coordination"]["enabled"] is True
