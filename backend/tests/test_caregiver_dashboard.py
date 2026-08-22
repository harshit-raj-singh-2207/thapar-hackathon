import os
import sys
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.child import Child
from app.models.location import Location
from app.models.device import Device
from app.models.safe_zone import SafeZone
from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent

client = TestClient(app)

def get_sarah_token():
    """Sarah is caregiver for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]

def get_david_token():
    """David is caregiver, but NOT for child-leo-1."""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]

# 1. Child Profile Endpoint
def test_get_child_profile():
    token = get_sarah_token()
    res = client.get("/api/v1/caregiver/child-leo-1/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["name"] == "Leo Mitchell"
    assert data["caregiver_id"] == "user-verified-sarah"
    assert data["account_status"] == "active"
    assert data["tracking_enabled"] is True

# 2. Child Status Endpoint
def test_get_child_status():
    token = get_sarah_token()
    res = client.get("/api/v1/caregiver/child-leo-1/status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["name"] == "Leo Mitchell"
    assert data["current_status"] in ["safe", "out_of_bounds", "separation_alert", "emergency"]
    assert "is_online" in data
    assert "safe_zone_status" in data
    assert "emergency_status" in data

# 3. Child Location Endpoint
def test_get_child_location_endpoint():
    token = get_sarah_token()
    res = client.get("/api/v1/caregiver/child-leo-1/location", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert "location_available" in data
    assert "status" in data

# 4. Device Status Endpoint
def test_get_child_device_endpoint():
    token = get_sarah_token()
    res = client.get("/api/v1/caregiver/child-leo-1/device", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "connection_status" in data
    assert "is_online" in data
    assert "battery_status" in data

# 5. Safety Overview Full Aggregation
def test_get_safety_overview():
    token = get_sarah_token()
    res = client.get("/api/v1/caregiver/child-leo-1/safety-overview", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "child" in data
    assert "location" in data
    assert "device" in data
    assert "safety" in data
    assert "emergency" in data
    assert "alerts" in data
    assert "events" in data
    assert data["child"]["name"] == "Leo Mitchell"

# 6. Recent Activity Endpoint
def test_get_recent_activity():
    token = get_sarah_token()
    db = SessionLocal()
    ev1 = SafetyEvent(
        child_id="child-leo-1",
        event_type="geofence_entry",
        severity="info",
        title="Entered Safe Zone",
        description="Entered Home Sanctuary",
        created_at=datetime.now(timezone.utc) - timedelta(minutes=10)
    )
    ev2 = SafetyEvent(
        child_id="child-leo-1",
        event_type="low_battery",
        severity="warning",
        title="Band Battery Low",
        description="Band at 15%",
        created_at=datetime.now(timezone.utc) - timedelta(minutes=2)
    )
    db.add_all([ev1, ev2])
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/recent-activity?limit=10", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 2
    # Ensure newest first
    assert events[0]["event_type"] == "low_battery"
    assert events[1]["event_type"] == "geofence_entry"

# 7. Alert Summary Endpoint
def test_get_alert_summary():
    token = get_sarah_token()
    db = SessionLocal()
    ev1 = SafetyEvent(
        child_id="child-leo-1",
        event_type="sos_triggered",
        severity="critical",
        title="SOS Emergency Alert",
        is_acknowledged=False,
    )
    ev2 = SafetyEvent(
        child_id="child-leo-1",
        event_type="separation_alert",
        severity="warning",
        title="Separation Warning",
        is_acknowledged=True,
    )
    ev3 = SafetyEvent(
        child_id="child-leo-1",
        event_type="device_offline",
        severity="info",
        title="Device Disconnected",
        is_acknowledged=False,
    )
    db.add_all([ev1, ev2, ev3])
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/alerts/summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_alerts"] >= 3
    assert summary["unread_alerts"] >= 2
    assert summary["critical_alerts"] >= 1
    assert summary["warning_alerts"] >= 1
    assert summary["info_alerts"] >= 1

# 8. Unauthenticated Request (401)
def test_unauthenticated_requests():
    assert client.get("/api/v1/caregiver/child-leo-1/profile").status_code == 401
    assert client.get("/api/v1/caregiver/child-leo-1/status").status_code == 401
    assert client.get("/api/v1/caregiver/child-leo-1/location").status_code == 401
    assert client.get("/api/v1/caregiver/child-leo-1/device").status_code == 401
    assert client.get("/api/v1/caregiver/child-leo-1/safety-overview").status_code == 401
    assert client.get("/api/v1/caregiver/child-leo-1/recent-activity").status_code == 401
    assert client.get("/api/v1/caregiver/child-leo-1/alerts/summary").status_code == 401

# 9. Unauthorized Caregiver (403)
def test_unauthorized_caregiver_access():
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}
    # David trying to access Sarah's child Leo
    assert client.get("/api/v1/caregiver/child-leo-1/profile", headers=headers).status_code == 403
    assert client.get("/api/v1/caregiver/child-leo-1/status", headers=headers).status_code == 403
    assert client.get("/api/v1/caregiver/child-leo-1/location", headers=headers).status_code == 403
    assert client.get("/api/v1/caregiver/child-leo-1/device", headers=headers).status_code == 403
    assert client.get("/api/v1/caregiver/child-leo-1/safety-overview", headers=headers).status_code == 403
    assert client.get("/api/v1/caregiver/child-leo-1/recent-activity", headers=headers).status_code == 403
    assert client.get("/api/v1/caregiver/child-leo-1/alerts/summary", headers=headers).status_code == 403

# 10. Non-existent Child (404)
def test_non_existent_child_404():
    sarah_token = get_sarah_token()
    headers = {"Authorization": f"Bearer {sarah_token}"}
    assert client.get("/api/v1/caregiver/child-nonexistent/profile", headers=headers).status_code == 404
    assert client.get("/api/v1/caregiver/child-nonexistent/status", headers=headers).status_code == 404
    assert client.get("/api/v1/caregiver/child-nonexistent/location", headers=headers).status_code == 404
    assert client.get("/api/v1/caregiver/child-nonexistent/device", headers=headers).status_code == 404
    assert client.get("/api/v1/caregiver/child-nonexistent/safety-overview", headers=headers).status_code == 404
    assert client.get("/api/v1/caregiver/child-nonexistent/recent-activity", headers=headers).status_code == 404
    assert client.get("/api/v1/caregiver/child-nonexistent/alerts/summary", headers=headers).status_code == 404

# 11. Authorized Caregiver (200)
def test_authorized_caregiver_access():
    sarah_token = get_sarah_token()
    headers = {"Authorization": f"Bearer {sarah_token}"}
    res = client.get("/api/v1/caregiver/child-leo-1/profile", headers=headers)
    assert res.status_code == 200

# 12. Child with Fresh GPS Location
def test_child_with_gps_location():
    token = get_sarah_token()
    db = SessionLocal()
    loc = Location(
        child_id="child-leo-1",
        latitude=37.7749,
        longitude=-122.4194,
        accuracy=5.0,
        source="gps",
        recorded_at=datetime.now(timezone.utc),
    )
    db.add(loc)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/location", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["location_available"] is True
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["accuracy"] == 5.0
    assert data["status"] == "fresh"

# 13. Child without Current GPS (Unavailable)
def test_child_without_current_gps():
    david_token = get_david_token()
    db = SessionLocal()
    child_no_gps = Child(
        id="child-david-no-gps",
        caregiver_id="user-verified-david",
        name="Sammy Nguyen",
        age=4,
        gender="Male",
        tracking_enabled=True,
        current_status="safe",
    )
    db.add(child_no_gps)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-david-no-gps/location", headers={"Authorization": f"Bearer {david_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["location_available"] is False
    assert data["status"] == "unavailable"

# 14. Child with Stale / Last Known Location
def test_child_with_only_last_known_location():
    david_token = get_david_token()
    db = SessionLocal()
    child_stale = Child(
        id="child-david-stale",
        caregiver_id="user-verified-david",
        name="Jenny Nguyen",
        age=9,
        gender="Female",
        tracking_enabled=True,
        current_status="safe",
    )
    # Stale location from 2 hours ago
    loc = Location(
        child_id="child-david-stale",
        latitude=37.7800,
        longitude=-122.4100,
        accuracy=15.0,
        source="cell",
        recorded_at=datetime.now(timezone.utc) - timedelta(hours=2),
    )
    db.add_all([child_stale, loc])
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-david-stale/location", headers={"Authorization": f"Bearer {david_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["location_available"] is True
    assert data["latitude"] == 37.7800
    assert data["status"] == "stale"

# 15. Child with Connected Band
def test_child_with_connected_band():
    token = get_sarah_token()
    db = SessionLocal()
    dev = db.query(Device).filter(Device.child_id == "child-leo-1").first()
    if not dev:
        dev = Device(
            id="band-leo-1",
            child_id="child-leo-1",
            device_identifier="BAND-LEO-001",
            device_name="Leo's Smart Band",
            device_type="gps_band",
        )
        db.add(dev)
    dev.connection_status = "connected"
    dev.is_online = True
    dev.battery_level = 85
    dev.gps_status = "active"
    dev.last_seen = datetime.now(timezone.utc)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/device", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["connection_status"] == "connected"
    assert data["is_online"] is True
    assert data["battery_level"] == 85
    assert data["battery_status"] == "good"

# 16. Child with Disconnected Band
def test_child_with_disconnected_band():
    token = get_sarah_token()
    db = SessionLocal()
    dev = db.query(Device).filter(Device.child_id == "child-leo-1").first()
    if not dev:
        dev = Device(
            id="band-leo-2",
            child_id="child-leo-1",
            device_identifier="BAND-LEO-002",
            device_name="Leo's Band",
            device_type="gps_band",
        )
        db.add(dev)
    dev.connection_status = "disconnected"
    dev.is_online = False
    dev.battery_level = 40
    dev.gps_status = "inactive"
    dev.last_seen = datetime.now(timezone.utc) - timedelta(minutes=30)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/device", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["connection_status"] == "disconnected"
    assert data["is_online"] is False

# 17. Child with Low Battery
def test_child_with_low_battery():
    token = get_sarah_token()
    db = SessionLocal()
    dev = db.query(Device).filter(Device.child_id == "child-leo-1").first()
    if not dev:
        dev = Device(
            id="band-leo-3",
            child_id="child-leo-1",
            device_identifier="BAND-LEO-003",
            device_name="Leo's Band",
            device_type="gps_band",
        )
        db.add(dev)
    dev.connection_status = "connected"
    dev.is_online = True
    dev.battery_level = 8
    dev.gps_status = "active"
    dev.last_seen = datetime.now(timezone.utc)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/device", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["battery_level"] == 8
    assert data["battery_status"] == "critical"

# 18. Child with Active SOS Emergency
def test_child_with_active_sos():
    token = get_sarah_token()
    db = SessionLocal()
    emg = EmergencyAlert(
        id="emg-sos-99",
        child_id="child-leo-1",
        triggered_by="child",
        status="active",
        severity="critical",
        message="Child pressed SOS panic button",
        latitude=37.7749,
        longitude=-122.4194,
    )
    db.add(emg)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["emergency_status"] == "active"
    assert data["active_emergency_id"] == "emg-sos-99"

# 19. Child with Active Separation
def test_child_with_active_separation():
    token = get_sarah_token()
    db = SessionLocal()
    dev = db.query(Device).filter(Device.child_id == "child-leo-1").first()
    if not dev:
        dev = Device(
            id="band-leo-sep",
            child_id="child-leo-1",
            device_identifier="BAND-SEP",
            device_type="gps_band",
        )
        db.add(dev)
    dev.connection_status = "disconnected"
    dev.is_online = False
    dev.battery_level = 50
    dev.last_seen = datetime.now(timezone.utc) - timedelta(minutes=10)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_separated"] is True

# 20. Child with Safe Zone Status
def test_child_with_safe_zone_status():
    token = get_sarah_token()
    db = SessionLocal()
    sz = db.query(SafeZone).filter(SafeZone.child_id == "child-leo-1").first()
    if not sz:
        sz = SafeZone(
            id="sz-home-1",
            child_id="child-leo-1",
            name="Home Safe Zone",
            center_latitude=37.7749,
            center_longitude=-122.4194,
            radius_meters=200.0,
            is_active=True,
        )
        db.add(sz)
    loc = Location(
        child_id="child-leo-1",
        latitude=37.7749,
        longitude=-122.4194,
        accuracy=5.0,
        source="gps",
        recorded_at=datetime.now(timezone.utc),
    )
    db.add(loc)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["safe_zone_status"] == "inside"

# 21. Child with Alerts & Safety Events
def test_child_with_alerts_and_events():
    token = get_sarah_token()
    db = SessionLocal()
    ev = SafetyEvent(
        id="ev-alert-1",
        child_id="child-leo-1",
        event_type="geofence_exit",
        severity="warning",
        title="Safe Zone Breached",
        description="Leo exited Home Safe Zone",
        is_acknowledged=False,
    )
    db.add(ev)
    db.commit()
    db.close()

    # Test summary
    summary_res = client.get("/api/v1/caregiver/child-leo-1/alerts/summary", headers={"Authorization": f"Bearer {token}"})
    assert summary_res.status_code == 200
    assert summary_res.json()["total_alerts"] >= 1

    # Test overview
    overview_res = client.get("/api/v1/caregiver/child-leo-1/safety-overview", headers={"Authorization": f"Bearer {token}"})
    assert overview_res.status_code == 200
    assert len(overview_res.json()["events"]) >= 1

# 22. Child with No Alerts/Events
def test_child_with_no_alerts_or_events():
    david_token = get_david_token()
    db = SessionLocal()
    child_clean = Child(
        id="child-david-clean",
        caregiver_id="user-verified-david",
        name="Oliver Nguyen",
        age=3,
        tracking_enabled=True,
        current_status="safe",
    )
    db.add(child_clean)
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-david-clean/alerts/summary", headers={"Authorization": f"Bearer {david_token}"})
    assert res.status_code == 200
    assert res.json()["total_alerts"] == 0
    assert res.json()["unread_alerts"] == 0

# 23. Safety Overview when Child is Completely Populated
def test_safety_overview_fully_populated():
    token = get_sarah_token()
    db = SessionLocal()
    loc = Location(
        child_id="child-leo-1",
        latitude=37.7749,
        longitude=-122.4194,
        accuracy=4.0,
        source="gps",
        recorded_at=datetime.now(timezone.utc),
    )
    dev = db.query(Device).filter(Device.child_id == "child-leo-1").first()
    if not dev:
        dev = Device(
            id="band-leo-full",
            child_id="child-leo-1",
            device_identifier="BAND-FULL",
            device_name="Leo Band",
            device_type="gps_band",
        )
        db.add(dev)
    dev.connection_status = "connected"
    dev.is_online = True
    dev.battery_level = 90
    dev.gps_status = "active"
    dev.last_seen = datetime.now(timezone.utc)

    ev = SafetyEvent(
        id="ev-full-1",
        child_id="child-leo-1",
        event_type="geofence_entry",
        severity="info",
        title="Safe Zone Entry",
        is_acknowledged=True,
    )
    db.add_all([loc, ev])
    db.commit()
    db.close()

    res = client.get("/api/v1/caregiver/child-leo-1/safety-overview", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["child"]["name"] == "Leo Mitchell"
    assert data["location"]["latitude"] == 37.7749
    assert data["device"]["battery_level"] == 90
    assert data["alerts"]["total"] >= 1
    assert len(data["events"]) >= 1
