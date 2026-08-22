from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import GroupMember, Conversation, DirectMessage, GroupMessage, Post, Comment
from app.domains.notifications.models import Notification
from app.realtime.connection_manager import manager
from app.realtime.presence_manager import presence_manager
from app.realtime.notification_manager import notification_manager

router = APIRouter(prefix="/community", tags=["Realtime WebSocket"])

@router.websocket("/ws")
async def community_websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    user_id = decode_access_token(token)
    if not user_id:
        await websocket.close(code=4001)
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        caregiver = db.query(Caregiver).filter(Caregiver.user_id == user_id).first() if user else None
        
        if not user or not caregiver or not caregiver.is_verified:
            await websocket.close(code=4003)
            return
        
        user_full_name = user.full_name if user else "Caregiver"
        await manager.connect(user_id, websocket)
        await websocket.send_json({"type": "connection_ack", "user_id": user_id})

        presence_manager.set_online(user_id)
        caregiver.is_online = True
        db.commit()

        # Broadcast online presence to other connected users
        await manager.broadcast_to_others({
            "type": "presence_change",
            "user_id": user_id,
            "is_online": True,
        }, exclude_user_id=user_id)

        # Deliver pending offline messages for this user and notify senders
        pending_msgs = db.query(DirectMessage).join(Conversation).filter(
            or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id),
            DirectMessage.sender_id != user_id,
            DirectMessage.status == "sent"
        ).all()
        for p_msg in pending_msgs:
            p_msg.status = "delivered"
            await manager.send_personal_message({
                "type": "message_delivered",
                "message_id": p_msg.id,
                "conversation_id": p_msg.conversation_id,
            }, p_msg.sender_id)
        if pending_msgs:
            db.commit()


        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            print(f"[WS Server] User {user_id} received frame type: {msg_type}", flush=True)

            try:
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type in ["chat", "direct_message", "chat_message"]:
                    chat_id = data.get("chat_id") or data.get("conversation_id")
                    text = data.get("text")
                    image_url = data.get("image_url") or data.get("attachment_url")
                    
                    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
                    if conv and (conv.user1_id == user_id or conv.user2_id == user_id):
                        recipient_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
                        is_recipient_online = manager.is_user_connected(recipient_id)
                        initial_status = "delivered" if is_recipient_online else "sent"
                        
                        msg = DirectMessage(
                            conversation_id=chat_id,
                            sender_id=user_id,
                            text=text,
                            attachment_url=image_url,
                            status=initial_status,
                        )
                        db.add(msg)
                        conv.updated_at = datetime.utcnow()
                        
                        notif = Notification(
                            user_id=recipient_id,
                            type="message",
                            title=user_full_name,
                            body=text or "Sent an attachment",
                        )
                        db.add(notif)
                        db.commit()
                        db.refresh(msg)
                        
                        event_payload = {
                            "type": "direct_message",
                            "id": msg.id,
                            "conversation_id": msg.conversation_id,
                            "chat_id": msg.conversation_id,
                            "sender_id": msg.sender_id,
                            "sender_name": user_full_name,
                            "text": msg.text,
                            "attachment_url": msg.attachment_url,
                            "status": msg.status,
                            "created_at": msg.created_at.isoformat(),
                        }
                        await manager.send_personal_message(event_payload, recipient_id)
                        await notification_manager.send_notification(recipient_id, notif)
                        
                        await websocket.send_json({
                            "type": "message_sent_ack",
                            "message_id": msg.id,
                            "conversation_id": msg.conversation_id,
                            "status": msg.status,
                        })

                        if initial_status == "delivered":
                            await websocket.send_json({
                                "type": "message_delivered",
                                "message_id": msg.id,
                                "conversation_id": msg.conversation_id,
                            })


                elif msg_type in ["message_read", "mark_read"]:
                    chat_id = data.get("chat_id") or data.get("conversation_id")
                    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
                    if conv and (conv.user1_id == user_id or conv.user2_id == user_id):
                        other_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
                        unread_msgs = db.query(DirectMessage).filter(
                            DirectMessage.conversation_id == chat_id,
                            DirectMessage.sender_id == other_id,
                            DirectMessage.status != "read"
                        ).all()
                        msg_ids = [m.id for m in unread_msgs]
                        if unread_msgs:
                            for m in unread_msgs:
                                m.status = "read"
                            db.commit()
                            await manager.send_personal_message({
                                "type": "message_read",
                                "chat_id": chat_id,
                                "conversation_id": chat_id,
                                "reader_id": user_id,
                                "message_ids": msg_ids,
                            }, other_id)

                elif msg_type in ["group_message", "group_chat"]:
                    group_id = data.get("group_id")
                    text = data.get("text")
                    image_url = data.get("image_url") or data.get("attachment_url")

                    membership = db.query(GroupMember).filter(
                        GroupMember.group_id == group_id, GroupMember.user_id == user_id
                    ).first()

                    if membership:
                        g_msg = GroupMessage(
                            group_id=group_id,
                            sender_id=user_id,
                            text=text,
                            attachment_url=image_url,
                        )
                        db.add(g_msg)
                        db.commit()
                        db.refresh(g_msg)

                        members = db.query(GroupMember).filter(
                            GroupMember.group_id == group_id,
                            GroupMember.user_id != user_id
                        ).all()
                        recipient_ids = [m.user_id for m in members]

                        event_payload = {
                            "type": "group_message",
                            "id": g_msg.id,
                            "group_id": g_msg.group_id,
                            "sender_id": g_msg.sender_id,
                            "sender_name": user_full_name,
                            "text": g_msg.text,
                            "attachment_url": g_msg.attachment_url,
                            "created_at": g_msg.created_at.isoformat(),
                        }
                        await manager.broadcast_to_users(event_payload, recipient_ids)

                        for r_id in recipient_ids:
                            notif = Notification(
                                user_id=r_id,
                                type="message",
                                title=f"Group Message in {group_id}",
                                body=f"{user_full_name}: {(text or 'Sent attachment')[:40]}",
                            )
                            db.add(notif)
                            db.commit()
                            await notification_manager.send_notification(r_id, notif)

                        await websocket.send_json({
                            "type": "message_sent_ack",
                            "message_id": g_msg.id,
                            "group_id": g_msg.group_id,
                            "status": "delivered",
                        })

                elif msg_type in ["comment", "new_comment", "create_comment"]:
                    post_id = data.get("post_id")
                    content = data.get("content") or data.get("text")

                    post = db.query(Post).filter(Post.id == post_id).first()
                    if post and content:
                        comment = Comment(
                            post_id=post_id,
                            author_id=user_id,
                            content=content,
                        )
                        db.add(comment)
                        post.comment_count = post.comment_count + 1

                        notif = None
                        if post.author_id != user_id:
                            notif = Notification(
                                user_id=post.author_id,
                                type="comment",
                                title="New Comment on Your Post",
                                body=f"{user_full_name} commented: '{content[:50]}...'",
                            )
                            db.add(notif)

                        db.commit()
                        db.refresh(comment)

                        comment_payload = {
                            "type": "new_comment",
                            "post_id": post_id,
                            "comment": {
                                "id": comment.id,
                                "post_id": comment.post_id,
                                "author_id": comment.author_id,
                                "author_name": user_full_name,
                                "author_avatar": caregiver.avatar_url if caregiver else None,
                                "is_verified": caregiver.is_verified if caregiver else False,
                                "content": comment.content,
                                "created_at": comment.created_at.isoformat(),
                            }
                        }
                        await manager.broadcast_all(comment_payload)

                        if notif:
                            await notification_manager.send_notification(post.author_id, notif)

                        await websocket.send_json({
                            "type": "comment_sent_ack",
                            "comment_id": comment.id,
                            "post_id": post_id,
                        })

                elif msg_type in ["run_program", "execute_program", "program"]:
                    from app.realtime.program_runner import ProgramRunner
                    prog_id = int(data.get("program_id") or data.get("id") or 1)
                    prog_inputs = data.get("inputs") or data.get("params") or {}
                    res = ProgramRunner.execute(prog_id, prog_inputs)
                    await websocket.send_json({
                        "type": "program_result",
                        "sender": "System",
                        "message": res.get("result") or res.get("output"),
                        "data": res
                    })

                elif msg_type in ["typing_start", "typing_stop"]:
                    chat_id = data.get("chat_id")
                    recipient_id = data.get("recipient_id")
                    group_id = data.get("group_id")

                    event_msg = {
                        "type": msg_type,
                        "sender_id": user_id,
                        "chat_id": chat_id,
                        "group_id": group_id,
                    }

                    if recipient_id:
                        await manager.send_personal_message(event_msg, recipient_id)
                    elif group_id:
                        members = db.query(GroupMember).filter(
                            GroupMember.group_id == group_id,
                            GroupMember.user_id != user_id
                        ).all()
                        recipient_ids = [m.user_id for m in members]
                        await manager.broadcast_to_users(event_msg, recipient_ids)

            except Exception as frame_err:
                print(f"Error processing frame for user {user_id}: {frame_err}", flush=True)

    except WebSocketDisconnect:

        manager.disconnect(user_id, websocket)
        presence_manager.set_offline(user_id)
        caregiver = db.query(Caregiver).filter(Caregiver.user_id == user_id).first()
        if caregiver:
            caregiver.is_online = False
            caregiver.last_seen = datetime.utcnow()
            db.commit()
        await manager.broadcast_to_others({
            "type": "presence_change",
            "user_id": user_id,
            "is_online": False,
            "last_seen": caregiver.last_seen.isoformat() if caregiver and caregiver.last_seen else None,
        }, exclude_user_id=user_id)

    except Exception:
        manager.disconnect(user_id, websocket)
        presence_manager.set_offline(user_id)
    finally:
        db.close()


@router.websocket("/ws/programs")
@router.websocket("/ws/{user_id}")
async def direct_programs_websocket_endpoint(websocket: WebSocket, user_id: str = "guest"):
    from app.realtime.program_runner import ProgramRunner
    await websocket.accept()
    await websocket.send_json({
        "type": "connection_ack",
        "sender": "System",
        "message": f"Connected to Program Execution Server as {user_id}",
        "user_id": user_id
    })
    try:
        while True:
            data = await websocket.receive_json()
            prog_id = int(data.get("program_id") or data.get("id") or 1)
            prog_inputs = data.get("inputs") or data.get("params") or data
            res = ProgramRunner.execute(prog_id, prog_inputs if isinstance(prog_inputs, dict) else {})
            await websocket.send_json({
                "type": "program_result",
                "sender": "System",
                "message": res.get("result") or res.get("output"),
                "data": res
            })
    except WebSocketDisconnect:
        pass
    except Exception as err:
        print(f"[Direct WS Program Runner Error]: {err}", flush=True)


