from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.safety_event import SafetyEvent
from app.models.emergency import EmergencyAlert
from app.schemas.alert import CaregiverAlertResponse, CaregiverAlertResolveRequest
from app.domains.safety.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Safety - Caregiver Alerts"])

@router.patch(
    "/{alert_id}/read",
    response_model=CaregiverAlertResponse,
    summary="Mark Alert as Read",
    description="Mark a safety or emergency alert as read/acknowledged."
)
def mark_alert_as_read(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AlertService(db)
    return service.mark_alert_as_read(alert_id, current_user)

@router.patch(
    "/{alert_id}/resolve",
    response_model=CaregiverAlertResponse,
    summary="Resolve Alert",
    description="Resolve an active safety or emergency alert."
)
def resolve_alert(
    alert_id: str,
    data: Optional[CaregiverAlertResolveRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AlertService(db)
    return service.resolve_alert(alert_id, data, current_user)

@router.get(
    "/{identifier}",
    response_model=Union[List[CaregiverAlertResponse], CaregiverAlertResponse],
    summary="Get Child Alerts or Single Alert Details",
    description="Get all caregiver alerts for a child (if identifier is child_id) or single alert details (if identifier is alert_id)."
)
def get_alerts_or_single_alert(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = AlertService(db)

    # 1. Check if identifier is a child ID
    child = db.query(Child).filter(Child.id == identifier).first()
    if child:
        return service.get_child_alerts(identifier, current_user)

    # 2. Check if identifier is an alert / safety event ID
    event = db.query(SafetyEvent).filter(SafetyEvent.id == identifier).first()
    if event:
        return service.get_alert_by_id(identifier, current_user)

    emg = db.query(EmergencyAlert).filter(EmergencyAlert.id == identifier).first()
    if emg:
        return service.get_alert_by_id(identifier, current_user)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resource with ID '{identifier}' not found as child or alert."
    )
