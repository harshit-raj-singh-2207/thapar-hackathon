import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

client = TestClient(app)

def test_registration_validation_and_creation():
    # 1. Missing fields
    res_empty = client.post("/api/v1/auth/register", json={"email": "", "password": "", "full_name": ""})
    assert res_empty.status_code == 400

    # 2. Short password
    res_short = client.post("/api/v1/auth/register", json={"email": "test@test.com", "password": "123", "full_name": "Test User"})
    assert res_short.status_code == 400
    assert "at least 6 characters" in res_short.json()["detail"]

    # 3. Successful registration
    new_email = f"new_caregiver_{os.urandom(4).hex()}@nivara.app"
    res = client.post("/api/v1/auth/register", json={
        "email": new_email,
        "password": "securepassword123",
        "full_name": "Dr. Eleanor Vance",
        "bio": "Pediatric specialist & caregiver"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["email"] == new_email
    assert data["full_name"] == "Dr. Eleanor Vance"
    assert data["is_verified"] == True

    # 4. Duplicate email rejected
    res_dup = client.post("/api/v1/auth/register", json={
        "email": new_email,
        "password": "securepassword123",
        "full_name": "Dr. Eleanor Vance"
    })
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"]

def test_login_validation_and_jwt():
    # 1. Missing email / password
    res_empty = client.post("/api/v1/auth/login", json={"email": "", "password": ""})
    assert res_empty.status_code == 400

    # 2. Wrong password
    res_wrong = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "wrongpassword"})
    assert res_wrong.status_code == 401
    assert "Incorrect email or password" in res_wrong.json()["detail"]

    # 3. Successful login as verified caregiver
    res_sarah = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res_sarah.status_code == 200
    sarah_data = res_sarah.json()
    assert sarah_data["is_verified"] == True
    assert "access_token" in sarah_data

    # 4. Successful login as unverified caregiver
    res_lisa = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    assert res_lisa.status_code == 200
    lisa_data = res_lisa.json()
    assert lisa_data["is_verified"] == False
    assert lisa_data["verification_status"] == "pending"

def test_forgot_password():
    res = client.post("/api/v1/auth/forgot-password", json={"email": "sarah@nivara.app"})
    assert res.status_code == 200
    assert "instructions have been sent" in res.json()["message"]
