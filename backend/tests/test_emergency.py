import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine

client = TestClient(app)

def get_sarah_auth():
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_trigger_sos_and_resolution_flow():
    headers = get_sarah_auth()

    # 1. Trigger SOS emergency
    sos_payload = {
        "child_id": "child-leo-1",
        "triggered_by": "sos_button",
        "severity": "critical",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "123 Serenity Way",
        "message": "Immediate SOS triggered by Leo via smartband button!",
    }
    sos_res = client.post("/api/v1/safety/emergencies/sos", json=sos_payload, headers=headers)
    assert sos_res.status_code == 201
    emg = sos_res.json()
    emg_id = emg["id"]
    assert emg["status"] == "active"
    assert emg["severity"] == "critical"

    # 2. List active emergencies
    active_res = client.get("/api/v1/safety/emergencies/active", headers=headers)
    assert active_res.status_code == 200
    active_list = active_res.json()
    assert any(e["id"] == emg_id for e in active_list)

    # 3. Verify safety event created
    events_res = client.get("/api/v1/safety/safety-events/?event_type=sos_triggered", headers=headers)
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 1

    # 4. Resolve emergency
    resolve_payload = {
        "status": "resolved",
        "resolution_notes": "Caregiver attended immediately. Child is calm and safe."
    }
    resolve_res = client.post(f"/api/v1/safety/emergencies/{emg_id}/resolve", json=resolve_payload, headers=headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "resolved"
    assert resolve_res.json()["resolved_by"] == "user-verified-sarah"

    # 5. Check active emergencies list is now empty
    active_after = client.get("/api/v1/safety/emergencies/active", headers=headers)
    assert not any(e["id"] == emg_id for e in active_after.json())

def test_emergency_contacts_crud():
    headers = get_sarah_auth()

    # Add contact: Officer Mark
    contact_data = {
        "child_id": "child-leo-1",
        "name": "Officer Mark Reynolds",
        "relationship_type": "Community Officer",
        "phone_number": "+1-555-0911",
        "email": "mreynolds@police.gov",
        "priority_order": 2,
        "notify_via_sms": True,
        "notify_via_call": True,
    }
    add_res = client.post("/api/v1/safety/emergency-contacts/", json=contact_data, headers=headers)
    assert add_res.status_code == 201
    c_id = add_res.json()["id"]

    # List contacts
    list_res = client.get("/api/v1/safety/emergency-contacts/", headers=headers)
    assert list_res.status_code == 200
    contacts = list_res.json()
    assert len(contacts) >= 2

    # Delete contact
    del_res = client.delete(f"/api/v1/safety/emergency-contacts/{c_id}", headers=headers)
    assert del_res.status_code == 200
