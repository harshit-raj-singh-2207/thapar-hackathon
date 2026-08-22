from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactResponse,
)
from app.utils.validators import validate_phone_number

router = APIRouter(prefix="/emergency-contacts", tags=["Safety - Emergency Contacts"])

@router.post("/", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_contact(
    data: EmergencyContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a trusted emergency contact (Family, Doctor, Therapist, Neighbor).
    """
    valid_phone, msg_phone = validate_phone_number(data.phone_number)
    if not valid_phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg_phone)

    contact = EmergencyContact(
        user_id=current_user.id,
        child_id=data.child_id,
        name=data.name,
        relationship_type=data.relationship_type,
        phone_number=data.phone_number,
        email=data.email,
        priority_order=data.priority_order,
        notify_via_sms=data.notify_via_sms,
        notify_via_call=data.notify_via_call,
        notify_via_push=data.notify_via_push,
        created_at=datetime.now(timezone.utc),
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.get("/", response_model=List[EmergencyContactResponse])
def list_emergency_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all emergency contacts ordered by priority.
    """
    contacts = (
        db.query(EmergencyContact)
        .filter(EmergencyContact.user_id == current_user.id)
        .order_by(EmergencyContact.priority_order.asc())
        .all()
    )
    return contacts

@router.put("/{contact_id}", response_model=EmergencyContactResponse)
def update_emergency_contact(
    contact_id: str,
    data: EmergencyContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update contact details or notification preferences.
    """
    contact = (
        db.query(EmergencyContact)
        .filter(EmergencyContact.id == contact_id, EmergencyContact.user_id == current_user.id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found.")

    if data.name is not None:
        contact.name = data.name
    if data.relationship_type is not None:
        contact.relationship_type = data.relationship_type
    if data.phone_number is not None:
        valid_phone, msg = validate_phone_number(data.phone_number)
        if not valid_phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        contact.phone_number = data.phone_number
    if data.email is not None:
        contact.email = data.email
    if data.priority_order is not None:
        contact.priority_order = data.priority_order
    if data.notify_via_sms is not None:
        contact.notify_via_sms = data.notify_via_sms
    if data.notify_via_call is not None:
        contact.notify_via_call = data.notify_via_call
    if data.notify_via_push is not None:
        contact.notify_via_push = data.notify_via_push

    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_200_OK)
def delete_emergency_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove an emergency contact.
    """
    contact = (
        db.query(EmergencyContact)
        .filter(EmergencyContact.id == contact_id, EmergencyContact.user_id == current_user.id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found.")
    db.delete(contact)
    db.commit()
    return {"message": "Emergency contact deleted successfully", "id": contact_id}
