import json
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.safety_event import SafetyEvent
from app.models.emergency import EmergencyAlert

class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_alerts_by_child_id(self, child_id: str, limit: int = 100) -> List[SafetyEvent]:
        return (
            self.db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == child_id)
            .order_by(desc(SafetyEvent.created_at))
            .limit(limit)
            .all()
        )

    def get_alert_by_id(self, alert_id: str) -> Optional[SafetyEvent]:
        # 1. Look up by SafetyEvent id
        event = self.db.query(SafetyEvent).filter(SafetyEvent.id == alert_id).first()
        if event:
            return event

        # 2. Look up by EmergencyAlert id and find linked SafetyEvent
        emg = self.db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
        if emg:
            # Look for linked event or construct a SafetyEvent
            event = (
                self.db.query(SafetyEvent)
                .filter(SafetyEvent.child_id == emg.child_id)
                .order_by(desc(SafetyEvent.created_at))
                .first()
            )
            return event
        return None

    def mark_as_read(self, event: SafetyEvent, user_id: str) -> SafetyEvent:
        now_utc = datetime.now(timezone.utc)
        event.is_acknowledged = True
        event.acknowledged_at = now_utc
        event.acknowledged_by = user_id
        self.db.commit()
        self.db.refresh(event)
        return event

    def resolve_alert(self, event: SafetyEvent, user_id: str, notes: Optional[str] = None) -> SafetyEvent:
        now_utc = datetime.now(timezone.utc)
        event.is_acknowledged = True
        event.acknowledged_at = now_utc
        event.acknowledged_by = user_id

        # If linked to an emergency, resolve the emergency as well
        if event.metadata_json:
            try:
                meta = json.loads(event.metadata_json)
                emg_id = meta.get("emergency_id")
                if emg_id:
                    emg = self.db.query(EmergencyAlert).filter(EmergencyAlert.id == emg_id).first()
                    if emg and emg.status != "resolved":
                        emg.status = "resolved"
                        emg.resolved_at = now_utc
                        emg.resolved_by = user_id
                        emg.resolution_notes = notes or "Resolved via alert management."
            except Exception:
                pass

        self.db.commit()
        self.db.refresh(event)
        return event
