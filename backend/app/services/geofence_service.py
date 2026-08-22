import json
import logging
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.models.safe_zone import SafeZone
from app.models.child import Child
from app.models.safety_event import SafetyEvent
from app.utils.distance import calculate_haversine_distance, is_point_in_radius, is_point_in_polygon
from app.services.notification_service import notification_service

logger = logging.getLogger("safety.geofence")

class GeofenceService:
    @staticmethod
    def is_inside_safe_zone(
        lat: float, lon: float, safe_zone: SafeZone
    ) -> Tuple[bool, float]:
        """
        Check if (lat, lon) is inside a specific safe zone and return distance to center.
        """
        dist_to_center = calculate_haversine_distance(
            lat, lon, safe_zone.center_latitude, safe_zone.center_longitude
        )

        if safe_zone.zone_type == "polygon" and safe_zone.polygon_coordinates:
            try:
                coords = json.loads(safe_zone.polygon_coordinates)
                inside = is_point_in_polygon(lat, lon, coords)
                return inside, dist_to_center
            except Exception as e:
                logger.error(f"Error parsing polygon coords for zone {safe_zone.id}: {e}")

        # Default circle calculation
        inside = dist_to_center <= safe_zone.radius_meters
        return inside, dist_to_center

    @classmethod
    def evaluate_location_against_safe_zones(
        cls,
        db: Session,
        child_id: str,
        lat: float,
        lon: float,
        create_events: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluates a new location ping against all active safe zones for a child.
        Generates SafetyEvent and notifications if a breach is detected.
        """
        child = db.query(Child).filter(Child.id == child_id).first()
        if not child:
            return {"error": "Child not found", "is_safe": False}

        safe_zones = (
            db.query(SafeZone)
            .filter(SafeZone.child_id == child_id, SafeZone.is_active == True)
            .all()
        )

        # If no active safe zones configured, default to safe
        if not safe_zones:
            return {
                "child_id": child_id,
                "is_inside_safe_zone": True,
                "active_zone_id": None,
                "active_zone_name": "No Safe Zones Configured",
                "nearest_zone_distance_meters": 0.0,
            }

        inside_any = False
        active_zone = None
        min_distance = float("inf")

        for zone in safe_zones:
            inside, dist = cls.is_inside_safe_zone(lat, lon, zone)
            if dist < min_distance:
                min_distance = dist
            if inside:
                inside_any = True
                active_zone = zone
                break

        # Check status transition
        previous_status = child.current_status
        if inside_any:
            new_status = "safe"
        else:
            new_status = "out_of_bounds"

        child.current_status = new_status
        db.commit()

        # Generate event if exited
        if create_events and not inside_any and previous_status != "out_of_bounds":
            event = SafetyEvent(
                child_id=child.id,
                event_type="geofence_exit",
                severity="critical",
                title=f"Geofence Breach: {child.name} has left safe boundaries",
                description=f"{child.name} is {round(min_distance, 1)}m away from closest safe zone.",
                latitude=lat,
                longitude=lon,
                metadata_json=json.dumps({
                    "distance_to_nearest_meters": min_distance,
                    "previous_status": previous_status,
                }),
            )
            db.add(event)
            db.commit()
            db.refresh(event)

            # Send alerts
            notification_service.send_emergency_alert(
                db=db,
                child=child,
                alert_title="GEOFENCE BREACH ALERT",
                alert_message=f"{child.name} has moved outside designated safe zones!",
                severity="critical",
                coordinates={"latitude": lat, "longitude": lon},
            )

        elif create_events and inside_any and previous_status == "out_of_bounds":
            event = SafetyEvent(
                child_id=child.id,
                event_type="geofence_entry",
                severity="info",
                title=f"Safe Zone Return: {child.name} entered {active_zone.name if active_zone else 'safe zone'}",
                description=f"{child.name} has safely returned inside boundaries.",
                latitude=lat,
                longitude=lon,
            )
            db.add(event)
            db.commit()

        return {
            "child_id": child_id,
            "is_inside_safe_zone": inside_any,
            "active_zone_id": active_zone.id if active_zone else None,
            "active_zone_name": active_zone.name if active_zone else None,
            "nearest_zone_distance_meters": round(min_distance, 2),
            "status": new_status,
        }

geofence_service = GeofenceService()
