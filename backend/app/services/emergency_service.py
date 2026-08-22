import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.emergency import EmergencyAlert
from app.models.child import Child
from app.models.safety_event import SafetyEvent
from app.schemas.emergency import EmergencyCreate, EmergencyResolveRequest
from app.services.notification_service import notification_service

logger = logging.getLogger("safety.emergency")

class EmergencyService:
    @staticmethod
    def trigger_emergency(
        db: Session,
        emergency_in: EmergencyCreate,
        caregiver_id: Optional[str] = None
    ) -> EmergencyAlert:
        child = db.query(Child).filter(Child.id == emergency_in.child_id).first()
        if not child:
            raise ValueError(f"Child with id '{emergency_in.child_id}' does not exist.")

        # Update child state
        child.current_status = "emergency"

        emergency = EmergencyAlert(
            child_id=emergency_in.child_id,
            caregiver_id=caregiver_id or child.caregiver_id,
            status="active",
            severity=emergency_in.severity or "critical",
            triggered_by=emergency_in.triggered_by or "sos_button",
            latitude=emergency_in.latitude,
            longitude=emergency_in.longitude,
            address=emergency_in.address,
            message=emergency_in.message or "EMERGENCY SOS Triggered!",
            created_at=datetime.now(timezone.utc),
        )
        db.add(emergency)

        # Log safety event
        event = SafetyEvent(
            child_id=child.id,
            event_type="sos_triggered",
            severity="critical",
            title=f"SOS EMERGENCY ACTIVATED FOR {child.name.upper()}",
            description=emergency_in.message,
            latitude=emergency_in.latitude,
            longitude=emergency_in.longitude,
            metadata_json=json.dumps({
                "emergency_id": emergency.id,
                "triggered_by": emergency_in.triggered_by,
            }),
        )
        db.add(event)
        db.commit()
        db.refresh(emergency)

        # Dispatch notifications
        coords = None
        if emergency_in.latitude is not None and emergency_in.longitude is not None:
            coords = {"latitude": emergency_in.latitude, "longitude": emergency_in.longitude}

        notification_service.send_emergency_alert(
            db=db,
            child=child,
            alert_title=f"🚨 SOS EMERGENCY ALERT: {child.name}",
            alert_message=emergency_in.message or "Immediate assistance required!",
            severity="critical",
            coordinates=coords,
        )

        return emergency

    @staticmethod
    def resolve_emergency(
        db: Session,
        emergency_id: str,
        resolve_in: EmergencyResolveRequest,
        resolved_by_user_id: str,
    ) -> Optional[EmergencyAlert]:
        emergency = db.query(EmergencyAlert).filter(EmergencyAlert.id == emergency_id).first()
        if not emergency:
            return None

        emergency.status = resolve_in.status
        emergency.resolved_at = datetime.now(timezone.utc)
        emergency.resolved_by = resolved_by_user_id
        emergency.resolution_notes = resolve_in.resolution_notes

        # Recheck child status if no other active emergencies
        other_active = (
            db.query(EmergencyAlert)
            .filter(
                EmergencyAlert.child_id == emergency.child_id,
                EmergencyAlert.status == "active",
                EmergencyAlert.id != emergency_id,
            )
            .count()
        )
        if other_active == 0:
            child = db.query(Child).filter(Child.id == emergency.child_id).first()
            if child:
                child.current_status = "safe"

        db.commit()
        db.refresh(emergency)
        return emergency

    @staticmethod
    def get_active_emergencies(db: Session, caregiver_id: Optional[str] = None) -> List[EmergencyAlert]:
        query = db.query(EmergencyAlert).filter(EmergencyAlert.status == "active")
        if caregiver_id:
            query = query.filter(EmergencyAlert.caregiver_id == caregiver_id)
        return query.order_by(desc(EmergencyAlert.created_at)).all()

emergency_service = EmergencyService()
