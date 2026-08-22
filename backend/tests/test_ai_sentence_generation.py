import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, sync_database_schema, engine
from app.models.user import User
from app.models.child import Child
from app.core.security import create_access_token, get_password_hash
from app.domains.communication.models import CommunicationLog

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    sync_database_schema(engine)
    db = SessionLocal()
    try:
        db.query(CommunicationLog).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def ai_comm_setup():
    db = SessionLocal()
    try:
        # Caregiver 1 (Sarah)
        cg1 = db.query(User).filter(User.id == "user-ai-cg1").first()
        if not cg1:
            cg1 = User(
                id="user-ai-cg1",
                email="caregiver_ai_1@example.com",
                full_name="Sarah Miller",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg1)
            db.commit()
            db.refresh(cg1)

        # Caregiver 2 (David - unauthorized for Child 1)
        cg2 = db.query(User).filter(User.id == "user-ai-cg2").first()
        if not cg2:
            cg2 = User(
                id="user-ai-cg2",
                email="caregiver_ai_2@example.com",
                full_name="David Nguyen",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg2)
            db.commit()
            db.refresh(cg2)

        # Child 1 (belongs to Sarah)
        child1 = db.query(Child).filter(Child.id == "child-ai-1").first()
        if not child1:
            child1 = Child(
                id="child-ai-1",
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
# 1. Valid AAC Token Expansion to Natural Sentence
# ------------------------------------------------------------------------------
def test_generate_sentence_from_aac_tokens(ai_comm_setup):
    headers = ai_comm_setup["headers_cg1"]
    child_id = ai_comm_setup["child1"].id

    payload = {
        "tokens": ["I", "WANT", "WATER"],
        "child_id": child_id,
        "emotion": "calm",
        "style": "natural",
    }

    res = client.post("/api/v1/communication/sentence/generate", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "water" in data["generated_sentence"].lower()
    assert data["simplified_sentence"] == "I want water."
    assert len(data["suggestions"]) > 0
    assert data["raw_tokens"] == ["I", "WANT", "WATER"]
    assert data["is_fallback"] is False
    assert data["log_id"] is not None


# ------------------------------------------------------------------------------
# 2. Emotion Modifier in Sentence Generation
# ------------------------------------------------------------------------------
def test_generate_sentence_with_emotion_tone(ai_comm_setup):
    headers = ai_comm_setup["headers_cg1"]

    payload = {
        "tokens": ["I", "FEEL", "TIRED"],
        "emotion": "tired",
    }

    res = client.post("/api/v1/communication/sentence/generate", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "tired" in data["generated_sentence"].lower()
    assert data["simplified_sentence"] == "I feel tired."


# ------------------------------------------------------------------------------
# 3. Text Simplification into Child-Friendly Steps & AAC Tokens
# ------------------------------------------------------------------------------
def test_simplify_complex_text(ai_comm_setup):
    headers = ai_comm_setup["headers_cg1"]

    payload = {
        "text": "Please walk over to the sink immediately because you must wash your hands and then drink water.",
        "target_level": "easy",
    }

    res = client.post("/api/v1/communication/sentence/simplify", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["original_text"] == payload["text"]
    assert "Drink water" in data["key_points"]
    assert "WATER" in data["matching_aac_tokens"]
    assert len(data["suggestions"]) > 0
    assert data["is_fallback"] is False


# ------------------------------------------------------------------------------
# 4. Empty Input Handling & Deterministic Fallback
# ------------------------------------------------------------------------------
def test_empty_tokens_fallback(ai_comm_setup):
    headers = ai_comm_setup["headers_cg1"]

    res = client.post("/api/v1/communication/sentence/generate", json={"tokens": []}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_fallback"] is True
    assert len(data["generated_sentence"]) > 0
    assert len(data["suggestions"]) > 0


def test_empty_text_simplification_fallback(ai_comm_setup):
    headers = ai_comm_setup["headers_cg1"]

    res = client.post("/api/v1/communication/sentence/simplify", json={"text": ""}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_fallback"] is True
    assert data["simplified_text"] == "Please speak simply."


# ------------------------------------------------------------------------------
# 5. Child Authorization & Security Checks
# ------------------------------------------------------------------------------
def test_unauthorized_caregiver_child_generation(ai_comm_setup):
    # Caregiver 2 attempts to generate for Caregiver 1's child
    res = client.post(
        "/api/v1/communication/sentence/generate",
        json={"tokens": ["I", "WANT", "PLAY"], "child_id": ai_comm_setup["child1"].id},
        headers=ai_comm_setup["headers_cg2"],
    )
    assert res.status_code == 403


def test_nonexistent_child_generation(ai_comm_setup):
    res = client.post(
        "/api/v1/communication/sentence/generate",
        json={"tokens": ["I", "NEED", "HELP"], "child_id": "child-nonexistent-12345"},
        headers=ai_comm_setup["headers_cg1"],
    )
    assert res.status_code == 404


# ------------------------------------------------------------------------------
# 6. Legacy & Alias Endpoints Backward Compatibility
# ------------------------------------------------------------------------------
def test_legacy_sentence_endpoints(ai_comm_setup):
    headers = ai_comm_setup["headers_cg1"]

    # Legacy POST /build-sentence
    res_build = client.post(
        "/api/v1/communication/build-sentence",
        json={"tokens": ["I", "WANT", "TOILET"]},
        headers=headers,
    )
    assert res_build.status_code == 200
    assert "restroom" in res_build.json()["generated_sentence"].lower() or "bathroom" in res_build.json()["generated_sentence"].lower()

    # Legacy POST /simplify-text
    res_simp = client.post(
        "/api/v1/communication/simplify-text",
        json={"text": "It is time to eat food."},
        headers=headers,
    )
    assert res_simp.status_code == 200
    assert "FOOD" in res_simp.json()["matching_aac_tokens"]
