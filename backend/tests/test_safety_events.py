import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine

client = TestClient(app)

def get_sarah_auth():
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_separation_check_and_event_logging():
    headers = get_sarah_auth()

    # Caregiver at (37.7749, -122.4194), Child at (37.7760, -122.4194) -> ~122 meters away > 50m threshold
    sep_payload = {
        "child_id": "child-leo-1",
        "child_lat": 37.7760,
        "child_lon": -122.4194,
        "caregiver_lat": 37.7749,
        "caregiver_lon": -122.4194,
        "threshold_meters": 50.0,
    }
    res = client.post(
        f"/api/v1/safety/separation-check?child_id={sep_payload['child_id']}&child_lat={sep_payload['child_lat']}&child_lon={sep_payload['child_lon']}&caregiver_lat={sep_payload['caregiver_lat']}&caregiver_lon={sep_payload['caregiver_lon']}&threshold_meters={sep_payload['threshold_meters']}",
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_separated"] is True
    assert data["distance_meters"] > 50

    # Verify event logged
    events_res = client.get("/api/v1/safety/safety-events/?event_type=separation_alert", headers=headers)
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 1
    event_id = events[0]["id"]
    assert events[0]["is_acknowledged"] is False

    # Acknowledge event
    ack_res = client.post(f"/api/v1/safety/safety-events/{event_id}/acknowledge", headers=headers)
    assert ack_res.status_code == 200
    assert ack_res.json()["is_acknowledged"] is True

def test_safety_overview_dashboard_endpoint():
    headers = get_sarah_auth()

    res = client.get("/api/v1/safety/overview", headers=headers)
    assert res.status_code == 200
    overviews = res.json()
    assert len(overviews) >= 1
    leo_summary = overviews[0]
    assert leo_summary["child_id"] == "child-leo-1"
    assert leo_summary["child_name"] == "Leo Mitchell"
    assert "battery_level" in leo_summary
    assert "active_safe_zones_count" in leo_summary
    assert "unacknowledged_alerts_count" in leo_summary
