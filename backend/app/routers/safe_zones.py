import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.safe_zone import SafeZone
from app.schemas.safe_zone import (
    SafeZoneCreate,
    SafeZoneUpdate,
    SafeZoneResponse,
    SafeZoneStatusCheck,
)
from app.services.geofence_service import geofence_service
from app.utils.validators import validate_coordinates, validate_safe_zone_radius

router = APIRouter(prefix="/safe-zones", tags=["Safety - Safe Zones & Geofencing"])

@router.post("/", response_model=SafeZoneResponse, status_code=status.HTTP_201_CREATED)
def create_safe_zone(
    data: SafeZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new geofenced safe zone (Home, School, Therapy Center, Park).
    """
    valid_coord, msg_coord = validate_coordinates(data.center_latitude, data.center_longitude)
    if not valid_coord:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg_coord)

    valid_rad, msg_rad = validate_safe_zone_radius(data.radius_meters)
    if not valid_rad:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg_rad)

    child = db.query(Child).filter(Child.id == data.child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found.")

    polygon_str = json.dumps(data.polygon_coordinates) if data.polygon_coordinates else None

    safe_zone = SafeZone(
        child_id=data.child_id,
        name=data.name,
        zone_type=data.zone_type,
        center_latitude=data.center_latitude,
        center_longitude=data.center_longitude,
        radius_meters=data.radius_meters,
        polygon_coordinates=polygon_str,
        address=data.address,
        is_active=data.is_active,
        alert_on_exit=data.alert_on_exit,
        alert_on_enter=data.alert_on_enter,
        created_at=datetime.now(timezone.utc),
    )
    db.add(safe_zone)
    db.commit()
    db.refresh(safe_zone)
    return safe_zone

@router.get("/child/{child_id}", response_model=List[SafeZoneResponse])
def get_child_safe_zones(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all configured safe zones for a specific child.
    """
    zones = db.query(SafeZone).filter(SafeZone.child_id == child_id).all()
    return zones

@router.get("/{safe_zone_id}", response_model=SafeZoneResponse)
def get_safe_zone_by_id(
    safe_zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get safe zone details and perimeter coordinates.
    """
    zone = db.query(SafeZone).filter(SafeZone.id == safe_zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Safe zone not found.")
    return zone

@router.put("/{safe_zone_id}", response_model=SafeZoneResponse)
def update_safe_zone(
    safe_zone_id: str,
    data: SafeZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update safe zone boundaries, radius, or alert trigger rules.
    """
    zone = db.query(SafeZone).filter(SafeZone.id == safe_zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Safe zone not found.")

    if data.name is not None:
        zone.name = data.name
    if data.zone_type is not None:
        zone.zone_type = data.zone_type
    if data.center_latitude is not None:
        zone.center_latitude = data.center_latitude
    if data.center_longitude is not None:
        zone.center_longitude = data.center_longitude
    if data.radius_meters is not None:
        zone.radius_meters = data.radius_meters
    if data.polygon_coordinates is not None:
        zone.polygon_coordinates = json.dumps(data.polygon_coordinates)
    if data.address is not None:
        zone.address = data.address
    if data.is_active is not None:
        zone.is_active = data.is_active
    if data.alert_on_exit is not None:
        zone.alert_on_exit = data.alert_on_exit
    if data.alert_on_enter is not None:
        zone.alert_on_enter = data.alert_on_enter

    db.commit()
    db.refresh(zone)
    return zone

@router.delete("/{safe_zone_id}", status_code=status.HTTP_200_OK)
def delete_safe_zone(
    safe_zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a safe zone.
    """
    zone = db.query(SafeZone).filter(SafeZone.id == safe_zone_id).first()
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Safe zone not found.")
    db.delete(zone)
    db.commit()
    return {"message": "Safe zone deleted successfully", "id": safe_zone_id}

@router.post("/evaluate", response_model=SafeZoneStatusCheck)
def test_location_containment(
    child_id: str,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a test (latitude, longitude) coordinate is inside the child's configured safe zones.
    """
    res = geofence_service.evaluate_location_against_safe_zones(
        db, child_id=child_id, lat=latitude, lon=longitude, create_events=False
    )
    return SafeZoneStatusCheck(
        child_id=child_id,
        latitude=latitude,
        longitude=longitude,
        is_inside_safe_zone=res.get("is_inside_safe_zone", True),
        active_zone_id=res.get("active_zone_id"),
        active_zone_name=res.get("active_zone_name"),
        distance_to_boundary_meters=res.get("nearest_zone_distance_meters"),
    )
