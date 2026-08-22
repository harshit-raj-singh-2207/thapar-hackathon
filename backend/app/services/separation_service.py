import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.child import Child
from app.models.safety_event import SafetyEvent
from app.utils.distance import calculate_haversine_distance
from app.config.settings import settings
from app.services.notification_service import notification_service

logger = logging.getLogger("safety.separation")

class SeparationService:
    @staticmethod
    def calculate_separation(
        child_lat: float,
        child_lon: float,
        caregiver_lat: float,
        caregiver_lon: float,
        max_allowed_distance_meters: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates distance between caregiver and child device.
        """
        threshold = max_allowed_distance_meters or settings.SEPARATION_ALERT_THRESHOLD_METERS
        distance = calculate_haversine_distance(
            child_lat, child_lon, caregiver_lat, caregiver_lon
        )
        is_separated = distance > threshold

        return {
            "distance_meters": round(distance, 2),
            "threshold_meters": threshold,
            "is_separated": is_separated,
            "severity": "critical" if distance > (threshold * 2) else ("warning" if is_separated else "normal"),
        }

    @classmethod
    def evaluate_separation(
        cls,
        db: Session,
        child_id: str,
        child_lat: float,
        child_lon: float,
        caregiver_lat: float,
        caregiver_lon: float,
        custom_threshold_meters: Optional[float] = None,
        create_event: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluates separation distance between caregiver and child and creates alert events when breached.
        """
        child = db.query(Child).filter(Child.id == child_id).first()
        if not child:
            return {"error": "Child not found"}

        result = cls.calculate_separation(
            child_lat, child_lon, caregiver_lat, caregiver_lon, custom_threshold_meters
        )

        if result["is_separated"]:
            child.current_status = "separation_alert"
            db.commit()

            if create_event:
                event = SafetyEvent(
                    child_id=child.id,
                    event_type="separation_alert",
                    severity=result["severity"],
                    title=f"Separation Warning: {child.name} is {result['distance_meters']}m away",
                    description=f"Distance exceeded safety perimeter threshold of {result['threshold_meters']}m.",
                    latitude=child_lat,
                    longitude=child_lon,
                    metadata_json=json.dumps(result),
                )
                db.add(event)
                db.commit()
                db.refresh(event)

                notification_service.send_emergency_alert(
                    db=db,
                    child=child,
                    alert_title="PROXIMITY SEPARATION ALERT",
                    alert_message=f"{child.name} has moved {result['distance_meters']}m away from you!",
                    severity=result["severity"],
                    coordinates={"latitude": child_lat, "longitude": child_lon},
                )
        else:
            if child.current_status == "separation_alert":
                child.current_status = "safe"
                db.commit()

        result["child_id"] = child_id
        result["child_name"] = child.name
        return result

separation_service = SeparationService()
