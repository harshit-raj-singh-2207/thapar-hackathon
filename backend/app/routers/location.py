from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.location import Location
from app.schemas.location import (
    LocationCreate,
    LocationResponse,
    CurrentLocationResponse,
)
from app.services.location_service import location_service
from app.services.geofence_service import geofence_service

router = APIRouter(prefix="/locations", tags=["Safety - Location Tracking"])

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def record_child_location(
    data: LocationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Log a new GPS coordinate ping for a child. Automatically checks geofence boundaries.
    """
    try:
        res = location_service.record_location(db, data, evaluate_geofence=True)
        return res["location"]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/current/{child_id}", response_model=CurrentLocationResponse)
def get_child_current_location(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Fetch the most up-to-date position, safety perimeter status, and active zone for a child.
    """
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found.")

    latest = location_service.get_latest_location(db, child_id)
    if not latest:
        return CurrentLocationResponse(
            child_id=child.id,
            child_name=child.name,
            current_location=None,
            is_safe=True,
            active_zone_name=None,
            is_device_online=False,
            last_updated=None,
        )

    geofence_eval = geofence_service.evaluate_location_against_safe_zones(
        db, child_id, latest.latitude, latest.longitude, create_events=False
    )

    device = child.devices[0] if child.devices else None

    return CurrentLocationResponse(
        child_id=child.id,
        child_name=child.name,
        current_location=LocationResponse.model_validate(latest),
        is_safe=geofence_eval.get("is_inside_safe_zone", True),
        active_zone_name=geofence_eval.get("active_zone_name"),
        battery_percentage=device.battery_level if device else None,
        is_device_online=device.is_online if device else True,
        last_updated=latest.created_at,
    )

@router.get("/history/{child_id}", response_model=List[LocationResponse])
def get_child_location_history(
    child_id: str,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Retrieve historical GPS breadcrumbs for breadcrumb visualization and route playback.
    """
    history = location_service.get_location_history(
        db, child_id=child_id, start_time=start_time, end_time=end_time, limit=limit
    )
    return history
