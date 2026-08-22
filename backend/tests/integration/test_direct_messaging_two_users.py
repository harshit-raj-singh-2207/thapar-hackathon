import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine, SessionLocal
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Conversation, DirectMessage

import pytest

client = TestClient(app)

def get_tokens():
    # User A: Sarah
    res_a = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res_a.status_code == 200
    token_a = res_a.json()["access_token"]
    id_a = res_a.json()["user_id"]

    # User B: David
    res_b = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res_b.status_code == 200
    token_b = res_b.json()["access_token"]
    id_b = res_b.json()["user_id"]

    # User C: Lisa (Third Party)
    res_c = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    assert res_c.status_code == 200
    token_c = res_c.json()["access_token"]
    id_c = res_c.json()["user_id"]

    return (token_a, id_a), (token_b, id_b), (token_c, id_c)

def receive_event_of_type(ws, target_type, max_reads=10):
    for _ in range(max_reads):
        data = ws.receive_json()
        print(f"WS received event: {data.get('type')} (looking for: {target_type})", flush=True)
        if data.get("type") == target_type:
            return data
    raise AssertionError(f"Expected event of type '{target_type}' not received within {max_reads} messages.")

def test_whatsapp_style_direct_messaging_full_flow():
    (token_a, id_a), (token_b, id_b), (token_c, id_c) = get_tokens()

    # Step 1: User A creates / starts conversation with User B
    conv_res = client.post(
        "/api/v1/community/chats",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"recipient_id": id_b}
    )
    assert conv_res.status_code in [200, 201]
    chat_id = conv_res.json()["id"]

    # Step 2: Verify chat history starts empty
    hist_res = client.get(
        f"/api/v1/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert hist_res.status_code == 200
    assert len(hist_res.json()) == 0

    # Step 3: LIVE MESSAGE DELIVERY (User B is connected to WebSocket)
    with client.websocket_connect(f"/api/v1/community/ws?token={token_b}") as ws_b:
        ack_b = receive_event_of_type(ws_b, "connection_ack")
        assert ack_b["user_id"] == id_b

        # User A sends "Hello B"
        send_res = client.post(
            f"/api/v1/community/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"text": "Hello B"}
        )
        assert send_res.status_code == 201
        assert send_res.json()["status"] == "delivered"
        msg1_id = send_res.json()["id"]

        # User B receives live direct_message event over WebSocket
        msg_b = receive_event_of_type(ws_b, "direct_message")
        assert msg_b["text"] == "Hello B"
        assert msg_b["sender_id"] == id_a
        assert msg_b["status"] == "delivered"
        assert msg_b["id"] == msg1_id

        # Step 4: DATABASE PERSISTENCE VERIFICATION
        db = SessionLocal()
        db_msg = db.query(DirectMessage).filter(DirectMessage.id == msg1_id).first()
        assert db_msg is not None
        assert db_msg.text == "Hello B"
        assert db_msg.status == "delivered"
        db.close()

        # Step 5: READ RECEIPT
        read_res = client.post(
            f"/api/v1/community/chats/{chat_id}/read",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert read_res.status_code == 200
        assert read_res.json()["marked_count"] >= 1

        # Verify DB status transitioned to 'read'
        db = SessionLocal()
        db_msg = db.query(DirectMessage).filter(DirectMessage.id == msg1_id).first()
        assert db_msg.status == "read"
        db.close()

    # Step 6: TWO-WAY REPLY (User A connects to WebSocket)
    with client.websocket_connect(f"/api/v1/community/ws?token={token_a}") as ws_a:
        ack_a = receive_event_of_type(ws_a, "connection_ack")
        assert ack_a["user_id"] == id_a

        # User B replies "Hello Sarah!"
        reply_res = client.post(
            f"/api/v1/community/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"text": "Hello Sarah!"}
        )
        assert reply_res.status_code == 201
        reply_id = reply_res.json()["id"]

        # User A receives reply live over WebSocket
        reply_ws = receive_event_of_type(ws_a, "direct_message")
        assert reply_ws["text"] == "Hello Sarah!"
        assert reply_ws["sender_id"] == id_b
        assert reply_ws["id"] == reply_id

        # Step 7: NATIVE WEBSOCKET SEND (User A sends via WebSocket frame)
        ws_a.send_json({
            "type": "direct_message",
            "chat_id": chat_id,
            "text": "Sent directly over WS"
        })
        ack_sent = receive_event_of_type(ws_a, "message_sent_ack")
        assert ack_sent["status"] in ["sent", "delivered"]
        ws_msg_id = ack_sent["message_id"]

        # Verify message is saved in DB
        db = SessionLocal()
        db_ws_msg = db.query(DirectMessage).filter(DirectMessage.id == ws_msg_id).first()
        assert db_ws_msg is not None
        assert db_ws_msg.text == "Sent directly over WS"
        db.close()

    # Step 8: OFFLINE TEST (User B is offline)
    send_offline_res = client.post(
        f"/api/v1/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"text": "Are you there?"}
    )
    assert send_offline_res.status_code == 201
    assert send_offline_res.json()["status"] == "sent"
    offline_msg_id = send_offline_res.json()["id"]

    # Verify message saved in DB with status "sent"
    db = SessionLocal()
    off_msg = db.query(DirectMessage).filter(DirectMessage.id == offline_msg_id).first()
    assert off_msg is not None
    assert off_msg.status == "sent"
    assert off_msg.text == "Are you there?"
    db.close()

    # Step 9: RECONNECTION & SYNC (User B reconnects)
    with client.websocket_connect(f"/api/v1/community/ws?token={token_b}") as ws_b_reconnected:
        ack_re = receive_event_of_type(ws_b_reconnected, "connection_ack")
        assert ack_re["user_id"] == id_b

        # User B fetches message history via REST API
        sync_res = client.get(
            f"/api/v1/community/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert sync_res.status_code == 200
        synced_messages = sync_res.json()
        assert len(synced_messages) == 4

        texts = [m["text"] for m in synced_messages]
        assert texts == ["Hello B", "Hello Sarah!", "Sent directly over WS", "Are you there?"]

        # Confirm no duplicate IDs
        msg_ids = [m["id"] for m in synced_messages]
        assert len(msg_ids) == len(set(msg_ids))

        # Check distinction of own vs received
        last_m = synced_messages[-1]
        assert last_m["is_own"] is False  # Received by B
        assert last_m["text"] == "Are you there?"

        reply_m = synced_messages[1]
        assert reply_m["is_own"] is True   # Sent by B ("Hello Sarah!")

    # Step 10: SECURITY TESTS
    # User C (Lisa) attempts to access Sarah & David's chat messages -> 403 Forbidden
    sec_get = client.get(
        f"/api/v1/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {token_c}"}
    )
    assert sec_get.status_code == 403

    # User C attempts to post a message into Sarah & David's chat -> 403 Forbidden
    sec_post = client.post(
        f"/api/v1/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {token_c}"},
        json={"text": "I am snooping"}
    )
    assert sec_post.status_code == 403

    # User C attempts to mark Sarah & David's chat read -> 403 Forbidden
    sec_read = client.post(
        f"/api/v1/community/chats/{chat_id}/read",
        headers={"Authorization": f"Bearer {token_c}"}
    )
    assert sec_read.status_code == 403

if __name__ == "__main__":
    test_whatsapp_style_direct_messaging_full_flow()
    print("ALL TWO-USER WHATSAPP-STYLE DIRECT MESSAGING INTEGRATION TESTS PASSED!")
