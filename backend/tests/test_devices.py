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

def test_register_and_list_devices():
    headers = get_sarah_auth()

    new_device = {
        "child_id": "child-leo-1",
        "device_name": "NIVARA GPS Tracker Pendant",
        "device_type": "pendant",
        "serial_number": "PENDANT-998877",
        "battery_level": 95,
        "firmware_version": "v2.0.1",
    }
    reg_res = client.post("/api/v1/safety/devices/", json=new_device, headers=headers)
    assert reg_res.status_code == 201
    dev_data = reg_res.json()
    assert dev_data["serial_number"] == "PENDANT-998877"
    assert dev_data["device_name"] == "NIVARA GPS Tracker Pendant"

    list_res = client.get("/api/v1/safety/devices/", headers=headers)
    assert list_res.status_code == 200
    devices = list_res.json()
    assert any(d["serial_number"] == "PENDANT-998877" for d in devices)

def test_device_heartbeat_and_low_battery_trigger():
    # Heartbeat endpoint with low battery (10%)
    hb_payload = {
        "serial_number": "NIVARA-BAND-LEO-001",
        "battery_level": 10,
        "latitude": 37.7749,
        "longitude": -122.4194,
    }
    hb_res = client.post("/api/v1/safety/devices/heartbeat", json=hb_payload)
    assert hb_res.status_code == 200
    res_data = hb_res.json()
    assert res_data["battery_level"] == 10
    assert "low_battery" in res_data["events_triggered"]

    # Verify battery updated on device
    headers = get_sarah_auth()
    dev_res = client.get("/api/v1/safety/devices/dev-band-leo-1", headers=headers)
    assert dev_res.status_code == 200
    assert dev_res.json()["battery_level"] == 10
