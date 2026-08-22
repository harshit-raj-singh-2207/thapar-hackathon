from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.location import LocationCreate, LocationResponse
from app.domains.safety.location_service import LocationService

router = APIRouter(tags=["Safety - GPS Location Core"])

@router.post(
    "/location",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save child's GPS location",
    description="Save a new GPS location ping for a child. Validates coordinates, accuracy, and verifies caregiver authorization."
)
def save_child_location(
    data: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save child's GPS location:
    - Latitude (-90 to 90)
    - Longitude (-180 to 180)
    - GPS accuracy (>= 0)
    - Timestamp
    - Location source
    - Child association
    - Authenticated caregiver authorization
    """
    service = LocationService(db)
    return service.save_location(location_in=data, current_user=current_user)

@router.get(
    "/location/{child_id}",
    response_model=LocationResponse,
    summary="Get child's latest location",
    description="Retrieve the latest recorded GPS location for an authorized child."
)
def get_child_latest_location(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get child's latest location.
    Requires authentication and authorization as the child's caregiver.
    """
    service = LocationService(db)
    return service.get_latest_location(child_id=child_id, current_user=current_user)

@router.get(
    "/location/{child_id}/last",
    response_model=LocationResponse,
    summary="Get child's last known location",
    description="Retrieve the last known GPS location for an authorized child."
)
def get_child_last_known_location(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get child's last known location.
    Requires authentication and authorization as the child's caregiver.
    """
    service = LocationService(db)
    return service.get_last_known_location(child_id=child_id, current_user=current_user)
