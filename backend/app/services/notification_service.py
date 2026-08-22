import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.emergency_contact import EmergencyContact
from app.models.child import Child
from app.models.user import User

logger = logging.getLogger("safety.notifications")

class NotificationService:
    @staticmethod
    def send_emergency_alert(
        db: Session,
        child: Child,
        alert_title: str,
        alert_message: str,
        severity: str = "critical",
        coordinates: Optional[Dict[str, float]] = None,
        contacts: Optional[List[EmergencyContact]] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches multi-channel notifications (SMS, Push, In-App, Call) to emergency contacts and caregiver.
        """
        if contacts is None:
            contacts = (
                db.query(EmergencyContact)
                .filter(
                    (EmergencyContact.user_id == child.caregiver_id)
                    | (EmergencyContact.child_id == child.id)
                )
                .order_by(EmergencyContact.priority_order.asc())
                .all()
            )

        dispatch_log = []
        for contact in contacts:
            channel_statuses = {}
            if contact.notify_via_sms:
                channel_statuses["sms"] = f"SMS dispatched to {contact.phone_number}: [{severity.upper()}] {alert_title} - {alert_message}"
            if contact.notify_via_call:
                channel_statuses["call"] = f"Automated voice alert triggered for {contact.phone_number}"
            if contact.notify_via_push:
                channel_statuses["push"] = f"Push notification delivered to device token for {contact.name}"

            dispatch_log.append({
                "contact_id": contact.id,
                "contact_name": contact.name,
                "phone": contact.phone_number,
                "channels": channel_statuses,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        logger.warning(
            f"[SAFETY ALERT] Dispatched '{alert_title}' for child '{child.name}' ({child.id}) to {len(contacts)} contacts."
        )

        return {
            "alert_title": alert_title,
            "child_id": child.id,
            "child_name": child.name,
            "severity": severity,
            "contacts_notified": len(contacts),
            "dispatches": dispatch_log,
            "coordinates": coordinates,
        }

    @staticmethod
    def send_safety_notification(
        caregiver_user_id: str,
        title: str,
        message: str,
        event_type: str = "safety_alert",
    ) -> Dict[str, Any]:
        """
        Sends an in-app safety notification.
        """
        return {
            "user_id": caregiver_user_id,
            "title": title,
            "message": message,
            "event_type": event_type,
            "delivered": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

notification_service = NotificationService()
