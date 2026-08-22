import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sound_endpoints():
    """Test sound generation endpoints for WAV output."""
    res_like = client.get("/api/sounds/like")
    assert res_like.status_code == 200
    assert res_like.headers["content-type"] == "audio/wav"
    assert len(res_like.content) > 100

    res_comment = client.get("/api/sounds/comment")
    assert res_comment.status_code == 200
    assert res_comment.headers["content-type"] == "audio/wav"
    assert len(res_comment.content) > 100

    res_notif = client.get("/api/sounds/notification")
    assert res_notif.status_code == 200
    assert res_notif.headers["content-type"] == "audio/wav"
    assert len(res_notif.content) > 100

def test_post_state_endpoint():
    """Test GET /api/post-state endpoint."""
    response = client.get("/api/post-state")
    assert response.status_code == 200
    data = response.json()
    assert "likes" in data
    assert "comments" in data
    assert isinstance(data["comments"], list)

def test_toggle_like_endpoint():
    """Test POST /api/like endpoint."""
    state_before = client.get("/api/post-state").json()
    initial_likes = state_before["likes"]

    res = client.post("/api/like")
    assert res.status_code == 200
    data = res.json()
    assert data["likes"] == initial_likes + 1

def test_add_comment_endpoint():
    """Test POST /api/comment endpoint."""
    payload = {"text": "Testing notification sound integration!"}
    res = client.post("/api/comment", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["text"] == "Testing notification sound integration!"
    assert "id" in data

    # Empty comment validation
    bad_res = client.post("/api/comment", json={"text": "   "})
    assert bad_res.status_code == 400
