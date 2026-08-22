from typing import Union, Dict, Any
from app.realtime.connection_manager import manager

class NotificationManager:
    async def send_notification(self, user_id: str, notification_data: Union[Dict[str, Any], Any]):
        if hasattr(notification_data, "id"):
            notif_type = getattr(notification_data, "type", "community")
            sound_name = "like" if notif_type == "like" else ("comment" if notif_type == "comment" else "notification")
            payload = {
                "id": notification_data.id,
                "type": notif_type,
                "title": getattr(notification_data, "title", "Notification"),
                "body": getattr(notification_data, "body", ""),
                "read": getattr(notification_data, "read", False),
                "sound": sound_name,
                "sound_url": f"/api/sounds/{sound_name}",
                "created_at": notification_data.created_at.isoformat() if hasattr(notification_data, "created_at") and notification_data.created_at else None,
            }
        else:
            payload = notification_data

        event = {
            "type": "notification",
            "data": payload
        }
        try:
            await manager.send_personal_message(event, user_id)
        except Exception:
            pass

notification_manager = NotificationManager()

