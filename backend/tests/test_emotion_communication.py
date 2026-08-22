import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, sync_database_schema, engine
from app.models.user import User
from app.models.child import Child
from app.core.security import create_access_token, get_password_hash
from app.domains.communication.models import EmotionRecord

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    sync_database_schema(engine)
    db = SessionLocal()
    try:
        db.query(EmotionRecord).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def emotion_setup():
    db = SessionLocal()
    try:
        # Create caregiver 1
        cg1 = db.query(User).filter(User.email == "caregiver_emotion_1@example.com").first()
        if not cg1:
            cg1 = User(
                id="user-emotion-cg1",
                email="caregiver_emotion_1@example.com",
                full_name="Sarah Miller",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg1)
            db.commit()
            db.refresh(cg1)

        # Create caregiver 2 (unauthorized)
        cg2 = db.query(User).filter(User.email == "caregiver_emotion_2@example.com").first()
        if not cg2:
            cg2 = User(
                id="user-emotion-cg2",
                email="caregiver_emotion_2@example.com",
                full_name="John Davis",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg2)
            db.commit()
            db.refresh(cg2)

        # Create child for caregiver 1
        child1 = db.query(Child).filter(Child.id == "child-emotion-1").first()
        if not child1:
            child1 = Child(
                id="child-emotion-1",
                name="Leo",
                age=7,
                caregiver_id=cg1.id,
            )
            db.add(child1)
            db.commit()
            db.refresh(child1)

        token1 = create_access_token(cg1.id)
        token2 = create_access_token(cg2.id)

        return {
            "headers_cg1": {"Authorization": f"Bearer {token1}"},
            "headers_cg2": {"Authorization": f"Bearer {token2}"},
            "cg1": cg1,
            "cg2": cg2,
            "child1": child1,
        }
    finally:
        db.close()


# ------------------------------------------------------------------------------
# 1. Valid Emotion Check-in & Persistence
# ------------------------------------------------------------------------------
def test_valid_emotion_checkin(emotion_setup):
    headers = emotion_setup["headers_cg1"]
    child_id = emotion_setup["child1"].id

    payload = {
        "emotion": "anxious",
        "intensity": 7,
        "child_id": child_id,
        "note": "Leo felt uneasy during loud transition.",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["emotion"] == "anxious"
    assert data["intensity"] == 7
    assert data["child_id"] == child_id
    assert data["note"] == "Leo felt uneasy during loud transition."
    assert len(data["calming_strategies"]) > 0
    assert len(data["recommended_phrases"]) > 0
    assert data["sensory_tip"] is not None
    assert data["id"] is not None
    assert data["created_at"] is not None


# ------------------------------------------------------------------------------
# 2. High Intensity Emergency Adaptations
# ------------------------------------------------------------------------------
def test_high_intensity_emotion_adaptation(emotion_setup):
    headers = emotion_setup["headers_cg1"]
    payload = {
        "emotion": "overwhelmed",
        "intensity": 9,
        "note": "Sensory overload at cafeteria",
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["intensity"] == 9
    # High intensity anxious/overwhelmed should insert urgent calming cues
    assert any("URGENT" in phrase for phrase in data["recommended_phrases"])


# ------------------------------------------------------------------------------
# 3. Invalid Emotion Name Handling (400 Bad Request)
# ------------------------------------------------------------------------------
def test_invalid_emotion_handling(emotion_setup):
    headers = emotion_setup["headers_cg1"]
    payload = {
        "emotion": "flying_spaceship",
        "intensity": 5,
    }

    res = client.post("/api/v1/communication/emotions/checkin", json=payload, headers=headers)
    assert res.status_code == 400
    assert "invalid emotion" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 4. Intensity Bounds Validation (422 Unprocessable Entity)
# ------------------------------------------------------------------------------
def test_intensity_out_of_bounds(emotion_setup):
    headers = emotion_setup["headers_cg1"]

    # Intensity below 1
    res_low = client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "calm", "intensity": 0},
        headers=headers,
    )
    assert res_low.status_code == 422

    # Intensity above 10
    res_high = client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "calm", "intensity": 11},
        headers=headers,
    )
    assert res_high.status_code == 422


# ------------------------------------------------------------------------------
# 5. Child Authorization Checks (403 Forbidden & 404 Not Found)
# ------------------------------------------------------------------------------
def test_unauthorized_caregiver_child_checkin(emotion_setup):
    # Caregiver 2 trying to check in for Caregiver 1's child
    res = client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "frustrated", "intensity": 6, "child_id": emotion_setup["child1"].id},
        headers=emotion_setup["headers_cg2"],
    )
    assert res.status_code == 403


def test_nonexistent_child_checkin(emotion_setup):
    res = client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "happy", "intensity": 5, "child_id": "child-non-existent-9999"},
        headers=emotion_setup["headers_cg1"],
    )
    assert res.status_code == 404


# ------------------------------------------------------------------------------
# 6. Emotion History Retrieval
# ------------------------------------------------------------------------------
def test_get_emotion_history(emotion_setup):
    headers = emotion_setup["headers_cg1"]
    child_id = emotion_setup["child1"].id

    # Create two check-ins
    client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "happy", "intensity": 8, "child_id": child_id, "note": "Morning checkin"},
        headers=headers,
    )
    client.post(
        "/api/v1/communication/emotions/checkin",
        json={"emotion": "tired", "intensity": 6, "child_id": child_id, "note": "Afternoon checkin"},
        headers=headers,
    )

    # Retrieve history filtered by child
    res = client.get(
        f"/api/v1/communication/emotions/history?child_id={child_id}",
        headers=headers,
    )
    assert res.status_code == 200
    history = res.json()
    assert len(history) >= 2
    # Verify latest first
    assert history[0]["emotion"] == "tired"
    assert history[1]["emotion"] == "happy"

    # Unauthorized caregiver should not see this child's history
    res_unauth = client.get(
        f"/api/v1/communication/emotions/history?child_id={child_id}",
        headers=emotion_setup["headers_cg2"],
    )
    assert res_unauth.status_code == 403


# ------------------------------------------------------------------------------
# 7. Emotion Suggestions & Calming Tips Endpoint
# ------------------------------------------------------------------------------
def test_get_emotion_suggestions(emotion_setup):
    headers = emotion_setup["headers_cg1"]

    res = client.get(
        "/api/v1/communication/emotions/suggestions?emotion=scared&intensity=6",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["emotion"] == "scared"
    assert data["intensity"] == 6
    assert len(data["calming_strategies"]) > 0
    assert len(data["recommended_phrases"]) > 0
    assert data["sensory_tip"] is not None

    # Invalid emotion in suggestions query
    res_invalid = client.get(
        "/api/v1/communication/emotions/suggestions?emotion=unknown_xyz",
        headers=headers,
    )
    assert res_invalid.status_code == 400


# ------------------------------------------------------------------------------
# 8. Legacy Alias Endpoints
# ------------------------------------------------------------------------------
def test_legacy_emotion_endpoints(emotion_setup):
    headers = emotion_setup["headers_cg1"]

    # Legacy POST /emotion-checkin
    res = client.post(
        "/api/v1/communication/emotion-checkin",
        json={"emotion": "calm", "intensity": 5},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["emotion"] == "calm"

    # Legacy GET /emotion-history
    res_hist = client.get(
        "/api/v1/communication/emotion-history",
        headers=headers,
    )
    assert res_hist.status_code == 200

    # Legacy GET /emotion-suggestions
    res_sugg = client.get(
        "/api/v1/communication/emotion-suggestions?emotion=calm&intensity=5",
        headers=headers,
    )
    assert res_sugg.status_code == 200


# ------------------------------------------------------------------------------
# 9. All 10 Supported Emotions Verification
# ------------------------------------------------------------------------------
def test_all_ten_supported_emotions(emotion_setup):
    headers = emotion_setup["headers_cg1"]
    child_id = emotion_setup["child1"].id
    
    emotions = [
        "happy", "sad", "angry", "anxious", "calm",
        "scared", "frustrated", "overwhelmed", "tired", "excited"
    ]
    
    for em in emotions:
        res = client.post(
            "/api/v1/communication/emotions/checkin",
            json={"emotion": em, "intensity": 5, "child_id": child_id},
            headers=headers,
        )
        assert res.status_code == 200, f"Failed for emotion: {em}"
        data = res.json()
        assert data["emotion"] == em
        assert len(data["calming_strategies"]) > 0
        assert len(data["recommended_phrases"]) > 0
        assert len(data["communication_suggestions"]) > 0
        assert data["timestamp"] is not None


# ------------------------------------------------------------------------------
# 10. Emotion AI Fallback Resilience
# ------------------------------------------------------------------------------
def test_emotion_ai_fallback_resilience(monkeypatch, emotion_setup):
    from app.ai.emotion_ai import EmotionAI
    
    # Directly test the fallback mechanism when an unexpected error occurs
    def broken_get(*args, **kwargs):
        raise RuntimeError("Simulated AI service connection failure")
    
    monkeypatch.setattr(EmotionAI, "EMOTION_KNOWLEDGE_BASE", None)
    
    fallback_res = EmotionAI.get_emotion_recommendations("anxious", 8)
    assert fallback_res["is_fallback"] is True
    assert len(fallback_res["calming_strategies"]) > 0
    assert len(fallback_res["recommended_phrases"]) > 0
    assert "anxious" in fallback_res["recommended_phrases"][0]


# ------------------------------------------------------------------------------
# 11. Emotion-Aware Sentence Construction Integration
# ------------------------------------------------------------------------------
def test_emotion_aware_sentence_integration(emotion_setup):
    headers = emotion_setup["headers_cg1"]
    child_id = emotion_setup["child1"].id

    # Sentence with anxious emotion tone
    res_anxious = client.post(
        "/api/v1/communication/sentence/generate",
        json={"tokens": ["I", "NEED", "BREAK"], "emotion": "anxious", "child_id": child_id},
        headers=headers,
    )
    assert res_anxious.status_code == 200
    data_anxious = res_anxious.json()
    assert "safe" in data_anxious["generated_sentence"].lower() or "break" in data_anxious["generated_sentence"].lower()

    # Sentence with excited emotion tone
    res_excited = client.post(
        "/api/v1/communication/sentence/generate",
        json={"tokens": ["I", "WANT", "PLAY"], "emotion": "excited", "child_id": child_id},
        headers=headers,
    )
    assert res_excited.status_code == 200
    assert res_excited.json()["generated_sentence"].endswith("!")
