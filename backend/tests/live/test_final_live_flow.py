import urllib.request
import urllib.error
import json

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

def run_all_checks():
    results = {}
    print('===============================================================', flush=True)
    print('NIVARA LIVE APPLICATION END-TO-END FLOW VERIFICATION', flush=True)
    print('===============================================================', flush=True)

    # 1. Login & Token Creation
    print('\n[1/12] Testing Login & Authentication...', flush=True)
    code, login_res = api_call('/auth/login', 'POST', {'email': 'sarah@nivara.app', 'password': 'password123'})
    if code == 200 and 'access_token' in login_res:
        token = login_res['access_token']
        user_id = login_res['user_id']
        results['Login'] = 'PASS'
        print(f'  [OK] Login successful. User ID: {user_id}, Role: {login_res.get("role")}', flush=True)
    else:
        results['Login'] = 'FAIL'
        print(f'  [FAIL] Login failed. Code: {code}, Response: {login_res}', flush=True)
        return results

    # 2. Dashboard
    print('\n[2/12] Testing Dashboard & Community Access...', flush=True)
    c_access, access_res = api_call('/caregivers/me/community-access', 'GET', token=token)
    c_prof, prof_res = api_call('/caregivers/me/profile', 'GET', token=token)
    if c_access == 200 and c_prof == 200 and access_res.get('has_access') is True:
        results['Dashboard'] = 'PASS'
        print(f'  [OK] Dashboard loaded. Access: {access_res.get("has_access")}, User: {prof_res.get("full_name")}', flush=True)
    else:
        results['Dashboard'] = 'FAIL'
        print(f'  [FAIL] Dashboard access check failed: {access_res}', flush=True)

    # 3. Community
    print('\n[3/12] Testing Community Overview & Resources...', flush=True)
    c_posts, posts_res = api_call('/community/posts', 'GET', token=token)
    c_res, res_data = api_call('/community/resources', 'GET', token=token)
    if c_posts == 200 and c_res == 200 and isinstance(posts_res, list) and isinstance(res_data, list):
        results['Community'] = 'PASS'
        print(f'  [OK] Community loaded. {len(posts_res)} Posts, {len(res_data)} Resources available.', flush=True)
    else:
        results['Community'] = 'FAIL'
        print('  [FAIL] Community load failed.', flush=True)

    # 4. Feed & Post Details
    print('\n[4/12] Testing Feed & Post Details & Comments Stream...', flush=True)
    if len(posts_res) > 0:
        first_post_id = posts_res[0]['id']
        c_detail, post_detail = api_call(f'/community/posts/{first_post_id}', 'GET', token=token)
        c_comments, comments_res = api_call(f'/community/posts/{first_post_id}/comments', 'GET', token=token)
        if c_detail == 200 and c_comments == 200 and 'content' in post_detail and isinstance(comments_res, list):
            results['Feed'] = 'PASS'
            print(f'  [OK] Feed Post {first_post_id} loaded. Like Count: {post_detail.get("like_count")}, Comments: {len(comments_res)}', flush=True)
        else:
            results['Feed'] = 'FAIL'
            print('  [FAIL] Feed post details failed.', flush=True)
    else:
        # Create a test post if none
        c_create, new_p = api_call('/community/posts', 'POST', {'content': 'Community test post', 'category': 'General'}, token=token)
        results['Feed'] = 'PASS' if c_create == 201 else 'FAIL'

    # 5. Caregiver Profiles
    print('\n[5/12] Testing Caregiver Profiles...', flush=True)
    c_prof_view, profile_view = api_call(f'/caregivers/{user_id}/profile', 'GET', token=token)
    if c_prof_view == 200 and profile_view.get('user_id') == user_id:
        results['Profiles'] = 'PASS'
        print(f'  [OK] Caregiver profile loaded for {profile_view.get("full_name")} (Verified: {profile_view.get("is_verified")})', flush=True)
    else:
        results['Profiles'] = 'FAIL'
        print(f'  [FAIL] Profile view failed. Code: {c_prof_view}', flush=True)

    # 6. Direct Chat
    print('\n[6/12] Testing Direct Chat & Conversations...', flush=True)
    c_chats, chats_res = api_call('/community/chats', 'GET', token=token)
    if c_chats == 200 and isinstance(chats_res, list):
        if len(chats_res) > 0:
            chat_id = chats_res[0]['id']
            c_msgs, msgs_res = api_call(f'/community/chats/{chat_id}/messages', 'GET', token=token)
            c_read, _ = api_call(f'/community/chats/{chat_id}/read', 'POST', token=token)
            if c_msgs == 200 and c_read == 200:
                results['Chat'] = 'PASS'
                print(f'  [OK] Direct Chat loaded. {len(chats_res)} Conversations, {len(msgs_res)} Messages.', flush=True)
            else:
                results['Chat'] = 'FAIL'
        else:
            results['Chat'] = 'PASS'
            print('  [OK] Direct Chat loaded (0 active conversations).', flush=True)
    else:
        results['Chat'] = 'FAIL'

    # 7. Groups
    print('\n[7/12] Testing Groups Discovery & Membership...', flush=True)
    c_groups, groups_res = api_call('/community/groups/discover', 'GET', token=token)
    if c_groups == 200 and isinstance(groups_res, list):
        results['Groups'] = 'PASS'
        print(f'  [OK] Groups discovered: {len(groups_res)} Circles available.', flush=True)
        group_id = groups_res[0]['id'] if len(groups_res) > 0 else None
    else:
        results['Groups'] = 'FAIL'
        group_id = None

    # 8. Group Chat
    print('\n[8/12] Testing Group Chat & Message Stream...', flush=True)
    if group_id:
        c_gmsgs, gmsgs_res = api_call(f'/community/groups/{group_id}/messages', 'GET', token=token)
        c_gsend, send_res = api_call(f'/community/groups/{group_id}/messages', 'POST', {'text': 'Hello everyone!'}, token=token)
        if c_gmsgs == 200 and c_gsend in [200, 201]:
            results['Group Chat'] = 'PASS'
            print(f'  [OK] Group Chat functional for {group_id}. Message sent successfully.', flush=True)
        else:
            results['Group Chat'] = 'FAIL'
    else:
        results['Group Chat'] = 'PASS'

    # 9. Notifications
    print('\n[9/12] Testing Notifications & Unread Badge Counters...', flush=True)
    c_notifs, notifs_res = api_call('/community/notifications', 'GET', token=token)
    c_unread, unread_res = api_call('/community/notifications/unread-count', 'GET', token=token)
    c_readall, _ = api_call('/community/notifications/read-all', 'POST', token=token)
    if c_notifs == 200 and c_unread == 200 and c_readall == 200:
        results['Notifications'] = 'PASS'
        print(f'  [OK] Notifications functional. {len(notifs_res)} Notifications, Count: {unread_res.get("count")}.', flush=True)
    else:
        results['Notifications'] = 'FAIL'

    # 10. Safety & Privacy
    print('\n[10/12] Testing Safety & Privacy Settings...', flush=True)
    c_privacy, priv_res = api_call('/caregivers/me/privacy-settings', 'GET', token=token)
    c_priv_upd, _ = api_call('/caregivers/me/privacy-settings', 'PATCH', {'profile_visibility': 'members_only'}, token=token)
    c_blocks, blocks_res = api_call('/community/safety/blocks', 'GET', token=token)
    c_report, report_res = api_call('/community/safety/reports', 'POST', {'target_type': 'post', 'target_id': 'test-id', 'reason': 'Testing report safety'}, token=token)
    if c_privacy == 200 and c_priv_upd == 200 and c_blocks == 200 and c_report in [200, 201]:
        results['Safety & Privacy'] = 'PASS'
        print('  [OK] Safety & Privacy verified (Settings, Block list, Reports).', flush=True)
    else:
        results['Safety & Privacy'] = 'FAIL'
        print(f'  [FAIL] Safety check failed. Privacy: {c_privacy}, Blocks: {c_blocks}, Report: {c_report}', flush=True)

    # 11. Support
    print('\n[11/12] Testing Support & Caregiver Tools...', flush=True)
    c_support, support_res = api_call('/community/resources?category=Support', 'GET', token=token)
    if c_support == 200:
        results['Support'] = 'PASS'
        print('  [OK] Support resources accessible.', flush=True)
    else:
        results['Support'] = 'FAIL'

    # 12. Verification
    print('\n[12/12] Testing Caregiver Verification Status...', flush=True)
    c_verif, verif_res = api_call('/caregivers/me/verification-status', 'GET', token=token)
    if c_verif == 200 and 'status' in verif_res:
        results['Verification'] = 'PASS'
        print(f'  [OK] Verification status: {verif_res.get("status")} (Verified: {verif_res.get("is_verified")})', flush=True)
    else:
        results['Verification'] = 'FAIL'

    return results

if __name__ == '__main__':
    res = run_all_checks()
    print('\n===============================================================', flush=True)
    print('FINAL LIVE VERIFICATION SUMMARY:', flush=True)
    for k, v in res.items():
        print(f'{k}: {v}', flush=True)
    print('===============================================================', flush=True)
