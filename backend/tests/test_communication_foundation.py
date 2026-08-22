import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.user import User, Caregiver
from app.models.child import Child
from app.domains.communication.models import AACCategory, AACCard
from app.config.security import create_access_token, get_password_hash

client = TestClient(app)

@pytest.fixture
def auth_setup(db: Session):
    """Setup authenticated caregiver, another caregiver, and a child."""
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

    # Ensure some global system cards exist
    if db.query(AACCard).filter(AACCard.child_id == None, AACCard.user_id == None).count() == 0:
        c1 = AACCard(id="card-sys-water", category_id="cat-quick", label="Water", spoken_text="Water please", icon="💧", is_quick_need=True)
        c2 = AACCard(id="card-sys-apple", category_id="cat-food", label="Apple", spoken_text="Apple", icon="🍎")
        db.add_all([c1, c2])
        db.commit()

    # Caregiver 1 (Sarah)
    user_sarah = db.query(User).filter(User.id == "user-sarah-test").first()
    if not user_sarah:
        user_sarah = User(
            id="user-sarah-test",
            email="sarah.comm@test.com",
            full_name="Sarah Mitchell",
            hashed_password=get_password_hash("Secret123!"),
            role="caregiver",
        )
        db.add(user_sarah)
        db.commit()

    # Caregiver 2 (John)
    user_john = db.query(User).filter(User.id == "user-john-test").first()
    if not user_john:
        user_john = User(
            id="user-john-test",
            email="john.comm@test.com",
            full_name="John Doe",
            hashed_password=get_password_hash("Secret123!"),
            role="caregiver",
        )
        db.add(user_john)
        db.commit()

    # Child for Sarah
    child = db.query(Child).filter(Child.id == "child-comm-1").first()
    if not child:
        child = Child(
            id="child-comm-1",
            caregiver_id=user_sarah.id,
            name="Leo Comm",
            age=8,
            gender="boy",
        )
        db.add(child)
        db.commit()

    token_sarah = create_access_token({"sub": user_sarah.id})
    token_john = create_access_token({"sub": user_john.id})

    return {
        "user_sarah": user_sarah,
        "token_sarah": token_sarah,
        "headers_sarah": {"Authorization": f"Bearer {token_sarah}"},
        "user_john": user_john,
        "token_john": token_john,
        "headers_john": {"Authorization": f"Bearer {token_john}"},
        "child": child,
    }


# ------------------------------------------------------------------------------
# 1. Get Categories
# ------------------------------------------------------------------------------
def test_get_categories(auth_setup):
    res = client.get("/api/v1/communication/categories")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 6
    names = [c["name"] for c in data]
    assert "Quick Needs" in names
    assert "Food" in names
    assert "Drink" in names
    assert "Feelings" in names
    assert "Actions" in names
    assert "Play" in names


# ------------------------------------------------------------------------------
# 2. Get All Cards
# ------------------------------------------------------------------------------
def test_get_cards(auth_setup):
    res = client.get("/api/v1/communication/cards")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    labels = [c["label"] for c in data]
    assert "Water" in labels


# ------------------------------------------------------------------------------
# 3. Filter Cards by Category
# ------------------------------------------------------------------------------
def test_filter_cards_by_category(auth_setup):
    # Filter by category name query
    res = client.get("/api/v1/communication/cards?category=Food")
    assert res.status_code == 200
    data = res.json()
    assert all(c["category_id"] == "cat-food" for c in data)

    # Filter by path parameter /cards/{category}
    res_path = client.get("/api/v1/communication/cards/cat-food")
    assert res_path.status_code == 200
    data_path = res_path.json()
    assert len(data_path) >= 1
    assert data_path[0]["label"] == "Apple"


# ------------------------------------------------------------------------------
# 4. Create Custom Picture Card
# ------------------------------------------------------------------------------
def test_create_card_success(auth_setup):
    payload = {
        "label": "Sensory Ball",
        "category_id": "cat-play",
        "spoken_text": "I want the squishy sensory ball, please.",
        "keyword": "ball",
        "icon": "⚽",
        "child_id": "child-comm-1",
        "part_of_speech": "noun",
    }
    res = client.post("/api/v1/communication/cards", json=payload, headers=auth_setup["headers_sarah"])
    assert res.status_code == 201
    card = res.json()
    assert card["label"] == "Sensory Ball"
    assert card["category_id"] == "cat-play"
    assert card["child_id"] == "child-comm-1"
    assert card["category_name"] == "Play"


# ------------------------------------------------------------------------------
# 5. Duplicate Card Prevention
# ------------------------------------------------------------------------------
def test_duplicate_card_prevention(auth_setup):
    payload = {
        "label": "Sensory Ball",
        "category_id": "cat-play",
        "child_id": "child-comm-1",
    }
    # Initial creation
    res1 = client.post("/api/v1/communication/cards", json=payload, headers=auth_setup["headers_sarah"])
    assert res1.status_code == 201

    # Duplicate for the same child in the same category
    res2 = client.post("/api/v1/communication/cards", json=payload, headers=auth_setup["headers_sarah"])
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


# ------------------------------------------------------------------------------
# 6. Invalid Category Handling
# ------------------------------------------------------------------------------
def test_invalid_category_handling(auth_setup):
    # Query with non-existent category
    res_get = client.get("/api/v1/communication/cards?category=non_existent_cat")
    assert res_get.status_code == 404
    assert "not found" in res_get.json()["detail"].lower()

    # Create card with non-existent category
    payload = {
        "label": "Invalid Cat Item",
        "category_id": "cat-does-not-exist",
        "child_id": "child-comm-1",
    }
    res_post = client.post("/api/v1/communication/cards", json=payload, headers=auth_setup["headers_sarah"])
    assert res_post.status_code == 404


# ------------------------------------------------------------------------------
# 7. Invalid Card ID Handling
# ------------------------------------------------------------------------------
def test_invalid_card_handling(auth_setup):
    res_get = client.get("/api/v1/communication/cards/invalid-card-id-12345")
    assert res_get.status_code == 404

    res_patch = client.patch(
        "/api/v1/communication/cards/invalid-card-id-12345",
        json={"label": "Updated"},
        headers=auth_setup["headers_sarah"]
    )
    assert res_patch.status_code == 404

    res_del = client.delete(
        "/api/v1/communication/cards/invalid-card-id-12345",
        headers=auth_setup["headers_sarah"]
    )
    assert res_del.status_code == 404


# ------------------------------------------------------------------------------
# 8. Unauthorized Request Handling
# ------------------------------------------------------------------------------
def test_unauthorized_requests(auth_setup):
    # Missing token on write API
    res_no_auth = client.post("/api/v1/communication/cards", json={"label": "No Auth"})
    assert res_no_auth.status_code == 401

    # Another caregiver trying to create/modify card for Sarah's child
    payload = {
        "label": "Forbidden Toy",
        "category_id": "cat-play",
        "child_id": "child-comm-1",
    }
    res_forbidden = client.post("/api/v1/communication/cards", json=payload, headers=auth_setup["headers_john"])
    assert res_forbidden.status_code == 403


# ------------------------------------------------------------------------------
# 9. Missing Child Handling
# ------------------------------------------------------------------------------
def test_missing_child_handling(auth_setup):
    payload = {
        "label": "Test Toy",
        "category_id": "cat-play",
        "child_id": "non-existent-child-999",
    }
    res = client.post("/api/v1/communication/cards", json=payload, headers=auth_setup["headers_sarah"])
    assert res.status_code == 404
    assert "child" in res.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 10. Invalid Request Body Validation
# ------------------------------------------------------------------------------
def test_invalid_request_body_validation(auth_setup):
    # Empty string label
    res = client.post(
        "/api/v1/communication/cards",
        json={"label": "", "category_id": "cat-play"},
        headers=auth_setup["headers_sarah"]
    )
    assert res.status_code == 422


# ------------------------------------------------------------------------------
# 11. Update and Delete Custom Card Flow
# ------------------------------------------------------------------------------
def test_update_and_delete_custom_card(auth_setup):
    # 1. Create a card
    create_res = client.post(
        "/api/v1/communication/cards",
        json={
            "label": "Plush Bear",
            "category_id": "cat-play",
            "child_id": "child-comm-1",
            "icon": "🧸"
        },
        headers=auth_setup["headers_sarah"]
    )
    assert create_res.status_code == 201
    card_id = create_res.json()["id"]

    # 2. Update the card
    patch_res = client.patch(
        f"/api/v1/communication/cards/{card_id}",
        json={"spoken_text": "I want my soft plush bear", "icon": "🐻"},
        headers=auth_setup["headers_sarah"]
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["spoken_text"] == "I want my soft plush bear"
    assert patch_res.json()["icon"] == "🐻"

    # 3. Delete the card
    del_res = client.delete(
        f"/api/v1/communication/cards/{card_id}",
        headers=auth_setup["headers_sarah"]
    )
    assert del_res.status_code == 200

    # 4. Verify card is gone
    get_res = client.get(f"/api/v1/communication/cards/{card_id}")
    assert get_res.status_code == 404


# ------------------------------------------------------------------------------
# 12. Protection for Global System Cards
# ------------------------------------------------------------------------------
def test_system_card_protection(auth_setup):
    # System card should not be deletable by non-admin caregiver
    del_res = client.delete(
        "/api/v1/communication/cards/card-water",
        headers=auth_setup["headers_sarah"]
    )
    assert del_res.status_code == 403
    assert "system" in del_res.json()["detail"].lower()
