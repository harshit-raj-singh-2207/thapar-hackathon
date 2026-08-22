import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.child import Child
from app.domains.communication.models import SavedPhrase, CommunicationLog
from app.config.security import create_access_token, get_password_hash

client = TestClient(app)

@pytest.fixture
def quick_comm_setup(db: Session):
    """Setup authenticated caregiver, another caregiver, child, and seed phrases."""
    # Caregiver 1 (Sarah)
    user_sarah = db.query(User).filter(User.id == "user-sarah-qc").first()
    if not user_sarah:
        user_sarah = User(
            id="user-sarah-qc",
            email="sarah.qc@test.com",
            full_name="Sarah Mitchell",
            hashed_password=get_password_hash("Secret123!"),
            role="caregiver",
        )
        db.add(user_sarah)
        db.commit()

    # Caregiver 2 (David)
    user_david = db.query(User).filter(User.id == "user-david-qc").first()
    if not user_david:
        user_david = User(
            id="user-david-qc",
            email="david.qc@test.com",
            full_name="David Nguyen",
            hashed_password=get_password_hash("Secret123!"),
            role="caregiver",
        )
        db.add(user_david)
        db.commit()

    # Child for Sarah
    child = db.query(Child).filter(Child.id == "child-qc-1").first()
    if not child:
        child = Child(
            id="child-qc-1",
            caregiver_id=user_sarah.id,
            name="Leo QuickComm",
            age=8,
            gender="boy",
        )
        db.add(child)
        db.commit()

    # Ensure some standard common phrases exist
    common_p = db.query(SavedPhrase).filter(SavedPhrase.id == "phrase-test-help").first()
    if not common_p:
        common_p = SavedPhrase(
            id="phrase-test-help",
            text="I need help right now",
            category="Emergency & Help",
            icon="🆘",
            is_favorite=False,
            usage_count=15,
            use_count=15,
        )
        db.add(common_p)
        db.commit()

    token_sarah = create_access_token(user_sarah.id)
    token_david = create_access_token(user_david.id)

    return {
        "user_sarah": user_sarah,
        "token_sarah": token_sarah,
        "headers_sarah": {"Authorization": f"Bearer {token_sarah}"},
        "user_david": user_david,
        "token_david": token_david,
        "headers_david": {"Authorization": f"Bearer {token_david}"},
        "child": child,
        "common_phrase": common_p,
    }


# ------------------------------------------------------------------------------
# 1. Get Common Phrases
# ------------------------------------------------------------------------------
def test_get_common_phrases(quick_comm_setup):
    res = client.get("/api/v1/communication/phrases/common")
    assert res.status_code == 200
    phrases = res.json()
    assert isinstance(phrases, list)
    assert len(phrases) >= 1
    assert any("help" in p["text"].lower() for p in phrases)

    # Alias check
    alias_res = client.get("/api/v1/communication/common-phrases")
    assert alias_res.status_code == 200
    assert len(alias_res.json()) == len(phrases)


# ------------------------------------------------------------------------------
# 2. Save Favorite Phrase & Retrieve Favorites
# ------------------------------------------------------------------------------
def test_save_and_get_favorite_phrase(quick_comm_setup):
    payload = {
        "child_id": "child-qc-1",
        "text": "I want to go for a walk in the park",
        "category": "Activities",
        "icon": "🌳",
        "is_favorite": True,
    }
    create_res = client.post(
        "/api/v1/communication/phrases/favorites",
        json=payload,
        headers=quick_comm_setup["headers_sarah"],
    )
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["text"] == "I want to go for a walk in the park"
    assert created["child_id"] == "child-qc-1"
    assert created["is_favorite"] is True
    phrase_id = created["id"]

    # Get favorites for child
    favs_res = client.get(
        "/api/v1/communication/phrases/favorites?child_id=child-qc-1",
        headers=quick_comm_setup["headers_sarah"],
    )
    assert favs_res.status_code == 200
    favs = favs_res.json()
    assert any(f["id"] == phrase_id for f in favs)


# ------------------------------------------------------------------------------
# 3. Duplicate Favorite Phrase Prevention (409 Conflict)
# ------------------------------------------------------------------------------
def test_duplicate_favorite_phrase_prevention(quick_comm_setup):
    payload = {
        "child_id": "child-qc-1",
        "text": "I want some warm tea",
        "category": "Food & Drink",
        "icon": "🍵",
        "is_favorite": True,
    }
    res1 = client.post(
        "/api/v1/communication/phrases/favorites",
        json=payload,
        headers=quick_comm_setup["headers_sarah"],
    )
    assert res1.status_code == 200

    # Repeat exact duplicate
    res2 = client.post(
        "/api/v1/communication/phrases/favorites",
        json=payload,
        headers=quick_comm_setup["headers_sarah"],
    )
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 4. Remove / Delete Favorite Phrase
# ------------------------------------------------------------------------------
def test_delete_favorite_phrase(quick_comm_setup):
    # Create phrase to delete
    create_res = client.post(
        "/api/v1/communication/phrases/favorites",
        json={"child_id": "child-qc-1", "text": "Temporary Phrase to Delete", "category": "Testing"},
        headers=quick_comm_setup["headers_sarah"],
    )
    assert create_res.status_code == 200
    phrase_id = create_res.json()["id"]

    # Delete phrase
    del_res = client.delete(
        f"/api/v1/communication/phrases/favorites/{phrase_id}",
        headers=quick_comm_setup["headers_sarah"],
    )
    assert del_res.status_code == 200
    assert "deleted" in del_res.json()["message"].lower()

    # Re-deleting should 404
    del_res2 = client.delete(
        f"/api/v1/communication/phrases/favorites/{phrase_id}",
        headers=quick_comm_setup["headers_sarah"],
    )
    assert del_res2.status_code == 404


# ------------------------------------------------------------------------------
# 5. Phrase Usage Tracking & History Logging
# ------------------------------------------------------------------------------
def test_phrase_usage_tracking(quick_comm_setup):
    # Create favorite phrase
    create_res = client.post(
        "/api/v1/communication/phrases/favorites",
        json={"child_id": "child-qc-1", "text": "I need my quiet headphones", "category": "Comfort & Calm"},
        headers=quick_comm_setup["headers_sarah"],
    )
    assert create_res.status_code == 200
    phrase_id = create_res.json()["id"]
    initial_usage = create_res.json()["usage_count"]

    # Record phrase usage by ID
    usage_res = client.post(
        f"/api/v1/communication/phrases/{phrase_id}/usage",
        headers=quick_comm_setup["headers_sarah"],
    )
    assert usage_res.status_code == 200
    usage_data = usage_res.json()
    assert usage_data["usage_count"] == initial_usage + 1
    assert usage_data["spoken_sentence"] == "I need my quiet headphones"
    assert usage_data["log_id"] is not None

    # Record usage via body text
    usage_res2 = client.post(
        "/api/v1/communication/phrases/usage",
        json={"text": "I need my quiet headphones", "child_id": "child-qc-1"},
        headers=quick_comm_setup["headers_sarah"],
    )
    assert usage_res2.status_code == 200
    assert usage_res2.json()["usage_count"] == initial_usage + 2


# ------------------------------------------------------------------------------
# 6. Child Authorization & Security Check (403 Forbidden)
# ------------------------------------------------------------------------------
def test_unauthorized_caregiver_child_phrase_access(quick_comm_setup):
    # David trying to save favorite phrase for Sarah's child Leo
    payload = {
        "child_id": "child-qc-1",
        "text": "Unauthorized Phrase",
    }
    res = client.post(
        "/api/v1/communication/phrases/favorites",
        json=payload,
        headers=quick_comm_setup["headers_david"],
    )
    assert res.status_code == 403
    assert "authorized" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 7. Non-Existent Child (404 Not Found)
# ------------------------------------------------------------------------------
def test_missing_child_phrase_access(quick_comm_setup):
    payload = {
        "child_id": "non-existent-child-999",
        "text": "Missing Child Phrase",
    }
    res = client.post(
        "/api/v1/communication/phrases/favorites",
        json=payload,
        headers=quick_comm_setup["headers_sarah"],
    )
    assert res.status_code == 404
    assert "child" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 8. Empty Phrase Input Validation (422 Unprocessable Entity)
# ------------------------------------------------------------------------------
def test_invalid_phrase_input(quick_comm_setup):
    # Empty string
    res1 = client.post(
        "/api/v1/communication/phrases/favorites",
        json={"text": ""},
        headers=quick_comm_setup["headers_sarah"],
    )
    assert res1.status_code == 422

    # Missing text
    res2 = client.post(
        "/api/v1/communication/phrases/favorites",
        json={},
        headers=quick_comm_setup["headers_sarah"],
    )
    assert res2.status_code == 422


# ------------------------------------------------------------------------------
# 9. Backward Compatibility with Legacy Endpoints
# ------------------------------------------------------------------------------
def test_legacy_saved_phrases_endpoints(quick_comm_setup):
    # POST /saved-phrases
    post_res = client.post(
        "/api/v1/communication/saved-phrases",
        json={"text": "Legacy Saved Phrase", "category": "Favorites"},
        headers=quick_comm_setup["headers_sarah"],
    )
    assert post_res.status_code == 200
    phrase_id = post_res.json()["id"]

    # GET /saved-phrases
    get_res = client.get("/api/v1/communication/saved-phrases", headers=quick_comm_setup["headers_sarah"])
    assert get_res.status_code == 200
    assert any(p["id"] == phrase_id for p in get_res.json())

    # DELETE /saved-phrases/{phrase_id}
    del_res = client.delete(f"/api/v1/communication/saved-phrases/{phrase_id}", headers=quick_comm_setup["headers_sarah"])
    assert del_res.status_code == 200
