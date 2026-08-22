from app.routers.safety import router as safety_router
from app.routers.location import router as location_router
from app.routers.devices import router as devices_router
from app.routers.safe_zones import router as safe_zones_router
from app.routers.emergencies import router as emergencies_router
from app.routers.emergency_contacts import router as emergency_contacts_router
from app.routers.safety_events import router as safety_events_router

__all__ = [
    "safety_router",
    "location_router",
    "devices_router",
    "safe_zones_router",
    "emergencies_router",
    "emergency_contacts_router",
    "safety_events_router",
]
