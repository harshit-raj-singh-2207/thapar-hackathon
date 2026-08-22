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

def test_1_unauthenticated_and_unverified_feed_access():
    _, _, lisa_token = get_tokens()

    # 1. Unauthenticated -> 401
    res_unauth = client.get("/api/v1/community/posts")
    assert res_unauth.status_code == 401

    # 2. Unverified caregiver -> 403
    res_lisa = client.get("/api/v1/community/posts", headers={"Authorization": f"Bearer {lisa_token}"})
    assert res_lisa.status_code == 403
    assert "UNVERIFIED_CAREGIVER" in res_lisa.json()["detail"]

def test_2_verified_caregiver_can_load_feed_and_create_post():
    (sarah_token, sarah_id), (david_token, _), _ = get_tokens()

    # Sarah loads feed -> 200
    feed_res = client.get("/api/v1/community/posts", headers={"Authorization": f"Bearer {sarah_token}"})
    assert feed_res.status_code == 200
    posts = feed_res.json()
    assert len(posts) >= 1

    # Sarah creates post with text & image -> 201
    create_res = client.post(
        "/api/v1/community/posts",
        json={
            "content": "Sensory-friendly quiet spaces in public parks — our comprehensive guide for caregivers.",
            "image_url": "/static/uploads/park_guide.jpg"
        },
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert create_res.status_code == 201
    post_data = create_res.json()
    assert post_data["author_id"] == sarah_id
    assert post_data["author_name"] == "Sarah Mitchell"
    assert post_data["is_verified_caregiver"] == True
    assert post_data["is_own"] == True
    assert post_data["image_url"] == "/static/uploads/park_guide.jpg"

def test_3_post_details_and_author_ownership_security():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Create post as Sarah
    create_res = client.post(
        "/api/v1/community/posts",
        json={"content": "Sarah's private caregiver reflection."},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    post_id = create_res.json()["id"]

    # David views post details -> 200, is_own is False
    details_res = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {david_token}"})
    assert details_res.status_code == 200
    assert details_res.json()["is_own"] == False
    assert details_res.json()["author_name"] == "Sarah Mitchell"

    # David attempts to edit Sarah's post -> 403 Forbidden
    edit_res = client.put(
        f"/api/v1/community/posts/{post_id}",
        json={"content": "Unauthorized edit attempt"},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert edit_res.status_code == 403
    assert "cannot edit" in edit_res.json()["detail"].lower()

    # David attempts to delete Sarah's post -> 403 Forbidden
    delete_res = client.delete(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {david_token}"})
    assert delete_res.status_code == 403
    assert "cannot delete" in delete_res.json()["detail"].lower()

    # Sarah updates own post -> 200
    sarah_edit = client.put(
        f"/api/v1/community/posts/{post_id}",
        json={"content": "Sarah's updated reflection with new insights."},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert sarah_edit.status_code == 200
    assert sarah_edit.json()["content"] == "Sarah's updated reflection with new insights."

    # Sarah deletes own post -> 200
    sarah_del = client.delete(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {sarah_token}"})
    assert sarah_del.status_code == 200

def test_4_category_filtering_and_likes():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Sarah creates a "Tips" post
    tip_res = client.post(
        "/api/v1/community/posts",
        json={"content": "Top 5 sensory calming tips.", "category": "Tips"},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert tip_res.status_code == 201
    post_id = tip_res.json()["id"]
    assert tip_res.json()["category"] == "Tips"

    # Filter feed by category "Tips"
    feed_tips = client.get("/api/v1/community/posts?category=Tips", headers={"Authorization": f"Bearer {david_token}"})
    assert feed_tips.status_code == 200
    assert any(p["id"] == post_id for p in feed_tips.json())

    # David likes Sarah's post
    like_res1 = client.post(f"/api/v1/community/posts/{post_id}/like", headers={"Authorization": f"Bearer {david_token}"})
    assert like_res1.status_code == 200
    assert like_res1.json()["like_count"] == 1
    assert like_res1.json()["is_liked"] == True

    # David unlikes the post
    like_res2 = client.post(f"/api/v1/community/posts/{post_id}/like", headers={"Authorization": f"Bearer {david_token}"})
    assert like_res2.status_code == 200
    assert like_res2.json()["like_count"] == 0
    assert like_res2.json()["is_liked"] == False

if __name__ == "__main__":
    test_1_unauthenticated_and_unverified_feed_access()
    test_2_verified_caregiver_can_load_feed_and_create_post()
    test_3_post_details_and_author_ownership_security()
    test_4_category_filtering_and_likes()
    print("ALL PHASE 6 COMMUNITY FEED & POSTS BACKEND TESTS PASSED PERFECTLY!")

