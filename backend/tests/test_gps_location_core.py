import sys
import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, startup_event
from app.config.database import Base, engine, SessionLocal
from app.models.location import Location
from app.models.child import Child

client = TestClient(app)

def get_sarah_token():
    """Sarah is caregiver for child-leo-1"""
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def get_david_token():
    """David is an authorized caregiver, but NOT caregiver for child-leo-1"""
    res = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]

def test_openapi_docs_registration():
    """Verify the GPS Location Core endpoints appear in OpenAPI schema / docs."""
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    assert "/api/v1/safety/location" in paths, "POST /api/v1/safety/location is not registered in OpenAPI"
    assert "post" in paths["/api/v1/safety/location"], "POST method missing on /api/v1/safety/location"

    assert "/api/v1/safety/location/{child_id}" in paths, "GET /api/v1/safety/location/{child_id} is not registered in OpenAPI"
    assert "get" in paths["/api/v1/safety/location/{child_id}"], "GET method missing on /api/v1/safety/location/{child_id}"

    assert "/api/v1/safety/location/{child_id}/last" in paths, "GET /api/v1/safety/location/{child_id}/last is not registered in OpenAPI"
    assert "get" in paths["/api/v1/safety/location/{child_id}/last"], "GET method missing on /api/v1/safety/location/{child_id}/last"

def test_save_gps_location_success():
    """Test saving a child's GPS location with all attributes."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "child_id": "child-leo-1",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 4.5,
        "source": "gps",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed": 1.2,
        "heading": 180.0,
        "address": "Golden Gate Park, San Francisco, CA"
    }

    res = client.post("/api/v1/safety/location", json=payload, headers=headers)
    assert res.status_code == 201, f"Expected 201 Created, got {res.status_code}: {res.text}"
    
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["accuracy"] == 4.5
    assert data["source"] == "gps"
    assert "id" in data
    assert "recorded_at" in data or "timestamp" in data

    # Verify persistence directly in DB
    db = SessionLocal()
    try:
        saved = db.query(Location).filter(Location.id == data["id"]).first()
        assert saved is not None
        assert saved.child_id == "child-leo-1"
        assert saved.latitude == 37.7749
        assert saved.longitude == -122.4194
        assert saved.accuracy == 4.5
        assert saved.source == "gps"
    finally:
        db.close()

def test_get_latest_gps_location():
    """Test retrieving child's latest location."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Record first location
    client.post(
        "/api/v1/safety/location",
        json={
            "child_id": "child-leo-1",
            "latitude": 37.7740,
            "longitude": -122.4190,
            "accuracy": 5.0,
            "source": "gps"
        },
        headers=headers
    )

    # Record newer second location
    client.post(
        "/api/v1/safety/location",
        json={
            "child_id": "child-leo-1",
            "latitude": 37.7755,
            "longitude": -122.4180,
            "accuracy": 3.0,
            "source": "gps"
        },
        headers=headers
    )

    res = client.get("/api/v1/safety/location/child-leo-1", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert data["latitude"] == 37.7755
    assert data["longitude"] == -122.4180
    assert data["accuracy"] == 3.0

def test_get_last_known_gps_location():
    """Test retrieving child's last known location."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/safety/location/child-leo-1/last", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == "child-leo-1"
    assert "latitude" in data
    assert "longitude" in data
    assert "accuracy" in data

def test_unauthenticated_access():
    """Test unauthenticated requests are rejected with 401."""
    res_post = client.post(
        "/api/v1/safety/location",
        json={
            "child_id": "child-leo-1",
            "latitude": 37.7749,
            "longitude": -122.4194,
        }
    )
    assert res_post.status_code == 401

    res_get = client.get("/api/v1/safety/location/child-leo-1")
    assert res_get.status_code == 401

    res_last = client.get("/api/v1/safety/location/child-leo-1/last")
    assert res_last.status_code == 401

def test_unauthorized_caregiver_access():
    """Test David cannot access or save locations for Sarah's child Leo (403 Forbidden)."""
    david_token = get_david_token()
    headers = {"Authorization": f"Bearer {david_token}"}

    # David attempting to save Leo's location
    res_post = client.post(
        "/api/v1/safety/location",
        json={
            "child_id": "child-leo-1",
            "latitude": 37.7749,
            "longitude": -122.4194,
        },
        headers=headers
    )
    assert res_post.status_code == 403

    # David attempting to get Leo's latest location
    res_get = client.get("/api/v1/safety/location/child-leo-1", headers=headers)
    assert res_get.status_code == 403

    # David attempting to get Leo's last known location
    res_last = client.get("/api/v1/safety/location/child-leo-1/last", headers=headers)
    assert res_last.status_code == 403

def test_missing_child_404():
    """Test operations on a non-existent child return 404."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    res_post = client.post(
        "/api/v1/safety/location",
        json={
            "child_id": "child-non-existent-999",
            "latitude": 37.7749,
            "longitude": -122.4194,
        },
        headers=headers
    )
    assert res_post.status_code == 404

    res_get = client.get("/api/v1/safety/location/child-non-existent-999", headers=headers)
    assert res_get.status_code == 404

    res_last = client.get("/api/v1/safety/location/child-non-existent-999/last", headers=headers)
    assert res_last.status_code == 404

def test_invalid_coordinates_and_accuracy():
    """Test validation bounds for latitude (-90 to 90), longitude (-180 to 180), accuracy (>= 0)."""
    token = get_sarah_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid latitude > 90
    res_lat_high = client.post(
        "/api/v1/safety/location",
        json={"child_id": "child-leo-1", "latitude": 91.0, "longitude": 0.0},
        headers=headers
    )
    assert res_lat_high.status_code == 422

    # Invalid latitude < -90
    res_lat_low = client.post(
        "/api/v1/safety/location",
        json={"child_id": "child-leo-1", "latitude": -91.0, "longitude": 0.0},
        headers=headers
    )
    assert res_lat_low.status_code == 422

    # Invalid longitude > 180
    res_lon_high = client.post(
        "/api/v1/safety/location",
        json={"child_id": "child-leo-1", "latitude": 0.0, "longitude": 181.0},
        headers=headers
    )
    assert res_lon_high.status_code == 422

    # Invalid longitude < -180
    res_lon_low = client.post(
        "/api/v1/safety/location",
        json={"child_id": "child-leo-1", "latitude": 0.0, "longitude": -181.0},
        headers=headers
    )
    assert res_lon_low.status_code == 422

    # Invalid accuracy < 0
    res_acc = client.post(
        "/api/v1/safety/location",
        json={"child_id": "child-leo-1", "latitude": 0.0, "longitude": 0.0, "accuracy": -1.0},
        headers=headers
    )
    assert res_acc.status_code == 422
