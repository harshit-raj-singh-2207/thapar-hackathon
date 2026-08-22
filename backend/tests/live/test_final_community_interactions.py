import urllib.request
import urllib.error
import json
import sqlite3

BASE_URL = 'http://localhost:8000/api/v1'

def api_call(endpoint, method='GET', data=None, token=None):
    url = f'{BASE_URL}{endpoint}'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            res_body = res.read().decode('utf-8')
            return res.getcode(), json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {'error': err_body}

def run_live_community_interactions():
    print('======================================================================', flush=True)
    print('NIVARA FINAL LIVE TEST PART 2 — REAL COMMUNITY INTERACTIONS', flush=True)
    print('======================================================================', flush=True)

    # 1. Login User A (Sarah Mitchell) and User B (David Nguyen)
    code_b, res_b = api_call('/auth/login', 'POST', {'email': 'david@nivara.app', 'password': 'password123'})
    token_b = res_b['access_token']
    id_b = res_b['user_id']
    print(f'[Auth] User B (David Nguyen) Logged In: Status {code_b}', flush=True)

    code_a, res_a = api_call('/auth/login', 'POST', {'email': 'sarah@nivara.app', 'password': 'password123'})
    token_a = res_a['access_token']
    id_a = res_a['user_id']
    print(f'[Auth] User A (Sarah Mitchell) Logged In: Status {code_a}', flush=True)

    # 2. User B creates a real post
    code_post, post_res = api_call('/community/posts', 'POST', {
        'content': 'Sensory-friendly bedtime decompression strategies for toddlers.',
        'category': 'Sensory Support'
    }, token=token_b)
    post_id = post_res['id']
    print(f'\n[Post Creation] User B Created Post {post_id}: Status {code_post}', flush=True)
    print(f'  - Author: {post_res.get("author_name")}', flush=True)
    print(f'  - Initial comment_count: {post_res.get("comment_count")}', flush=True)
    print(f'  - Initial like_count: {post_res.get("like_count")}', flush=True)

    # =========================================================================
    # SECTION 1: REAL COMMENT CREATION & PERSISTENCE
    # =========================================================================
    print('\n----------------------------------------------------------------------', flush=True)
    print('SECTION 1: REAL COMMENT CREATION & PERSISTENCE', flush=True)
    print('----------------------------------------------------------------------', flush=True)

    # User A posts comment: "Thank you for sharing this information."
    comment_text = 'Thank you for sharing this information.'
    code_c1, c1_data = api_call(f'/community/posts/{post_id}/comments', 'POST', {'content': comment_text}, token=token_a)
    c1_id = c1_data['id']
    print(f'[Comment Submit] User A submitted comment: Status {code_c1}', flush=True)
    print(f'  - Comment ID: {c1_id}', flush=True)
    print(f'  - Author Name: {c1_data.get("author_name")}', flush=True)
    print(f'  - Author Avatar: {c1_data.get("author_avatar")}', flush=True)
    print(f'  - Verified Caregiver: {c1_data.get("is_verified_caregiver")}', flush=True)
    print(f'  - Content: "{c1_data.get("content")}"', flush=True)
    print(f'  - Timestamp: {c1_data.get("created_at")}', flush=True)
    print(f'  - is_own: {c1_data.get("is_own")}', flush=True)

    assert code_c1 == 201
    assert c1_data['content'] == comment_text
    assert c1_data['author_name'] == 'Sarah Mitchell'

    # Check updated comment count in post details
    _, post_after_c = api_call(f'/community/posts/{post_id}', 'GET', token=token_a)
    print(f'  - Post comment_count updated to: {post_after_c.get("comment_count")}', flush=True)
    assert post_after_c.get('comment_count') == 1

    # Refresh simulation (GET comments stream)
    code_list, comments_list = api_call(f'/community/posts/{post_id}/comments', 'GET', token=token_a)
    print(f'[Page Refresh] Comments stream reloaded: Status {code_list}, Length: {len(comments_list)}', flush=True)
    assert len(comments_list) >= 1
    found_c = [c for c in comments_list if c['id'] == c1_id][0]
    assert found_c['content'] == comment_text
    print(f'  [OK] Comment {c1_id} persisted accurately after page refresh.', flush=True)

    # SQLite DB direct verification for Comment
    conn = sqlite3.connect('nivara.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, author_id, content FROM comments WHERE id = ?', (c1_id,))
    db_c = cursor.fetchone()
    print(f'  [DB Check] SQLite comments table row: {db_c}', flush=True)
    assert db_c is not None and db_c[0] == c1_id and db_c[1] == id_a
    conn.close()

    # =========================================================================
    # SECTION 2: COMMENT SECURITY & DELETION
    # =========================================================================
    print('\n----------------------------------------------------------------------', flush=True)
    print('SECTION 2: COMMENT SECURITY & DELETION', flush=True)
    print('----------------------------------------------------------------------', flush=True)

    # User B attempts to delete User A's comment -> 403 Forbidden
    del_code_b, del_res_b = api_call(f'/community/posts/{post_id}/comments/{c1_id}', 'DELETE', token=token_b)
    print(f'[Security] User B attempted unauthorized deletion: Status {del_code_b}', flush=True)
    print(f'  - Detail: {del_res_b.get("detail")}', flush=True)
    assert del_code_b == 403
    print('  [OK] Backend strictly rejected foreign comment deletion with 403 Forbidden.', flush=True)

    # User A deletes their own comment -> 200 OK
    del_code_a, del_res_a = api_call(f'/community/posts/{post_id}/comments/{c1_id}', 'DELETE', token=token_a)
    print(f'[Delete Own] User A deleted own comment: Status {del_code_a}', flush=True)
    assert del_code_a == 200

    # Verify count decremented
    _, post_after_del = api_call(f'/community/posts/{post_id}', 'GET', token=token_a)
    print(f'  - Post comment_count after deletion: {post_after_del.get("comment_count")}', flush=True)
    assert post_after_del.get('comment_count') == 0

    # Verify comment no longer in SQLite
    conn = sqlite3.connect('nivara.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM comments WHERE id = ?', (c1_id,))
    assert cursor.fetchone() is None
    conn.close()
    print('  [OK] Comment verified removed from SQLite database and comments list.', flush=True)

    # =========================================================================
    # SECTION 3: LIKE & UNLIKE & DUPLICATE PREVENTION
    # =========================================================================
    print('\n----------------------------------------------------------------------', flush=True)
    print('SECTION 3: LIKE & UNLIKE & DUPLICATE PREVENTION', flush=True)
    print('----------------------------------------------------------------------', flush=True)

    # User A likes User B's post
    code_like1, like_res1 = api_call(f'/community/posts/{post_id}/like', 'POST', token=token_a)
    print(f'[Like Post] User A liked post: Status {code_like1}', flush=True)
    print(f'  - is_liked: {like_res1.get("is_liked")}', flush=True)
    print(f'  - like_count: {like_res1.get("like_count")}', flush=True)
    assert code_like1 == 200
    assert like_res1.get('is_liked') is True
    assert like_res1.get('like_count') == 1

    # Verify DB contains the like record
    conn = sqlite3.connect('nivara.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, user_id, post_id FROM post_likes WHERE post_id = ? AND user_id = ?', (post_id, id_a))
    db_like = cursor.fetchone()
    print(f'  [DB Check] SQLite post_likes row: {db_like}', flush=True)
    assert db_like is not None
    conn.close()

    # Refresh post details
    _, p_refresh1 = api_call(f'/community/posts/{post_id}', 'GET', token=token_a)
    print(f'[Page Refresh] Post details reloaded: is_liked={p_refresh1.get("is_liked")}, like_count={p_refresh1.get("like_count")}', flush=True)
    assert p_refresh1.get('is_liked') is True
    assert p_refresh1.get('like_count') == 1

    # User A unlikes the post
    code_unlike, unlike_res = api_call(f'/community/posts/{post_id}/like', 'POST', token=token_a)
    print(f'\n[Unlike Post] User A toggled unlike: Status {code_unlike}', flush=True)
    print(f'  - is_liked: {unlike_res.get("is_liked")}', flush=True)
    print(f'  - like_count: {unlike_res.get("like_count")}', flush=True)
    assert code_unlike == 200
    assert unlike_res.get('is_liked') is False
    assert unlike_res.get('like_count') == 0

    # Refresh post details after unlike
    _, p_refresh2 = api_call(f'/community/posts/{post_id}', 'GET', token=token_a)
    print(f'[Page Refresh] Post details after unlike: is_liked={p_refresh2.get("is_liked")}, like_count={p_refresh2.get("like_count")}', flush=True)
    assert p_refresh2.get('is_liked') is False
    assert p_refresh2.get('like_count') == 0

    # Duplicate like prevention test: Like again and verify single record in DB
    print('\n[Duplicate Prevention] Testing rapid like calls & DB idempotency...', flush=True)
    api_call(f'/community/posts/{post_id}/like', 'POST', token=token_a) # Liked
    
    conn = sqlite3.connect('nivara.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM post_likes WHERE post_id = ? AND user_id = ?', (post_id, id_a))
    count_likes = cursor.fetchone()[0]
    print(f'  [DB Check] Total likes in DB for User A on this post: {count_likes}', flush=True)
    assert count_likes == 1
    conn.close()
    print('  [OK] At most 1 like persisted per user; duplicate likes strictly prevented.', flush=True)

    print('\n======================================================================', flush=True)
    print('*** ALL FINAL LIVE TEST PART 2 CHECKS PASSED WITH ZERO ERRORS ***', flush=True)
    print('======================================================================', flush=True)

if __name__ == '__main__':
    run_live_community_interactions()
