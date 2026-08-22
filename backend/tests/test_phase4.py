import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

import pytest

client = TestClient(app)

def get_tokens():
    # Login Sarah (Verified Caregiver 1)
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    sarah_token = res1.json()["access_token"]
    sarah_id = res1.json()["user_id"]

    # Login David (Verified Caregiver 2)
    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    david_token = res2.json()["access_token"]
    david_id = res2.json()["user_id"]

    # Login Lisa (Unverified Caregiver)
    res3 = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    lisa_token = res3.json()["access_token"]

    return (sarah_token, sarah_id), (david_token, david_id), lisa_token

def test_1_websocket_unauthenticated_rejected():
    # Unauthenticated connection -> Closed
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/community/ws") as websocket:
            pass

def test_2_websocket_unverified_caregiver_rejected():
    # Unverified caregiver -> Rejected
    _, _, lisa_token = get_tokens()
    with pytest.raises(Exception):
        with client.websocket_connect(f"/api/v1/community/ws?token={lisa_token}") as websocket:
            pass

def test_3_websocket_verified_caregiver_connected_and_ping_pong():
    # Verified caregiver connection -> Accepted & Ping/Pong works
    (sarah_token, sarah_id), _, _ = get_tokens()
    with client.websocket_connect(f"/api/v1/community/ws?token={sarah_token}") as websocket:
        ack = websocket.receive_json()
        assert ack["type"] == "connection_ack"
        assert ack["user_id"] == sarah_id

        # Send Ping -> Receive Pong
        websocket.send_json({"type": "ping"})
        pong = websocket.receive_json()
        assert pong["type"] == "pong"

def test_4_websocket_typing_indicator_events():
    # Test typing indicator events between Sarah and David
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    with client.websocket_connect(f"/api/v1/community/ws?token={sarah_token}") as ws_sarah:
        ws_sarah.receive_json() # connection_ack

        with client.websocket_connect(f"/api/v1/community/ws?token={david_token}") as ws_david:
            ws_david.receive_json() # connection_ack

            # Sarah sends typing start to David
            ws_sarah.send_json({
                "type": "typing_start",
                "chat_id": "chat-test-123",
                "recipient_id": david_id
            })

            typing_event = ws_david.receive_json()
            assert typing_event["type"] == "typing_start"
            assert typing_event["sender_id"] == sarah_id

            # Sarah sends typing stop to David
            ws_sarah.send_json({
                "type": "typing_stop",
                "chat_id": "chat-test-123",
                "recipient_id": david_id
            })

            stop_event = ws_david.receive_json()
            assert stop_event["type"] == "typing_stop"
            assert stop_event["sender_id"] == sarah_id

if __name__ == "__main__":
    test_1_websocket_unauthenticated_rejected()
    test_2_websocket_unverified_caregiver_rejected()
    test_3_websocket_verified_caregiver_connected_and_ping_pong()
    test_4_websocket_typing_indicator_events()
    print("ALL PHASE 4 REAL-TIME WEBSOCKET TESTS PASSED PERFECTLY!")
