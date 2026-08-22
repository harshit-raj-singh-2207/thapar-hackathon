import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.child import Child
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.domains.safety.alert_repository import AlertRepository
from app.schemas.alert import CaregiverAlertResponse, CaregiverAlertResolveRequest

logger = logging.getLogger("safety.alerts")

class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AlertRepository(db)

    def _verify_child_authorization(self, child_id: str, current_user: User) -> Child:
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child with ID '{child_id}' not found."
            )
        if child.caregiver_id != current_user.id and getattr(current_user, "role", None) != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You do not have permission to view alerts for this child."
            )
        return child

    def _verify_event_authorization(self, event: SafetyEvent, current_user: User) -> Child:
        return self._verify_child_authorization(event.child_id, current_user)

    def get_child_alerts(self, child_id: str, current_user: User) -> List[CaregiverAlertResponse]:
        self._verify_child_authorization(child_id, current_user)
        events = self.repo.get_alerts_by_child_id(child_id)
        return [CaregiverAlertResponse.model_validate(ev) for ev in events]

    def get_alert_by_id(self, alert_id: str, current_user: User) -> CaregiverAlertResponse:
        event = self.repo.get_alert_by_id(alert_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Caregiver alert with ID '{alert_id}' not found."
            )
        self._verify_event_authorization(event, current_user)
        return CaregiverAlertResponse.model_validate(event)

    def mark_alert_as_read(self, alert_id: str, current_user: User) -> CaregiverAlertResponse:
        event = self.repo.get_alert_by_id(alert_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Caregiver alert with ID '{alert_id}' not found."
            )
        self._verify_event_authorization(event, current_user)
        try:
            updated = self.repo.mark_as_read(event, current_user.id)
            return CaregiverAlertResponse.model_validate(updated)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error marking alert {alert_id} as read: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating alert."
            )

    def resolve_alert(
        self,
        alert_id: str,
        data: Optional[CaregiverAlertResolveRequest],
        current_user: User
    ) -> CaregiverAlertResponse:
        event = self.repo.get_alert_by_id(alert_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Caregiver alert with ID '{alert_id}' not found."
            )
        self._verify_event_authorization(event, current_user)
        notes = data.resolution_notes if data else "Resolved by caregiver."
        try:
            resolved = self.repo.resolve_alert(event, current_user.id, notes)
            return CaregiverAlertResponse.model_validate(resolved)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error resolving alert {alert_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while resolving alert."
            )
