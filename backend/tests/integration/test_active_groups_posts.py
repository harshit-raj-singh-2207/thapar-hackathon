import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine, SessionLocal
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Post, Group

client = TestClient(app)

def get_tokens():
    res = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"], res.json()["user_id"]

def test_active_groups_posts_flow():
    token, user_id = get_tokens()

    # Step 1: Fetch seeded posts for "Parents of Newly Diagnosed" category
    feed_res = client.get(
        "/api/v1/community/posts?category=Parents of Newly Diagnosed",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert feed_res.status_code == 200
    posts = feed_res.json()
    assert len(posts) >= 2
    contents = [p["content"] for p in posts]
    assert any("diagnosis last week" in c for c in contents)
    assert any("noise-canceling headphones" in c for c in contents)

    # Step 2: Create a new update / question post in "Parents of Newly Diagnosed" category
    new_post_res = client.post(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content": "Can anyone share tips on organizing IEP documents for newly diagnosed toddlers?",
            "category": "Parents of Newly Diagnosed"
        }
    )
    assert new_post_res.status_code == 201
    post_data = new_post_res.json()
    assert post_data["category"] == "Parents of Newly Diagnosed"
    assert "organizing IEP documents" in post_data["content"]
    post_id = post_data["id"]

    # Step 3: Toggle like on the newly created post
    like_res = client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert like_res.status_code == 200
    assert like_res.json()["is_liked"] is True
    assert like_res.json()["like_count"] == 1

    # Step 4: Verify updated feed has the new post
    updated_feed = client.get(
        "/api/v1/community/posts?category=Parents of Newly Diagnosed",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert updated_feed.status_code == 200
    updated_posts = updated_feed.json()
    assert updated_posts[0]["id"] == post_id
    assert updated_posts[0]["is_liked"] is True

if __name__ == "__main__":
    test_active_groups_posts_flow()
    print("ACTIVE GROUPS POSTS INTEGRATION TEST PASSED!")
