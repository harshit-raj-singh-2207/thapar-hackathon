import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.location import Location
from app.models.child import Child
from app.models.device import Device
from app.schemas.location import LocationCreate
from app.services.geofence_service import geofence_service

logger = logging.getLogger("safety.location")

class LocationService:
    @staticmethod
    def record_location(
        db: Session,
        location_in: LocationCreate,
        evaluate_geofence: bool = True
    ) -> Dict[str, Any]:
        """
        Records a new GPS coordinate ping for a child and evaluates geofence rules.
        """
        child = db.query(Child).filter(Child.id == location_in.child_id).first()
        if not child:
            raise ValueError(f"Child with id '{location_in.child_id}' does not exist.")

        loc_obj = Location(
            child_id=location_in.child_id,
            device_id=location_in.device_id,
            latitude=location_in.latitude,
            longitude=location_in.longitude,
            accuracy=location_in.accuracy or 5.0,
            altitude=location_in.altitude,
            speed=location_in.speed or 0.0,
            heading=location_in.heading or 0.0,
            battery_level=location_in.battery_level,
            address=location_in.address,
            recorded_at=location_in.recorded_at or datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        db.add(loc_obj)

        # Update device last ping if device_id provided
        if location_in.device_id:
            device = db.query(Device).filter(Device.id == location_in.device_id).first()
            if device:
                device.last_ping_at = datetime.now(timezone.utc)
                if location_in.battery_level is not None:
                    device.battery_level = int(location_in.battery_level)

        db.commit()
        db.refresh(loc_obj)

        geofence_status = {}
        if evaluate_geofence:
            geofence_status = geofence_service.evaluate_location_against_safe_zones(
                db=db,
                child_id=child.id,
                lat=location_in.latitude,
                lon=location_in.longitude,
                create_events=True,
            )

        return {
            "location": loc_obj,
            "geofence_evaluation": geofence_status,
        }

    @staticmethod
    def get_latest_location(db: Session, child_id: str) -> Optional[Location]:
        return (
            db.query(Location)
            .filter(Location.child_id == child_id)
            .order_by(desc(Location.created_at))
            .first()
        )

    @staticmethod
    def get_location_history(
        db: Session,
        child_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Location]:
        query = db.query(Location).filter(Location.child_id == child_id)
        if start_time:
            query = query.filter(Location.created_at >= start_time)
        if end_time:
            query = query.filter(Location.created_at <= end_time)

        return query.order_by(desc(Location.created_at)).limit(limit).all()

location_service = LocationService()
