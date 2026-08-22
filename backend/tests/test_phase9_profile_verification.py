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

    # Login Lisa (Unverified Caregiver)
    res2 = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    lisa_token = res2.json()["access_token"]

    return sarah_token, lisa_token

def test_1_unauthenticated_profile_update_and_verification_rejected():
    res1 = client.patch("/api/v1/caregivers/me/profile", json={"bio": "Hacker Bio"})
    assert res1.status_code == 401

    res2 = client.post("/api/v1/caregivers/me/verification-request", json={"role_bio": "Hacker Role"})
    assert res2.status_code == 401

def test_2_profile_update_and_persistence():
    sarah_token, _ = get_tokens()
    headers = {"Authorization": f"Bearer {sarah_token}"}

    # Update bio and avatar
    update_res = client.patch(
        "/api/v1/caregivers/me/profile",
        json={"bio": "Parent of child with ASD, active in community", "avatar_url": "https://example.com/sarah_new.jpg"},
        headers=headers
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["bio"] == "Parent of child with ASD, active in community"
    assert data["avatar_url"] == "https://example.com/sarah_new.jpg"

    # Persistence check
    get_res = client.get("/api/v1/caregivers/me/profile", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["bio"] == "Parent of child with ASD, active in community"

def test_3_verification_request_submission_and_duplicate_update():
    _, lisa_token = get_tokens()
    headers = {"Authorization": f"Bearer {lisa_token}"}

    # 1. Invalid verification submission (empty role_bio)
    invalid_res = client.post(
        "/api/v1/caregivers/me/verification-request",
        json={"role_bio": "   ", "document_notes": "None"},
        headers=headers
    )
    assert invalid_res.status_code == 400

    # 2. Valid submission
    sub_res = client.post(
        "/api/v1/caregivers/me/verification-request",
        json={"role_bio": "Parent of 8-year-old child with Autism", "document_notes": "Submitted IEP & Diagnosis letter"},
        headers=headers
    )
    assert sub_res.status_code == 201
    sub_data = sub_res.json()
    assert sub_data["status"] == "pending"
    assert sub_data["role_bio"] == "Parent of 8-year-old child with Autism"

    # 3. View status endpoint
    status_res = client.get("/api/v1/caregivers/me/verification-status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "pending"
    assert status_res.json()["role_bio"] == "Parent of 8-year-old child with Autism"

    # 4. Duplicate request updates existing pending submission
    dup_res = client.post(
        "/api/v1/caregivers/me/verification-request",
        json={"role_bio": "Updated Bio: Parent & Special Ed Teacher", "document_notes": "Added Teacher Credential"},
        headers=headers
    )
    assert dup_res.status_code == 201
    assert dup_res.json()["role_bio"] == "Updated Bio: Parent & Special Ed Teacher"
    assert dup_res.json()["id"] == sub_data["id"]  # Same record updated

def test_4_caregiver_jwt_isolation_ownership():
    sarah_token, lisa_token = get_tokens()
    sarah_headers = {"Authorization": f"Bearer {sarah_token}"}
    lisa_headers = {"Authorization": f"Bearer {lisa_token}"}

    # Sarah's profile update only affects Sarah
    client.patch("/api/v1/caregivers/me/profile", json={"bio": "Sarah Unique Bio"}, headers=sarah_headers)

    lisa_profile = client.get("/api/v1/caregivers/me/profile", headers=lisa_headers).json()
    assert lisa_profile["bio"] != "Sarah Unique Bio"

if __name__ == "__main__":
    test_1_unauthenticated_profile_update_and_verification_rejected()
    test_2_profile_update_and_persistence()
    test_3_verification_request_submission_and_duplicate_update()
    test_4_caregiver_jwt_isolation_ownership()
    print("ALL PHASE 2 PROFILE & VERIFICATION TESTS PASSED PERFECTLY!")
