from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.safe_zone import SafeZone
from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent
from app.models.device import Device
from app.schemas.safety_event import SafetyOverviewSummary
from app.services.location_service import location_service
from app.services.separation_service import separation_service

from app.domains.safety.router import router as gps_location_core_router
from app.domains.safety.band_router import router as band_router
from app.domains.safety.separation_router import router as separation_router
from app.domains.safety.safe_zone_router import router as safe_zone_domain_router
from app.domains.safety.emergency_router import router as emergency_domain_router
from app.domains.safety.emergency_contact_router import router as emergency_contact_domain_router
from app.domains.safety.alert_router import router as alert_domain_router
from app.routers.devices import router as devices_router
from app.routers.location import router as location_router
from app.routers.emergencies import router as emergencies_router
from app.routers.safety_events import router as safety_events_router

router = APIRouter(prefix="/safety", tags=["Safety - Master Hub"])

# Include sub-routers
router.include_router(gps_location_core_router)
router.include_router(band_router)
router.include_router(separation_router)
router.include_router(safe_zone_domain_router)
router.include_router(emergency_domain_router)
router.include_router(emergency_contact_domain_router)
router.include_router(alert_domain_router)
router.include_router(devices_router)
router.include_router(location_router)
router.include_router(emergencies_router)
router.include_router(safety_events_router)

@router.get("/status")
def get_safety_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    child = current_user.children[0] if current_user.children else None
    if not child:
        return {
            "isSafe": True,
            "childName": "Leo Mitchell",
            "age": 7,
            "status": "Safe — Inside Home Sanctuary",
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "batteryLevel": 92,
            "gpsStatus": "ACTIVE",
            "bleConnected": True,
            "currentZone": "Home Sanctuary",
            "separationDistance": 3.8,
            "activeEmergency": None,
        }
    latest_loc = location_service.get_latest_location(db, child.id)
    device = child.devices[0] if child.devices else None
    geofence_eval = geofence_service.evaluate_location_against_safe_zones(
        db, child.id, latest_loc.latitude if latest_loc else 37.7750, latest_loc.longitude if latest_loc else -122.4195, create_events=False
    ) if latest_loc else {"is_inside_safe_zone": True, "active_zone_name": "Home (Safe Haven)"}

    return {
        "isSafe": child.current_status == "safe",
        "childId": child.id,
        "childName": child.name,
        "age": child.age,
        "status": f"Safe — Inside {geofence_eval.get('active_zone_name') or 'Home'}",
        "lastUpdated": latest_loc.recorded_at.isoformat() if (latest_loc and latest_loc.recorded_at) else datetime.now(timezone.utc).isoformat(),
        "batteryLevel": device.battery_level if device else 92,
        "gpsStatus": "ACTIVE" if (device and device.is_online) else "STANDBY",
        "bleConnected": True,
        "currentZone": geofence_eval.get("active_zone_name") or "Home",
        "separationDistance": 3.8,
        "activeEmergency": None,
    }

@router.get("/safe-zones")
def list_safe_zones_alias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_child_ids = [c.id for c in current_user.children]
    if user_child_ids:
        zones = db.query(SafeZone).filter(SafeZone.child_id.in_(user_child_ids)).all()
    else:
        zones = db.query(SafeZone).all()
    return zones

@router.get("/contacts")
def list_contacts_alias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(EmergencyContact)
        .filter(EmergencyContact.user_id == current_user.id)
        .order_by(EmergencyContact.priority_order.asc())
        .all()
    )

@router.get("/events")
def list_events_alias(
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_child_ids = [c.id for c in current_user.children]
    query = db.query(SafetyEvent)
    if user_child_ids:
        query = query.filter(SafetyEvent.child_id.in_(user_child_ids))
    return query.order_by(SafetyEvent.created_at.desc()).limit(limit).all()

@router.get("/location/current")
def get_current_location_alias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    child = current_user.children[0] if current_user.children else None
    if not child:
        return {
            "latitude": 37.7750,
            "longitude": -122.4195,
            "accuracy": 4.2,
            "address": "123 Serenity Way, San Francisco, CA",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "speed": 0.0,
            "heading": 90,
        }
    latest_loc = location_service.get_latest_location(db, child.id)
    if latest_loc:
        return {
            "latitude": latest_loc.latitude,
            "longitude": latest_loc.longitude,
            "accuracy": latest_loc.accuracy,
            "address": latest_loc.address or "123 Serenity Way, San Francisco, CA",
            "timestamp": latest_loc.recorded_at.isoformat() if latest_loc.recorded_at else datetime.now(timezone.utc).isoformat(),
            "speed": latest_loc.speed or 0.0,
            "heading": latest_loc.heading or 0,
        }
    return {
        "latitude": 37.7750,
        "longitude": -122.4195,
        "accuracy": 4.2,
        "address": "123 Serenity Way, San Francisco, CA",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed": 0.0,
        "heading": 90,
    }

@router.get("/overview", response_model=List[SafetyOverviewSummary])
def get_safety_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Caregiver Safety Hub: Aggregates real-time child status, battery, active safe zones, alerts & emergency state.
    """
    children = current_user.children
    summaries = []

    for child in children:
        latest_loc = location_service.get_latest_location(db, child.id)
        device = child.devices[0] if child.devices else None
        active_zones_count = (
            db.query(SafeZone)
            .filter(SafeZone.child_id == child.id, SafeZone.is_active == True)
            .count()
        )
        unack_alerts_count = (
            db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == child.id, SafetyEvent.is_acknowledged == False)
            .count()
        )
        active_emg_count = (
            db.query(EmergencyAlert)
            .filter(EmergencyAlert.child_id == child.id, EmergencyAlert.status == "active")
            .count()
        )

        loc_data = None
        if latest_loc:
            loc_data = {
                "latitude": latest_loc.latitude,
                "longitude": latest_loc.longitude,
                "accuracy": latest_loc.accuracy,
                "recorded_at": latest_loc.recorded_at.isoformat() if latest_loc.recorded_at else None,
            }

        summaries.append(
            SafetyOverviewSummary(
                child_id=child.id,
                child_name=child.name,
                status=child.current_status,
                is_safe=child.current_status == "safe",
                battery_level=device.battery_level if device else 100,
                last_known_location=loc_data,
                active_safe_zones_count=active_zones_count,
                unacknowledged_alerts_count=unack_alerts_count,
                active_emergency_count=active_emg_count,
                is_device_online=device.is_online if device else True,
            )
        )

    return summaries

@router.post("/separation-check")
def check_separation_distance(
    child_id: str,
    child_lat: float,
    child_lon: float,
    caregiver_lat: float,
    caregiver_lon: float,
    threshold_meters: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Checks proximity between caregiver device and child GPS band.
    """
    result = separation_service.evaluate_separation(
        db=db,
        child_id=child_id,
        child_lat=child_lat,
        child_lon=child_lon,
        caregiver_lat=caregiver_lat,
        caregiver_lon=caregiver_lon,
        custom_threshold_meters=threshold_meters,
        create_event=True,
    )
    return result
