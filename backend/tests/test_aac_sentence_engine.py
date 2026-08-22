import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.child import Child
from app.domains.communication.models import AACCategory, AACCard, CommunicationLog
from app.config.security import create_access_token, get_password_hash

client = TestClient(app)

@pytest.fixture
def aac_setup(db: Session):
    """Setup authenticated caregiver, another caregiver, child, and active/inactive cards."""
    # Ensure standard categories exist
    if db.query(AACCategory).count() == 0:
        cat_quick = AACCategory(id="cat-quick", name="Quick Needs", icon="⭐", color="#2563EB", order=1)
        cat_food = AACCategory(id="cat-food", name="Food", icon="🍴", color="#F59E0B", order=2)
        cat_drink = AACCategory(id="cat-drink", name="Drink", icon="🥤", color="#3B82F6", order=3)
        cat_feelings = AACCategory(id="cat-feelings", name="Feelings", icon="❤️", color="#EF4444", order=4)
        cat_actions = AACCategory(id="cat-actions", name="Actions", icon="🏃", color="#10B981", order=5)
        cat_play = AACCategory(id="cat-play", name="Play", icon="🧸", color="#8B5CF6", order=6)
        db.add_all([cat_quick, cat_food, cat_drink, cat_feelings, cat_actions, cat_play])
        db.commit()

    # Caregiver 1 (Sarah)
    user_sarah = db.query(User).filter(User.id == "user-sarah-aac").first()
    if not user_sarah:
        user_sarah = User(
            id="user-sarah-aac",
            email="sarah.aac@test.com",
            full_name="Sarah Mitchell",
            hashed_password=get_password_hash("Secret123!"),
            role="caregiver",
        )
        db.add(user_sarah)
        db.commit()

    # Caregiver 2 (David)
    user_david = db.query(User).filter(User.id == "user-david-aac").first()
    if not user_david:
        user_david = User(
            id="user-david-aac",
            email="david.aac@test.com",
            full_name="David Nguyen",
            hashed_password=get_password_hash("Secret123!"),
            role="caregiver",
        )
        db.add(user_david)
        db.commit()

    # Child for Sarah
    child = db.query(Child).filter(Child.id == "child-aac-1").first()
    if not child:
        child = Child(
            id="child-aac-1",
            caregiver_id=user_sarah.id,
            name="Leo AAC",
            age=7,
            gender="boy",
        )
        db.add(child)
        db.commit()

    # Ensure required active & inactive test cards exist
    cards_data = [
        ("card-i", "cat-actions", "I", "I", "I", True),
        ("card-want", "cat-actions", "WANT", "want", "WANT", True),
        ("card-need", "cat-actions", "NEED", "need", "NEED", True),
        ("card-water", "cat-quick", "Water", "water", "WATER", True),
        ("card-apple", "cat-food", "Apple", "apple", "APPLE", True),
        ("card-juice", "cat-drink", "Juice", "juice", "JUICE", True),
        ("card-help", "cat-quick", "Help", "help", "HELP", True),
        ("card-inactive-toy", "cat-play", "Old Broken Toy", "broken toy", "TOY", False),  # Inactive card
    ]

    for cid, cat_id, label, spoken, keyword, is_act in cards_data:
        existing = db.query(AACCard).filter(AACCard.id == cid).first()
        if not existing:
            card = AACCard(
                id=cid,
                category_id=cat_id,
                label=label,
                spoken_text=spoken,
                keyword=keyword,
                icon="💬",
                is_active=is_act,
                usage_count=5,
            )
            db.add(card)
        else:
            existing.is_active = is_act
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
    }


# ------------------------------------------------------------------------------
# 1. Valid Token Sequence [I] + [WANT] + [WATER] via Card IDs
# ------------------------------------------------------------------------------
def test_build_sentence_valid_card_ids(aac_setup):
    payload = {
        "child_id": "child-aac-1",
        "card_ids": ["card-i", "card-want", "card-water"],
        "style": "natural",
    }
    res = client.post("/api/v1/communication/aac/sentence", json=payload, headers=aac_setup["headers_sarah"])
    assert res.status_code == 200
    data = res.json()
    assert "tokens" in data
    assert "labels" in data
    assert "constructed_sentence" in data
    assert data["labels"] == ["I", "WANT", "Water"]
    assert "water" in data["constructed_sentence"].lower()
    assert data["timestamp"] is not None
    assert data["log_id"] is not None


# ------------------------------------------------------------------------------
# 2. Valid Token Sequence via Raw String Tokens
# ------------------------------------------------------------------------------
def test_build_sentence_valid_raw_tokens(aac_setup):
    payload = {
        "tokens": ["I", "WANT", "WATER"],
        "emotion": "happy",
    }
    res = client.post("/api/v1/communication/aac/sentence", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["labels"] == ["I", "WANT", "Water"]
    assert "water" in data["constructed_sentence"].lower()
    assert "excited" in data["constructed_sentence"].lower() or "happy" in data["constructed_sentence"].lower() or "please" in data["constructed_sentence"].lower()


# ------------------------------------------------------------------------------
# 3. Preserve Strict Token Ordering
# ------------------------------------------------------------------------------
def test_preserve_token_order(aac_setup):
    # Order 1: Apple then Juice
    res1 = client.post("/api/v1/communication/aac/sentence", json={"card_ids": ["card-apple", "card-juice"]})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["card_ids"] == ["card-apple", "card-juice"]
    assert data1["labels"] == ["Apple", "Juice"]

    # Order 2: Juice then Apple
    res2 = client.post("/api/v1/communication/aac/sentence", json={"card_ids": ["card-juice", "card-apple"]})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["card_ids"] == ["card-juice", "card-apple"]
    assert data2["labels"] == ["Juice", "Apple"]


# ------------------------------------------------------------------------------
# 4. Inactive Card Rejection (400 Bad Request)
# ------------------------------------------------------------------------------
def test_inactive_card_validation(aac_setup):
    payload = {
        "child_id": "child-aac-1",
        "card_ids": ["card-i", "card-want", "card-inactive-toy"],
    }
    res = client.post("/api/v1/communication/aac/sentence", json=payload, headers=aac_setup["headers_sarah"])
    assert res.status_code == 400
    assert "inactive" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 5. Invalid / Non-Existent Card ID (404 Not Found)
# ------------------------------------------------------------------------------
def test_invalid_card_id(aac_setup):
    payload = {
        "card_ids": ["card-i", "non-existent-card-999"],
    }
    res = client.post("/api/v1/communication/aac/sentence", json=payload)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 6. Empty Token / Card List Validation (422 Unprocessable Entity)
# ------------------------------------------------------------------------------
def test_empty_tokens_validation(aac_setup):
    # Empty card_ids
    res1 = client.post("/api/v1/communication/aac/sentence", json={"card_ids": []})
    assert res1.status_code == 422

    # Empty tokens list
    res2 = client.post("/api/v1/communication/aac/sentence", json={"tokens": []})
    assert res2.status_code == 422

    # Missing both fields
    res3 = client.post("/api/v1/communication/aac/sentence", json={})
    assert res3.status_code == 422


# ------------------------------------------------------------------------------
# 7. Non-Existent Child (404 Not Found)
# ------------------------------------------------------------------------------
def test_missing_child(aac_setup):
    payload = {
        "child_id": "non-existent-child-888",
        "card_ids": ["card-water"],
    }
    res = client.post("/api/v1/communication/aac/sentence", json=payload, headers=aac_setup["headers_sarah"])
    assert res.status_code == 404
    assert "child" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 8. Unauthorized Caregiver Access for Child (403 Forbidden)
# ------------------------------------------------------------------------------
def test_unauthorized_child_access(aac_setup):
    # David attempting to generate communication on behalf of Sarah's child Leo
    payload = {
        "child_id": "child-aac-1",
        "card_ids": ["card-water"],
    }
    res = client.post("/api/v1/communication/aac/sentence", json=payload, headers=aac_setup["headers_david"])
    assert res.status_code == 403
    assert "authorized" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 9. Persistence & Spoken Communication History Retrieval
# ------------------------------------------------------------------------------
def test_sentence_persistence_and_history(aac_setup):
    payload = {
        "child_id": "child-aac-1",
        "card_ids": ["card-need", "card-help"],
        "emotion": "anxious",
        "save_log": True,
    }
    res = client.post("/api/v1/communication/aac/sentence", json=payload, headers=aac_setup["headers_sarah"])
    assert res.status_code == 200
    log_id = res.json()["log_id"]
    assert log_id is not None

    # Retrieve history
    hist_res = client.get("/api/v1/communication/history", headers=aac_setup["headers_sarah"])
    data = hist_res.json()
    logs = data.get("items", data) if isinstance(data, dict) else data
    assert len(logs) >= 1
    assert any(l["id"] == log_id for l in logs)
    matching = next(l for l in logs if l["id"] == log_id)
    assert matching["source"] == "aac"
    assert matching["emotion"] == "anxious"


# ------------------------------------------------------------------------------
# 10. Card Usage Count Increment
# ------------------------------------------------------------------------------
def test_card_usage_count_increments(aac_setup):
    # Check initial usage count of card-apple
    get_res = client.get("/api/v1/communication/cards/card-apple")
    assert get_res.status_code == 200
    initial_count = get_res.json()["usage_count"]

    # Use card-apple in sentence
    build_res = client.post("/api/v1/communication/aac/sentence", json={"card_ids": ["card-apple"]})
    assert build_res.status_code == 200

    # Verify updated usage count
    get_res2 = client.get("/api/v1/communication/cards/card-apple")
    assert get_res2.status_code == 200
    assert get_res2.json()["usage_count"] == initial_count + 1
