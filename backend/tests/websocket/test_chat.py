import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine, SessionLocal
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver

client = TestClient(app)

def get_user_tokens():
    res_a = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    token_a = res_a.json()["access_token"]
    id_a = res_a.json()["user_id"]

    res_b = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    token_b = res_b.json()["access_token"]
    id_b = res_b.json()["user_id"]

    return (token_a, id_a), (token_b, id_b)

def receive_event_of_type(ws, target_type, max_reads=10):
    for _ in range(max_reads):
        data = ws.receive_json()
        if data.get("type") == target_type:
            return data
    raise AssertionError(f"Expected event of type '{target_type}' not received within {max_reads} messages.")

def test_websocket_realtime_comments_and_notifications():
    (token_a, id_a), (token_b, id_b) = get_user_tokens()

    # Step 1: User A creates a post
    post_res = client.post(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"content": "What are your child's favorite calming sensory toys?", "category": "Sensory"}
    )
    assert post_res.status_code == 201
    post_id = post_res.json()["id"]

    # Step 2: User A connects to WebSocket to receive live comment notifications and stream
    with client.websocket_connect(f"/api/v1/community/ws?token={token_a}") as ws_a:
        ack_a = receive_event_of_type(ws_a, "connection_ack")
        assert ack_a["user_id"] == id_a

        # User B connects to WebSocket and sends a comment frame
        with client.websocket_connect(f"/api/v1/community/ws?token={token_b}") as ws_b:
            ack_b = receive_event_of_type(ws_b, "connection_ack")
            assert ack_b["user_id"] == id_b

            ws_b.send_json({
                "type": "comment",
                "post_id": post_id,
                "content": "We love weighted blankets and chewable necklaces!"
            })

            ack_sent = receive_event_of_type(ws_b, "comment_sent_ack")
            assert ack_sent["post_id"] == post_id

            # User A receives new_comment broadcast live frame
            comment_evt = receive_event_of_type(ws_a, "new_comment")
            assert comment_evt["post_id"] == post_id
            assert comment_evt["comment"]["content"] == "We love weighted blankets and chewable necklaces!"

            # User A receives comment notification frame
            notif_evt = receive_event_of_type(ws_a, "notification")
            assert notif_evt["data"]["type"] == "comment"

    # Step 3: Verify comments fetched via REST API
    get_comments = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert get_comments.status_code == 200
    comments = get_comments.json()
    assert len(comments) == 1
    assert comments[0]["content"] == "We love weighted blankets and chewable necklaces!"

if __name__ == "__main__":
    test_websocket_realtime_comments_and_notifications()
    print("CHAT WEBSOCKET COMMENTS AND NOTIFICATIONS INTEGRATION TEST PASSED!")
