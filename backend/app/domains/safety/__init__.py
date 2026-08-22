# Bridge exports from new app.services and app.models for backwards compatibility
from app.services.location_service import location_service
from app.services.device_service import device_service
from app.services.geofence_service import geofence_service
from app.services.separation_service import separation_service
from app.services.emergency_service import emergency_service
from app.services.notification_service import notification_service
from app.models.location import Location
from app.models.device import Device
from app.models.safe_zone import SafeZone
from app.models.emergency import EmergencyAlert
from app.models.emergency_contact import EmergencyContact
from app.models.safety_event import SafetyEvent
from app.models.child import Child

from app.domains.safety.gps_band_service import GPSBandService
from app.domains.safety.location_service import LocationService as LocationCoreService

__all__ = [
    "location_service",
    "device_service",
    "geofence_service",
    "separation_service",
    "emergency_service",
    "notification_service",
    "GPSBandService",
    "LocationCoreService",
    "Location",
    "Device",
    "SafeZone",
    "EmergencyAlert",
    "EmergencyContact",
    "SafetyEvent",
    "Child",
]
