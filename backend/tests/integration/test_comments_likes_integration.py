import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine, SessionLocal
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Post, Comment, PostLike
from app.domains.notifications.models import Notification

import pytest

client = TestClient(app)

def get_tokens():
    # User A: Sarah Mitchell (Verified)
    res_a = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    assert res_a.status_code == 200
    token_a = res_a.json()["access_token"]
    id_a = res_a.json()["user_id"]

    # User B: David Nguyen (Verified)
    res_b = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    assert res_b.status_code == 200
    token_b = res_b.json()["access_token"]
    id_b = res_b.json()["user_id"]

    # User C: Lisa Chen (Unverified)
    res_c = client.post("/api/v1/auth/login", json={"email": "lisa@nivara.app", "password": "password123"})
    assert res_c.status_code == 200
    token_c = res_c.json()["access_token"]
    id_c = res_c.json()["user_id"]

    return (token_a, id_a), (token_b, id_b), (token_c, id_c)

def test_comments_and_likes_full_integration():
    (token_a, id_a), (token_b, id_b), (token_c, id_c) = get_tokens()

    # Step 1: User B (David) creates a community post
    post_res = client.post(
        "/api/v1/community/posts",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "content": "Sensory decompression strategies for evening routine.",
            "category": "Sensory Support"
        }
    )
    assert post_res.status_code == 201
    post_id = post_res.json()["id"]
    assert post_res.json()["like_count"] == 0
    assert post_res.json()["comment_count"] == 0

    # Step 2: User A (Sarah) likes User B's post
    like_res1 = client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert like_res1.status_code == 200
    assert like_res1.json()["is_liked"] is True
    assert like_res1.json()["like_count"] == 1

    # Verify DB persistence for Like
    db = SessionLocal()
    like_in_db = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == id_a).first()
    assert like_in_db is not None
    # Verify like notification created for User B
    like_notif = db.query(Notification).filter(Notification.user_id == id_b, Notification.type == "like").first()
    assert like_notif is not None
    assert "Sarah Mitchell" in like_notif.body or "liked" in like_notif.body
    db.close()

    # Step 3: User A toggles unlike
    unlike_res = client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert unlike_res.status_code == 200
    assert unlike_res.json()["is_liked"] is False
    assert unlike_res.json()["like_count"] == 0

    db = SessionLocal()
    assert db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == id_a).first() is None
    db.close()

    # Step 4: User A likes again (like_count -> 1)
    client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_a}"}
    )

    # Step 5: User B likes their own post (like_count -> 2)
    b_like = client.post(
        f"/api/v1/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert b_like.status_code == 200
    assert b_like.json()["is_liked"] is True
    assert b_like.json()["like_count"] == 2

    # Verify post details reflect accurate like states
    details_a = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert details_a.json()["is_liked"] is True
    assert details_a.json()["like_count"] == 2

    details_b = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert details_b.json()["is_liked"] is True
    assert details_b.json()["like_count"] == 2

    # Unverified User C is rejected by security dependency
    details_c = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {token_c}"})
    assert details_c.status_code == 403

    # Step 6: User A creates a comment
    comment_res1 = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"content": "This routine helped us tremendously!"}
    )
    assert comment_res1.status_code == 201
    c1 = comment_res1.json()
    c1_id = c1["id"]
    assert c1["author_id"] == id_a
    assert c1["author_name"] == "Sarah Mitchell"
    assert c1["is_own"] is True

    # Check comment count incremented
    post_check = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert post_check.json()["comment_count"] == 1

    # Verify comment notification created for User B
    db = SessionLocal()
    c_notif = db.query(Notification).filter(Notification.user_id == id_b, Notification.type == "comment").first()
    assert c_notif is not None
    assert "Sarah Mitchell" in c_notif.body
    db.close()

    # Step 7: User B creates a comment on own post
    comment_res2 = client.post(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"content": "Thanks Sarah! Glad it worked for you."}
    )
    assert comment_res2.status_code == 201
    c2 = comment_res2.json()
    c2_id = c2["id"]
    assert c2["author_id"] == id_b

    # Check comment count is now 2
    post_check2 = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert post_check2.json()["comment_count"] == 2

    # Step 8: Get comments stream & test is_own distinction
    comments_for_a = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_a}"}
    ).json()
    assert len(comments_for_a) == 2
    assert comments_for_a[0]["id"] == c1_id
    assert comments_for_a[0]["is_own"] is True
    assert comments_for_a[1]["id"] == c2_id
    assert comments_for_a[1]["is_own"] is False

    comments_for_b = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_b}"}
    ).json()
    assert comments_for_b[0]["is_own"] is False
    assert comments_for_b[1]["is_own"] is True

    # Step 9: COMMENT DELETE AUTHORIZATION SECURITY
    # User B attempts to delete User A's comment -> 403 Forbidden
    del_fail_b = client.delete(
        f"/api/v1/community/posts/{post_id}/comments/{c1_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert del_fail_b.status_code == 403
    assert "cannot delete" in del_fail_b.json()["detail"]

    # User C attempts to delete User A's comment -> 403 Forbidden
    del_fail_c = client.delete(
        f"/api/v1/community/posts/{post_id}/comments/{c1_id}",
        headers={"Authorization": f"Bearer {token_c}"}
    )
    assert del_fail_c.status_code == 403

    # User A deletes their own comment -> 200 OK
    del_success = client.delete(
        f"/api/v1/community/posts/{post_id}/comments/{c1_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert del_success.status_code == 200

    # Verify comment count decremented to 1 in DB and API
    post_check3 = client.get(f"/api/v1/community/posts/{post_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert post_check3.json()["comment_count"] == 1

    remaining_comments = client.get(
        f"/api/v1/community/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_a}"}
    ).json()
    assert len(remaining_comments) == 1
    assert remaining_comments[0]["id"] == c2_id

if __name__ == "__main__":
    test_comments_and_likes_full_integration()
    print("ALL COMMENTS AND LIKES INTEGRATION & SECURITY TESTS PASSED!")
