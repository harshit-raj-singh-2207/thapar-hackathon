"""
Safety Domain Models
Re-exports core and safety models for domain encapsulation.
"""
from app.models.location import Location
from app.models.child import Child
from app.models.user import User, Caregiver
from app.models.device import Device
from app.models.safe_zone import SafeZone
from app.models.emergency import EmergencyAlert
from app.models.emergency_contact import EmergencyContact
from app.models.safety_event import SafetyEvent

__all__ = [
    "Location",
    "Child",
    "User",
    "Caregiver",
    "Device",
    "SafeZone",
    "EmergencyAlert",
    "EmergencyContact",
    "SafetyEvent",
]
