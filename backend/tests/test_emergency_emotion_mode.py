import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, sync_database_schema, engine
from app.models.user import User
from app.models.child import Child
from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences
from app.domains.communication.models import EmotionRecord, CommunicationLog
from app.core.security import create_access_token, get_password_hash
from app.ai.emotion_ai import EmotionAI

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    sync_database_schema(engine)
    db = SessionLocal()
    try:
        db.query(EmotionRecord).delete()
        db.query(CommunicationLog).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def emergency_emotion_fixture():
    db = SessionLocal()
    try:
        # Caregiver 1 (Authorized)
        cg1 = db.query(User).filter(User.email == "sarah.emotion@nivara.app").first()
        if not cg1:
            cg1 = User(
                id="user-cg-emg-1",
                email="sarah.emotion@nivara.app",
                full_name="Sarah Miller",
                role="caregiver",
                hashed_password=get_password_hash("password123"),
            )
            db.add(cg1)
            db.commit()
            db.refresh(cg1)

        # Caregiver 2 (Unauthorized)
        cg2 = db.query(User).filter(User.email == "david.emotion@nivara.app").first()
        if not cg2:
            cg2 = User(
                id="user-cg-emg-2",
                email="david.emotion@nivara.app",
                full_name="David Clark",
                role="caregiver",
                hashed_password=get_password_hash("password123"),
            )
            db.add(cg2)
            db.commit()
            db.refresh(cg2)

        # Child 1 (Leo) -> belongs to cg1
        child1 = db.query(Child).filter(Child.id == "child-leo-emg-1").first()
        if not child1:
            child1 = Child(
                id="child-leo-emg-1",
                name="Leo Miller",
                age=8,
                caregiver_id=cg1.id,
            )
            db.add(child1)
            db.commit()
            db.refresh(child1)

        # Child 2 (Mia) -> belongs to cg2
        child2 = db.query(Child).filter(Child.id == "child-mia-emg-2").first()
        if not child2:
            child2 = Child(
                id="child-mia-emg-2",
                name="Mia Clark",
                age=6,
                caregiver_id=cg2.id,
            )
            db.add(child2)
            db.commit()
            db.refresh(child2)

        # Set up active Emergency Mode for Child 1
        db.query(EmergencyMode).filter(EmergencyMode.child_id == child1.id).delete()
        db.commit()

        emg1 = EmergencyMode(
            id="emg-leo-1",
            child_id=child1.id,
            caregiver_id=cg1.id,
            status="active",
            emergency_type="quarantine_90_days",
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=89),
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

        token1 = create_access_token(cg1.id)
        token2 = create_access_token(cg2.id)

        return {
            "headers_cg1": {"Authorization": f"Bearer {token1}"},
            "headers_cg2": {"Authorization": f"Bearer {token2}"},
            "cg1": cg1,
            "cg2": cg2,
            "child1": child1,
            "child2": child2,
            "emg1": emg1,
        }
    finally:
        db.close()


# ------------------------------------------------------------------------------
# 1. Emergency Emotion Mode Active Check-in & Summary
# ------------------------------------------------------------------------------
def test_emergency_emotion_mode_active(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]
    child_id = emergency_emotion_fixture["child1"].id

    payload = {
        "emotion": "anxious",
        "intensity": 6,
        "child_id": child_id,
        "note": "Leo missing daily school group during isolation.",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["emotion"] == "anxious"
    assert data["is_emergency_mode"] is True
    assert data["suitable_activity"] is not None
    assert data["suitable_activity"]["title"] == "Sensory Calm Down Jar & Box Breathing"
    assert any("Emergency Home Tip" in s or "Remote Caregiver" in s for s in data["calming_strategies"])

    # Test Emergency Summary endpoint
    res_summary = client.get(
        f"/api/v1/communication/emotions/emergency-summary/{child_id}",
        headers=headers,
    )
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["child_id"] == child_id
    assert summary["is_emergency_mode"] is True
    assert summary["emergency_status"] == "active"
    assert len(summary["supported_emotions"]) == 10
    assert len(summary["recommended_sensory_strategies"]) > 0
    assert len(summary["recommended_activities"]) > 0


# ------------------------------------------------------------------------------
# 2. Low Intensity Handling (1-3)
# ------------------------------------------------------------------------------
def test_low_intensity_handling(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]
    child_id = emergency_emotion_fixture["child1"].id

    payload = {
        "emotion": "calm",
        "intensity": 2,
        "child_id": child_id,
        "note": "Relaxed in quiet tent",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["intensity"] == 2
    assert data["intensity_level"] == "low"
    assert data["caregiver_alert_recommended"] is False
    assert "gentle breath" in data["immediate_calming_guidance"].lower()
    # Simple phrases for low intensity
    assert len(data["recommended_phrases"]) >= 1


# ------------------------------------------------------------------------------
# 3. Medium Intensity Handling (4-7)
# ------------------------------------------------------------------------------
def test_medium_intensity_handling(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]
    child_id = emergency_emotion_fixture["child1"].id

    payload = {
        "emotion": "frustrated",
        "intensity": 6,
        "child_id": child_id,
        "note": "Difficulty with puzzle task",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["intensity"] == 6
    assert data["intensity_level"] == "medium"
    assert data["caregiver_alert_recommended"] is False
    assert data["suitable_activity"] is not None
    assert "Kinetic Sand" in data["suitable_activity"]["title"]
    assert len(data["calming_strategies"]) >= 2


# ------------------------------------------------------------------------------
# 4. High Intensity Handling (8-10) with Urgent Guidance & Caregiver Alert
# ------------------------------------------------------------------------------
def test_high_intensity_handling(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]
    child_id = emergency_emotion_fixture["child1"].id

    payload = {
        "emotion": "overwhelmed",
        "intensity": 9,
        "child_id": child_id,
        "note": "Loud noise outside caused severe sensory distress.",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["intensity"] == 9
    assert data["intensity_level"] == "high"
    assert data["caregiver_alert_recommended"] is True
    assert "quiet place" in data["immediate_calming_guidance"].lower()
    assert any("URGENT" in p for p in data["recommended_phrases"])
    assert any("low-stimulus" in s.lower() for s in data["calming_strategies"])


# ------------------------------------------------------------------------------
# 5. AI Suggestion Generation
# ------------------------------------------------------------------------------
def test_ai_suggestion_generation(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]

    res = client.get(
        "/api/v1/communication/emotions/suggestions?emotion=angry&intensity=5",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["emotion"] == "angry"
    assert data["intensity"] == 5
    assert data["intensity_level"] == "medium"
    assert data["suitable_activity"] is not None
    assert "Sensory Dough" in data["suitable_activity"]["title"]
    assert len(data["calming_strategies"]) > 0
    assert len(data["communication_suggestions"]) > 0
    assert data["is_fallback"] is False


# ------------------------------------------------------------------------------
# 6. AI Fallback Resilience
# ------------------------------------------------------------------------------
def test_ai_fallback_resilience(monkeypatch):
    monkeypatch.setattr(EmotionAI, "EMOTION_KNOWLEDGE_BASE", None)

    fallback = EmotionAI.get_emotion_recommendations("scared", intensity=9, is_emergency_mode=True)
    assert fallback["is_fallback"] is True
    assert fallback["emotion"] == "scared"
    assert fallback["intensity_level"] == "high"
    assert fallback["caregiver_alert_recommended"] is True
    assert len(fallback["calming_strategies"]) > 0
    assert len(fallback["recommended_phrases"]) > 0
    assert fallback["suitable_activity"] is not None


# ------------------------------------------------------------------------------
# 7. Emotion Persistence & Communication Log Cross-Logging
# ------------------------------------------------------------------------------
def test_emotion_persistence_and_cross_logging(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]
    child_id = emergency_emotion_fixture["child1"].id

    payload = {
        "emotion": "happy",
        "intensity": 8,
        "child_id": child_id,
        "note": "Completed morning visual routine happily.",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    record_id = res.json()["id"]

    db = SessionLocal()
    try:
        record = db.query(EmotionRecord).filter(EmotionRecord.id == record_id).first()
        assert record is not None
        assert record.emotion == "happy"
        assert record.intensity == 8
        assert record.child_id == child_id

        # Verify cross-logging to CommunicationLog
        log = db.query(CommunicationLog).filter(
            CommunicationLog.child_id == child_id,
            CommunicationLog.source == "emotion",
        ).first()
        assert log is not None
        assert log.emotion == "happy"
    finally:
        db.close()


# ------------------------------------------------------------------------------
# 8. Emotion History Retrieval (Query & Path Parameter)
# ------------------------------------------------------------------------------
def test_emotion_history_retrieval(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]
    child_id = emergency_emotion_fixture["child1"].id

    # Create two check-ins
    client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "tired", "intensity": 4, "child_id": child_id, "note": "Rest time"},
        headers=headers,
    )
    client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "excited", "intensity": 7, "child_id": child_id, "note": "Game time"},
        headers=headers,
    )

    # Query param retrieval
    res_query = client.get(
        f"/api/v1/communication/emotions/history?child_id={child_id}",
        headers=headers,
    )
    assert res_query.status_code == 200
    items = res_query.json()
    assert len(items) >= 2
    assert items[0]["emotion"] == "excited"
    assert items[1]["emotion"] == "tired"

    # Path param retrieval
    res_path = client.get(
        f"/api/v1/communication/emotions/history/{child_id}",
        headers=headers,
    )
    assert res_path.status_code == 200
    assert len(res_path.json()) >= 2


# ------------------------------------------------------------------------------
# 9. Caregiver Authorization & Supervisory Review
# ------------------------------------------------------------------------------
def test_caregiver_authorization_and_review(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg1"]
    child_id = emergency_emotion_fixture["child1"].id

    # Create check-ins including high distress
    client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "anxious", "intensity": 9, "child_id": child_id, "note": "High distress"},
        headers=headers,
    )
    client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "calm", "intensity": 3, "child_id": child_id, "note": "Calmed down"},
        headers=headers,
    )

    # Authorized caregiver fetches review
    res = client.get(
        f"/api/v1/communication/emotions/caregiver-review/{child_id}",
        headers=headers,
    )
    assert res.status_code == 200
    review = res.json()
    assert review["child_id"] == child_id
    assert review["child_name"] == "Leo Miller"
    assert review["is_emergency_mode"] is True
    assert review["emergency_status"] == "active"
    assert review["total_checkins_count"] >= 2
    assert len(review["high_intensity_alerts"]) >= 1
    assert review["high_intensity_alerts"][0]["intensity"] == 9
    assert review["average_intensity"] > 0
    assert len(review["active_calming_strategies"]) > 0
    assert len(review["recommended_activities"]) > 0


# ------------------------------------------------------------------------------
# 10. Unauthorized Access & Missing Child Blocked
# ------------------------------------------------------------------------------
def test_unauthorized_access_and_missing_child(emergency_emotion_fixture):
    headers_cg2 = emergency_emotion_fixture["headers_cg2"]  # David Clark
    child1_id = emergency_emotion_fixture["child1"].id      # Leo Miller (belongs to Sarah)

    # 1. Unauthorized check-in -> 403 Forbidden
    res_checkin = client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "sad", "intensity": 5, "child_id": child1_id},
        headers=headers_cg2,
    )
    assert res_checkin.status_code == 403

    # 2. Unauthorized caregiver review -> 403 Forbidden
    res_review = client.get(
        f"/api/v1/communication/emotions/caregiver-review/{child1_id}",
        headers=headers_cg2,
    )
    assert res_review.status_code == 403

    # 3. Missing child -> 404 Not Found
    res_missing = client.get(
        "/api/v1/communication/emotions/caregiver-review/non-existent-child-999",
        headers=emergency_emotion_fixture["headers_cg1"],
    )
    assert res_missing.status_code == 404


# ------------------------------------------------------------------------------
# 11. Emergency Mode Inactive Behavior
# ------------------------------------------------------------------------------
def test_emergency_mode_inactive_behavior(emergency_emotion_fixture):
    headers = emergency_emotion_fixture["headers_cg2"]
    child2_id = emergency_emotion_fixture["child2"].id  # Mia has no emergency mode

    payload = {
        "emotion": "happy",
        "intensity": 5,
        "child_id": child2_id,
        "note": "Normal non-emergency check-in",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["emotion"] == "happy"
    assert data["is_emergency_mode"] is False

    # Review shows emergency mode inactive
    res_review = client.get(
        f"/api/v1/communication/emotions/caregiver-review/{child2_id}",
        headers=headers,
    )
    assert res_review.status_code == 200
    assert res_review.json()["is_emergency_mode"] is False
    assert res_review.json()["emergency_status"] == "inactive"
