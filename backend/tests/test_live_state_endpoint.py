from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.live_state.schemas import LiveStateResponse
from app.main import app


client = TestClient(app)


def _override_authenticated_user():
    return SimpleNamespace(id="user-authenticated")


def _override_db():
    yield Mock()


def test_authenticated_user_can_fetch_own_live_state():
    expected = LiveStateResponse(
        user_id="user-authenticated",
        last_updated=datetime.now(timezone.utc),
    )
    service = Mock()
    service.get_user_live_state.return_value = expected

    app.dependency_overrides[get_current_user] = _override_authenticated_user
    app.dependency_overrides[get_db] = _override_db
    try:
        with patch(
            "app.domains.live_state.router.LiveStateService", return_value=service
        ):
            response = client.get("/api/v1/live-state/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["user_id"] == "user-authenticated"
    service.get_user_live_state.assert_called_once_with("user-authenticated")


def test_live_state_rejects_unauthenticated_requests():
    response = client.get("/api/v1/live-state/me")

    assert response.status_code == 401


def test_live_state_endpoint_handles_missing_state_cleanly():
    empty_state = LiveStateResponse(
        user_id="user-authenticated",
        last_updated=datetime.now(timezone.utc),
    )
    service = Mock()
    service.get_user_live_state.return_value = empty_state

    app.dependency_overrides[get_current_user] = _override_authenticated_user
    app.dependency_overrides[get_db] = _override_db
    try:
        with patch(
            "app.domains.live_state.router.LiveStateService", return_value=service
        ):
            response = client.get("/api/v1/live-state/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["emotion"]["status"] == "unavailable"
    assert body["location"]["data"] is None
    assert body["communication"]["status"] == "unavailable"
