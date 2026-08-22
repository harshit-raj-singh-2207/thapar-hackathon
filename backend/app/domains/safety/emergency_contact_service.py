import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.child import Child
from app.models.emergency_contact import EmergencyContact
from app.models.user import User
from app.domains.safety.emergency_contact_repository import EmergencyContactRepository
from app.schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactStatusUpdate,
    EmergencyContactResponse,
)

logger = logging.getLogger("safety.emergency_contacts")

class EmergencyContactService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmergencyContactRepository(db)

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
                detail="Unauthorized: You do not have permission to manage contacts for this child."
            )
        return child

    def _verify_contact_authorization(self, contact: EmergencyContact, current_user: User):
        if contact.child_id:
            child = self.db.query(Child).filter(Child.id == contact.child_id).first()
            if child and child.caregiver_id != current_user.id and contact.user_id != current_user.id and getattr(current_user, "role", None) != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized: You do not have permission to access or modify this emergency contact."
                )
        elif contact.user_id != current_user.id and getattr(current_user, "role", None) != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You do not have permission to access or modify this emergency contact."
            )

    def create_contact(self, data: EmergencyContactCreate, current_user: User) -> EmergencyContact:
        if data.child_id:
            self._verify_child_authorization(data.child_id, current_user)

        try:
            contact = self.repo.create_contact(
                user_id=current_user.id,
                child_id=data.child_id,
                name=data.name.strip(),
                relationship_type=data.relationship or data.relationship_type or "Family",
                phone_number=data.phone or data.phone_number,
                priority_order=data.priority if data.priority is not None else (data.priority_order or 1),
                is_active=data.active if data.active is not None else (data.is_active if data.is_active is not None else True),
                email=data.email,
                notify_sms=data.notify_via_sms,
                notify_call=data.notify_via_call,
                notify_push=data.notify_via_push,
            )
            return contact
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating emergency contact: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating emergency contact."
            )

    def get_child_contacts(self, child_id: str, current_user: User) -> List[EmergencyContact]:
        self._verify_child_authorization(child_id, current_user)
        return self.repo.get_contacts_by_child_id(child_id)

    def get_contact_by_id(self, contact_id: str, current_user: User) -> EmergencyContact:
        contact = self.repo.get_by_id(contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emergency contact with ID '{contact_id}' not found."
            )
        self._verify_contact_authorization(contact, current_user)
        return contact

    def update_contact(
        self,
        contact_id: str,
        data: EmergencyContactUpdate,
        current_user: User
    ) -> EmergencyContact:
        contact = self.get_contact_by_id(contact_id, current_user)
        updates: Dict[str, Any] = {}

        if data.name is not None:
            updates["name"] = data.name.strip()
        if data.relationship or data.relationship_type:
            updates["relationship_type"] = data.relationship or data.relationship_type
        if data.phone or data.phone_number:
            updates["phone_number"] = data.phone or data.phone_number
        if data.priority is not None or data.priority_order is not None:
            updates["priority_order"] = data.priority if data.priority is not None else data.priority_order
        if data.active is not None or data.is_active is not None:
            updates["is_active"] = data.active if data.active is not None else data.is_active
        if data.email is not None:
            updates["email"] = data.email
        if data.notify_via_sms is not None:
            updates["notify_via_sms"] = data.notify_via_sms
        if data.notify_via_call is not None:
            updates["notify_via_call"] = data.notify_via_call
        if data.notify_via_push is not None:
            updates["notify_via_push"] = data.notify_via_push

        try:
            return self.repo.update_contact(contact, updates)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating contact {contact_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating emergency contact."
            )

    def set_contact_status(
        self,
        contact_id: str,
        is_active: bool,
        current_user: User
    ) -> EmergencyContact:
        contact = self.get_contact_by_id(contact_id, current_user)
        try:
            return self.repo.update_contact(contact, {"is_active": is_active})
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error setting contact status {contact_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating contact status."
            )

    def list_contacts_for_user(self, user_id: str) -> List[EmergencyContact]:
        return self.repo.get_contacts_by_user_or_child(user_id=user_id)

    def delete_contact(self, contact_id: str, current_user: User) -> dict:
        contact = self.get_contact_by_id(contact_id, current_user)
        try:
            self.repo.delete_contact(contact)
            return {"message": "Emergency contact deleted successfully", "id": contact_id}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting contact {contact_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting emergency contact."
            )
