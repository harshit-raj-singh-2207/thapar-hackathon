from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.support.models import SupportTicket, ScheduledSupportCall

def get_hotlines_directory():
    return {
        "emergency_hotline": "1-800-CAREGIVER",
        "operating_hours": "Mon-Fri: 9:00 AM - 5:00 PM EST, Sat: 10:00 AM - 2:00 PM EST, Sun: Closed",
        "hotlines": [
            {"label": "Crisis Hotline", "number": "1-800-273-8255", "region": "Crisis 24/7", "availability": "Available 24/7"},
            {"label": "Local Services", "number": "1-800-555-0199", "region": "Local Support", "availability": "Available 24/7"},
            {"label": "US & CANADA SUPPORT", "number": "1-800-CAREGIVER", "region": "US/CA", "availability": "Mon-Fri: 9am - 5pm EST"},
            {"label": "UK SUPPORT", "number": "+44 800 123 4567", "region": "UK", "availability": "Mon-Fri: 9am - 5pm GMT"},
            {"label": "AUSTRALIA SUPPORT", "number": "+61 1800 987 654", "region": "AU", "availability": "Mon-Fri: 9am - 5pm AEST"},
        ]
    }

def create_support_ticket(db: Session, user_id: str, req):
    if not req.subject or not req.subject.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject is required for support ticket."
        )
    if not req.description or not req.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description is required for support ticket."
        )

    ticket = SupportTicket(
        user_id=user_id,
        subject=req.subject.strip(),
        category=req.category or "General Inquiry",
        description=req.description.strip(),
        status="in_progress"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def list_user_tickets(db: Session, user_id: str):
    tickets = db.query(SupportTicket).filter(
        SupportTicket.user_id == user_id
    ).order_by(SupportTicket.created_at.desc()).all()
    return tickets

def get_ticket_details(db: Session, user_id: str, ticket_id: str):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support ticket not found."
        )
    if ticket.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to support ticket."
        )
    return ticket

def schedule_support_call(db: Session, user_id: str, req):
    if not req.time_slot or not req.time_slot.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot is required to schedule call."
        )

    call = ScheduledSupportCall(
        user_id=user_id,
        specialist_name="Sarah J.",
        scheduled_time=req.time_slot.strip(),
        phone_number=req.phone_number,
        status="scheduled"
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call

def list_user_calls(db: Session, user_id: str):
    calls = db.query(ScheduledSupportCall).filter(
        ScheduledSupportCall.user_id == user_id
    ).order_by(ScheduledSupportCall.created_at.desc()).all()
    return calls
