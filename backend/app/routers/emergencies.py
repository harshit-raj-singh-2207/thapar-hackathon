from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.emergency import EmergencyAlert
from app.schemas.emergency import (
    EmergencyCreate,
    EmergencyResolveRequest,
    EmergencyResponse,
)
from app.services.emergency_service import emergency_service

router = APIRouter(prefix="/emergencies", tags=["Safety - Emergency & SOS"])

@router.post("/sos", response_model=EmergencyResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos_alert(
    data: EmergencyCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Trigger critical SOS alert. Immediately broadcasts to all emergency contacts and updates child status.
    """
    caregiver_id = current_user.id if current_user else None
    try:
        emergency = emergency_service.trigger_emergency(db, data, caregiver_id=caregiver_id)
        return emergency
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/active", response_model=List[EmergencyResponse])
def get_active_emergencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all currently active emergencies for the user/caregiver.
    """
    emergencies = emergency_service.get_active_emergencies(db, caregiver_id=current_user.id)
    return emergencies

@router.get("/{emergency_id}", response_model=EmergencyResponse)
def get_emergency_detail(
    emergency_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get emergency alert details, coordinates, and resolution audit info.
    """
    emg = db.query(EmergencyAlert).filter(EmergencyAlert.id == emergency_id).first()
    if not emg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency record not found.")
    return emg

@router.post("/{emergency_id}/resolve", response_model=EmergencyResponse)
def resolve_emergency(
    emergency_id: str,
    data: EmergencyResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resolve active emergency alert or mark as false alarm.
    """
    resolved = emergency_service.resolve_emergency(
        db,
        emergency_id=emergency_id,
        resolve_in=data,
        resolved_by_user_id=current_user.id,
    )
    if not resolved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency not found.")
    return resolved
