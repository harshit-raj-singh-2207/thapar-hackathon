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
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_record_child_location_and_get_current():
    headers = get_sarah_auth()

    # 1. Post a new location ping for Leo (inside home safe zone)
    payload = {
        "child_id": "child-leo-1",
        "device_id": "dev-band-leo-1",
        "latitude": 37.77495,
        "longitude": -122.41945,
        "accuracy": 3.5,
        "speed": 0.2,
        "heading": 45.0,
        "battery_level": 90.0,
        "address": "Living Room, 123 Serenity Way"
    }
    post_res = client.post("/api/v1/safety/locations/", json=payload, headers=headers)
    assert post_res.status_code == 201
    loc_data = post_res.json()
    assert loc_data["child_id"] == "child-leo-1"
    assert loc_data["latitude"] == 37.77495

    # 2. Get current location & safety status
    curr_res = client.get("/api/v1/safety/locations/current/child-leo-1", headers=headers)
    assert curr_res.status_code == 200
    curr_data = curr_res.json()
    assert curr_data["child_id"] == "child-leo-1"
    assert curr_data["is_safe"] is True
    assert curr_data["active_zone_name"] == "Home (Safe Haven)"

def test_location_history_and_bounds():
    headers = get_sarah_auth()

    # Add 3 pings
    for i in range(3):
        client.post(
            "/api/v1/safety/locations/",
            json={
                "child_id": "child-leo-1",
                "latitude": 37.7749 + (i * 0.0001),
                "longitude": -122.4194 + (i * 0.0001),
            },
            headers=headers
        )

    hist_res = client.get("/api/v1/safety/locations/history/child-leo-1?limit=10", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 3

def test_invalid_location_coordinates():
    headers = get_sarah_auth()
    invalid_payload = {
        "child_id": "child-leo-1",
        "latitude": 120.0,  # invalid latitude > 90
        "longitude": -122.4194,
    }
    res = client.post("/api/v1/safety/locations/", json=invalid_payload, headers=headers)
    assert res.status_code == 422
