import os
import sys
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def get_caregiver_token(email: str = "sarah@nivara.app", password: str = "password123") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


# ==============================================================================
# 1. Create Emergency Mode API (POST /api/v1/emergency/mode)
# ==============================================================================

def test_api_create_emergency_mode():
    token = get_caregiver_token("sarah@nivara.app")
    payload = {
        "child_id": "child-leo-1",
        "status": "active",
        "emergency_type": "pandemic_lockdown",
        "duration_days": 90,
        "reason": "Worldwide 90-Day Emergency Support Mode",
        "preferences": {
            "communication_enabled": True,
            "learning_enabled": True,
            "emotional_support_enabled": True,
            "games_enabled": True,
            "safety_monitoring_enabled": True,
            "caregiver_notifications_enabled": True
        }
    }
    res = client.post(
        "/api/v1/emergency/mode",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["status"] == "active"
    assert data["emergency_type"] == "pandemic_lockdown"
    assert data["is_active"] is True
    assert data["is_expired"] is False
    assert data["duration_days"] == 90
    assert data["days_remaining"] >= 89
    assert data["preferences"]["communication_enabled"] is True
    assert data["preferences"]["learning_enabled"] is True
    assert data["preferences"]["safety_monitoring_enabled"] is True


# ==============================================================================
# 2. Get Emergency Mode API (GET /api/v1/emergency/mode/{child_id})
# ==============================================================================

def test_api_get_emergency_mode():
    token = get_caregiver_token("sarah@nivara.app")
    # Ensure mode exists
    client.post(
        "/api/v1/emergency/mode",
        json={"child_id": "child-leo-1", "duration_days": 90},
        headers={"Authorization": f"Bearer {token}"}
    )

    res = client.get(
        "/api/v1/emergency/mode/child-leo-1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["is_active"] is True
    assert "preferences" in data
    assert data["preferences"]["caregiver_notifications_enabled"] is True


# ==============================================================================
# 3. Update Emergency Mode API (PATCH /api/v1/emergency/mode/{child_id})
# ==============================================================================

def test_api_update_emergency_mode():
    token = get_caregiver_token("sarah@nivara.app")
    # Create mode first
    client.post(
        "/api/v1/emergency/mode",
        json={"child_id": "child-leo-1", "duration_days": 90},
        headers={"Authorization": f"Bearer {token}"}
    )

    patch_payload = {
        "status": "inactive",
        "reason": "Emergency period temporarily paused",
        "preferences": {
            "games_enabled": False,
            "emotional_support_enabled": True
        }
    }
    res = client.patch(
        "/api/v1/emergency/mode/child-leo-1",
        json=patch_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "inactive"
    assert data["is_active"] is False
    assert data["reason"] == "Emergency period temporarily paused"
    assert data["preferences"]["games_enabled"] is False


# ==============================================================================
# 4. Unauthorized Caregiver Access (403 Forbidden)
# ==============================================================================

def test_api_unauthorized_caregiver_access():
    sarah_token = get_caregiver_token("sarah@nivara.app")
    david_token = get_caregiver_token("david@nivara.app")

    # Sarah creates emergency mode for child-leo-1
    client.post(
        "/api/v1/emergency/mode",
        json={"child_id": "child-leo-1", "duration_days": 90},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )

    # David attempts GET -> 403 Forbidden
    res_get = client.get(
        "/api/v1/emergency/mode/child-leo-1",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert res_get.status_code == 403, res_get.text
    assert "Unauthorized" in res_get.json()["detail"]

    # David attempts PATCH -> 403 Forbidden
    res_patch = client.patch(
        "/api/v1/emergency/mode/child-leo-1",
        json={"status": "inactive"},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert res_patch.status_code == 403, res_patch.text

    # David attempts POST for Sarah's child -> 403 Forbidden
    res_post = client.post(
        "/api/v1/emergency/mode",
        json={"child_id": "child-leo-1", "duration_days": 30},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert res_post.status_code == 403, res_post.text


# ==============================================================================
# 5. Missing Child (404 Not Found)
# ==============================================================================

def test_api_missing_child():
    token = get_caregiver_token("sarah@nivara.app")
    missing_id = "child-missing-9999"

    res_get = client.get(
        f"/api/v1/emergency/mode/{missing_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_get.status_code == 404, res_get.text
    assert "not found" in res_get.json()["detail"].lower()

    res_post = client.post(
        "/api/v1/emergency/mode",
        json={"child_id": missing_id, "duration_days": 90},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_post.status_code == 404, res_post.text

    res_patch = client.patch(
        f"/api/v1/emergency/mode/{missing_id}",
        json={"status": "active"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_patch.status_code == 404, res_patch.text


# ==============================================================================
# 6. Invalid Dates & Duration (400 Bad Request)
# ==============================================================================

def test_api_invalid_dates():
    token = get_caregiver_token("sarah@nivara.app")
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=15)

    # End date before start date
    payload_invalid = {
        "child_id": "child-leo-1",
        "start_date": now.isoformat(),
        "end_date": past.isoformat(),
    }
    res = client.post(
        "/api/v1/emergency/mode",
        json=payload_invalid,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 400, res.text
    assert "cannot be earlier" in res.json()["detail"]


# ==============================================================================
# 7. Unauthenticated Request (401 Unauthorized)
# ==============================================================================

def test_api_unauthenticated_request():
    # No Authorization header
    res_get = client.get("/api/v1/emergency/mode/child-leo-1")
    assert res_get.status_code == 401, res_get.text

    res_post = client.post("/api/v1/emergency/mode", json={"child_id": "child-leo-1"})
    assert res_post.status_code == 401, res_post.text

    # Invalid token format
    res_bad_token = client.get(
        "/api/v1/emergency/mode/child-leo-1",
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert res_bad_token.status_code == 401, res_bad_token.text
