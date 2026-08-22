from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_caregiver
from app.domains.caregivers.models import Caregiver
from app.domains.support.schemas import (
    SupportTicketCreateSchema,
    SupportTicketResponseSchema,
    ScheduledCallCreateSchema,
    ScheduledCallResponseSchema,
    HotlineDirectoryResponseSchema,
)
from app.domains.support.service import (
    get_hotlines_directory,
    create_support_ticket,
    list_user_tickets,
    get_ticket_details,
    schedule_support_call,
    list_user_calls,
)

router = APIRouter(prefix="/support", tags=["Support Center"])

@router.get("/hotlines", response_model=HotlineDirectoryResponseSchema)
def get_hotlines():
    """
    Get emergency hotlines directory and operating hours.
    """
    return get_hotlines_directory()

@router.get("/tickets")
def get_my_tickets(
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    List all support tickets created by the authenticated caregiver.
    """
    tickets = list_user_tickets(db, caregiver.user_id)
    return [
        {
            "id": t.id,
            "ticket_number": t.ticket_number,
            "user_id": t.user_id,
            "subject": t.subject,
            "category": t.category,
            "description": t.description,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
        }
        for t in tickets
    ]

@router.post("/tickets", status_code=status.HTTP_201_CREATED)
def post_support_ticket(
    req: SupportTicketCreateSchema,
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket.
    """
    t = create_support_ticket(db, caregiver.user_id, req)
    return {
        "id": t.id,
        "ticket_number": t.ticket_number,
        "user_id": t.user_id,
        "subject": t.subject,
        "category": t.category,
        "description": t.description,
        "status": t.status,
        "created_at": t.created_at.isoformat(),
    }

@router.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: str,
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Get details for a single support ticket owned by the authenticated caregiver.
    """
    t = get_ticket_details(db, caregiver.user_id, ticket_id)
    return {
        "id": t.id,
        "ticket_number": t.ticket_number,
        "user_id": t.user_id,
        "subject": t.subject,
        "category": t.category,
        "description": t.description,
        "status": t.status,
        "created_at": t.created_at.isoformat(),
    }

@router.post("/calls/schedule", status_code=status.HTTP_201_CREATED)
def post_schedule_call(
    req: ScheduledCallCreateSchema,
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Book a scheduled 1-on-1 support call.
    """
    c = schedule_support_call(db, caregiver.user_id, req)
    return {
        "id": c.id,
        "user_id": c.user_id,
        "specialist_name": c.specialist_name,
        "scheduled_time": c.scheduled_time,
        "status": c.status,
        "created_at": c.created_at.isoformat(),
    }

@router.get("/calls")
def get_my_calls(
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    List all scheduled calls for the authenticated caregiver.
    """
    calls = list_user_calls(db, caregiver.user_id)
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "specialist_name": c.specialist_name,
            "scheduled_time": c.scheduled_time,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
        }
        for c in calls
    ]
