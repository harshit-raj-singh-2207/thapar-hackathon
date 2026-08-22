import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine, SessionLocal
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Post
from app.domains.notifications.models import Notification

import pytest

client = TestClient(app)

def get_tokens():
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res1.status_code == 200
    sarah_token = res1.json()["access_token"]
    sarah_id = res1.json()["user_id"]

    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res2.status_code == 200
    david_token = res2.json()["access_token"]
    david_id = res2.json()["user_id"]

    return (sarah_token, sarah_id), (david_token, david_id)

def test_live_notifications_two_users_flow():
    (sarah_token, sarah_id), (david_token, david_id) = get_tokens()

    # Step 1: User B (David) creates a post
    post_res = client.post(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {david_token}"},
        json={"content": "David's autism sensory strategy post", "category": "Sensory"}
    )
    assert post_res.status_code == 201
    post_id = post_res.json()["id"]

    # Step 2: User B connects to WebSocket
    with client.websocket_connect(f"/api/v1/community/ws?token={david_token}") as ws_david:
        ack = ws_david.receive_json()
        assert ack["type"] == "connection_ack"
        assert ack["user_id"] == david_id

        # Step 3: User A (Sarah) comments on User B's post
        comment_res = client.post(
            f"/api/v1/community/posts/{post_id}/comments",
            headers={"Authorization": f"Bearer {sarah_token}"},
            json={"content": "Great strategy David! We use this daily."}
        )
        assert comment_res.status_code == 201

        # Step 4: User B receives LIVE WebSocket notification
        ws_msg = ws_david.receive_json()
        assert ws_msg["type"] == "notification"
        notif_data = ws_msg["data"]
        assert notif_data["type"] == "comment"
        assert "Sarah Mitchell" in notif_data["body"] or "commented" in notif_data["body"]
        notif_id = notif_data["id"]

        # Step 5: Check User B's unread count via API
        count_res = client.get(
            "/api/v1/community/notifications/unread-count",
            headers={"Authorization": f"Bearer {david_token}"}
        )
        assert count_res.status_code == 200
        initial_count = count_res.json()["count"]
        assert initial_count >= 1

        # Step 6: User B marks the notification as read
        mark_res = client.post(
            f"/api/v1/community/notifications/{notif_id}/read",
            headers={"Authorization": f"Bearer {david_token}"}
        )
        assert mark_res.status_code == 200
        assert mark_res.json()["read"] is True

        # Step 7: Verify unread count decreased
        count_res2 = client.get(
            "/api/v1/community/notifications/unread-count",
            headers={"Authorization": f"Bearer {david_token}"}
        )
        assert count_res2.status_code == 200
        assert count_res2.json()["count"] == initial_count - 1

    # Step 8: Offline Test: User B is disconnected. User A sends direct message
    chat_res = client.post(
        "/api/v1/community/chats",
        headers={"Authorization": f"Bearer {sarah_token}"},
        json={"recipient_id": david_id}
    )
    assert chat_res.status_code in [200, 201]
    chat_id = chat_res.json()["id"]

    send_res = client.post(
        f"/api/v1/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {sarah_token}"},
        json={"text": "Hey David, sent while you were offline."}
    )
    assert send_res.status_code == 201

    # Step 9: User B logs in / fetches notifications -> New unread message notification is present
    login_notifs = client.get(
        "/api/v1/community/notifications",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert login_notifs.status_code == 200
    all_notifs = login_notifs.json()
    assert len(all_notifs) >= 1
    offline_notif = next((n for n in all_notifs if n["type"] == "message" and not n["read"]), None)
    assert offline_notif is not None

    # Step 10: Security Test: User A attempts to mark User B's notification as read -> 404
    hack_res = client.post(
        f"/api/v1/community/notifications/{offline_notif['id']}/read",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert hack_res.status_code == 404

    # Step 11: Mark all as read test
    mark_all_res = client.post(
        "/api/v1/community/notifications/read-all",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert mark_all_res.status_code == 200

    count_res3 = client.get(
        "/api/v1/community/notifications/unread-count",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert count_res3.json()["count"] == 0

if __name__ == "__main__":
    test_live_notifications_two_users_flow()
    print("ALL TWO-USER LIVE NOTIFICATION INTEGRATION TESTS PASSED!")
