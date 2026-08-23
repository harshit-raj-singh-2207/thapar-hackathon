from types import SimpleNamespace
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.main import app


client = TestClient(app)


def _authenticated_user():
    return SimpleNamespace(id="user-sensory")


def _database_override():
    yield Mock()


def _enable_auth_overrides():
    app.dependency_overrides[get_current_user] = _authenticated_user
    app.dependency_overrides[get_db] = _database_override


def test_authenticated_user_can_report_and_fetch_latest_sensory_state(db):
    def real_database_override():
        yield db

    app.dependency_overrides[get_current_user] = _authenticated_user
    app.dependency_overrides[get_db] = real_database_override
    try:
        created = client.post(
            "/api/v1/sensory/state",
            json={
                "sensory_state": "too_noisy",
                "intensity": 8,
                "optional_note": "Busy cafeteria",
            },
        )
        latest = client.get("/api/v1/sensory/latest")
    finally:
        app.dependency_overrides.clear()

    assert created.status_code == 201
    assert created.json()["user_id"] == "user-sensory"
    assert created.json()["sensory_state"] == "too_noisy"
    assert created.json()["created_at"]
    assert any("quieter" in item.lower() for item in created.json()["suggestions"])
    assert latest.status_code == 200
    assert latest.json()["id"] == created.json()["id"]
    assert latest.json()["suggestions"] == created.json()["suggestions"]


def test_invalid_sensory_state_is_rejected():
    _enable_auth_overrides()
    try:
        response = client.post(
            "/api/v1/sensory/state",
            json={"sensory_state": "very_loud", "intensity": 5},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422


def test_sensory_endpoints_require_authentication():
    post_response = client.post(
        "/api/v1/sensory/state",
        json={"sensory_state": "need_quiet", "intensity": 6},
    )
    get_response = client.get("/api/v1/sensory/latest")
    assert post_response.status_code == 401
    assert get_response.status_code == 401


def test_latest_is_null_when_user_has_not_reported_state(db):
    def real_database_override():
        yield db

    app.dependency_overrides[get_current_user] = _authenticated_user
    app.dependency_overrides[get_db] = real_database_override
    try:
        response = client.get("/api/v1/sensory/latest")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() is None
