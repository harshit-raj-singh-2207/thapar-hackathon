import urllib.request
import json

def test_api():
    base = 'http://localhost:8000/api/v1'
    print('Testing Auth...')
    req = urllib.request.Request(
        f'{base}/auth/login',
        data=json.dumps({'email': 'sarah@nivara.app', 'password': 'password123'}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    token = json.loads(res.read())['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print('Auth Success! Token obtained.')

    endpoints = [
        ('GET', '/dashboard'),
        ('GET', '/groups/my/count'),
        ('GET', '/messages/unread/count'),
        ('GET', '/notifications/unread/count'),
        ('GET', '/notifications'),
        ('GET', '/community/online/count'),
        ('GET', '/posts/feed?limit=10'),
        ('GET', '/events/upcoming'),
        ('GET', '/groups/suggested'),
        ('GET', '/caregivers/spotlight'),
        ('GET', '/caregivers'),
        ('GET', '/search?query=support'),
    ]

    for method, path in endpoints:
        r = urllib.request.Request(f'{base}{path}', headers=headers, method=method)
        resp = urllib.request.urlopen(r)
        body = json.loads(resp.read())
        print(f'[{resp.status}] {method} {path} -> SUCCESS (Items/Keys: {len(body)})')

    # Test Post Creation
    create_req = urllib.request.Request(
        f'{base}/posts',
        data=json.dumps({'content': 'Integration test post verification', 'category': 'Daily Wins'}).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    create_res = urllib.request.urlopen(create_req)
    post_data = json.loads(create_res.read())
    post_id = post_data['id']
    print(f'[201] POST /posts -> Created {post_id}')

    # Test Like
    like_req = urllib.request.Request(f'{base}/posts/{post_id}/like', headers=headers, method='POST')
    like_res = urllib.request.urlopen(like_req)
    like_body = json.loads(like_res.read())
    print(f'[{like_res.status}] POST /posts/{post_id}/like -> Liked: {like_body.get("liked")}')

    # Test Unlike
    unlike_req = urllib.request.Request(f'{base}/posts/{post_id}/like', headers=headers, method='DELETE')
    unlike_res = urllib.request.urlopen(unlike_req)
    unlike_body = json.loads(unlike_res.read())
    print(f'[{unlike_res.status}] DELETE /posts/{post_id}/like -> Liked: {unlike_body.get("liked")}')

    # Test Save
    save_req = urllib.request.Request(f'{base}/posts/{post_id}/save', headers=headers, method='POST')
    save_res = urllib.request.urlopen(save_req)
    save_body = json.loads(save_res.read())
    print(f'[{save_res.status}] POST /posts/{post_id}/save -> Saved: {save_body.get("saved")}')

    # Test Unsave
    unsave_req = urllib.request.Request(f'{base}/posts/{post_id}/save', headers=headers, method='DELETE')
    unsave_res = urllib.request.urlopen(unsave_req)
    unsave_body = json.loads(unsave_res.read())
    print(f'[{unsave_res.status}] DELETE /posts/{post_id}/save -> Saved: {unsave_body.get("saved")}')

    # Test Group Join & Leave
    join_req = urllib.request.Request(f'{base}/groups/group-sensory-1/join', headers=headers, method='POST')
    join_res = urllib.request.urlopen(join_req)
    join_body = json.loads(join_res.read())
    print(f'[{join_res.status}] POST /groups/group-sensory-1/join -> Joined: {join_body.get("is_joined")}')

    leave_req = urllib.request.Request(f'{base}/groups/group-sensory-1/leave', headers=headers, method='DELETE')
    leave_res = urllib.request.urlopen(leave_req)
    leave_body = json.loads(leave_res.read())
    print(f'[{leave_res.status}] DELETE /groups/group-sensory-1/leave -> Joined: {leave_body.get("is_joined")}')

    print('ALL DASHBOARD ENDPOINTS VERIFIED SUCCESSFULLY!')

if __name__ == '__main__':
    test_api()
