import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.ai.communication_ai import CommunicationAI

client = TestClient(app)

def get_auth_token(email: str = "sarah@nivara.app", password: str = "password123") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


# ==============================================================================
# 1. Emergency Communication Mode Endpoint (GET /api/v1/communication/emergency-mode/{child_id})
# ==============================================================================

def test_1_get_emergency_communication_mode():
    token = get_auth_token("sarah@nivara.app")
    res = client.get(
        "/api/v1/communication/emergency-mode/child-leo-1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["status"] == "active"
    assert data["is_emergency_mode"] is True
    assert isinstance(data["emergency_phrases"], list)
    assert len(data["emergency_phrases"]) > 0
    assert isinstance(data["quick_needs_cards"], list)
    assert isinstance(data["calming_strategies"], list)
    assert len(data["calming_strategies"]) > 0
    assert "speech_config" in data
    assert data["speech_config"]["voice"] == "friendly_child"


# ==============================================================================
# 2. AAC Sentence Generation with Emergency Intent Preservation
# ==============================================================================

def test_2_aac_sentence_generation_preserves_meaning():
    token = get_auth_token("sarah@nivara.app")
    # Case: "I + WANT + QUIET" -> "I need a quiet place."
    res = client.post(
        "/api/v1/communication/sentence/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "child_id": "child-leo-1",
            "tokens": ["I", "WANT", "QUIET"],
            "style": "natural"
        }
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["generated_sentence"] == "I need a quiet place."
    assert "I" in data["raw_tokens"]
    assert "QUIET" in data["raw_tokens"]
    assert data["log_id"] is not None


# ==============================================================================
# 3. Quick Communication & Usage Tracking
# ==============================================================================

def test_3_quick_communication_and_usage():
    token = get_auth_token("sarah@nivara.app")
    # Get common phrases
    res = client.get(
        "/api/v1/communication/phrases/common",
        headers={"Authorization": f"Bearer {token}"},
        params={"child_id": "child-leo-1"}
    )
    assert res.status_code == 200, res.text
    phrases = res.json()
    assert len(phrases) >= 10

    # Record phrase usage
    first_phrase = phrases[0]
    usage_res = client.post(
        "/api/v1/communication/phrases/usage",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "phrase_id": first_phrase["id"],
            "child_id": "child-leo-1"
        }
    )
    assert usage_res.status_code == 200, usage_res.text
    usage_data = usage_res.json()
    assert usage_data["phrase_id"] == first_phrase["id"]
    assert usage_data["usage_count"] >= 1
    assert usage_data["log_id"] is not None


# ==============================================================================
# 4. Emergency Phrases Coverage (All 10 Essential Emergency Situations)
# ==============================================================================

def test_4_emergency_phrases_comprehensive_coverage():
    token = get_auth_token("sarah@nivara.app")
    res = client.get(
        "/api/v1/communication/phrases/common",
        headers={"Authorization": f"Bearer {token}"},
        params={"child_id": "child-leo-1"}
    )
    assert res.status_code == 200, res.text
    phrase_texts = [p["text"].lower() for p in res.json()]

    expected_situations = [
        "i need help",
        "i don't feel well",
        "i am scared",
        "i am hungry",
        "i need water",
        "i want to talk",
        "i need quiet",
        "i want my caregiver",
        "i need a break",
        "i feel sick",
    ]

    for expected in expected_situations:
        assert any(expected in p for p in phrase_texts), f"Expected emergency phrase '{expected}' not found in {phrase_texts}"


# ==============================================================================
# 5. AI Sentence Generation for Remote Isolation Needs
# ==============================================================================

def test_5_ai_sentence_generation_remote_needs():
    # Test multiple remote emergency token sets
    cases = [
        (["I", "WANT", "CAREGIVER"], "I want my caregiver."),
        (["I", "FEEL", "SICK"], "I feel sick."),
        (["I", "AM", "SCARED"], "I am scared."),
        (["I", "NEED", "WATER"], "I need water, please."),
        (["I", "WANT", "TALK"], "I want to talk."),
    ]
    for tokens, expected in cases:
        out = CommunicationAI.generate_sentence_from_tokens(tokens=tokens)
        assert out["generated_sentence"] == expected, f"Failed for {tokens}: got '{out['generated_sentence']}', expected '{expected}'"
        assert out["is_fallback"] is False


# ==============================================================================
# 6. Sentence Simplification
# ==============================================================================

def test_6_sentence_simplification():
    token = get_auth_token("sarah@nivara.app")
    complex_text = "Please stay in your quiet room and drink some water while taking a deep breath."
    res = client.post(
        "/api/v1/communication/sentence/simplify",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "child_id": "child-leo-1",
            "text": complex_text,
            "target_level": "easy"
        }
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["original_text"] == complex_text
    assert len(data["key_points"]) > 0
    assert isinstance(data["matching_aac_tokens"], list)
    assert len(data["matching_aac_tokens"]) > 0


# ==============================================================================
# 7. Text-to-Speech Response
# ==============================================================================

def test_7_text_to_speech_response():
    token = get_auth_token("sarah@nivara.app")
    res = client.post(
        "/api/v1/communication/speech/synthesize",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "child_id": "child-leo-1",
            "text": "I need help right now, please.",
            "voice": "friendly_child"
        }
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["text"] == "I need help right now, please."
    assert "web_speech_config" in data
    assert "phonetic_guide" in data
    assert "ssml_hint" in data
    assert data["provider"] == "web_speech_api"


# ==============================================================================
# 8. Communication History Persistence and Retrieval
# ==============================================================================

def test_8_communication_history():
    token = get_auth_token("sarah@nivara.app")
    # Log an emergency communication
    log_res = client.post(
        "/api/v1/communication/log",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "child_id": "child-leo-1",
            "sentence": "I need help right now.",
            "tokens": ["I", "NEED", "HELP"],
            "source": "emergency",
            "category": "Emergency & Help",
            "emotion": "scared",
            "audio_played": True
        }
    )
    assert log_res.status_code == 200, log_res.text
    logged_item = log_res.json()
    assert logged_item["sentence"] == "I need help right now."

    # Retrieve history
    hist_res = client.get(
        "/api/v1/communication/history",
        headers={"Authorization": f"Bearer {token}"},
        params={"child_id": "child-leo-1", "page": 1, "page_size": 10}
    )
    assert hist_res.status_code == 200, hist_res.text
    hist_data = hist_res.json()
    assert hist_data["total"] >= 1
    assert any(item["id"] == logged_item["id"] for item in hist_data["items"])


# ==============================================================================
# 9. Favorite Phrase Management
# ==============================================================================

def test_9_favorite_phrase_workflow():
    token = get_auth_token("sarah@nivara.app")
    phrase_text = "I need my quiet space now"
    # Create favorite
    create_res = client.post(
        "/api/v1/communication/phrases/favorites",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "child_id": "child-leo-1",
            "text": phrase_text,
            "category": "Comfort & Calm",
            "icon": "🤫",
            "is_favorite": True
        }
    )
    # 200 or 409 if already exists
    assert create_res.status_code in [200, 409], create_res.text

    # List favorites
    fav_res = client.get(
        "/api/v1/communication/phrases/favorites",
        headers={"Authorization": f"Bearer {token}"},
        params={"child_id": "child-leo-1"}
    )
    assert fav_res.status_code == 200, fav_res.text
    favs = fav_res.json()
    assert any(f["text"] == phrase_text for f in favs)


# ==============================================================================
# 10. Caregiver Remote Communication Review (Authorized)
# ==============================================================================

def test_10_caregiver_remote_review_authorized():
    token = get_auth_token("sarah@nivara.app")
    res = client.get(
        "/api/v1/communication/caregiver-review/child-leo-1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert "child_name" in data
    assert "recent_communications" in data
    assert "frequently_used_phrases" in data
    assert "emotion_communications" in data
    assert "saved_favorite_phrases" in data
    assert "emergency_communications" in data
    assert "total_logs_count" in data


# ==============================================================================
# 11. Unauthorized Caregiver Access Blocked
# ==============================================================================

def test_11_unauthorized_caregiver_blocked():
    david_token = get_auth_token("david@nivara.app")
    # David should NOT be able to view Leo's caregiver communication review
    res = client.get(
        "/api/v1/communication/caregiver-review/child-leo-1",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert res.status_code == 403, f"Expected 403 Forbidden, got {res.status_code}: {res.text}"


# ==============================================================================
# 12. AI Failure Fallback Response
# ==============================================================================

def test_12_ai_failure_fallback():
    # Empty or unusual tokens
    fallback_out = CommunicationAI.generate_sentence_from_tokens(tokens=[])
    assert fallback_out["is_fallback"] is True
    assert fallback_out["generated_sentence"] != ""
    assert isinstance(fallback_out["suggestions"], list)
    assert len(fallback_out["suggestions"]) > 0

    # Simplification empty input
    simple_fallback = CommunicationAI.simplify_complex_text(text="")
    assert simple_fallback["is_fallback"] is True
    assert simple_fallback["simplified_text"] != ""
