import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine, SessionLocal
from app.domains.community.models import Post, Comment, PostLike

client = TestClient(app)

def test_two_users_comments_and_likes_flow():
    """
    End-to-end multi-user security & database persistence test for comments & likes.
    """
    # 1. Login User A (Sarah - Verified Caregiver)
    login_a = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]
    user_a_id = login_a.json()["user_id"]

    # 2. Login User B (David - Verified Caregiver)
    login_b = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]
    user_b_id = login_b.json()["user_id"]

    # 3. User A creates a post
    post_res = client.post(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "content": "User A post: Morning sensory routines discussion.",
            "category": "Sensory"
        }
    )
    assert post_res.status_code == 201
    post_id = post_res.json()["id"]
    assert post_res.json()["author_id"] == user_a_id
    assert post_res.json()["like_count"] == 0
    assert post_res.json()["comment_count"] == 0

    # 4. User A adds a comment to own post
    com_a_res = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"content": "User A first comment: We find dim lighting helps."}
    )
    assert com_a_res.status_code == 201
    comment_a = com_a_res.json()
    comment_a_id = comment_a["id"]
    assert comment_a["author_id"] == user_a_id
    assert comment_a["is_own"] is True
    assert comment_a["content"] == "User A first comment: We find dim lighting helps."

    # 5. User B retrieves the post and comments
    post_b_view = client.get(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert post_b_view.status_code == 200
    assert post_b_view.json()["is_own"] is False
    assert post_b_view.json()["comment_count"] == 1
    assert post_b_view.json()["like_count"] == 0
    assert post_b_view.json()["is_liked"] is False

    # 6. Verify User B sees User A's comment
    comments_b_view = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert comments_b_view.status_code == 200
    comments_b_list = comments_b_view.json()
    assert len(comments_b_list) == 1
    assert comments_b_list[0]["id"] == comment_a_id
    assert comments_b_list[0]["author_name"] == "Sarah Mitchell"
    assert comments_b_list[0]["is_own"] is False

    # 7. Security: User B CANNOT delete User A's comment -> 403
    unauth_del = client.delete(
        f"/api/v1/community/posts/{post_id}/comments/{comment_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert unauth_del.status_code == 403

    # 8. User B comments on the post
    com_b_res = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"content": "User B reply: Sound machines also make a huge difference."}
    )
    assert com_b_res.status_code == 201
    comment_b = com_b_res.json()
    comment_b_id = comment_b["id"]
    assert comment_b["author_id"] == user_b_id
    assert comment_b["is_own"] is True

    # 9. Verify User A can see User B's comment
    comments_a_view = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert comments_a_view.status_code == 200
    comments_a_list = comments_a_view.json()
    assert len(comments_a_list) == 2
    assert any(c["id"] == comment_b_id and c["is_own"] is False and c["author_name"] == "David Nguyen" for c in comments_a_list)

    # 10. User B likes the post
    like_res = client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert like_res.status_code == 200
    assert like_res.json()["like_count"] == 1
    assert like_res.json()["is_liked"] is True

    # Check post view from User A: like_count is 1, is_liked is False
    post_a_view = client.get(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert post_a_view.json()["like_count"] == 1
    assert post_a_view.json()["is_liked"] is False

    # Check post view from User B: like_count is 1, is_liked is True
    post_b_view2 = client.get(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert post_b_view2.json()["like_count"] == 1
    assert post_b_view2.json()["is_liked"] is True

    # 11. User B unlikes the post
    unlike_res = client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert unlike_res.status_code == 200
    assert unlike_res.json()["like_count"] == 0
    assert unlike_res.json()["is_liked"] is False

    # 12. Direct Database persistence check
    db = SessionLocal()
    try:
        db_post = db.query(Post).filter(Post.id == post_id).first()
        assert db_post is not None
        db_comments = db.query(Comment).filter(Comment.post_id == post_id).all()
        assert len(db_comments) == 2
        db_likes = db.query(PostLike).filter(PostLike.post_id == post_id).all()
        assert len(db_likes) == 0
    finally:
        db.close()

    # 13. User B deletes User B's own comment -> 200
    del_b_res = client.delete(
        f"/api/v1/community/posts/{post_id}/comments/{comment_b_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert del_b_res.status_code == 200

    # 14. User A deletes own post -> 200 (cascade removes remaining comments)
    del_post_res = client.delete(
        f"/api/v1/community/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert del_post_res.status_code == 200
