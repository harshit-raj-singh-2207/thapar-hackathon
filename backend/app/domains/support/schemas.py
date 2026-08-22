from typing import Optional, List
from pydantic import BaseModel

class SupportTicketCreateSchema(BaseModel):
    subject: str
    category: Optional[str] = "General Inquiry"
    description: str

class SupportTicketResponseSchema(BaseModel):
    id: str
    ticket_number: str
    user_id: str
    subject: str
    category: str
    description: str
    status: str
    created_at: str

    class Config:
        from_attributes = True

class ScheduledCallCreateSchema(BaseModel):
    time_slot: str
    phone_number: Optional[str] = None

class ScheduledCallResponseSchema(BaseModel):
    id: str
    user_id: str
    specialist_name: str
    scheduled_time: str
    status: str
    created_at: str

    class Config:
        from_attributes = True

class HotlineItemSchema(BaseModel):
    label: str
    number: str
    region: str
    availability: Optional[str] = "Available 24/7"

class HotlineDirectoryResponseSchema(BaseModel):
    emergency_hotline: str
    operating_hours: str
    hotlines: List[HotlineItemSchema]
