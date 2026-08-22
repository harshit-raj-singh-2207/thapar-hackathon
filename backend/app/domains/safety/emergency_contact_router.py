from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactStatusUpdate,
    EmergencyContactResponse,
)
from app.domains.safety.emergency_contact_service import EmergencyContactService

router = APIRouter(prefix="/emergency-contacts", tags=["Safety - Emergency Contacts"])

@router.post(
    "",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Emergency Contact",
    description="Add a trusted emergency contact for a child or caregiver."
)
@router.post(
    "/",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_emergency_contact(
    data: EmergencyContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EmergencyContactService(db)
    return service.create_contact(data, current_user)

@router.get(
    "",
    response_model=List[EmergencyContactResponse],
    summary="List Emergency Contacts",
    description="Retrieve all emergency contacts for current user."
)
@router.get(
    "/",
    response_model=List[EmergencyContactResponse],
    include_in_schema=False
)
def list_emergency_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EmergencyContactService(db)
    return service.list_contacts_for_user(current_user.id)

@router.patch(
    "/{contact_id}/status",
    response_model=EmergencyContactResponse,
    summary="Toggle Contact Active Status",
    description="Enable or disable an emergency contact."
)
def update_contact_status(
    contact_id: str,
    data: EmergencyContactStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EmergencyContactService(db)
    is_act = data.active if data.active is not None else (data.is_active if data.is_active is not None else True)
    return service.set_contact_status(contact_id, is_act, current_user)

@router.get(
    "/{identifier}",
    response_model=Union[List[EmergencyContactResponse], EmergencyContactResponse],
    summary="Get Emergency Contacts or Contact Details",
    description="Get all emergency contacts for a child (if identifier is child_id) or single contact details (if identifier is contact_id)."
)
def get_contacts_or_single_contact(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EmergencyContactService(db)
    # Check if identifier matches a child ID
    child = db.query(Child).filter(Child.id == identifier).first()
    if child:
        return service.get_child_contacts(identifier, current_user)

    # Check if identifier matches a contact ID
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == identifier).first()
    if contact:
        return service.get_contact_by_id(identifier, current_user)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resource with ID '{identifier}' not found as child or emergency contact."
    )

@router.patch(
    "/{contact_id}",
    response_model=EmergencyContactResponse,
    summary="Update Emergency Contact",
    description="Update emergency contact details, priority, or notification preferences."
)
def update_emergency_contact(
    contact_id: str,
    data: EmergencyContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EmergencyContactService(db)
    return service.update_contact(contact_id, data, current_user)

@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Emergency Contact",
    description="Remove an emergency contact."
)
def delete_emergency_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EmergencyContactService(db)
    return service.delete_contact(contact_id, current_user)
