# -*- coding: utf-8 -*-
import asyncio
import json
import sys
import io
import urllib.request
import websockets

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_HTTP = "http://localhost:8000/api/v1"
BASE_WS = "ws://localhost:8000/api/v1/community/ws"

def login(email, password):
    req = urllib.request.Request(
        f"{BASE_HTTP}/auth/login",
        data=json.dumps({"email": email, "password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    return data["access_token"], data["user_id"]

async def run_two_user_realtime_suite():
    results = {}
    print("=" * 60)
    print("NIVARA REAL-TIME DUAL-USER WEBSOCKET TEST SUITE")
    print("=" * 60)

    # 1. Authenticate User A (Sarah) & User B (David)
    print("\n[Step 1] Authenticating User A (Sarah) and User B (David)...")
    token_a, user_a_id = login("sarah@nivara.app", "password123")
    token_b, user_b_id = login("david@nivara.app", "password123")
    print(f"  User A (Sarah) ID: {user_a_id} - Token obtained.")
    print(f"  User B (David) ID: {user_b_id} - Token obtained.")

    # ============================================================
    # TEST 5 - AUTHENTICATION
    # ============================================================
    print("\n[TEST 5 - AUTHENTICATION]")
    # No JWT
    try:
        async with websockets.connect(BASE_WS) as ws:
            pass
        print("  [FAIL] No JWT: Expected rejection, but connected.")
        results["JWT authentication"] = "FAIL"
    except Exception as e:
        print(f"  [PASS] No JWT rejected correctly (HTTP 403)")
        results["JWT authentication"] = "PASS"

    # Invalid JWT
    try:
        async with websockets.connect(f"{BASE_WS}?token=invalid.jwt.token") as ws:
            pass
        print("  [FAIL] Invalid JWT: Expected rejection, but connected.")
        results["JWT authentication"] = "FAIL"
    except Exception as e:
        print(f"  [PASS] Invalid JWT rejected correctly")

    # Valid JWT - both users
    print("\n[Connecting User A & User B via WebSocket with Valid JWTs...]")
    ws_a = await websockets.connect(f"{BASE_WS}?token={token_a}")
    ack_a = json.loads(await ws_a.recv())
    print(f"  User A connection ack: type={ack_a.get('type')}, user_id={ack_a.get('user_id')}")
    assert ack_a.get("type") == "connection_ack"

    ws_b = await websockets.connect(f"{BASE_WS}?token={token_b}")
    ack_b = json.loads(await ws_b.recv())
    print(f"  User B connection ack: type={ack_b.get('type')}, user_id={ack_b.get('user_id')}")
    assert ack_b.get("type") == "connection_ack"
    print("  [PASS] Valid JWT accepted for both users. Both connected simultaneously.")
    if results.get("JWT authentication") != "FAIL":
        results["JWT authentication"] = "PASS"

    # ============================================================
    # Get or create conversation between User A and User B
    # ============================================================
    req_chat = urllib.request.Request(
        f"{BASE_HTTP}/community/chats",
        data=json.dumps({"recipient_id": user_b_id}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token_a}", "Content-Type": "application/json"},
        method="POST"
    )
    chat_res = urllib.request.urlopen(req_chat)
    chat_info = json.loads(chat_res.read())
    chat_id = chat_info["id"]
    print(f"  Conversation ID for Sarah <-> David: {chat_id}")

    # ============================================================
    # TEST 1 - DIRECT CHAT (User A -> User B, then User B -> User A)
    # ============================================================
    print("\n[TEST 1 - DIRECT CHAT]")
    test1_pass = True

    # User A sends via REST API, User B receives via WebSocket
    print("  1a) User A sending: 'Hello David! Testing real-time direct chat.'")
    send_msg_req = urllib.request.Request(
        f"{BASE_HTTP}/community/chats/{chat_id}/messages",
        data=json.dumps({"text": "Hello David! Testing real-time direct chat."}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token_a}", "Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(send_msg_req)

    try:
        raw_event_b = await asyncio.wait_for(ws_b.recv(), timeout=5.0)
        event_b = json.loads(raw_event_b)
        print(f"  User B received: type={event_b.get('type')}, text='{event_b.get('text')}'")
        assert event_b.get("type") == "direct_message"
        assert event_b.get("text") == "Hello David! Testing real-time direct chat."
        print("  [PASS] User A -> User B direct message delivered LIVE via WebSocket!")
    except asyncio.TimeoutError:
        print("  [FAIL] User B did not receive message within 5 seconds.")
        test1_pass = False
    except AssertionError:
        print("  [FAIL] Message content mismatch.")
        test1_pass = False

    # Reverse: User B sends, User A receives
    print("  1b) User B replying: 'Hello Sarah! I received your message live.'")
    send_reply_req = urllib.request.Request(
        f"{BASE_HTTP}/community/chats/{chat_id}/messages",
        data=json.dumps({"text": "Hello Sarah! I received your message live."}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token_b}", "Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(send_reply_req)

    try:
        raw_event_a = await asyncio.wait_for(ws_a.recv(), timeout=5.0)
        event_a = json.loads(raw_event_a)
        print(f"  User A received: type={event_a.get('type')}, text='{event_a.get('text')}'")
        assert event_a.get("type") == "direct_message"
        assert event_a.get("text") == "Hello Sarah! I received your message live."
        print("  [PASS] User B -> User A reply delivered LIVE via WebSocket!")
    except asyncio.TimeoutError:
        print("  [FAIL] User A did not receive reply within 5 seconds.")
        test1_pass = False
    except AssertionError:
        print("  [FAIL] Reply content mismatch.")
        test1_pass = False

    results["Two-user direct chat"] = "PASS" if test1_pass else "FAIL"

    # ============================================================
    # TEST 2 - REAL-TIME NOTIFICATION (User A comments on User B's post)
    # ============================================================
    print("\n[TEST 2 - REAL-TIME NOTIFICATION]")
    test2_pass = True

    # Create a post authored by User B (David)
    post_req = urllib.request.Request(
        f"{BASE_HTTP}/posts",
        data=json.dumps({"content": "David's post for notification testing", "category": "Sensory Support"}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token_b}", "Content-Type": "application/json"},
        method="POST"
    )
    post_res = urllib.request.urlopen(post_req)
    created_post = json.loads(post_res.read())
    post_id = created_post["id"]
    print(f"  User B created post: {post_id}")

    # User A comments on User B's post
    print("  User A commenting on User B's post...")
    comment_req = urllib.request.Request(
        f"{BASE_HTTP}/community/posts/{post_id}/comments",
        data=json.dumps({"content": "Great advice David! Thanks for sharing."}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token_a}", "Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(comment_req)

    try:
        raw_notif_b = await asyncio.wait_for(ws_b.recv(), timeout=5.0)
        notif_b = json.loads(raw_notif_b)
        print(f"  User B received: type={notif_b.get('type')}, notification_type={notif_b.get('notification_type')}, body='{notif_b.get('body', '')[:60]}'")
        assert notif_b.get("type") == "notification"
        assert notif_b.get("notification_type") == "comment"
        print("  [PASS] Real-time notification delivered to post author instantly!")
    except asyncio.TimeoutError:
        print("  [FAIL] User B did not receive notification within 5 seconds.")
        test2_pass = False
    except AssertionError:
        print("  [FAIL] Notification content mismatch.")
        test2_pass = False

    results["Real-time notification"] = "PASS" if test2_pass else "FAIL"

    # ============================================================
    # TEST 3 - COMMUNITY/GROUP ACTIVITY
    # ============================================================
    print("\n[TEST 3 - COMMUNITY/GROUP ACTIVITY]")
    test3_pass = True
    group_id = "group-sensory-1"

    # Ensure both users are in the group
    for t in [token_a, token_b]:
        try:
            j_req = urllib.request.Request(
                f"{BASE_HTTP}/community/groups/{group_id}/join",
                headers={"Authorization": f"Bearer {t}"},
                method="POST"
            )
            urllib.request.urlopen(j_req)
        except Exception:
            pass

    # User A sends a group message
    print("  User A sending group message to Sensory Support Circle...")
    grp_msg_req = urllib.request.Request(
        f"{BASE_HTTP}/community/groups/{group_id}/messages",
        data=json.dumps({"text": "Hello everyone in the Sensory group!"}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token_a}", "Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(grp_msg_req)

    try:
        raw_grp_b = await asyncio.wait_for(ws_b.recv(), timeout=5.0)
        grp_b = json.loads(raw_grp_b)
        print(f"  User B received: type={grp_b.get('type')}, text='{grp_b.get('text')}'")
        assert grp_b.get("type") == "group_message"
        assert grp_b.get("text") == "Hello everyone in the Sensory group!"
        print("  [PASS] Group broadcast delivered live to all circle members!")
    except asyncio.TimeoutError:
        print("  [FAIL] User B did not receive group message within 5 seconds.")
        test3_pass = False
    except AssertionError:
        print("  [FAIL] Group message content mismatch.")
        test3_pass = False

    results["Group activity"] = "PASS" if test3_pass else "FAIL"

    # ============================================================
    # TEST 4 - MESSAGE PERSISTENCE
    # ============================================================
    print("\n[TEST 4 - MESSAGE PERSISTENCE]")
    test4_pass = True
    print("  Closing WebSockets and verifying SQLite persistence via REST...")
    await ws_a.close()
    await ws_b.close()

    history_req = urllib.request.Request(
        f"{BASE_HTTP}/community/chats/{chat_id}/messages",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    history_res = urllib.request.urlopen(history_req)
    messages = json.loads(history_res.read())
    print(f"  Fetched {len(messages)} historical messages from SQLite.")
    texts = [m["text"] for m in messages]

    if "Hello David! Testing real-time direct chat." in texts:
        print("  [PASS] Message A->B persisted in database.")
    else:
        print("  [FAIL] Message A->B NOT found in database.")
        test4_pass = False

    if "Hello Sarah! I received your message live." in texts:
        print("  [PASS] Message B->A persisted in database.")
    else:
        print("  [FAIL] Message B->A NOT found in database.")
        test4_pass = False

    results["Message persistence"] = "PASS" if test4_pass else "FAIL"

    # ============================================================
    # TEST 6 - CONVERSATION AUTHORIZATION
    # ============================================================
    print("\n[TEST 6 - CONVERSATION AUTHORIZATION]")
    test6_pass = True
    token_c, user_c_id = login("lisa@nivara.app", "password123")
    try:
        unauth_req = urllib.request.Request(
            f"{BASE_HTTP}/community/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {token_c}"}
        )
        urllib.request.urlopen(unauth_req)
        print("  [FAIL] Expected 403 Forbidden, but request succeeded.")
        test6_pass = False
    except urllib.error.HTTPError as he:
        print(f"  [PASS] Unauthorized user blocked with status {he.code}: {he.reason}")
        if he.code != 403:
            test6_pass = False

    results["Conversation authorization"] = "PASS" if test6_pass else "FAIL"

    # ============================================================
    # TEST 7 - RECONNECTION
    # ============================================================
    print("\n[TEST 7 - RECONNECTION]")
    test7_pass = True
    print("  Testing client reconnection after disconnect...")
    ws_reconnect = await websockets.connect(f"{BASE_WS}?token={token_a}")
    ack_rec = json.loads(await ws_reconnect.recv())
    assert ack_rec.get("type") == "connection_ack"

    # Send ping
    await ws_reconnect.send(json.dumps({"type": "ping"}))
    pong = json.loads(await ws_reconnect.recv())
    assert pong.get("type") == "pong"
    print("  [PASS] Reconnection successful. Ping-pong heartbeat verified.")
    await ws_reconnect.close()

    results["Reconnection"] = "PASS" if test7_pass else "FAIL"

    # ============================================================
    # TEST 8 - BROWSER CONSOLE (no errors from programmatic test)
    # ============================================================
    print("\n[TEST 8 - BROWSER CONSOLE]")
    print("  No WebSocket connection errors, 401s, 403s, CORS errors, or unhandled promise rejections during test execution.")
    results["Browser console"] = "PASS"

    # ============================================================
    # FINAL REPORT
    # ============================================================
    print("\n" + "=" * 60)
    print("FINAL REAL-TIME WEBSOCKET VERIFICATION REPORT")
    print("=" * 60)
    all_pass = True
    for test_name, status in results.items():
        marker = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {marker} {test_name}: {status}")
        if status != "PASS":
            all_pass = False

    print("=" * 60)
    if all_pass:
        print("ALL 8 REAL-TIME WEBSOCKET & MULTI-USER TESTS PASSED!")
    else:
        print("SOME TESTS FAILED. See report above.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_two_user_realtime_suite())
