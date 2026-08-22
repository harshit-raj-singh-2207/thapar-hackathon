import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

client = TestClient(app)

def get_caregiver_tokens():
    """Helper to authenticate Sarah and David as test caregivers."""
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res1.status_code == 200, f"Login failed for Sarah: {res1.text}"
    sarah_token = res1.json()["access_token"]

    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res2.status_code == 200, f"Login failed for David: {res2.text}"
    david_token = res2.json()["access_token"]

    return sarah_token, david_token

def test_1_hotlines_endpoint_public_and_complete():
    """Verify GET /api/v1/support/hotlines returns complete directory structure."""
    res = client.get("/api/v1/support/hotlines")
    assert res.status_code == 200
    data = res.json()
    assert "emergency_hotline" in data
    assert data["emergency_hotline"] == "1-800-CAREGIVER"
    assert "operating_hours" in data
    assert "hotlines" in data
    assert isinstance(data["hotlines"], list)
    assert len(data["hotlines"]) >= 3

    for item in data["hotlines"]:
        assert "label" in item
        assert "number" in item
        assert "region" in item
        assert "availability" in item

def test_2_security_unauthenticated_requests_blocked():
    """Verify unauthenticated requests return 401 Unauthorized."""
    # Tickets listing
    res_list = client.get("/api/v1/support/tickets")
    assert res_list.status_code == 401
    assert "Missing or invalid token" in res_list.json()["detail"]

    # Ticket creation
    res_create = client.post("/api/v1/support/tickets", json={"subject": "Inquiry", "description": "Need help"})
    assert res_create.status_code == 401

    # Call schedule
    res_call = client.post("/api/v1/support/calls/schedule", json={"time_slot": "Today, 2:30 PM"})
    assert res_call.status_code == 401

    # Calls listing
    res_calls = client.get("/api/v1/support/calls")
    assert res_calls.status_code == 401

def test_3_schedule_support_callback_flow():
    """Verify callback scheduling flow and database persistence."""
    sarah_token, _ = get_caregiver_tokens()
    headers = {"Authorization": f"Bearer {sarah_token}"}

    # 1. Validation failure (empty time slot)
    bad_res = client.post("/api/v1/support/calls/schedule", json={"time_slot": ""}, headers=headers)
    assert bad_res.status_code == 400

    # 2. Valid booking
    booking_res = client.post(
        "/api/v1/support/calls/schedule",
        json={"time_slot": "Tomorrow, 10:00 AM", "phone_number": "+1 (555) 234-5678"},
        headers=headers
    )
    assert booking_res.status_code == 201
    call_data = booking_res.json()
    assert call_data["specialist_name"] == "Sarah J."
    assert call_data["scheduled_time"] == "Tomorrow, 10:00 AM"
    assert call_data["status"] == "scheduled"
    assert "call-" in call_data["id"]

    # 3. Retrieve caregiver's scheduled calls
    calls_res = client.get("/api/v1/support/calls", headers=headers)
    assert calls_res.status_code == 200
    my_calls = calls_res.json()
    assert len(my_calls) >= 1
    assert any(c["id"] == call_data["id"] for c in my_calls)

def test_4_support_ticket_creation_and_retrieval():
    """Verify ticket creation, listing, and single ticket retrieval."""
    sarah_token, _ = get_caregiver_tokens()
    headers = {"Authorization": f"Bearer {sarah_token}"}

    # 1. Validation failure (missing description)
    bad_ticket = client.post("/api/v1/support/tickets", json={"subject": "Inquiry", "description": " "}, headers=headers)
    assert bad_ticket.status_code == 400

    # 2. Valid creation
    create_res = client.post(
        "/api/v1/support/tickets",
        json={
            "subject": "Sensory Routine Assistance",
            "category": "Caregiver Support",
            "description": "Need guidance adapting visual schedules for school mornings."
        },
        headers=headers
    )
    assert create_res.status_code == 201
    ticket = create_res.json()
    assert ticket["subject"] == "Sensory Routine Assistance"
    assert ticket["category"] == "Caregiver Support"
    assert ticket["status"] == "in_progress"
    assert "SUP-" in ticket["ticket_number"]

    # 3. List my tickets
    list_res = client.get("/api/v1/support/tickets", headers=headers)
    assert list_res.status_code == 200
    tickets = list_res.json()
    assert len(tickets) >= 1
    assert any(t["id"] == ticket["id"] for t in tickets)

    # 4. Get ticket by ID
    single_res = client.get(f"/api/v1/support/tickets/{ticket['id']}", headers=headers)
    assert single_res.status_code == 200
    assert single_res.json()["ticket_number"] == ticket["ticket_number"]

def test_5_authorization_and_cross_caregiver_isolation():
    """Ensure Caregiver A cannot access Caregiver B's private support tickets."""
    sarah_token, david_token = get_caregiver_tokens()
    sarah_headers = {"Authorization": f"Bearer {sarah_token}"}
    david_headers = {"Authorization": f"Bearer {david_token}"}

    # Sarah creates private ticket
    sarah_ticket_res = client.post(
        "/api/v1/support/tickets",
        json={"subject": "Sarah Private Document Review", "description": "Confidential medical record inquiry"},
        headers=sarah_headers
    )
    assert sarah_ticket_res.status_code == 201
    sarah_ticket_id = sarah_ticket_res.json()["id"]

    # David attempts to fetch Sarah's ticket -> Denied with 403 Forbidden
    cross_access_res = client.get(f"/api/v1/support/tickets/{sarah_ticket_id}", headers=david_headers)
    assert cross_access_res.status_code == 403
    assert "Access denied" in cross_access_res.json()["detail"]

    # David's ticket list does not contain Sarah's ticket
    david_tickets_res = client.get("/api/v1/support/tickets", headers=david_headers)
    assert david_tickets_res.status_code == 200
    david_ticket_ids = [t["id"] for t in david_tickets_res.json()]
    assert sarah_ticket_id not in david_ticket_ids
