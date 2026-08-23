import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, sync_database_schema, engine
from app.models.user import User
from app.models.child import Child
from app.models.device import Device
from app.models.location import Location
from app.models.safe_zone import SafeZone
from app.models.emergency import EmergencyAlert
from app.models.emergency_contact import EmergencyContact
from app.models.safety_event import SafetyEvent
from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences
from app.core.security import create_access_token, get_password_hash

client = TestClient(app)


@pytest.fixture
def safety_setup():
    sync_database_schema(engine)
    db = SessionLocal()
    try:
        # Caregiver 1 (Sarah Miller - Authorized)
        cg1 = db.query(User).filter(User.email == "sarah.safety@nivara.app").first()
        if not cg1:
            cg1 = User(
                id="user-safety-cg1",
                email="sarah.safety@nivara.app",
                full_name="Sarah Miller",
                role="caregiver",
                hashed_password=get_password_hash("password123"),
            )
            db.add(cg1)
            db.commit()
            db.refresh(cg1)

        # Caregiver 2 (David Clark - Unauthorized)
        cg2 = db.query(User).filter(User.email == "david.safety@nivara.app").first()
        if not cg2:
            cg2 = User(
                id="user-safety-cg2",
                email="david.safety@nivara.app",
                full_name="David Clark",
                role="caregiver",
                hashed_password=get_password_hash("password123"),
            )
            db.add(cg2)
            db.commit()
            db.refresh(cg2)

        # Child 1 (Leo) -> belongs to cg1
        child1 = db.query(Child).filter(Child.id == "child-leo-safety-1").first()
        if not child1:
            child1 = Child(
                id="child-leo-safety-1",
                name="Leo Miller",
                age=7,
                caregiver_id=cg1.id,
                current_status="safe",
            )
            db.add(child1)
            db.commit()
            db.refresh(child1)

        # Child 2 (Mia) -> belongs to cg2
        child2 = db.query(Child).filter(Child.id == "child-mia-safety-2").first()
        if not child2:
            child2 = Child(
                id="child-mia-safety-2",
                name="Mia Clark",
                age=5,
                caregiver_id=cg2.id,
                current_status="safe",
            )
            db.add(child2)
            db.commit()
            db.refresh(child2)

        # Active Emergency Mode for Child 1
        db.query(EmergencyMode).filter(EmergencyMode.child_id == child1.id).delete()
        db.commit()

        emg1 = EmergencyMode(
            id="emg-safety-leo-1",
            child_id=child1.id,
            caregiver_id=cg1.id,
            status="active",
            emergency_type="quarantine_90_days",
            start_date=datetime.now(timezone.utc) - timedelta(days=2),
            end_date=datetime.now(timezone.utc) + timedelta(days=88),
            reason="90-Day Lockdown Remote Safety Continuity",
        )
        db.add(emg1)
        db.commit()

        pref1 = EmergencySupportPreferences(
            emergency_mode_id=emg1.id,
            communication_enabled=True,
            learning_enabled=True,
            emotion_support_enabled=True,
            emotional_support_enabled=True,
            games_enabled=True,
            safety_monitoring_enabled=True,
            caregiver_notifications_enabled=True,
        )
        db.add(pref1)
        db.commit()

        # Wearable Band for Child 1
        dev1 = db.query(Device).filter(Device.id == "band-leo-safety-001").first()
        if not dev1:
            dev1 = Device(
                id="band-leo-safety-001",
                child_id=child1.id,
                device_name="Leo's SafeBand Pro",
                device_type="gps_band",
                device_identifier="NV-BAND-LEO-01",
                serial_number="NV-BAND-LEO-01",
                nfc_tag_id="NFC-LEO-SAFE-99",
                battery_level=88,
                status="active",
                is_active=True,
                is_online=True,
                connection_status="connected",
                gps_status="active",
                last_seen_at=datetime.now(timezone.utc),
            )
            db.add(dev1)
            db.commit()
            db.refresh(dev1)

        # Emergency Contacts for Child 1
        db.query(EmergencyContact).filter(EmergencyContact.child_id == child1.id).delete()
        c1 = EmergencyContact(
            id="ec-leo-1",
            user_id=cg1.id,
            child_id=child1.id,
            name="Sarah Miller (Mother)",
            relationship_type="Mother",
            phone_number="+1 (555) 987-6543",
            priority_order=1,
            is_active=True,
        )
        c2 = EmergencyContact(
            id="ec-leo-2",
            user_id=cg1.id,
            child_id=child1.id,
            name="Grandmother Elena",
            relationship_type="Grandmother",
            phone_number="+1 (555) 444-3322",
            priority_order=2,
            is_active=True,
        )
        db.add_all([c1, c2])
        db.commit()

        # Safe Zone for Child 1 (Home Perimeter)
        db.query(SafeZone).filter(SafeZone.child_id == child1.id).delete()
        sz1 = SafeZone(
            id="sz-leo-home-1",
            child_id=child1.id,
            name="Home Quarantine Perimeter",
            latitude=37.7749,
            longitude=-122.4194,
            radius=150.0,
            zone_type="home",
            is_active=True,
        )
        db.add(sz1)
        db.commit()

        # Location breadcrumbs
        db.query(Location).filter(Location.child_id == child1.id).delete()
        loc1 = Location(
            child_id=child1.id,
            latitude=37.77492,
            longitude=-122.41941,
            accuracy=4.5,
            speed=0.0,
            battery_level=88,
        )
        db.add(loc1)
        db.commit()

        token1 = create_access_token(cg1.id)
        token2 = create_access_token(cg2.id)

        return {
            "headers_cg1": {"Authorization": f"Bearer {token1}"},
            "headers_cg2": {"Authorization": f"Bearer {token2}"},
            "cg1": cg1,
            "cg2": cg2,
            "child1": child1,
            "child2": child2,
            "dev1": dev1,
            "sz1": sz1,
            "emg1": emg1,
        }
    finally:
        db.close()


# ------------------------------------------------------------------------------
# 1. Emergency Safety Mode Integration
# ------------------------------------------------------------------------------
def test_1_emergency_safety_mode(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    res = client.get(f"/api/v1/emergency/dashboard/{child_id}", headers=headers)
    assert res.status_code == 200
    dash = res.json()
    assert dash["is_emergency_mode_active"] is True
    assert dash["safety_support"]["status"] == "ACTIVE"
    assert dash["safety_support"]["enabled"] is True
    assert "SmartBand GPS & Live Location" in dash["safety_support"]["available_tools"]


# ------------------------------------------------------------------------------
# 2. GPS Tracking & Telemetry
# ------------------------------------------------------------------------------
def test_2_gps_tracking_and_telemetry(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    # Post new live GPS location
    loc_payload = {
        "child_id": child_id,
        "latitude": 37.7750,
        "longitude": -122.4195,
        "accuracy": 3.8,
        "speed": 0.5,
        "battery_level": 86,
    }
    res_loc = client.post("/api/v1/safety/location", json=loc_payload, headers=headers)
    assert res_loc.status_code == 201 or res_loc.status_code == 200

    # Retrieve latest location
    res_latest = client.get(f"/api/v1/safety/location/{child_id}", headers=headers)
    assert res_latest.status_code == 200
    latest = res_latest.json()
    assert abs(latest["latitude"] - 37.7750) < 0.001
    assert abs(latest["longitude"] - (-122.4195)) < 0.001
    assert latest["accuracy"] is not None


# ------------------------------------------------------------------------------
# 3. Wearable Band Status & Telemetry
# ------------------------------------------------------------------------------
def test_3_wearable_status_and_telemetry(safety_setup):
    headers = safety_setup["headers_cg1"]
    band_id = safety_setup["dev1"].id

    # Send wearable heartbeat
    res_hb = client.post(
        f"/api/v1/safety/bands/{band_id}/heartbeat",
        json={"battery_level": 85, "connection_status": "connected", "gps_status": "active"},
        headers=headers,
    )
    assert res_hb.status_code == 200

    # Check band status
    res_status = client.get(f"/api/v1/safety/bands/{band_id}/status", headers=headers)
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["is_online"] is True
    assert status_data["battery_level"] == 85
    assert status_data["gps_status"] == "active"


# ------------------------------------------------------------------------------
# 4. NFC Safe Emergency Identification Card
# ------------------------------------------------------------------------------
def test_4_nfc_safe_emergency_identification(safety_setup):
    nfc_tag_id = safety_setup["dev1"].nfc_tag_id

    # Public scan without auth (first responder / good samaritan)
    res = client.get(f"/api/v1/emergency/nfc-card/{nfc_tag_id}")
    assert res.status_code == 200
    card = res.json()
    assert card["nfc_tag_id"] == nfc_tag_id
    assert card["child_display_name"] == "Leo Miller"
    assert card["is_emergency_mode_active"] is True
    assert card["emergency_status"] == "active"
    assert card["caregiver_name"] == "Sarah Miller"
    assert card["caregiver_phone"] is not None
    assert len(card["emergency_contacts"]) >= 1
    assert "autistic" in card["safety_instructions"]

    # Verify a SafetyEvent was logged to alert caregiver
    db = SessionLocal()
    try:
        ev = (
            db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == safety_setup["child1"].id, SafetyEvent.event_type == "NFC_EMERGENCY_SCAN")
            .order_by(SafetyEvent.created_at.desc())
            .first()
        )
        assert ev is not None
        assert "NFC Emergency Pass Scanned" in ev.title
    finally:
        db.close()


# ------------------------------------------------------------------------------
# 5. Safe Zones & Geofencing
# ------------------------------------------------------------------------------
def test_5_safe_zones_geofencing(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    # List child safe zones
    res_list = client.get(f"/api/v1/safety/safe-zones/child/{child_id}", headers=headers)
    assert res_list.status_code == 200
    zones = res_list.json()
    assert len(zones) >= 1
    assert zones[0]["name"] == "Home Quarantine Perimeter"

    # Verify boundary coordinates
    assert abs(zones[0]["latitude"] - 37.7749) < 0.001
    assert zones[0]["radius"] >= 100.0


# ------------------------------------------------------------------------------
# 6. Separation Detection
# ------------------------------------------------------------------------------
def test_6_separation_detection(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    # Evaluate separation with distance threshold
    res_sep = client.get(
        f"/api/v1/safety/separation/{child_id}?caregiver_lat=37.7750&caregiver_lon=-122.4195&threshold_meters=50.0",
        headers=headers
    )
    assert res_sep.status_code == 200
    sep_data = res_sep.json()
    assert sep_data["child_id"] == child_id

    # Check separation status summary
    res_stat = client.get(f"/api/v1/safety/separation/{child_id}/status", headers=headers)
    assert res_stat.status_code == 200
    stat_data = res_stat.json()
    assert stat_data["child_id"] == child_id


# ------------------------------------------------------------------------------
# 7. SOS Trigger & Emergency Alert
# ------------------------------------------------------------------------------
def test_7_sos_trigger_and_alert(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    # Trigger SOS panic button
    sos_payload = {
        "child_id": child_id,
        "latitude": 37.7749,
        "longitude": -122.4194,
        "message": "Emergency SOS triggered from child wearable band during home isolation.",
    }
    res_sos = client.post("/api/v1/safety/emergency/sos", json=sos_payload, headers=headers)
    assert res_sos.status_code == 201 or res_sos.status_code == 200
    sos_data = res_sos.json()
    assert sos_data["status"] == "active"
    assert sos_data["child_id"] == child_id

    # Verify SOS status in emergency dashboard
    res_dash = client.get(f"/api/v1/emergency/dashboard/{child_id}", headers=headers)
    assert res_dash.status_code == 200
    assert res_dash.json()["sos_emergency_status"]["status"] == "ALERT_ACTIVE"


# ------------------------------------------------------------------------------
# 8. Emergency Alerts Resolution
# ------------------------------------------------------------------------------
def test_8_emergency_alert_resolution(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    db = SessionLocal()
    try:
        # Find active alert
        alert = db.query(EmergencyAlert).filter(EmergencyAlert.child_id == child_id).first()
        alert_id = alert.id if alert else None
    finally:
        db.close()

    if alert_id:
        res_resolve = client.post(
            f"/api/v1/safety/emergency/resolve/{alert_id}",
            json={"resolution_notes": "Caregiver verified child is safe and calm at home."},
            headers=headers,
        )
        assert res_resolve.status_code == 200


# ------------------------------------------------------------------------------
# 9. Caregiver Consolidated Safety Overview
# ------------------------------------------------------------------------------
def test_9_caregiver_consolidated_safety_overview(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    res = client.get(f"/api/v1/emergency/dashboard/{child_id}", headers=headers)
    assert res.status_code == 200
    dash = res.json()

    # Consolidated Safety check
    assert dash["child_id"] == child_id
    assert dash["child_name"] == "Leo Miller"
    assert dash["gps_status"] is not None
    assert dash["gps_status"]["details"]["has_live_gps"] is True
    assert dash["nfc_device_status"] is not None
    assert dash["nfc_device_status"]["details"]["battery_level"] is not None
    assert dash["caregiver_coordination"]["status"] == "CONNECTED"


# ------------------------------------------------------------------------------
# 10. Caregiver Authorization (Sarah authorized)
# ------------------------------------------------------------------------------
def test_10_caregiver_authorization(safety_setup):
    headers_cg1 = safety_setup["headers_cg1"]
    child1_id = safety_setup["child1"].id

    # Authorized caregiver Sarah fetches dashboard
    res = client.get(f"/api/v1/emergency/dashboard/{child1_id}", headers=headers_cg1)
    assert res.status_code == 200


# ------------------------------------------------------------------------------
# 11. Unauthorized Access Rejection (David blocked with 403)
# ------------------------------------------------------------------------------
def test_11_unauthorized_access_rejection(safety_setup):
    headers_cg2 = safety_setup["headers_cg2"]  # David Clark
    child1_id = safety_setup["child1"].id      # Leo Miller (Sarah's child)

    # Unauthorized dashboard access -> 403 Forbidden
    res_dash = client.get(f"/api/v1/emergency/dashboard/{child1_id}", headers=headers_cg2)
    assert res_dash.status_code == 403

    # Unauthorized mode access -> 403 Forbidden
    res_mode = client.get(f"/api/v1/emergency/mode/{child1_id}", headers=headers_cg2)
    assert res_mode.status_code == 403

    # Non-existent child -> 404 Not Found
    res_404 = client.get("/api/v1/emergency/dashboard/child-missing-9999", headers=headers_cg2)
    assert res_404.status_code == 404


# ------------------------------------------------------------------------------
# 12. Emergency Mode Active State
# ------------------------------------------------------------------------------
def test_12_emergency_mode_active_state(safety_setup):
    headers = safety_setup["headers_cg1"]
    child_id = safety_setup["child1"].id

    res = client.get(f"/api/v1/emergency/mode/{child_id}", headers=headers)
    assert res.status_code == 200
    mode = res.json()
    assert mode["is_active"] is True
    assert mode["effective_status"] == "active"
    assert mode["preferences"]["safety_monitoring_enabled"] is True


# ------------------------------------------------------------------------------
# 13. Emergency Mode Inactive State
# ------------------------------------------------------------------------------
def test_13_emergency_mode_inactive_state(safety_setup):
    headers = safety_setup["headers_cg2"]
    child2_id = safety_setup["child2"].id  # Mia has no active emergency mode

    # Safety system operates normally even without emergency mode
    res_dash = client.get(f"/api/v1/emergency/dashboard/{child2_id}", headers=headers)
    assert res_dash.status_code == 200
    dash = res_dash.json()
    assert dash is not None
    assert dash["is_emergency_mode_active"] is False
