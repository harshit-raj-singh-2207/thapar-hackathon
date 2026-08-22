from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent

class EmergencyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, emergency_id: str) -> Optional[EmergencyAlert]:
        return self.db.query(EmergencyAlert).filter(EmergencyAlert.id == emergency_id).first()

    def get_active_by_child_id(self, child_id: str) -> Optional[EmergencyAlert]:
        return (
            self.db.query(EmergencyAlert)
            .filter(EmergencyAlert.child_id == child_id, EmergencyAlert.status == "active")
            .order_by(desc(EmergencyAlert.created_at))
            .first()
        )

    def get_latest_by_child_id(self, child_id: str) -> Optional[EmergencyAlert]:
        return (
            self.db.query(EmergencyAlert)
            .filter(EmergencyAlert.child_id == child_id)
            .order_by(desc(EmergencyAlert.created_at))
            .first()
        )

    def create_emergency(
        self,
        child_id: str,
        caregiver_id: Optional[str],
        triggered_by: str,
        severity: str,
        latitude: Optional[float],
        longitude: Optional[float],
        message: str,
        address: Optional[str] = None,
    ) -> EmergencyAlert:
        now_utc = datetime.now(timezone.utc)
        emergency = EmergencyAlert(
            child_id=child_id,
            caregiver_id=caregiver_id,
            status="active",
            severity=severity,
            triggered_by=triggered_by,
            latitude=latitude,
            longitude=longitude,
            address=address,
            message=message,
            created_at=now_utc,
        )
        self.db.add(emergency)
        self.db.commit()
        self.db.refresh(emergency)
        return emergency

    def resolve(
        self,
        emergency: EmergencyAlert,
        resolved_by: str,
        resolution_notes: Optional[str] = None
    ) -> EmergencyAlert:
        now_utc = datetime.now(timezone.utc)
        emergency.status = "resolved"
        emergency.resolved_at = now_utc
        emergency.resolved_by = resolved_by
        emergency.resolution_notes = resolution_notes
        self.db.commit()
        self.db.refresh(emergency)
        return emergency
