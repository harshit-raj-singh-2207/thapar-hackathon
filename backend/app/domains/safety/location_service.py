import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.location import Location
from app.models.child import Child
from app.models.user import User
from app.models.device import Device
from app.schemas.location import LocationCreate
from app.domains.safety.repository import LocationRepository

logger = logging.getLogger("safety.gps_location_core")

class LocationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LocationRepository(db)

    def _validate_coordinates(self, latitude: float, longitude: float, accuracy: Optional[float] = None):
        """Validate latitude, longitude bounds and accuracy."""
        if latitude < -90.0 or latitude > 90.0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid latitude: {latitude}. Must be between -90 and 90 degrees."
            )
        if longitude < -180.0 or longitude > 180.0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid longitude: {longitude}. Must be between -180 and 180 degrees."
            )
        if accuracy is not None and accuracy < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid accuracy: {accuracy}. Must be greater than or equal to 0."
            )

    def _verify_child_and_authorization(self, child_id: str, current_user: User) -> Child:
        """Verify child exists and current authenticated user is authorized caregiver."""
        if child_id == "current":
            child = current_user.children[0] if current_user.children else None
            if not child:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No child associated with current user."
                )
            return child

        child = self.repo.get_child_by_id(child_id)
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child with ID '{child_id}' not found."
            )

        # Check authorization: user must be the assigned caregiver or an admin
        if child.caregiver_id != current_user.id and getattr(current_user, "role", None) != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You do not have permission to access or modify this child's location data."
            )

        return child

    def save_location(
        self,
        location_in: LocationCreate,
        current_user: User,
    ) -> Location:
        """
        Validate coordinates, verify child and authorization, and persist GPS location to the database.
        """
        # Validate coordinates & accuracy
        self._validate_coordinates(
            latitude=location_in.latitude,
            longitude=location_in.longitude,
            accuracy=location_in.accuracy
        )

        # Verify child and authorization
        child = self._verify_child_and_authorization(location_in.child_id, current_user)

        now_utc = datetime.now(timezone.utc)
        record_time = location_in.recorded_at or location_in.timestamp or now_utc

        loc_obj = Location(
            child_id=child.id,
            device_id=location_in.device_id,
            latitude=location_in.latitude,
            longitude=location_in.longitude,
            accuracy=location_in.accuracy if location_in.accuracy is not None else 5.0,
            source=location_in.source or "gps",
            altitude=location_in.altitude,
            speed=location_in.speed or 0.0,
            heading=location_in.heading or 0.0,
            battery_level=location_in.battery_level,
            address=location_in.address,
            recorded_at=record_time,
            created_at=now_utc,
        )

        try:
            saved_loc = self.repo.create_location(loc_obj)

            # Update device if device_id is linked
            if location_in.device_id:
                device = self.db.query(Device).filter(Device.id == location_in.device_id).first()
                if device:
                    device.last_ping_at = now_utc
                    if location_in.battery_level is not None:
                        device.battery_level = int(location_in.battery_level)
                    self.db.commit()

            return saved_loc
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while saving location for child {child.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A database error occurred while saving the GPS location."
            )

    def get_latest_location(
        self,
        child_id: str,
        current_user: User,
    ) -> Location:
        """
        Retrieve the latest GPS location for an authorized child.
        """
        self._verify_child_and_authorization(child_id, current_user)
        latest_loc = self.repo.get_latest_location(child_id)
        if not latest_loc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No location records found for child ID '{child_id}'."
            )
        return latest_loc

    def get_last_known_location(
        self,
        child_id: str,
        current_user: User,
    ) -> Location:
        """
        Retrieve the last known GPS location for an authorized child.
        """
        self._verify_child_and_authorization(child_id, current_user)
        last_loc = self.repo.get_last_known_location(child_id)
        if not last_loc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No last known location found for child ID '{child_id}'."
            )
        return last_loc
