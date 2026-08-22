"""
Tests for Communication History module.
Covers: creation, retrieval, search, filtering, pagination,
        authorization, missing records, replay, favorite toggle,
        soft delete, and persistence.
"""
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
def hist_setup():
    db = SessionLocal()
    try:
        # Caregiver A (owner)
        cg_a = db.query(User).filter(User.id == "user-hist-cga").first()
        if not cg_a:
            cg_a = User(
                id="user-hist-cga",
                email="hist_cga@example.com",
                full_name="Hist CG A",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg_a)
            db.commit()
            db.refresh(cg_a)

        # Caregiver B (unauthorized)
        cg_b = db.query(User).filter(User.id == "user-hist-cgb").first()
        if not cg_b:
            cg_b = User(
                id="user-hist-cgb",
                email="hist_cgb@example.com",
                full_name="Hist CG B",
                role="caregiver",
                hashed_password=get_password_hash("Secret123!"),
            )
            db.add(cg_b)
            db.commit()
            db.refresh(cg_b)

        # Child belonging to cg_a
        child = db.query(Child).filter(Child.id == "child-hist-1").first()
        if not child:
            child = Child(
                id="child-hist-1",
                name="Aria",
                age=7,
                caregiver_id=cg_a.id,
            )
            db.add(child)
            db.commit()
            db.refresh(child)

        return {
            "headers_a": {"Authorization": f"Bearer {create_access_token(cg_a.id)}"},
            "headers_b": {"Authorization": f"Bearer {create_access_token(cg_b.id)}"},
            "child_id": child.id,
            "user_id_a": cg_a.id,
        }
    finally:
        db.close()


def _log(client, headers, sentence, source="aac", child_id=None, tokens=None, category=None, emotion=None):
    payload = {"sentence": sentence, "source": source}
    if child_id:
        payload["child_id"] = child_id
    if tokens:
        payload["tokens"] = tokens
    if category:
        payload["category"] = category
    if emotion:
        payload["emotion"] = emotion
    res = client.post("/api/v1/communication/log", json=payload, headers=headers)
    assert res.status_code == 200, f"Log failed: {res.text}"
    return res.json()


# ------------------------------------------------------------------------------
# 1. History Creation — log_id returned, fields persisted
# ------------------------------------------------------------------------------
def test_history_creation(hist_setup):
    headers = hist_setup["headers_a"]
    entry = _log(client, headers, "I want some water.", tokens=["I", "WANT", "WATER"])

    assert "id" in entry
    assert entry["sentence"] == "I want some water."
    assert entry["tokens"] == ["I", "WANT", "WATER"]
    assert entry["source"] == "aac"
    assert entry["is_favorite"] is False


# ------------------------------------------------------------------------------
# 2. Retrieve Paginated History
# ------------------------------------------------------------------------------
def test_retrieve_history_paginated(hist_setup):
    headers = hist_setup["headers_a"]
    for i in range(5):
        _log(client, headers, f"Sentence number {i}.")

    res = client.get("/api/v1/communication/history?page=1&page_size=3", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["items"]) <= 3


# ------------------------------------------------------------------------------
# 3. Get History Entry by ID
# ------------------------------------------------------------------------------
def test_get_history_by_id(hist_setup):
    headers = hist_setup["headers_a"]
    created = _log(client, headers, "I feel happy.")
    log_id = created["id"]

    res = client.get(f"/api/v1/communication/history/{log_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == log_id
    assert res.json()["sentence"] == "I feel happy."


# ------------------------------------------------------------------------------
# 4. Missing Record → 404
# ------------------------------------------------------------------------------
def test_history_missing_returns_404(hist_setup):
    headers = hist_setup["headers_a"]
    res = client.get("/api/v1/communication/history/no-such-id-xyz", headers=headers)
    assert res.status_code == 404


# ------------------------------------------------------------------------------
# 5. Search History by Text
# ------------------------------------------------------------------------------
def test_search_history(hist_setup):
    headers = hist_setup["headers_a"]
    _log(client, headers, "I need more juice please.")
    _log(client, headers, "I want to go outside.")
    _log(client, headers, "Give me the juice cup.")

    res = client.get("/api/v1/communication/history?search=juice", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 2
    for item in data["items"]:
        assert "juice" in item["sentence"].lower()


# ------------------------------------------------------------------------------
# 6. Filter by Source
# ------------------------------------------------------------------------------
def test_filter_by_source(hist_setup):
    headers = hist_setup["headers_a"]
    _log(client, headers, "I am tired.", source="emotion")
    _log(client, headers, "I want food.", source="aac")

    res = client.get("/api/v1/communication/history?source=emotion", headers=headers)
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["source"] == "emotion"


# ------------------------------------------------------------------------------
# 7. Filter by Emotion
# ------------------------------------------------------------------------------
def test_filter_by_emotion(hist_setup):
    headers = hist_setup["headers_a"]
    _log(client, headers, "I feel sad.", emotion="sad")
    _log(client, headers, "I want to play.", emotion="happy")

    res = client.get("/api/v1/communication/history?emotion=sad", headers=headers)
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["emotion"] == "sad"


# ------------------------------------------------------------------------------
# 8. Filter Favorites Only
# ------------------------------------------------------------------------------
def test_filter_favorites_only(hist_setup):
    headers = hist_setup["headers_a"]
    created = _log(client, headers, "Fav entry test sentence.")
    log_id = created["id"]

    # Toggle favorite
    fav_res = client.post(f"/api/v1/communication/history/{log_id}/favorite", headers=headers)
    assert fav_res.status_code == 200
    assert fav_res.json()["is_favorite"] is True

    # Filter favorites
    res = client.get("/api/v1/communication/history?favorites_only=true", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["is_favorite"] is True


# ------------------------------------------------------------------------------
# 9. Pagination — has_next, has_prev
# ------------------------------------------------------------------------------
def test_pagination_navigation(hist_setup):
    headers = hist_setup["headers_a"]
    for i in range(6):
        _log(client, headers, f"Pagination test {i}.")

    page1 = client.get("/api/v1/communication/history?page=1&page_size=3", headers=headers).json()
    page2 = client.get("/api/v1/communication/history?page=2&page_size=3", headers=headers).json()

    assert page1["has_prev"] is False
    if page1["total"] > 3:
        assert page1["has_next"] is True
    assert page2["has_prev"] is True


# ------------------------------------------------------------------------------
# 10. Recent Communications
# ------------------------------------------------------------------------------
def test_recent_communications(hist_setup):
    headers = hist_setup["headers_a"]
    for i in range(3):
        _log(client, headers, f"Recent {i}.")

    res = client.get("/api/v1/communication/history/recent?limit=5", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) <= 5


# ------------------------------------------------------------------------------
# 11. Replay Communication
# ------------------------------------------------------------------------------
def test_replay_history_entry(hist_setup):
    headers = hist_setup["headers_a"]
    original = _log(client, headers, "I want to swim.", tokens=["I", "WANT", "SWIM"])
    log_id = original["id"]

    replay_res = client.post(f"/api/v1/communication/history/{log_id}/replay", headers=headers)
    assert replay_res.status_code == 200
    replayed = replay_res.json()
    assert replayed["sentence"] == "I want to swim."
    assert replayed["tokens"] == ["I", "WANT", "SWIM"]
    assert replayed["id"] != log_id  # new entry


# ------------------------------------------------------------------------------
# 12. Soft Delete — entry no longer accessible
# ------------------------------------------------------------------------------
def test_soft_delete_history(hist_setup):
    headers = hist_setup["headers_a"]
    entry = _log(client, headers, "Delete me please.")
    log_id = entry["id"]

    del_res = client.delete(f"/api/v1/communication/history/{log_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

    # Should be gone
    get_res = client.get(f"/api/v1/communication/history/{log_id}", headers=headers)
    assert get_res.status_code == 404


# ------------------------------------------------------------------------------
# 13. Delete Non-existent → 404
# ------------------------------------------------------------------------------
def test_delete_nonexistent_returns_404(hist_setup):
    headers = hist_setup["headers_a"]
    res = client.delete("/api/v1/communication/history/ghost-id-999", headers=headers)
    assert res.status_code == 404


# ------------------------------------------------------------------------------
# 14. Child-Scoped History — unauthorized caregiver blocked
# ------------------------------------------------------------------------------
def test_child_history_unauthorized(hist_setup):
    child_id = hist_setup["child_id"]
    headers_b = hist_setup["headers_b"]  # does NOT own child

    res = client.get(f"/api/v1/communication/history?child_id={child_id}", headers=headers_b)
    assert res.status_code == 403


# ------------------------------------------------------------------------------
# 15. Child-Scoped History — authorized caregiver succeeds
# ------------------------------------------------------------------------------
def test_child_history_authorized(hist_setup):
    headers_a = hist_setup["headers_a"]
    child_id = hist_setup["child_id"]

    _log(client, headers_a, "Child sentence for Aria.", child_id=child_id)

    res = client.get(f"/api/v1/communication/history?child_id={child_id}", headers=headers_a)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["child_id"] == child_id


# ------------------------------------------------------------------------------
# 16. Persistence — entry survives across new service instances
# ------------------------------------------------------------------------------
def test_persistence(hist_setup):
    headers = hist_setup["headers_a"]
    entry = _log(client, headers, "Persisted entry check.")
    log_id = entry["id"]

    # Retrieve with a new client call (new service instance per FastAPI request)
    res = client.get(f"/api/v1/communication/history/{log_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["sentence"] == "Persisted entry check."


# ------------------------------------------------------------------------------
# 17. Category Filter
# ------------------------------------------------------------------------------
def test_filter_by_category(hist_setup):
    headers = hist_setup["headers_a"]
    _log(client, headers, "I need sensory break.", category="sensory")
    _log(client, headers, "I want water.", category="basic_needs")

    res = client.get("/api/v1/communication/history?category=sensory", headers=headers)
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["category"] == "sensory"
