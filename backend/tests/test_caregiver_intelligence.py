from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.security import create_access_token, get_password_hash
from app.domains.communication.models import CommunicationLog, EmotionRecord
from app.domains.entitlements.models import UserSubscription
from app.domains.sensory.models import SensoryStateRecord
from app.main import app
from app.models.child import Child
from app.models.safety_event import SafetyEvent
from app.models.user import User


client = TestClient(app)


def _linked_account(db, suffix: str):
    caregiver = User(
        id=f"caregiver-insight-{suffix}",
        email=f"insight-{suffix}@example.com",
        full_name=f"Caregiver {suffix}",
        hashed_password=get_password_hash("Secret123!"),
        role="caregiver",
    )
    child = Child(
        id=f"child-insight-{suffix}",
        caregiver_id=caregiver.id,
        name=f"Child {suffix}",
        current_status="safe",
    )
    db.add_all([caregiver, child])
    db.commit()
    headers = {"Authorization": f"Bearer {create_access_token(caregiver.id)}"}
    return caregiver, child, headers


def test_linked_caregiver_has_free_basic_access(db):
    _, child, headers = _linked_account(db, "free")
    db.add(EmotionRecord(child_id=child.id, emotion="calm", intensity=6))
    db.commit()
    response = client.get(f"/api/v1/caregiver/users/{child.id}/insights", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["basic"]["current_status"] == "safe"
    assert body["basic"]["latest_emotion"]["emotion"] == "calm"
    assert body["premium_analytics_available"] is False
    assert body["premium"] is None


def test_unrelated_caregiver_is_blocked(db):
    _, child, _ = _linked_account(db, "owner")
    _, _, unrelated_headers = _linked_account(db, "other")
    response = client.get(f"/api/v1/caregiver/users/{child.id}/insights", headers=unrelated_headers)
    assert response.status_code == 403


def test_premium_caregiver_receives_deterministic_analytics(db):
    caregiver, child, headers = _linked_account(db, "premium")
    db.add_all([
        UserSubscription(user_id=caregiver.id, plan="PREMIUM", status="active"),
        EmotionRecord(child_id=child.id, emotion="happy", intensity=7),
        SensoryStateRecord(user_id=caregiver.id, sensory_state="too_noisy", intensity=5),
        CommunicationLog(child_id=child.id, sentence="Water", source="aac"),
        SafetyEvent(child_id=child.id, event_type="geofence_exit", severity="warning", title="Zone exit"),
    ])
    db.commit()
    response = client.get(f"/api/v1/caregiver/users/{child.id}/insights", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["premium_analytics_available"] is True
    assert body["premium"]["weekly"]["emotion_trends"] == {"happy": 1}
    assert body["premium"]["weekly"]["sensory_trigger_patterns"] == {"too_noisy": 1}
    assert body["premium"]["weekly"]["communication_usage_trends"] == {"aac": 1}
    assert body["premium"]["weekly"]["safety_events"] == {"geofence_exit": 1}


def test_missing_history_returns_clean_empty_analytics(db):
    caregiver, child, headers = _linked_account(db, "empty")
    db.add(UserSubscription(user_id=caregiver.id, plan="PREMIUM", status="active"))
    db.commit()
    response = client.get(f"/api/v1/caregiver/users/{child.id}/insights", headers=headers)
    assert response.status_code == 200
    weekly = response.json()["premium"]["weekly"]
    assert weekly["emotion_trends"] == {}
    assert weekly["sensory_trigger_patterns"] == {}
    assert weekly["game_progress"]["status"] == "unavailable"


def test_generated_summaries_make_no_medical_claims(db):
    caregiver, child, headers = _linked_account(db, "wording")
    db.add(UserSubscription(user_id=caregiver.id, plan="PREMIUM", status="active"))
    db.commit()
    body = client.get(f"/api/v1/caregiver/users/{child.id}/insights", headers=headers).json()
    summaries = " ".join(body["premium"]["progress_insights"]).lower()
    assert "diagnose" not in summaries
    assert "treatment" not in summaries
    assert "cure" not in summaries
    assert "observed" in summaries
