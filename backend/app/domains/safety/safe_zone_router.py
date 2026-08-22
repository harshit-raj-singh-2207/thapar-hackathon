from typing import List, Optional, Union, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

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
from app.domains.safety.safe_zone_service import SafeZoneService

router = APIRouter(prefix="/safe-zones", tags=["Safety - Safe Zones & Geofencing"])

@router.post(
    "",
    response_model=SafeZoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Safe Zone",
    description="Create a new geofenced safe zone for a child."
)
@router.post(
    "/",
    response_model=SafeZoneResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_safe_zone(
    data: SafeZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new safe zone. Only authorized caregivers can create zones for their children.
    """
    service = SafeZoneService(db)
    return service.create_safe_zone(data=data, current_user=current_user)

@router.post(
    "/evaluate",
    response_model=SafeZoneStatusCheck,
    summary="Evaluate Test Coordinates Against Safe Zones",
    description="Evaluate test coordinates against child's configured safe zones without persisting events."
)
def evaluate_test_coordinates(
    child_id: str,
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test coordinate containment against safe zones.
    """
    service = SafeZoneService(db)
    return service.evaluate_child_geofence(
        child_id=child_id,
        current_user=current_user,
        latitude=latitude,
        longitude=longitude,
        create_events=False,
    )

@router.get(
    "/child/{child_id}",
    response_model=List[SafeZoneResponse],
    summary="Get Child Safe Zones",
    description="List all safe zones for a specific child."
)
def get_child_safe_zones(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return all safe zones belonging to the child.
    """
    service = SafeZoneService(db)
    return service.get_child_safe_zones(child_id=child_id, current_user=current_user)

@router.get(
    "/{identifier}/check",
    response_model=SafeZoneStatusCheck,
    summary="Check Child Location Against Safe Zones",
    description="Evaluate child's GPS location against safe zones with entry/exit breach detection."
)
@router.post(
    "/{identifier}/check",
    response_model=SafeZoneStatusCheck,
    summary="Check Child Location Against Safe Zones (POST)",
    description="Evaluate child's GPS location against safe zones with entry/exit breach detection."
)
def check_child_geofence(
    identifier: str,
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    create_events: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check child's GPS location against safe zones. Detects inside/outside, entry, and exit.
    """
    service = SafeZoneService(db)
    return service.evaluate_child_geofence(
        child_id=identifier,
        current_user=current_user,
        latitude=latitude,
        longitude=longitude,
        create_events=create_events,
    )

@router.get(
    "/{identifier}",
    response_model=Union[SafeZoneResponse, List[SafeZoneResponse]],
    summary="Get Safe Zone(s) by Identifier",
    description="Intelligently returns either all safe zones for a child (by child ID) or a single safe zone (by zone ID)."
)
def get_safe_zone_or_child_zones(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return all safe zones belonging to a child if identifier is a child ID,
    or return one safe zone if identifier is a zone ID.
    """
    service = SafeZoneService(db)

    # 1. Check if identifier matches a child
    child = db.query(Child).filter(Child.id == identifier).first()
    if child:
        return service.get_child_safe_zones(child_id=identifier, current_user=current_user)

    # 2. Check if identifier matches a safe zone
    zone = db.query(SafeZone).filter(SafeZone.id == identifier).first()
    if zone:
        return service.get_safe_zone(zone_id=identifier, current_user=current_user)

    # 3. If identifier looks like a child id (e.g. starts with 'child-'), verify child ownership to return 403 or 404 properly
    if identifier.startswith("child-") or identifier.startswith("child_"):
        return service.get_child_safe_zones(child_id=identifier, current_user=current_user)

    # 4. Fall back to get_safe_zone to trigger appropriate 404
    return service.get_safe_zone(zone_id=identifier, current_user=current_user)

@router.patch(
    "/{zone_id}",
    response_model=SafeZoneResponse,
    summary="Update Safe Zone",
    description="Update safe zone name, coordinates, radius, or active state."
)
@router.put(
    "/{zone_id}",
    response_model=SafeZoneResponse,
    include_in_schema=False
)
def update_safe_zone(
    zone_id: str,
    data: SafeZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a safe zone.
    """
    service = SafeZoneService(db)
    return service.update_safe_zone(zone_id=zone_id, data=data, current_user=current_user)

@router.delete(
    "/{zone_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Safe Zone",
    description="Delete a safe zone."
)
def delete_safe_zone(
    zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a safe zone.
    """
    service = SafeZoneService(db)
    return service.delete_safe_zone(zone_id=zone_id, current_user=current_user)
