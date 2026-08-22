from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.emergency_contact import EmergencyContact

class EmergencyContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, contact_id: str) -> Optional[EmergencyContact]:
        return self.db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()

    def get_contacts_by_child_id(self, child_id: str) -> List[EmergencyContact]:
        return (
            self.db.query(EmergencyContact)
            .filter(EmergencyContact.child_id == child_id)
            .order_by(asc(EmergencyContact.priority_order))
            .all()
        )

    def get_contacts_by_user_or_child(self, user_id: str, child_id: Optional[str] = None) -> List[EmergencyContact]:
        query = self.db.query(EmergencyContact)
        if child_id:
            query = query.filter((EmergencyContact.child_id == child_id) | (EmergencyContact.user_id == user_id))
        else:
            query = query.filter(EmergencyContact.user_id == user_id)
        return query.order_by(asc(EmergencyContact.priority_order)).all()

    def create_contact(
        self,
        user_id: str,
        child_id: Optional[str],
        name: str,
        relationship_type: str,
        phone_number: str,
        priority_order: int = 1,
        is_active: bool = True,
        email: Optional[str] = None,
        notify_sms: bool = True,
        notify_call: bool = True,
        notify_push: bool = True,
    ) -> EmergencyContact:
        now_utc = datetime.now(timezone.utc)
        contact = EmergencyContact(
            user_id=user_id,
            child_id=child_id,
            name=name,
            relationship_type=relationship_type,
            phone_number=phone_number,
            email=email,
            priority_order=priority_order,
            is_active=is_active,
            notify_via_sms=notify_sms,
            notify_via_call=notify_call,
            notify_via_push=notify_push,
            created_at=now_utc,
            updated_at=now_utc,
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def update_contact(self, contact: EmergencyContact, updates: Dict[str, Any]) -> EmergencyContact:
        for k, v in updates.items():
            if hasattr(contact, k) and v is not None:
                setattr(contact, k, v)
        contact.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete_contact(self, contact: EmergencyContact) -> None:
        self.db.delete(contact)
        self.db.commit()
