from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.security import create_access_token, get_password_hash
from app.domains.caregivers.models import CaregiverPrivacySettings
from app.domains.entitlements.models import UserSubscription
from app.main import app
from app.models.child import Child
from app.models.location import Location
from app.models.safety_event import SafetyEvent
from app.models.user import User


client = TestClient(app)


def _account(db, suffix: str):
    user = User(
        id=f"user-safety-{suffix}",
        email=f"safety-{suffix}@example.com",
        full_name=f"Safety {suffix}",
        hashed_password=get_password_hash("Secret123!"),
        role="caregiver",
    )
    child = Child(
        id=f"child-safety-{suffix}",
        caregiver_id=user.id,
        name=f"Child {suffix}",
        current_status="safe",
    )
    db.add_all([user, child])
    db.commit()
    return user, child, {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _zone(child_id: str, name: str, latitude: float = 30.0):
    return {
        "child_id": child_id,
        "name": name,
        "latitude": latitude,
        "longitude": 76.0,
        "radius": 150.0,
        "alert_on_exit": True,
    }


def test_sos_remains_free_without_subscription(db):
    _, child, headers = _account(db, "sos-free")
    response = client.post(
        "/api/v1/safety/emergency/sos",
        json={"child_id": child.id, "message": "Explicit SOS"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_free_plan_can_create_one_safe_zone(db):
    _, child, headers = _account(db, "one-zone")
    response = client.post(
        "/api/v1/safety/safe-zones/",
        json=_zone(child.id, "Home"),
        headers=headers,
    )
    assert response.status_code == 201


def test_free_plan_is_denied_second_safe_zone(db):
    _, child, headers = _account(db, "zone-limit")
    first = client.post(
        "/api/v1/safety/safe-zones/", json=_zone(child.id, "Home"), headers=headers
    )
    second = client.post(
        "/api/v1/safety/safe-zones/",
        json=_zone(child.id, "School", 30.01),
        headers=headers,
    )
    assert first.status_code == 201
    assert second.status_code == 403
    assert second.json()["detail"]["free_limit"] == 1


def test_premium_plan_can_create_multiple_safe_zones(db):
    user, child, headers = _account(db, "multi-zone")
    db.add(UserSubscription(user_id=user.id, plan="PREMIUM", status="active"))
    db.commit()
    first = client.post(
        "/api/v1/safety/safe-zones/", json=_zone(child.id, "Home"), headers=headers
    )
    second = client.post(
        "/api/v1/safety/safe-zones/",
        json=_zone(child.id, "School", 30.01),
        headers=headers,
    )
    assert first.status_code == 201
    assert second.status_code == 201


def test_unrelated_caregiver_cannot_access_safe_zone_or_location(db):
    _, child, owner_headers = _account(db, "owned")
    _, _, unrelated_headers = _account(db, "unrelated")
    client.post(
        "/api/v1/safety/safe-zones/",
        json=_zone(child.id, "Home"),
        headers=owner_headers,
    )
    zones = client.get(
        f"/api/v1/safety/safe-zones/child/{child.id}", headers=unrelated_headers
    )
    location = client.get(
        f"/api/v1/safety/locations/current/{child.id}", headers=unrelated_headers
    )
    assert zones.status_code == 403
    assert location.status_code == 403


def test_location_privacy_blocks_coordinate_response(db):
    user, child, headers = _account(db, "private-location")
    db.add_all([
        CaregiverPrivacySettings(user_id=user.id, show_location=False),
        Location(
            child_id=child.id,
            latitude=30.2,
            longitude=76.3,
            recorded_at=datetime.now(timezone.utc),
        ),
    ])
    db.commit()
    response = client.get(
        f"/api/v1/safety/locations/current/{child.id}", headers=headers
    )
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_local_geofence_exit_creates_wandering_alert(db):
    _, child, headers = _account(db, "wander")
    created = client.post(
        "/api/v1/safety/safe-zones/",
        json=_zone(child.id, "Home"),
        headers=headers,
    )
    assert created.status_code == 201
    response = client.post(
        f"/api/v1/safety/safe-zones/{child.id}/check"
        "?latitude=31.0&longitude=77.0&create_events=true",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "out_of_bounds"
    event = db.query(SafetyEvent).filter(
        SafetyEvent.child_id == child.id,
        SafetyEvent.event_type == "geofence_exit",
    ).first()
    assert event is not None
