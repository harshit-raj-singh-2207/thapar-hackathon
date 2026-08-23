import os
import sys
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.config.database import SessionLocal
from app.models.device import Device
from app.models.location import Location
from app.models.safe_zone import SafeZone
from app.models.emergency import EmergencyAlert

client = TestClient(app)

def get_caregiver_token(email: str = "sarah@nivara.app", password: str = "password123") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


# ==============================================================================
# 1. Full Dashboard Summary with Active Emergency Mode
# ==============================================================================

def test_emergency_dashboard_active_mode():
    token = get_caregiver_token("sarah@nivara.app")
    
    # 1. Activate Emergency Mode
    client.post(
        "/api/v1/emergency/mode",
        json={
            "child_id": "child-leo-1",
            "duration_days": 90,
            "reason": "Pandemic Lockdown Remote Care Protocol",
            "preferences": {
                "communication_enabled": True,
                "learning_enabled": True,
                "emotional_support_enabled": True,
                "games_enabled": True,
                "safety_monitoring_enabled": True,
                "caregiver_notifications_enabled": True,
            }
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # 2. Query Unified Dashboard
    res = client.get(
        "/api/v1/emergency/dashboard/child-leo-1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200, res.text
    data = res.json()

    # Child Information
    assert data["child_id"] == "child-leo-1"
    assert data["child_name"] == "Leo Mitchell"
    assert data["current_status"] in ["safe", "normal", "active"]


    # Emergency Mode Status
    assert data["is_emergency_mode_active"] is True
    assert data["emergency_mode"] is not None
    assert data["emergency_mode"]["duration_days"] == 90
    assert data["emergency_mode"]["days_remaining"] >= 89

    # Communication & AAC Status
    assert data["communication_support"]["status"] == "ACTIVE"
    assert data["communication_support"]["enabled"] is True
    assert len(data["communication_support"]["available_tools"]) > 0

    # Learning & AI Tutor Status
    assert data["learning_support"]["status"] == "ACTIVE"
    assert data["learning_support"]["enabled"] is True
    assert "AI Personalized Tutor" in data["learning_support"]["available_tools"]

    # Emotion Support Status
    assert data["emotional_support"]["status"] == "ACTIVE"
    assert data["emotional_support"]["enabled"] is True
    assert "Sensory Calming Soundscapes" in data["emotional_support"]["available_tools"]

    # Games Status
    assert data["games_support"]["status"] == "ACTIVE"
    assert data["games_support"]["enabled"] is True

    # GPS Status
    assert data["gps_status"] is not None
    assert data["gps_status"]["enabled"] is True

    # NFC / Wearable Device Status
    assert data["nfc_device_status"] is not None
    assert "NFC Emergency Profile Pass" in data["nfc_device_status"]["available_tools"]

    # SOS / Emergency Status
    assert data["sos_emergency_status"] is not None
    assert data["sos_emergency_status"]["status"] in ["NORMAL", "ALERT_ACTIVE"]

    # Caregiver Coordination & Notifications
    assert data["caregiver_coordination"]["status"] == "CONNECTED"
    assert data["caregiver_coordination"]["enabled"] is True


# ==============================================================================
# 2. Dashboard with Inactive / Disabled Modules
# ==============================================================================

def test_emergency_dashboard_toggled_preferences():
    token = get_caregiver_token("sarah@nivara.app")

    # Ensure emergency mode exists first
    client.post(
        "/api/v1/emergency/mode",
        json={"child_id": "child-leo-1", "duration_days": 90},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Update preferences: disable games and communication
    patch_res = client.patch(
        "/api/v1/emergency/mode/child-leo-1",
        json={
            "preferences": {
                "communication_enabled": False,
                "games_enabled": False,
                "caregiver_notifications_enabled": False,
            }
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert patch_res.status_code == 200, patch_res.text
    patch_data = patch_res.json()
    assert patch_data["preferences"]["communication_enabled"] is False
    assert patch_data["preferences"]["games_enabled"] is False

    res = client.get(
        "/api/v1/emergency/dashboard/child-leo-1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200, res.text
    data = res.json()

    assert data["communication_support"]["status"] == "DISABLED"
    assert data["communication_support"]["enabled"] is False
    assert data["games_support"]["status"] == "DISABLED"
    assert data["games_support"]["enabled"] is False
    assert data["caregiver_coordination"]["status"] == "MUTED"
    assert data["caregiver_coordination"]["enabled"] is False


# ==============================================================================
# 3. Dashboard with Inactive / Expired Emergency Mode
# ==============================================================================

def test_emergency_dashboard_inactive_and_expired_mode():
    token = get_caregiver_token("sarah@nivara.app")

    # Ensure emergency mode exists first
    client.post(
        "/api/v1/emergency/mode",
        json={"child_id": "child-leo-1", "duration_days": 90},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Set mode inactive
    client.patch(
        "/api/v1/emergency/mode/child-leo-1",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"}
    )


    res = client.get(
        "/api/v1/emergency/dashboard/child-leo-1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["is_emergency_mode_active"] is False

    # Create expired mode (past end_date)
    now = datetime.now(timezone.utc)
    client.post(
        "/api/v1/emergency/mode",
        json={
            "child_id": "child-leo-1",
            "start_date": (now - timedelta(days=95)).isoformat(),
            "end_date": (now - timedelta(days=5)).isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    res_expired = client.get(
        "/api/v1/emergency/dashboard/child-leo-1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_expired.status_code == 200, res_expired.text
    data_expired = res_expired.json()
    assert data_expired["emergency_mode"]["is_expired"] is True
    assert data_expired["emergency_mode"]["days_remaining"] == 0
    assert data_expired["is_emergency_mode_active"] is False


# ==============================================================================
# 4. Error Handling: Missing Child, Unauthorized Caregiver, Unauthenticated
# ==============================================================================

def test_emergency_dashboard_authorization_and_errors():
    sarah_token = get_caregiver_token("sarah@nivara.app")
    david_token = get_caregiver_token("david@nivara.app")

    # 404 Missing Child
    res_404 = client.get(
        "/api/v1/emergency/dashboard/child-unknown-404",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res_404.status_code == 404, res_404.text

    # 403 Unauthorized Caregiver (David accessing Sarah's child)
    res_403 = client.get(
        "/api/v1/emergency/dashboard/child-leo-1",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert res_403.status_code == 403, res_403.text

    # 401 Unauthenticated Request
    res_401 = client.get("/api/v1/emergency/dashboard/child-leo-1")
    assert res_401.status_code == 401, res_401.text
