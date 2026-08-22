import urllib.request
import json
import sqlite3

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req) as res:
        return res.getcode(), json.loads(res.read().decode())

def get(url, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
        return res.getcode(), json.loads(res.read().decode())

def run_live_comment_verification():
    # 1. Login User A (Sarah Mitchell) and User B (David Nguyen)
    code_b, res_b = post('http://localhost:8000/api/v1/auth/login', {'email': 'david@nivara.app', 'password': 'password123'})
    token_b, id_b = res_b['access_token'], res_b['user_id']
    print('[Step 1] User B (David Nguyen) Logged In: Status', code_b)

    code_a, res_a = post('http://localhost:8000/api/v1/auth/login', {'email': 'sarah@nivara.app', 'password': 'password123'})
    token_a, id_a = res_a['access_token'], res_a['user_id']
    print('[Step 1] User A (Sarah Mitchell) Logged In: Status', code_a)

    # 2. User B creates a post
    code_post, post_data = post(
        'http://localhost:8000/api/v1/community/posts',
        {'content': 'Sensory regulation strategies for evening bedtime routine.', 'category': 'Sensory Support'},
        token_b
    )
    post_id = post_data['id']
    print('\n[Step 2] User B Created Post:')
    print('  - Post ID:', post_id)
    print('  - Author Name:', post_data['author_name'])
    print('  - Content:', post_data['content'])
    print('  - Initial comment_count:', post_data['comment_count'])

    # 3. User A views post before commenting
    code_details, details_before = get(f'http://localhost:8000/api/v1/community/posts/{post_id}', token_a)
    print('\n[Step 3] User A Views Post:')
    print('  - HTTP Status:', code_details)
    print('  - Pre-comment count:', details_before['comment_count'])

    # 4. User A posts comment "Great information!"
    code_c, comment_data = post(
        f'http://localhost:8000/api/v1/community/posts/{post_id}/comments',
        {'content': 'Great information!'},
        token_a
    )
    print('\n[Step 4] User A Submits Comment "Great information!":')
    print('  - HTTP Status:', code_c)
    print('  - Comment ID:', comment_data['id'])
    print('  - Author Name:', comment_data['author_name'])
    print('  - Content:', comment_data['content'])
    print('  - Created At (Timestamp):', comment_data['created_at'])

    # 5. User A loads comments list
    code_clist, comments_list = get(f'http://localhost:8000/api/v1/community/posts/{post_id}/comments', token_a)
    print('\n[Step 5] Loaded Comments List:')
    print('  - HTTP Status:', code_clist)
    print('  - Comments Count:', len(comments_list))
    for c in comments_list:
        print(f'  - [Comment] "{c["content"]}" by {c["author_name"]} (is_own: {c["is_own"]}, timestamp: {c["created_at"]})')

    # 6. Reload post details to verify persistent comment count
    code_reload, details_after = get(f'http://localhost:8000/api/v1/community/posts/{post_id}', token_a)
    print('\n[Step 6] Reloaded Post Details:')
    print('  - HTTP Status:', code_reload)
    print('  - Updated comment_count:', details_after['comment_count'])

    # 7. Check SQLite database directly
    conn = sqlite3.connect('nivara.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, author_id, content, created_at FROM comments WHERE post_id = ?', (post_id,))
    rows = cursor.fetchall()
    print('\n[Step 7] Direct SQLite Database Verification:')
    for r in rows:
        print(f'  - DB comments row -> ID: {r[0]} | Author ID: {r[1]} | Content: "{r[2]}" | Created At: {r[3]}')

    cursor.execute('SELECT id, comment_count FROM posts WHERE id = ?', (post_id,))
    p_row = cursor.fetchone()
    print(f'  - DB posts row -> ID: {p_row[0]} | DB comment_count: {p_row[1]}')
    conn.close()

    assert code_c == 201
    assert comment_data['content'] == 'Great information!'
    assert comment_data['author_name'] == 'Sarah Mitchell'
    assert details_after['comment_count'] == 1
    assert len(rows) >= 1
    assert p_row[1] >= 1
    print('\n======================================================')
    print('*** ALL LIVE TWO-USER COMMENT TEST VERIFICATIONS PASSED ***')
    print('======================================================')

if __name__ == '__main__':
    run_live_comment_verification()
