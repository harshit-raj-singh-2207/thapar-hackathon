import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

import pytest

client = TestClient(app)

def get_tokens():
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    sarah_token = res1.json()["access_token"]
    sarah_id = res1.json()["user_id"]

    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    david_token = res2.json()["access_token"]
    david_id = res2.json()["user_id"]

    res3 = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    lisa_token = res3.json()["access_token"]

    return (sarah_token, sarah_id), (david_token, david_id), lisa_token

def test_1_block_and_unblock_caregiver():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Sarah blocks David -> 201
    block_res = client.post(
        "/api/v1/community/safety/blocks",
        json={"blocked_user_id": david_id},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert block_res.status_code == 201
    assert block_res.json()["blocked_id"] == david_id

    # List blocked caregivers
    list_res = client.get("/api/v1/community/safety/blocks", headers={"Authorization": f"Bearer {sarah_token}"})
    assert list_res.status_code == 200
    assert any(b["blocked_id"] == david_id for b in list_res.json())

    # Backend enforcement: Sarah tries to DM David while blocked -> 403 Forbidden
    dm_res = client.post(
        "/api/v1/community/chats",
        json={"recipient_id": david_id},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert dm_res.status_code == 403
    assert "blocked" in dm_res.json()["detail"].lower()

    # Sarah unblocks David -> 200
    unblock_res = client.delete(
        f"/api/v1/community/safety/blocks/{david_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert unblock_res.status_code == 200
    assert unblock_res.json()["blocked_id"] == david_id

    # DM allowed after unblocking -> 201
    dm_res2 = client.post(
        "/api/v1/community/chats",
        json={"recipient_id": david_id},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert dm_res2.status_code == 201

def test_2_reporting_caregiver_post_comment_group_and_duplicate_handling():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Report caregiver
    r1 = client.post(
        "/api/v1/community/safety/reports",
        json={"target_type": "user", "target_id": david_id, "reason": "Inappropriate bio"},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert r1.status_code == 201
    assert r1.json()["status"] == "pending"

    # Duplicate report handling -> returns existing report gracefully
    r1_dup = client.post(
        "/api/v1/community/safety/reports",
        json={"target_type": "user", "target_id": david_id, "reason": "Inappropriate bio"},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert r1_dup.status_code == 201
    assert "already submitted" in r1_dup.json()["message"].lower()

    # Report post
    r2 = client.post(
        "/api/v1/community/safety/reports",
        json={"target_type": "post", "target_id": "post-welcome-1", "reason": "Spam"},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert r2.status_code == 201

    # Report group
    r3 = client.post(
        "/api/v1/community/safety/reports",
        json={"target_type": "group", "target_id": "group-sensory-1", "reason": "Off-topic"},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert r3.status_code == 201

def test_3_notifications_creation_reading_and_unread_tracking():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Sarah sends message to David -> generates message notification for David
    chat_res = client.post("/api/v1/community/chats", json={"recipient_id": david_id}, headers={"Authorization": f"Bearer {sarah_token}"})
    chat_id = chat_res.json()["id"]
    client.post(f"/api/v1/community/chats/{chat_id}/messages", json={"text": "Hello David!"}, headers={"Authorization": f"Bearer {sarah_token}"})

    # David fetches notifications -> receives 1 unread notification
    n_res = client.get("/api/v1/community/notifications", headers={"Authorization": f"Bearer {david_token}"})
    assert n_res.status_code == 200
    notifs = n_res.json()
    assert len(notifs) >= 1
    msg_notif = notifs[0]
    assert msg_notif["read"] == False

    # David marks notification as read
    read_res = client.post(f"/api/v1/community/notifications/{msg_notif['id']}/read", headers={"Authorization": f"Bearer {david_token}"})
    assert read_res.status_code == 200
    assert read_res.json()["read"] == True

    # Mark all read
    read_all = client.post("/api/v1/community/notifications/read-all", headers={"Authorization": f"Bearer {david_token}"})
    assert read_all.status_code == 200

if __name__ == "__main__":
    test_1_block_and_unblock_caregiver()
    test_2_reporting_caregiver_post_comment_group_and_duplicate_handling()
    test_3_notifications_creation_reading_and_unread_tracking()
    print("ALL PHASE 5 SAFETY & NOTIFICATIONS TESTS PASSED PERFECTLY!")
