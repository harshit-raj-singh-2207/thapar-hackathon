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

def test_safe_zone_crud_and_containment():
    headers = get_sarah_auth()

    # 1. Create a safe zone: School
    sz_payload = {
        "child_id": "child-leo-1",
        "name": "Sunshine Academy School",
        "zone_type": "circle",
        "center_latitude": 37.7800,
        "center_longitude": -122.4200,
        "radius_meters": 250.0,
        "address": "456 Learning Blvd",
        "alert_on_exit": True,
    }
    create_res = client.post("/api/v1/safety/safe-zones/", json=sz_payload, headers=headers)
    assert create_res.status_code == 201
    zone = create_res.json()
    assert zone["name"] == "Sunshine Academy School"
    zone_id = zone["id"]

    # 2. List child safe zones (should have Home + School)
    list_res = client.get("/api/v1/safety/safe-zones/child/child-leo-1", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 2

    # 3. Test containment: Coordinate inside school
    eval_res = client.post(
        "/api/v1/safety/safe-zones/evaluate?child_id=child-leo-1&latitude=37.7801&longitude=-122.4201",
        headers=headers
    )
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["is_inside_safe_zone"] is True
    assert eval_data["active_zone_name"] == "Sunshine Academy School"

    # 4. Test containment: Coordinate far outside all safe zones
    eval_out = client.post(
        "/api/v1/safety/safe-zones/evaluate?child_id=child-leo-1&latitude=37.9000&longitude=-122.5000",
        headers=headers
    )
    assert eval_out.status_code == 200
    assert eval_out.json()["is_inside_safe_zone"] is False

    # 5. Delete safe zone
    del_res = client.delete(f"/api/v1/safety/safe-zones/{zone_id}", headers=headers)
    assert del_res.status_code == 200

def test_geofence_breach_detection_via_location():
    headers = get_sarah_auth()

    # Child location ping far outside home perimeter -> triggers breach event
    breach_ping = {
        "child_id": "child-leo-1",
        "latitude": 37.8100,  # ~4 km away
        "longitude": -122.4100,
    }
    client.post("/api/v1/safety/locations/", json=breach_ping, headers=headers)

    # Check child status changed to out_of_bounds
    curr_res = client.get("/api/v1/safety/locations/current/child-leo-1", headers=headers)
    assert curr_res.json()["is_safe"] is False

    # Check that a geofence_exit safety event was logged
    events_res = client.get("/api/v1/safety/safety-events/?event_type=geofence_exit", headers=headers)
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 1
    assert "left safe boundaries" in events[0]["title"]
