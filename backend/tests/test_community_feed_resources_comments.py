import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

client = TestClient(app)

def get_tokens():
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    sarah_token = res1.json()["access_token"]
    sarah_id = res1.json()["user_id"]

    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    david_token = res2.json()["access_token"]
    david_id = res2.json()["user_id"]

    res3 = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    lisa_token = res3.json()["access_token"]

    return (sarah_token, sarah_id), (david_token, david_id), lisa_token

def test_1_feed_get_and_filter():
    (sarah_token, _), _, _ = get_tokens()
    # Get all posts
    res = client.get(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res.status_code == 200
    posts = res.json()
    assert isinstance(posts, list)
    assert len(posts) >= 1
    assert "author" in posts[0]
    assert "content" in posts[0]

    # Filter by category
    res_cat = client.get(
        "/api/v1/community/posts?category=Resources",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res_cat.status_code == 200
    filtered = res_cat.json()
    for p in filtered:
        assert p["category"].lower() == "resources"

def test_2_post_crud_and_like():
    (sarah_token, _), (david_token, _), _ = get_tokens()
    # Create post
    create_res = client.post(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {sarah_token}"},
        json={
            "content": "Sensory-friendly morning routine tips for non-verbal kids.",
            "category": "Tips"
        }
    )
    assert create_res.status_code == 201
    post = create_res.json()
    post_id = post["id"]
    assert post["content"] == "Sensory-friendly morning routine tips for non-verbal kids."
    assert post["is_own"] is True

    # Toggle like from David
    like_res = client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert like_res.status_code == 200
    assert like_res.json()["like_count"] == 1
    assert like_res.json()["is_liked"] is True

    # Update post by Sarah (owner)
    update_res = client.put(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {sarah_token}"},
        json={"content": "Updated sensory-friendly morning routine tips.", "category": "Sensory"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["content"] == "Updated sensory-friendly morning routine tips."

    # David cannot delete Sarah's post
    unauth_del = client.delete(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert unauth_del.status_code == 403

    # Sarah deletes her own post
    del_res = client.delete(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert del_res.status_code == 200

def test_3_resources_crud():
    (sarah_token, _), (david_token, _), _ = get_tokens()
    # List resources
    res_list = client.get(
        "/api/v1/community/resources",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res_list.status_code == 200
    resources = res_list.json()
    assert isinstance(resources, list)
    assert len(resources) >= 1

    # Create new resource
    new_res = client.post(
        "/api/v1/community/resources",
        headers={"Authorization": f"Bearer {sarah_token}"},
        json={
            "title": "ABA Token Economy Printable Board",
            "description": "Visual token economy reward system chart with token cutouts.",
            "category": "ABA",
            "file_type": "template",
            "url": "https://nivara.app/resources/token-economy.pdf"
        }
    )
    assert new_res.status_code == 201
    res_data = new_res.json()
    res_id = res_data["id"]
    assert res_data["title"] == "ABA Token Economy Printable Board"
    assert res_data["author"]["name"] == "Sarah Mitchell"

    # Get details
    detail_res = client.get(
        f"/api/v1/community/resources/{res_id}",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == res_id

    # Update resource
    upd = client.put(
        f"/api/v1/community/resources/{res_id}",
        headers={"Authorization": f"Bearer {sarah_token}"},
        json={"title": "Updated ABA Token Economy Board"}
    )
    assert upd.status_code == 200
    assert upd.json()["title"] == "Updated ABA Token Economy Board"

    # Delete resource
    del_r = client.delete(
        f"/api/v1/community/resources/{res_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert del_r.status_code == 200

def test_4_comments_crud_and_count():
    (sarah_token, _), (david_token, _), _ = get_tokens()
    # Create a post first
    post_res = client.post(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {sarah_token}"},
        json={"content": "Post for comment testing.", "category": "Questions"}
    )
    assert post_res.status_code == 201
    post_id = post_res.json()["id"]

    # Add comment by David
    com_res = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {david_token}"},
        json={"content": "Here is a helpful suggestion for your question."}
    )
    assert com_res.status_code == 201
    comment = com_res.json()
    comment_id = comment["id"]
    assert comment["content"] == "Here is a helpful suggestion for your question."
    assert comment["author_name"] == "David Nguyen"

    # Fetch comments for post
    list_com = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert list_com.status_code == 200
    comments = list_com.json()
    assert len(comments) == 1
    assert comments[0]["id"] == comment_id

    # Update comment by David
    upd_com = client.put(
        f"/api/v1/community/comments/{comment_id}",
        headers={"Authorization": f"Bearer {david_token}"},
        json={"content": "Updated suggestion for your question."}
    )
    assert upd_com.status_code == 200
    assert upd_com.json()["content"] == "Updated suggestion for your question."

    # Sarah cannot delete David's comment
    unauth_del = client.delete(
        f"/api/v1/community/comments/{comment_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert unauth_del.status_code == 403

    # David deletes his own comment
    del_com = client.delete(
        f"/api/v1/community/comments/{comment_id}",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert del_com.status_code == 200

    # Clean up post
    await_del = client.delete(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert await_del.status_code == 200
