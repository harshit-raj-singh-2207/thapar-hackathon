import sys
import os
import io

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

client = TestClient(app)

def get_tokens():
    # Login Sarah (Verified Caregiver 1, Creator of group-sensory-1)
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    sarah_token = res1.json()["access_token"]
    sarah_id = res1.json()["user_id"]

    # Login David (Verified Caregiver 2, Not initial member of group-sensory-1)
    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    david_token = res2.json()["access_token"]
    david_id = res2.json()["user_id"]

    # Login Lisa (Unverified Caregiver)
    res3 = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    lisa_token = res3.json()["access_token"]

    return (sarah_token, sarah_id), (david_token, david_id), lisa_token

def test_1_unverified_and_non_member_group_chat_access_denied():
    (sarah_token, _), (david_token, _), lisa_token = get_tokens()
    group_id = "group-sensory-1"

    # 1. Unverified caregiver -> 403
    res_lisa = client.get(f"/api/v1/community/groups/{group_id}/messages", headers={"Authorization": f"Bearer {lisa_token}"})
    assert res_lisa.status_code == 403
    assert "UNVERIFIED_CAREGIVER" in res_lisa.json()["detail"]

    # 2. Non-member verified caregiver (David before joining) -> 403
    res_david = client.get(f"/api/v1/community/groups/{group_id}/messages", headers={"Authorization": f"Bearer {david_token}"})
    assert res_david.status_code == 403
    assert "must be a member" in res_david.json()["detail"].lower()

def test_2_member_can_send_and_retrieve_group_messages():
    (sarah_token, _), (david_token, _), _ = get_tokens()
    group_id = "group-sensory-1"

    # Sarah (Creator/Member) sends text message -> 201
    send_res = client.post(
        f"/api/v1/community/groups/{group_id}/messages",
        json={"text": "Welcome to the Sensory Support Circle! Share your favorite calming tools."},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert send_res.status_code == 201
    assert send_res.json()["group_id"] == group_id
    assert send_res.json()["is_own"] == True

    # Sarah sends image message
    img_res = client.post(
        f"/api/v1/community/groups/{group_id}/messages",
        json={"text": "Weighted blanket setup", "image_url": "/static/uploads/blanket.jpg"},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert img_res.status_code == 201
    assert img_res.json()["attachment_url"] == "/static/uploads/blanket.jpg"

    # David joins group
    client.post(f"/api/v1/community/groups/{group_id}/join", headers={"Authorization": f"Bearer {david_token}"})

    # David (New member) retrieves message history -> 200
    history_res = client.get(f"/api/v1/community/groups/{group_id}/messages", headers={"Authorization": f"Bearer {david_token}"})
    assert history_res.status_code == 200
    messages = history_res.json()
    assert len(messages) >= 2
    assert messages[0]["text"] == "Welcome to the Sensory Support Circle! Share your favorite calming tools."
    assert messages[0]["is_own"] == False # False for David

def test_3_leaving_group_revokes_group_chat_access():
    (sarah_token, _), (david_token, _), _ = get_tokens()
    group_id = "group-sensory-1"

    # David leaves group
    client.post(f"/api/v1/community/groups/{group_id}/leave", headers={"Authorization": f"Bearer {david_token}"})

    # David attempts to read group messages -> 403 Access Denied
    res = client.get(f"/api/v1/community/groups/{group_id}/messages", headers={"Authorization": f"Bearer {david_token}"})
    assert res.status_code == 403

def test_4_realtime_group_typing_events():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()
    group_id = "group-sensory-1"

    # David rejoins group for real-time typing test
    client.post(f"/api/v1/community/groups/{group_id}/join", headers={"Authorization": f"Bearer {david_token}"})

    c1 = TestClient(app)
    with c1.websocket_connect(f"/api/v1/community/ws?token={sarah_token}") as ws_sarah:
        ack_sarah = ws_sarah.receive_json()
        assert ack_sarah["type"] == "connection_ack"

if __name__ == "__main__":
    test_1_unverified_and_non_member_group_chat_access_denied()
    test_2_member_can_send_and_retrieve_group_messages()
    test_3_leaving_group_revokes_group_chat_access()
    test_4_realtime_group_typing_events()
    print("ALL PHASE 5 GROUP CHAT BACKEND TESTS PASSED PERFECTLY!")
