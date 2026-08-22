import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

client = TestClient(app)

def get_tokens():
    # Login Sarah (Verified Caregiver)
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    sarah_token = res1.json()["access_token"]

    # Login David (Verified Caregiver 2)
    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    david_token = res2.json()["access_token"]

    return sarah_token, david_token

def test_1_hotlines_directory():
    res = client.get("/api/v1/support/hotlines")
    assert res.status_code == 200
    data = res.json()
    assert data["emergency_hotline"] == "1-800-CAREGIVER"
    assert len(data["hotlines"]) >= 3

def test_2_unauthenticated_support_requests_rejected():
    res1 = client.get("/api/v1/support/tickets")
    assert res1.status_code == 401

    res2 = client.post("/api/v1/support/tickets", json={"subject": "Help", "description": "Details"})
    assert res2.status_code == 401

    res3 = client.post("/api/v1/support/calls/schedule", json={"time_slot": "Today 3pm"})
    assert res3.status_code == 401

def test_3_create_and_list_support_tickets():
    sarah_token, _ = get_tokens()
    headers = {"Authorization": f"Bearer {sarah_token}"}

    # 1. Invalid ticket creation (empty subject)
    inv_res = client.post("/api/v1/support/tickets", json={"subject": "", "description": "Details"}, headers=headers)
    assert inv_res.status_code == 400

    # 2. Valid ticket creation
    ticket_res = client.post(
        "/api/v1/support/tickets",
        json={
            "subject": "Caregiver Verification Inquiry",
            "category": "Verification Status Query",
            "description": "Please review my submitted IEP document."
        },
        headers=headers
    )
    assert ticket_res.status_code == 201
    ticket_data = ticket_res.json()
    assert ticket_data["subject"] == "Caregiver Verification Inquiry"
    assert ticket_data["status"] == "in_progress"
    assert "SUP-" in ticket_data["ticket_number"]

    # 3. List tickets
    list_res = client.get("/api/v1/support/tickets", headers=headers)
    assert list_res.status_code == 200
    user_tickets = list_res.json()
    assert len(user_tickets) == 1
    assert user_tickets[0]["id"] == ticket_data["id"]

    # 4. Get ticket details
    detail_res = client.get(f"/api/v1/support/tickets/{ticket_data['id']}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["subject"] == "Caregiver Verification Inquiry"

def test_4_ticket_ownership_isolation():
    sarah_token, david_token = get_tokens()
    sarah_headers = {"Authorization": f"Bearer {sarah_token}"}
    david_headers = {"Authorization": f"Bearer {david_token}"}

    # Sarah creates a ticket
    ticket_res = client.post(
        "/api/v1/support/tickets",
        json={"subject": "Sarah Private Ticket", "description": "Private inquiry"},
        headers=sarah_headers
    )
    ticket_id = ticket_res.json()["id"]

    # David attempts to access Sarah's ticket -> Denied (403)
    denied_res = client.get(f"/api/v1/support/tickets/{ticket_id}", headers=david_headers)
    assert denied_res.status_code == 403

def test_5_schedule_support_call():
    sarah_token, _ = get_tokens()
    headers = {"Authorization": f"Bearer {sarah_token}"}

    # 1. Invalid call schedule (empty time_slot)
    inv_res = client.post("/api/v1/support/calls/schedule", json={"time_slot": " "}, headers=headers)
    assert inv_res.status_code == 400

    # 2. Valid call schedule
    call_res = client.post(
        "/api/v1/support/calls/schedule",
        json={"time_slot": "Today, 2:30 PM", "phone_number": "+1-800-555-0199"},
        headers=headers
    )
    assert call_res.status_code == 201
    call_data = call_res.json()
    assert call_data["scheduled_time"] == "Today, 2:30 PM"
    assert call_data["status"] == "scheduled"

    # 3. List calls
    list_res = client.get("/api/v1/support/calls", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

if __name__ == "__main__":
    test_1_hotlines_directory()
    test_2_unauthenticated_support_requests_rejected()
    test_3_create_and_list_support_tickets()
    test_4_ticket_ownership_isolation()
    test_5_schedule_support_call()
    print("ALL PHASE 3 SUPPORT CENTER TESTS PASSED PERFECTLY!")
