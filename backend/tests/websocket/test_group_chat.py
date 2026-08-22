import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine, SessionLocal
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Group, GroupMember, GroupMessage

client = TestClient(app)

def get_user_tokens():
    # Sarah (User A)
    res_a = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    token_a = res_a.json()["access_token"]
    id_a = res_a.json()["user_id"]

    # David (User B)
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

def test_group_chat_realtime_websocket_flow():
    (token_a, id_a), (token_b, id_b) = get_user_tokens()

    # Step 1: Create a group with User A
    create_res = client.post(
        "/api/v1/community/groups",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "ABA Strategies Support Group", "description": "Sharing ABA therapy tools", "category": "Sensory"}
    )
    assert create_res.status_code == 201
    group_id = create_res.json()["id"]

    # Step 2: User B joins the group
    join_res = client.post(
        f"/api/v1/community/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert join_res.status_code == 200
    assert join_res.json()["is_joined"] is True

    # Step 3: User B connects to WebSocket and receives live group message sent by User A via WS frame
    with client.websocket_connect(f"/api/v1/community/ws?token={token_b}") as ws_b:
        ack_b = receive_event_of_type(ws_b, "connection_ack")
        assert ack_b["user_id"] == id_b

        # User A sends a message via WebSocket frame
        with client.websocket_connect(f"/api/v1/community/ws?token={token_a}") as ws_a:
            ack_a = receive_event_of_type(ws_a, "connection_ack")
            assert ack_a["user_id"] == id_a

            ws_a.send_json({
                "type": "group_message",
                "group_id": group_id,
                "text": "Welcome to our ABA support circle!"
            })

            # User A gets message_sent_ack
            ack_sent = receive_event_of_type(ws_a, "message_sent_ack")
            assert ack_sent["group_id"] == group_id

            # User B receives live group message frame
            g_msg_b = receive_event_of_type(ws_b, "group_message")
            assert g_msg_b["text"] == "Welcome to our ABA support circle!"
            assert g_msg_b["sender_id"] == id_a

            # User B receives group notification frame
            notif_b = receive_event_of_type(ws_b, "notification")
            assert "Group Message" in notif_b["data"]["title"]

    # Step 4: Verify message persistence via REST API
    msgs_res = client.get(
        f"/api/v1/community/groups/{group_id}/messages",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert msgs_res.status_code == 200
    msgs = msgs_res.json()
    assert len(msgs) >= 1
    assert msgs[0]["text"] == "Welcome to our ABA support circle!"

if __name__ == "__main__":
    test_group_chat_realtime_websocket_flow()
    print("GROUP CHAT WEBSOCKET INTEGRATION TEST PASSED!")
