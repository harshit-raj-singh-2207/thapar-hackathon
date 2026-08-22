import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app.models.child import Child
from app.models.device import Device
from app.models.location import Location
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.config.settings import settings
from app.utils.distance import calculate_haversine_distance
from app.schemas.separation import (
    SeparationEvaluationResponse,
    SeparationStatusResponse,
    SeparationResolveResponse,
)

logger = logging.getLogger("safety.separation_service")

class SeparationDomainService:
    def __init__(self, db: Session):
        self.db = db

    def _verify_caregiver_authorization(self, child_id: str, current_user: User) -> Child:
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
                detail="Unauthorized: You do not have permission to access safety data for this child."
            )
        return child

    def evaluate_separation(
        self,
        child_id: str,
        current_user: User,
        caregiver_lat: Optional[float] = None,
        caregiver_lon: Optional[float] = None,
        custom_threshold_meters: Optional[float] = None,
        custom_heartbeat_timeout_seconds: Optional[int] = None,
        create_event: bool = True,
    ) -> SeparationEvaluationResponse:
        """
        Evaluate separation for a child:
        1. Band disconnected check
        2. Heartbeat timeout check
        3. Distance-based separation check (if caregiver coordinates provided)
        4. Trigger safety event, alert creation & last known location saving
        """
        child = self._verify_caregiver_authorization(child_id, current_user)

        threshold_distance = custom_threshold_meters or settings.SEPARATION_ALERT_THRESHOLD_METERS
        heartbeat_timeout = custom_heartbeat_timeout_seconds or settings.HEARTBEAT_TIMEOUT_SECONDS

        now_utc = datetime.now(timezone.utc)

        # Get paired device
        device = (
            self.db.query(Device)
            .filter(Device.child_id == child.id, Device.is_active == True)
            .first()
        )

        # Get latest location
        latest_loc = (
            self.db.query(Location)
            .filter(Location.child_id == child.id)
            .order_by(desc(Location.recorded_at), desc(Location.created_at))
            .first()
        )

        last_known_loc_data = None
        if latest_loc:
            last_known_loc_data = {
                "latitude": latest_loc.latitude,
                "longitude": latest_loc.longitude,
                "accuracy": latest_loc.accuracy,
                "source": latest_loc.source or "gps",
                "timestamp": (latest_loc.recorded_at or latest_loc.created_at).isoformat(),
            }

        is_separated = False
        separation_reason = None
        severity = "normal"
        time_since_last_hb = None
        is_band_connected = True
        distance_meters = None

        # 1. Band Disconnected Check
        if device:
            conn_status = device.connection_status or ("online" if device.is_online else "offline")
            if conn_status in ["disconnected", "offline"] or not device.is_online or not device.is_active:
                is_band_connected = False
                is_separated = True
                separation_reason = "band_disconnected"
                severity = "warning"

            # 2. Heartbeat Timeout Check
            last_seen = device.last_seen or device.last_ping_at
            if last_seen:
                last_seen_aware = last_seen if last_seen.tzinfo else last_seen.replace(tzinfo=timezone.utc)
                time_since_last_hb = (now_utc - last_seen_aware).total_seconds()
                if time_since_last_hb > heartbeat_timeout:
                    is_separated = True
                    separation_reason = "heartbeat_timeout"
                    severity = "critical" if time_since_last_hb > (heartbeat_timeout * 2) else "warning"

        # 3. Distance-based Separation Check
        if caregiver_lat is not None and caregiver_lon is not None and latest_loc:
            dist = calculate_haversine_distance(
                latest_loc.latitude, latest_loc.longitude, caregiver_lat, caregiver_lon
            )
            distance_meters = round(dist, 2)
            if dist > threshold_distance:
                is_separated = True
                separation_reason = "distance_exceeded"
                severity = "critical" if dist > (threshold_distance * 2) else "warning"

        active_event_id = None
        alert_created = False

        if is_separated:
            child.current_status = "separation_alert"

            if create_event:
                # Format descriptive event title & description
                if separation_reason == "distance_exceeded":
                    title = f"Separation Alert: {child.name} is {distance_meters}m away"
                    description = f"Child has moved {distance_meters}m away, exceeding the perimeter threshold of {threshold_distance}m."
                elif separation_reason == "heartbeat_timeout":
                    title = f"Heartbeat Timeout Alert for {child.name}"
                    description = f"No telemetry received from child's band for {int(time_since_last_hb or 0)} seconds (timeout limit: {heartbeat_timeout}s)."
                else:
                    title = f"Band Disconnected Alert for {child.name}"
                    description = f"Child's wearable band disconnected unexpectedly."

                metadata = {
                    "reason": separation_reason,
                    "distance_meters": distance_meters,
                    "threshold_meters": threshold_distance,
                    "heartbeat_timeout_seconds": heartbeat_timeout,
                    "time_since_last_heartbeat": time_since_last_hb,
                    "is_band_connected": is_band_connected,
                    "last_known_location": last_known_loc_data,
                }

                event = SafetyEvent(
                    child_id=child.id,
                    event_type="separation_alert",
                    severity=severity,
                    title=title,
                    description=description,
                    latitude=latest_loc.latitude if latest_loc else None,
                    longitude=latest_loc.longitude if latest_loc else None,
                    metadata_json=json.dumps(metadata),
                    is_acknowledged=False,
                    created_at=now_utc,
                )
                self.db.add(event)
                self.db.commit()
                self.db.refresh(event)
                active_event_id = event.id
                alert_created = True
            else:
                self.db.commit()
        else:
            if child.current_status == "separation_alert":
                child.current_status = "safe"
            self.db.commit()

        return SeparationEvaluationResponse(
            child_id=child.id,
            child_name=child.name,
            is_separated=is_separated,
            separation_reason=separation_reason,
            severity=severity,
            distance_meters=distance_meters,
            threshold_meters=threshold_distance,
            heartbeat_timeout_seconds=heartbeat_timeout,
            time_since_last_heartbeat_seconds=round(time_since_last_hb, 1) if time_since_last_hb is not None else None,
            is_band_connected=is_band_connected,
            last_known_location=last_known_loc_data,
            active_event_id=active_event_id,
            alert_created=alert_created,
        )

    def get_separation_status(self, child_id: str, current_user: User) -> SeparationStatusResponse:
        """Get concise separation status for child."""
        child = self._verify_caregiver_authorization(child_id, current_user)

        eval_res = self.evaluate_separation(
            child_id=child_id,
            current_user=current_user,
            create_event=False
        )

        active_alert_count = (
            self.db.query(SafetyEvent)
            .filter(
                SafetyEvent.child_id == child.id,
                SafetyEvent.event_type == "separation_alert",
                SafetyEvent.is_acknowledged == False,
            )
            .count()
        )

        return SeparationStatusResponse(
            child_id=child.id,
            child_name=child.name,
            is_separated=eval_res.is_separated,
            separation_reason=eval_res.separation_reason,
            current_status=child.current_status,
            distance_meters=eval_res.distance_meters,
            threshold_meters=eval_res.threshold_meters,
            is_band_connected=eval_res.is_band_connected,
            last_known_location=eval_res.last_known_location,
            has_active_alert=active_alert_count > 0 or eval_res.is_separated,
        )

    def resolve_separation(self, child_id: str, current_user: User) -> SeparationResolveResponse:
        """
        Resolve active separation events for child and restore safe status.
        """
        child = self._verify_caregiver_authorization(child_id, current_user)
        now_utc = datetime.now(timezone.utc)

        # Find unacknowledged separation events
        unack_events = (
            self.db.query(SafetyEvent)
            .filter(
                SafetyEvent.child_id == child.id,
                SafetyEvent.event_type == "separation_alert",
                SafetyEvent.is_acknowledged == False,
            )
            .all()
        )

        count = len(unack_events)
        for ev in unack_events:
            ev.is_acknowledged = True
            ev.acknowledged_at = now_utc
            ev.acknowledged_by = current_user.id

        child.current_status = "safe"

        try:
            self.db.commit()
            return SeparationResolveResponse(
                child_id=child.id,
                resolved=True,
                resolved_events_count=count,
                current_status="safe",
                message=f"Separation resolved successfully. {count} active alert(s) acknowledged.",
                resolved_at=now_utc,
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error resolving separation for child {child_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while resolving separation."
            )
