import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

import pytest

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_unauthenticated_profile_access_denied():
    # Attempting to fetch a profile without JWT token must be denied (401)
    res = client.get("/api/v1/caregivers/user-verified-sarah/profile")
    assert res.status_code == 401
    assert "token" in res.json()["detail"].lower()

def test_unverified_caregiver_access_denied():
    # Login as unverified caregiver (Lisa)
    login_res = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert login_res.json()["is_verified"] == False

    # 1. Access check endpoint
    access_res = client.get("/api/v1/caregivers/me/community-access", headers={"Authorization": f"Bearer {token}"})
    assert access_res.status_code == 200
    assert access_res.json()["has_access"] == False

    # 2. Accessing community profile endpoint MUST be denied with 403
    profile_res = client.get("/api/v1/caregivers/user-verified-sarah/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 403
    assert "UNVERIFIED_CAREGIVER" in profile_res.json()["detail"]

def test_verified_caregiver_access_granted():
    # Login as verified caregiver (Sarah)
    login_res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert login_res.json()["is_verified"] == True

    # 1. Access check endpoint
    access_res = client.get("/api/v1/caregivers/me/community-access", headers={"Authorization": f"Bearer {token}"})
    assert access_res.status_code == 200
    assert access_res.json()["has_access"] == True

    # 2. Accessing community profile endpoint MUST succeed (200)
    profile_res = client.get("/api/v1/caregivers/user-verified-sarah/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    data = profile_res.json()
    assert data["name"] == "Sarah Mitchell"
    assert data["is_verified"] == True
    assert "password" not in data
    assert "email" not in data  # Sensitive account data excluded!

if __name__ == "__main__":
    test_health()
    test_unauthenticated_profile_access_denied()
    test_unverified_caregiver_access_denied()
    test_verified_caregiver_access_granted()
    print("ALL PHASE 1 BACKEND & SECURITY VERIFICATION TESTS PASSED PERFECTLY!")
