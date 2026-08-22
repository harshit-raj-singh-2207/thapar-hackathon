import asyncio
import json
import urllib.request
import urllib.error
import websockets

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

def delete(url, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers, method='DELETE')
    try:
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

async def main():
    # 1. Login User A (Sarah) and User B (David)
    code_b, res_b = post('http://localhost:8000/api/v1/auth/login', {'email': 'david@nivara.app', 'password': 'password123'})
    token_b, id_b = res_b['access_token'], res_b['user_id']
    print('[Step 1] User B (David) Logged In:', code_b, flush=True)

    code_a, res_a = post('http://localhost:8000/api/v1/auth/login', {'email': 'sarah@nivara.app', 'password': 'password123'})
    token_a, id_a = res_a['access_token'], res_a['user_id']
    print('[Step 1] User A (Sarah) Logged In:', code_a, flush=True)

    # 2. User B creates a post
    code_post, post_data = post(
        'http://localhost:8000/api/v1/community/posts',
        {'content': 'Discussion on visual schedules for non-verbal children.', 'category': 'Daily Routine'},
        token_b
    )
    post_id = post_data['id']
    print(f'\n[Step 2] User B Created Post ({post_id}): Status {code_post}', flush=True)

    # 3. User B connects to live WebSocket
    ws_uri = f'ws://localhost:8000/api/v1/community/ws?token={token_b}'
    print(f'\n[Step 3] User B Connecting to WebSocket: {ws_uri}', flush=True)

    async with websockets.connect(ws_uri) as ws_b:
        # Receive connection_ack
        handshake_raw = await ws_b.recv()
        handshake = json.loads(handshake_raw)
        print('  - WebSocket Handshake Received:', handshake, flush=True)
        assert handshake.get('type') == 'connection_ack'

        # Fetch initial unread count for User B
        _, count_before = get('http://localhost:8000/api/v1/community/notifications/unread-count', token_b)
        initial_unread = count_before.get('count', 0)
        print('  - Initial Unread Notification Count for User B:', initial_unread, flush=True)

        # 4. User A posts a comment on User B's post
        print('\n[Step 4] User A Posting Comment on User B\'s Post...', flush=True)
        code_c, comment_data = post(
            f'http://localhost:8000/api/v1/community/posts/{post_id}/comments',
            {'content': 'Visual schedules worked wonders for our morning routine!'},
            token_a
        )
        print(f'  - User A Comment Created: Status {code_c}, ID: {comment_data["id"]}', flush=True)
        comment_id = comment_data['id']

        # 5. User B receives real-time WebSocket notification LIVE
        print('\n[Step 5] Awaiting Live WebSocket Notification for User B...', flush=True)
        notif_msg_raw = await asyncio.wait_for(ws_b.recv(), timeout=5.0)
        notif_msg = json.loads(notif_msg_raw)
        print('  - Live Notification Event Received on WS:', notif_msg, flush=True)

        assert notif_msg.get('type') == 'notification'
        notif_payload = notif_msg.get('data', {})
        assert notif_payload.get('type') == 'comment'
        assert 'Sarah Mitchell' in notif_payload.get('body', '')
        notif_id = notif_payload.get('id')
        print(f'  [OK] User B received live comment notification for ID: {notif_id}', flush=True)

        # 6. Verify notification badge / unread count increased
        _, count_after = get('http://localhost:8000/api/v1/community/notifications/unread-count', token_b)
        new_unread = count_after.get('count', 0)
        print(f'\n[Step 6] Updated Unread Count for User B: {new_unread} (was {initial_unread})', flush=True)
        assert new_unread == initial_unread + 1

        # 7. User B marks notification as read
        print(f'\n[Step 7] User B Opening/Marking Notification {notif_id} as Read...', flush=True)
        code_read, read_res = post(f'http://localhost:8000/api/v1/community/notifications/{notif_id}/read', {}, token_b)
        print('  - Mark Read Status:', code_read, read_res, flush=True)
        assert code_read == 200
        assert read_res.get('read') is True

        # Verify unread count returned to initial
        _, count_final = get('http://localhost:8000/api/v1/community/notifications/unread-count', token_b)
        assert count_final.get('count', 0) == initial_unread
        print('  [OK] Unread count verified decremented after read action.', flush=True)

    # 8. SECURITY TESTS: COMMENT DELETION OWNERSHIP
    print('\n[Step 8] Testing Comment Deletion Security & Ownership...', flush=True)

    # User B attempts to delete User A's comment -> 403 Forbidden
    del_code_b, del_res_b = delete(
        f'http://localhost:8000/api/v1/community/posts/{post_id}/comments/{comment_id}',
        token_b
    )
    print(f'  - User B Unauthorized Delete Attempt -> Status: {del_code_b}, Detail: {del_res_b.get("detail")}', flush=True)
    assert del_code_b == 403
    assert 'cannot delete' in del_res_b.get('detail', '')
    print('  [OK] Backend rejected unauthorized deletion with HTTP 403 Forbidden.', flush=True)

    # User A deletes their own comment -> 200 OK
    del_code_a, del_res_a = delete(
        f'http://localhost:8000/api/v1/community/posts/{post_id}/comments/{comment_id}',
        token_a
    )
    print(f'  - User A Authorized Delete Attempt -> Status: {del_code_a}, Response: {del_res_a}', flush=True)
    assert del_code_a == 200
    print('  [OK] User A deleted their own comment successfully.', flush=True)

    print('\n======================================================', flush=True)
    print('*** ALL PART 3.3C NOTIFICATION & SECURITY TESTS PASSED ***', flush=True)
    print('======================================================', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
