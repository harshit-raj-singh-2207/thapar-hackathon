import sys
import os

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

def test_1_unauthenticated_group_access_denied():
    # Test 1: Unauthenticated request -> 401
    res = client.get("/api/v1/community/groups/discover")
    assert res.status_code == 401

def test_2_unverified_caregiver_group_access_denied():
    # Test 2: Unverified caregiver -> 403
    _, _, lisa_token = get_tokens()
    res = client.post(
        "/api/v1/community/groups",
        json={"name": "Test Unverified Group"},
        headers={"Authorization": f"Bearer {lisa_token}"}
    )
    assert res.status_code == 403
    assert "UNVERIFIED_CAREGIVER" in res.json()["detail"]

def test_3_and_4_create_group_and_creator_becomes_admin():
    # Test 3 & 4: Verified caregiver creates group & automatically becomes admin/member
    (sarah_token, sarah_id), _, _ = get_tokens()

    res = client.post(
        "/api/v1/community/groups",
        json={
            "name": "IEP Advocacy & Educational Rights",
            "description": "Navigating special education, IEP plans, and accommodations.",
            "category": "Education"
        },
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res.status_code == 201
    group_data = res.json()
    assert group_data["name"] == "IEP Advocacy & Educational Rights"
    assert group_data["creator_id"] == sarah_id
    assert group_data["is_joined"] == True
    assert group_data["user_role"] == "admin"
    assert group_data["member_count"] == 1

    return group_data["id"]

def test_5_and_6_discover_and_search_groups():
    # Test 5 & 6: Discover & search groups
    (david_token, _), _, _ = get_tokens()
    group_id = test_3_and_4_create_group_and_creator_becomes_admin()

    # Discover all groups
    res1 = client.get("/api/v1/community/groups/discover", headers={"Authorization": f"Bearer {david_token}"})
    assert res1.status_code == 200
    groups = res1.json()
    assert len(groups) >= 1

    # Search group by keyword "IEP"
    res2 = client.get("/api/v1/community/groups/discover?search=IEP", headers={"Authorization": f"Bearer {david_token}"})
    assert res2.status_code == 200
    search_results = res2.json()
    assert len(search_results) >= 1
    assert "IEP" in search_results[0]["name"]

def test_7_8_9_10_join_duplicate_leave_and_members():
    # Test 7, 8, 9, 10: Join group, prevent duplicate join, list members, leave group
    _, (david_token, david_id), _ = get_tokens()
    group_id = test_3_and_4_create_group_and_creator_becomes_admin()

    # David joins group -> 200
    join_res = client.post(f"/api/v1/community/groups/{group_id}/join", headers={"Authorization": f"Bearer {david_token}"})
    assert join_res.status_code == 200
    assert join_res.json()["is_joined"] == True
    assert join_res.json()["member_count"] == 2

    # David tries to join again -> 400 Bad Request (duplicate prevented)
    dup_res = client.post(f"/api/v1/community/groups/{group_id}/join", headers={"Authorization": f"Bearer {david_token}"})
    assert dup_res.status_code == 400

    # Retrieve members list -> David and Sarah listed
    members_res = client.get(f"/api/v1/community/groups/{group_id}/members", headers={"Authorization": f"Bearer {david_token}"})
    assert members_res.status_code == 200
    members = members_res.json()
    assert len(members) == 2

    # David leaves group -> 200
    leave_res = client.post(f"/api/v1/community/groups/{group_id}/leave", headers={"Authorization": f"Bearer {david_token}"})
    assert leave_res.status_code == 200
    assert leave_res.json()["is_joined"] == False
    assert leave_res.json()["member_count"] == 1

if __name__ == "__main__":
    test_1_unauthenticated_group_access_denied()
    test_2_unverified_caregiver_group_access_denied()
    test_3_and_4_create_group_and_creator_becomes_admin()
    test_5_and_6_discover_and_search_groups()
    test_7_8_9_10_join_duplicate_leave_and_members()
    print("ALL PHASE 3 CAREGIVER GROUPS BACKEND TESTS PASSED PERFECTLY!")
