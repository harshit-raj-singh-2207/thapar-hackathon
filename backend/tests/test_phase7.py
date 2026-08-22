import sys
import os

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

def test_1_unauthenticated_and_unverified_comment_access():
    (sarah_token, sarah_id), _, lisa_token = get_tokens()

    # Create post as Sarah
    post_res = client.post(
        "/api/v1/community/posts",
        json={"content": "Sensory kit recommendations."},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    post_id = post_res.json()["id"]

    # 1. Unauthenticated -> 401
    res_unauth = client.get(f"/api/v1/community/posts/{post_id}/comments")
    assert res_unauth.status_code == 401

    # 2. Unverified caregiver -> 403
    res_lisa = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        json={"content": "Test comment"},
        headers={"Authorization": f"Bearer {lisa_token}"}
    )
    assert res_lisa.status_code == 403

def test_2_add_and_list_comments_with_count_tracking():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Create post as Sarah
    post_res = client.post(
        "/api/v1/community/posts",
        json={"content": "What visual schedule app works best?"},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    post_id = post_res.json()["id"]
    assert post_res.json()["comment_count"] == 0

    # David comments on Sarah's post -> 201
    c1_res = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        json={"content": "We use ChoiceWorks and love it!"},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert c1_res.status_code == 201
    c1_data = c1_res.json()
    assert c1_data["author_name"] == "David Nguyen"
    assert c1_data["is_own"] == True # True for David who submitted it

    # Sarah comments on own post -> 201
    c2_res = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        json={"content": "Thanks David, checking that out now."},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert c2_res.status_code == 201
    assert c2_res.json()["is_own"] == True

    # Fetch comments as Sarah -> 200, length == 2
    comments_res = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert comments_res.status_code == 200
    comments = comments_res.json()
    assert len(comments) == 2
    assert comments[0]["content"] == "We use ChoiceWorks and love it!"
    assert comments[0]["is_own"] == False # False for Sarah viewing David's comment
    assert comments[1]["content"] == "Thanks David, checking that out now."
    assert comments[1]["is_own"] == True

    # Check updated post details comment_count == 2
    p_details = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {sarah_token}"})
    assert p_details.json()["comment_count"] == 2

def test_3_delete_comment_ownership_security():
    (sarah_token, sarah_id), (david_token, david_id), _ = get_tokens()

    # Create post as Sarah
    post_res = client.post(
        "/api/v1/community/posts",
        json={"content": "Discussion post."},
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    post_id = post_res.json()["id"]

    # David comments
    c_res = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        json={"content": "David's comment."},
        headers={"Authorization": f"Bearer {david_token}"}
    )
    comment_id = c_res.json()["id"]

    # Sarah attempts to delete David's comment -> 403 Forbidden
    sarah_del = client.delete(
        f"/api/v1/community/posts/{post_id}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert sarah_del.status_code == 403
    assert "cannot delete" in sarah_del.json()["detail"].lower()

    # David deletes own comment -> 200
    david_del = client.delete(
        f"/api/v1/community/posts/{post_id}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert david_del.status_code == 200

    # Post comment count back to 0
    p_details = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {sarah_token}"})
    assert p_details.json()["comment_count"] == 0

if __name__ == "__main__":
    test_1_unauthenticated_and_unverified_comment_access()
    test_2_add_and_list_comments_with_count_tracking()
    test_3_delete_comment_ownership_security()
    print("ALL PHASE 7 COMMUNITY COMMENTS BACKEND TESTS PASSED PERFECTLY!")
