import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app.models.child import Child
from app.models.safe_zone import SafeZone
from app.models.location import Location
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.domains.safety.safe_zone_repository import SafeZoneRepository
from app.schemas.safe_zone import SafeZoneCreate, SafeZoneUpdate, SafeZoneStatusCheck
from app.utils.distance import calculate_haversine_distance, is_point_in_polygon
from app.services.notification_service import notification_service

logger = logging.getLogger("safety.safe_zone_service")

class SafeZoneService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SafeZoneRepository(db)

    def _verify_caregiver_authorization_for_child(self, child_id: str, current_user: User) -> Child:
        """Verify child exists and user is authorized caregiver."""
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child with ID '{child_id}' not found."
            )
        if child.caregiver_id != current_user.id and getattr(current_user, "role", None) != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You do not have permission to manage safe zones for this child."
            )
        return child

    def _verify_caregiver_authorization_for_zone(self, safe_zone: SafeZone, current_user: User) -> Child:
        """Verify user is authorized to manage the given safe zone."""
        return self._verify_caregiver_authorization_for_child(safe_zone.child_id, current_user)

    def create_safe_zone(self, data: SafeZoneCreate, current_user: User) -> SafeZone:
        """Create a new safe zone for an authorized child."""
        child = self._verify_caregiver_authorization_for_child(data.child_id, current_user)

        lat = data.latitude if data.latitude is not None else data.center_latitude
        lon = data.longitude if data.longitude is not None else data.center_longitude
        rad = data.radius if data.radius is not None else data.radius_meters
        active = data.active if data.active is not None else data.is_active

        if lat is None or lat < -90.0 or lat > 90.0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Latitude must be between -90 and 90.")
        if lon is None or lon < -180.0 or lon > 180.0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Longitude must be between -180 and 180.")
        if rad is None or rad <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Radius must be greater than 0.")

        try:
            return self.repo.create(
                child_id=child.id,
                name=data.name,
                latitude=lat,
                longitude=lon,
                radius=rad,
                is_active=True if active is None else bool(active),
                zone_type=data.zone_type or "circle",
                polygon_coordinates=data.polygon_coordinates,
                address=data.address,
                alert_on_exit=data.alert_on_exit if data.alert_on_exit is not None else True,
                alert_on_enter=data.alert_on_enter if data.alert_on_enter is not None else False,
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating safe zone: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating safe zone."
            )

    def get_child_safe_zones(self, child_id: str, current_user: User) -> List[SafeZone]:
        """Get all safe zones configured for a child."""
        child = self._verify_caregiver_authorization_for_child(child_id, current_user)
        return self.repo.get_by_child_id(child.id)

    def get_safe_zone(self, zone_id: str, current_user: User) -> SafeZone:
        """Get a single safe zone by ID."""
        zone = self.repo.get_by_id(zone_id)
        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Safe zone with ID '{zone_id}' not found."
            )
        self._verify_caregiver_authorization_for_zone(zone, current_user)
        return zone

    def update_safe_zone(self, zone_id: str, data: SafeZoneUpdate, current_user: User) -> SafeZone:
        """Update safe zone parameters."""
        zone = self.get_safe_zone(zone_id, current_user)

        lat = data.latitude if data.latitude is not None else data.center_latitude
        lon = data.longitude if data.longitude is not None else data.center_longitude
        rad = data.radius if data.radius is not None else data.radius_meters
        active = data.active if data.active is not None else data.is_active

        if lat is not None and (lat < -90.0 or lat > 90.0):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Latitude must be between -90 and 90.")
        if lon is not None and (lon < -180.0 or lon > 180.0):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Longitude must be between -180 and 180.")
        if rad is not None and rad <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Radius must be greater than 0.")

        update_kwargs = {}
        if data.name is not None:
            update_kwargs["name"] = data.name
        if lat is not None:
            update_kwargs["center_latitude"] = lat
        if lon is not None:
            update_kwargs["center_longitude"] = lon
        if rad is not None:
            update_kwargs["radius_meters"] = rad
        if active is not None:
            update_kwargs["is_active"] = bool(active)
        if data.zone_type is not None:
            update_kwargs["zone_type"] = data.zone_type
        if data.polygon_coordinates is not None:
            update_kwargs["polygon_coordinates"] = json.dumps(data.polygon_coordinates)
        if data.address is not None:
            update_kwargs["address"] = data.address
        if data.alert_on_exit is not None:
            update_kwargs["alert_on_exit"] = data.alert_on_exit
        if data.alert_on_enter is not None:
            update_kwargs["alert_on_enter"] = data.alert_on_enter

        try:
            return self.repo.update(zone, **update_kwargs)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating safe zone {zone_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating safe zone."
            )

    def delete_safe_zone(self, zone_id: str, current_user: User) -> Dict[str, Any]:
        """Delete a safe zone."""
        zone = self.get_safe_zone(zone_id, current_user)
        try:
            self.repo.delete(zone)
            return {"message": "Safe zone deleted successfully", "id": zone_id}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting safe zone {zone_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting safe zone."
            )

    def evaluate_child_geofence(
        self,
        child_id: str,
        current_user: User,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        create_events: bool = True
    ) -> SafeZoneStatusCheck:
        """
        Evaluate child's GPS location against all active safe zones.
        Detects Inside/Outside, Entry (Outside -> Inside), and Exit (Inside -> Outside).
        Creates SafetyEvent and Caregiver Alerts on breach/return.
        """
        child = self._verify_caregiver_authorization_for_child(child_id, current_user)

        # Get coordinates: use parameters if provided, else child's latest recorded location
        if latitude is None or longitude is None:
            latest_loc = (
                self.db.query(Location)
                .filter(Location.child_id == child.id)
                .order_by(desc(Location.recorded_at), desc(Location.created_at))
                .first()
            )
            if not latest_loc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No GPS location recorded for this child and no coordinates provided."
                )
            eval_lat = latest_loc.latitude
            eval_lon = latest_loc.longitude
        else:
            eval_lat = latitude
            eval_lon = longitude

        active_zones = self.repo.get_by_child_id(child.id, active_only=True)

        if not active_zones:
            return SafeZoneStatusCheck(
                child_id=child.id,
                latitude=eval_lat,
                longitude=eval_lon,
                is_inside_safe_zone=True,
                is_inside=True,
                active_zone_id=None,
                active_zone_name="No Safe Zones Configured",
                distance_to_boundary_meters=0.0,
                distance_to_center_meters=0.0,
                status="safe",
            )

        inside_any = False
        matching_zone = None
        min_dist_to_center = float("inf")

        for zone in active_zones:
            dist = calculate_haversine_distance(
                eval_lat, eval_lon, zone.center_latitude, zone.center_longitude
            )
            if dist < min_dist_to_center:
                min_dist_to_center = dist

            is_inside_this_zone = False
            if zone.zone_type == "polygon" and zone.polygon_coordinates:
                try:
                    coords = json.loads(zone.polygon_coordinates)
                    is_inside_this_zone = is_point_in_polygon(eval_lat, eval_lon, coords)
                except Exception:
                    is_inside_this_zone = dist <= zone.radius_meters
            else:
                is_inside_this_zone = dist <= zone.radius_meters

            if is_inside_this_zone:
                inside_any = True
                matching_zone = zone
                break

        previous_status = child.current_status
        now_utc = datetime.now(timezone.utc)

        # 1. Exit Detection: Transition Inside -> Outside
        if not inside_any:
            new_status = "out_of_bounds"
            child.current_status = new_status

            if create_events and previous_status != "out_of_bounds":
                event = SafetyEvent(
                    child_id=child.id,
                    event_type="geofence_exit",
                    severity="critical",
                    title=f"Geofence Exit: {child.name} left safe zone",
                    description=f"{child.name} has moved outside safe boundaries ({round(min_dist_to_center, 1)}m away from closest zone).",
                    latitude=eval_lat,
                    longitude=eval_lon,
                    metadata_json=json.dumps({
                        "distance_to_center": min_dist_to_center,
                        "previous_status": previous_status,
                        "timestamp": now_utc.isoformat(),
                    }),
                    is_acknowledged=False,
                    created_at=now_utc,
                )
                self.db.add(event)

                from app.models.emergency import EmergencyAlert
                alert = EmergencyAlert(
                    child_id=child.id,
                    caregiver_id=child.caregiver_id,
                    status="active",
                    severity="critical",
                    triggered_by="geofence_breach",
                    latitude=eval_lat,
                    longitude=eval_lon,
                    message=f"GEOFENCE BREACH: {child.name} has exited safe boundaries ({round(min_dist_to_center, 1)}m away).",
                    created_at=now_utc,
                )
                self.db.add(alert)

                notification_service.send_emergency_alert(
                    db=self.db,
                    child=child,
                    alert_title="GEOFENCE BREACH ALERT",
                    alert_message=f"{child.name} has moved outside designated safe zones!",
                    severity="critical",
                    coordinates={"latitude": eval_lat, "longitude": eval_lon},
                )
            self.db.commit()

        # 2. Entry Detection: Transition Outside -> Inside
        else:
            new_status = "safe"
            child.current_status = new_status

            if create_events and previous_status == "out_of_bounds":
                event = SafetyEvent(
                    child_id=child.id,
                    event_type="geofence_entry",
                    severity="info",
                    title=f"Safe Zone Return: {child.name} entered {matching_zone.name if matching_zone else 'safe zone'}",
                    description=f"{child.name} has safely returned inside {matching_zone.name if matching_zone else 'safe zone'}.",
                    latitude=eval_lat,
                    longitude=eval_lon,
                    metadata_json=json.dumps({
                        "zone_id": matching_zone.id if matching_zone else None,
                        "zone_name": matching_zone.name if matching_zone else None,
                        "previous_status": previous_status,
                        "timestamp": now_utc.isoformat(),
                    }),
                    is_acknowledged=False,
                    created_at=now_utc,
                )
                self.db.add(event)
            self.db.commit()

        return SafeZoneStatusCheck(
            child_id=child.id,
            latitude=eval_lat,
            longitude=eval_lon,
            is_inside_safe_zone=inside_any,
            is_inside=inside_any,
            active_zone_id=matching_zone.id if matching_zone else None,
            active_zone_name=matching_zone.name if matching_zone else None,
            distance_to_boundary_meters=round(min_dist_to_center, 2),
            distance_to_center_meters=round(min_dist_to_center, 2),
            status=child.current_status,
        )
