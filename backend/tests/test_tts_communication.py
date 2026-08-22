import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, sync_database_schema, engine
from app.models.user import User
from app.models.child import Child
from app.core.security import create_access_token, get_password_hash

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    sync_database_schema(engine)


@pytest.fixture
def tts_setup():
    db = SessionLocal()
    try:
        # Caregiver 1
        cg1 = db.query(User).filter(User.id == "user-tts-cg1").first()
        if not cg1:
            cg1 = User(
                id="user-tts-cg1",
                email="tts_cg1@example.com",
                full_name="Amy Chen",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg1)
            db.commit()
            db.refresh(cg1)

        # Caregiver 2 (unauthorized)
        cg2 = db.query(User).filter(User.id == "user-tts-cg2").first()
        if not cg2:
            cg2 = User(
                id="user-tts-cg2",
                email="tts_cg2@example.com",
                full_name="Ben Park",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg2)
            db.commit()
            db.refresh(cg2)

        # Child (belongs to cg1)
        child = db.query(Child).filter(Child.id == "child-tts-1").first()
        if not child:
            child = Child(
                id="child-tts-1",
                name="Mia",
                age=6,
                caregiver_id=cg1.id,
            )
            db.add(child)
            db.commit()
            db.refresh(child)

        return {
            "headers_cg1": {"Authorization": f"Bearer {create_access_token(cg1.id)}"},
            "headers_cg2": {"Authorization": f"Bearer {create_access_token(cg2.id)}"},
            "child_id": child.id,
        }
    finally:
        db.close()


# ------------------------------------------------------------------------------
# 1. Valid TTS Request — Core Sentence
# ------------------------------------------------------------------------------
def test_valid_tts_request(tts_setup):
    headers = tts_setup["headers_cg1"]

    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "I want some water please.",
        "voice": "friendly_child",
        "speed": 1.0,
        "pitch": 1.0,
    }, headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["text"] == "I want some water please."
    assert data["phonetic_guide"] is not None
    assert "i" in data["phonetic_guide"]
    assert data["duration_estimate_sec"] > 0
    assert data["is_fallback"] is False
    assert data["provider"] == "web_speech_api"
    assert data["voice_used"] == "friendly_child"


# ------------------------------------------------------------------------------
# 2. SSML Hint Generated Correctly
# ------------------------------------------------------------------------------
def test_ssml_hint_generated(tts_setup):
    headers = tts_setup["headers_cg1"]

    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "I need help now.",
        "voice": "calm_female",
    }, headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["ssml_hint"] is not None
    assert "<speak>" in data["ssml_hint"]
    assert "I need help now." in data["ssml_hint"]


# ------------------------------------------------------------------------------
# 3. Web Speech Config Returned
# ------------------------------------------------------------------------------
def test_web_speech_config_returned(tts_setup):
    headers = tts_setup["headers_cg1"]

    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "I feel happy today.",
        "voice": "gentle_neutral",
        "speed": 0.9,
        "pitch": 1.1,
    }, headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["web_speech_config"] is not None
    cfg = data["web_speech_config"]
    assert "text" in cfg
    assert "lang" in cfg
    assert "rate" in cfg
    assert "pitch" in cfg
    assert cfg["text"] == "I feel happy today."


# ------------------------------------------------------------------------------
# 4. Child Authorization Enforced
# ------------------------------------------------------------------------------
def test_tts_with_authorized_child(tts_setup):
    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "I want to play.",
        "child_id": tts_setup["child_id"],
    }, headers=tts_setup["headers_cg1"])

    assert res.status_code == 200
    assert res.json()["is_fallback"] is False


def test_tts_unauthorized_caregiver(tts_setup):
    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "Hello.",
        "child_id": tts_setup["child_id"],
    }, headers=tts_setup["headers_cg2"])

    assert res.status_code == 403


def test_tts_nonexistent_child(tts_setup):
    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "Hello.",
        "child_id": "child-does-not-exist-xyz",
    }, headers=tts_setup["headers_cg1"])

    assert res.status_code == 404


# ------------------------------------------------------------------------------
# 5. Empty Text → 400 Bad Request
# ------------------------------------------------------------------------------
def test_empty_text_returns_400(tts_setup):
    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "",
    }, headers=tts_setup["headers_cg1"])

    assert res.status_code == 400


def test_whitespace_only_text_returns_400(tts_setup):
    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "   ",
    }, headers=tts_setup["headers_cg1"])

    assert res.status_code == 400


# ------------------------------------------------------------------------------
# 6. Text Too Long → 400 Bad Request
# ------------------------------------------------------------------------------
def test_text_too_long_returns_400(tts_setup):
    long_text = "I want water. " * 50  # > 500 chars
    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": long_text,
    }, headers=tts_setup["headers_cg1"])

    assert res.status_code == 400


# ------------------------------------------------------------------------------
# 7. Voice Profile Variants
# ------------------------------------------------------------------------------
def test_different_voice_profiles(tts_setup):
    headers = tts_setup["headers_cg1"]

    for voice in ["friendly_child", "calm_female", "clear_male", "gentle_neutral"]:
        res = client.post("/api/v1/communication/speech/synthesize", json={
            "text": "I need a break.",
            "voice": voice,
        }, headers=headers)

        assert res.status_code == 200, f"Failed for voice: {voice}"
        assert res.json()["voice_used"] == voice


# ------------------------------------------------------------------------------
# 8. Legacy Aliases Backward Compatibility
# ------------------------------------------------------------------------------
def test_legacy_tts_alias(tts_setup):
    headers = tts_setup["headers_cg1"]

    # Legacy /text-to-speech alias
    res = client.post("/api/v1/communication/text-to-speech", json={
        "text": "I feel tired.",
    }, headers=headers)
    assert res.status_code == 200
    assert "tired" in res.json()["text"]

    # /tts shorthand
    res_tts = client.post("/api/v1/communication/tts", json={
        "text": "I want food.",
    }, headers=headers)
    assert res_tts.status_code == 200
    assert res_tts.json()["phonetic_guide"] is not None


# ------------------------------------------------------------------------------
# 9. Duration Estimate Scales With Text Length
# ------------------------------------------------------------------------------
def test_duration_estimate_scaling(tts_setup):
    headers = tts_setup["headers_cg1"]

    res_short = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "Yes.",
    }, headers=headers)

    res_long = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "I would like to have some water and also some food please, thank you very much.",
    }, headers=headers)

    assert res_short.status_code == 200
    assert res_long.status_code == 200
    assert res_long.json()["duration_estimate_sec"] > res_short.json()["duration_estimate_sec"]


# ------------------------------------------------------------------------------
# 10. Unauthenticated Request (Optional Auth — should still work without child)
# ------------------------------------------------------------------------------
def test_unauthenticated_tts_without_child():
    res = client.post("/api/v1/communication/speech/synthesize", json={
        "text": "I am ready.",
    })
    assert res.status_code == 200
    assert res.json()["is_fallback"] is False


# ------------------------------------------------------------------------------
# 11. AAC Sentence Speech Synthesis
# ------------------------------------------------------------------------------
def test_aac_sentence_speech_synthesis(tts_setup):
    headers = tts_setup["headers_cg1"]
    res = client.post("/api/v1/communication/speech/aac", json={
        "tokens": ["I", "WANT", "WATER"],
        "voice": "friendly_child",
        "child_id": tts_setup["child_id"],
    }, headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert "water" in data["text"].lower()
    assert data["phonetic_guide"] is not None
    assert data["web_speech_config"] is not None
    assert data["is_fallback"] is False


def test_aac_sentence_speech_empty_tokens_returns_400(tts_setup):
    headers = tts_setup["headers_cg1"]
    res = client.post("/api/v1/communication/speech/aac", json={
        "tokens": [],
    }, headers=headers)
    assert res.status_code == 400


# ------------------------------------------------------------------------------
# 12. AI-Generated Sentence Speech with Emotion Prosody Modulation
# ------------------------------------------------------------------------------
def test_ai_sentence_speech_with_emotion_prosody(tts_setup):
    headers = tts_setup["headers_cg1"]
    
    # Excited tone (higher pitch / faster)
    res_excited = client.post("/api/v1/communication/speech/ai-sentence", json={
        "sentence": "I did it! I finished my puzzle!",
        "emotion": "excited",
        "child_id": tts_setup["child_id"],
    }, headers=headers)
    assert res_excited.status_code == 200
    excited_cfg = res_excited.json()["web_speech_config"]

    # Calm tone (lower / slower)
    res_calm = client.post("/api/v1/communication/speech/ai-sentence", json={
        "sentence": "I am feeling peaceful and quiet now.",
        "emotion": "calm",
        "child_id": tts_setup["child_id"],
    }, headers=headers)
    assert res_calm.status_code == 200
    calm_cfg = res_calm.json()["web_speech_config"]

    assert excited_cfg["rate"] > calm_cfg["rate"]


def test_ai_sentence_speech_empty_sentence_returns_400(tts_setup):
    headers = tts_setup["headers_cg1"]
    res = client.post("/api/v1/communication/speech/ai-sentence", json={
        "sentence": "   ",
    }, headers=headers)
    assert res.status_code == 400


# ------------------------------------------------------------------------------
# 13. AAC & AI Sentence Speech Authorization Security
# ------------------------------------------------------------------------------
def test_aac_speech_unauthorized_caregiver(tts_setup):
    res = client.post("/api/v1/communication/speech/aac", json={
        "tokens": ["HELP"],
        "child_id": tts_setup["child_id"],
    }, headers=tts_setup["headers_cg2"])
    assert res.status_code == 403


def test_ai_sentence_speech_nonexistent_child(tts_setup):
    res = client.post("/api/v1/communication/speech/ai-sentence", json={
        "sentence": "Hello world.",
        "child_id": "nonexistent-child-xyz",
    }, headers=tts_setup["headers_cg1"])
    assert res.status_code == 404

