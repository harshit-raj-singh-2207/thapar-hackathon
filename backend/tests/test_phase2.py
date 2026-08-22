import sys
import os
import io

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

def test_1_unauthenticated_chat_access_denied():
    # Test 1: Unauthenticated request -> 401
    res = client.get("/api/v1/community/chats")
    assert res.status_code == 401

def test_2_unverified_chat_access_denied():
    # Test 2: Unverified caregiver -> 403
    _, _, lisa_token = get_tokens()
    res = client.get("/api/v1/community/chats", headers={"Authorization": f"Bearer {lisa_token}"})
    assert res.status_code == 403
    assert "UNVERIFIED_CAREGIVER" in res.json()["detail"]

def test_3_create_conversation_and_prevent_duplicates():
    # Test 3 & 8: Verified caregiver can create conversation and duplicate is prevented
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Sarah creates chat with David
    res1 = client.post(
        "/api/v1/community/chats",
        json={"recipient_id": david_id},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res1.status_code == 201
    chat_id = res1.json()["id"]

    # David starts chat with Sarah -> Returns same conversation ID (duplicate prevented!)
    res2 = client.post(
        "/api/v1/community/chats",
        json={"recipient_id": sarah_id},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert res2.status_code == 201
    assert res2.json()["id"] == chat_id

    return chat_id

def test_4_send_and_retrieve_messages():
    # Test 4, 5, 6, 9: Send text and media messages, retrieve history
    (sarah_token, _), (david_token, _), _ = get_tokens()
    chat_id = test_3_create_conversation_and_prevent_duplicates()

    # Sarah sends text message
    msg_res = client.post(
        f"/api/v1/community/chats/{chat_id}/messages",
        json={"text": "Hello David! How is your son doing with visual schedules?"},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert msg_res.status_code == 201
    assert msg_res.json()["text"] == "Hello David! How is your son doing with visual schedules?"
    assert msg_res.json()["is_own"] == True

    # Upload media attachment
    file_data = io.BytesIO(b"fake image bytes")
    upload_res = client.post(
        "/api/v1/community/media/upload",
        files={"file": ("sensory_kit.jpg", file_data, "image/jpeg")},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert upload_res.status_code == 200
    media_url = upload_res.json()["url"]

    # Send message with image attachment
    img_msg_res = client.post(
        f"/api/v1/community/chats/{chat_id}/messages",
        json={"text": "Here is our setup!", "image_url": media_url},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert img_msg_res.status_code == 201
    assert img_msg_res.json()["attachment_url"] == media_url

    # David retrieves conversation messages
    history_res = client.get(
        f"/api/v1/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert history_res.status_code == 200
    messages = history_res.json()
    assert len(messages) >= 2
    assert messages[0]["text"] == "Hello David! How is your son doing with visual schedules?"
    assert messages[0]["is_own"] == False  # False for David!

def test_7_unauthorized_caregiver_cannot_access_private_chat():
    # Test 7: Registered caregiver not in conversation cannot read private chat
    _, _, lisa_token = get_tokens()
    chat_id = test_3_create_conversation_and_prevent_duplicates()

    # Lisa tries to access Sarah & David's private conversation -> 403 Forbidden
    res = client.get(
        f"/api/v1/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {lisa_token}"}
    )
    assert res.status_code == 403

if __name__ == "__main__":
    test_1_unauthenticated_chat_access_denied()
    test_2_unverified_chat_access_denied()
    test_3_create_conversation_and_prevent_duplicates()
    test_4_send_and_retrieve_messages()
    test_7_unauthorized_caregiver_cannot_access_private_chat()
    print("ALL PHASE 2 ONE-TO-ONE CHAT BACKEND TESTS PASSED PERFECTLY!")
