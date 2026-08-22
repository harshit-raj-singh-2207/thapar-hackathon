import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.child import Child
from app.models.user import User
from app.models.location import Location
from app.models.device import Device
from app.models.safe_zone import SafeZone
from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent
from app.domains.safety.separation_service import SeparationDomainService
from app.domains.safety.safe_zone_service import SafeZoneService
from app.schemas.caregiver_dashboard import (
    ChildProfileResponse,
    ChildStatusResponse,
    ChildLocationResponse,
    DeviceStatusResponse,
    SafetyOverviewResponse,
    RecentActivityItem,
    AlertSummaryResponse,
)

logger = logging.getLogger("caregiver.dashboard")

class CaregiverDashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _verify_child_authorization(self, child_id: str, current_user: User) -> Child:
        """Verify child exists and current user is the authorized caregiver or admin."""
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child with ID '{child_id}' not found."
            )
        if child.caregiver_id != current_user.id and getattr(current_user, "role", None) != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You do not have permission to view dashboard data for this child."
            )
        return child

    def get_child_profile(self, child_id: str, current_user: User) -> ChildProfileResponse:
        """Get child's basic profile."""
        child = self._verify_child_authorization(child_id, current_user)
        cg_name = child.caregiver.full_name if child.caregiver else current_user.full_name

        return ChildProfileResponse(
            child_id=child.id,
            name=child.name,
            age=child.age,
            gender=child.gender,
            avatar_url=child.avatar_url,
            autism_level=child.autism_level,
            medical_notes=child.medical_notes,
            caregiver_id=child.caregiver_id,
            caregiver_name=cg_name,
            account_status="active",
            tracking_enabled=child.tracking_enabled if child.tracking_enabled is not None else True,
            current_status=child.current_status or "safe",
            created_at=child.created_at or datetime.now(timezone.utc),
            updated_at=child.updated_at,
        )

    def get_child_location(self, child_id: str, current_user: User) -> ChildLocationResponse:
        """Get child's current or last known location and freshness."""
        child = self._verify_child_authorization(child_id, current_user)
        latest_loc = (
            self.db.query(Location)
            .filter(Location.child_id == child.id)
            .order_by(desc(Location.recorded_at), desc(Location.created_at))
            .first()
        )

        if not latest_loc:
            return ChildLocationResponse(
                child_id=child.id,
                latitude=None,
                longitude=None,
                accuracy=None,
                timestamp=None,
                recorded_at=None,
                source=None,
                is_live=False,
                location_available=False,
                status="unavailable",
            )

        now_utc = datetime.now(timezone.utc)
        rec_time = latest_loc.recorded_at or latest_loc.created_at
        is_fresh = False
        if rec_time:
            # Make sure timezone comparison is safe
            if rec_time.tzinfo is None:
                rec_time = rec_time.replace(tzinfo=timezone.utc)
            is_fresh = (now_utc - rec_time) < timedelta(minutes=5)

        loc_status = "fresh" if is_fresh else "stale"

        return ChildLocationResponse(
            child_id=child.id,
            latitude=latest_loc.latitude,
            longitude=latest_loc.longitude,
            accuracy=latest_loc.accuracy,
            timestamp=latest_loc.recorded_at or latest_loc.created_at,
            recorded_at=latest_loc.recorded_at or latest_loc.created_at,
            source=latest_loc.source or "gps",
            is_live=is_fresh,
            location_available=True,
            status=loc_status,
        )

    def get_child_device(self, child_id: str, current_user: User) -> DeviceStatusResponse:
        """Get child's GPS band device telemetry and status."""
        child = self._verify_child_authorization(child_id, current_user)
        device = self.db.query(Device).filter(Device.child_id == child.id).first()

        if not device:
            return DeviceStatusResponse(
                band_id=None,
                device_identifier=None,
                device_name=None,
                device_type=None,
                connection_status="none",
                is_online=False,
                is_paired=False,
                battery_level=None,
                battery_status="unknown",
                gps_status="unknown",
                last_seen=None,
                firmware_version=None,
                is_stale=False,
            )

        bat_level = device.battery_level
        bat_status = "unknown"
        if bat_level is not None:
            if bat_level <= 10:
                bat_status = "critical"
            elif bat_level <= 20:
                bat_status = "low"
            else:
                bat_status = "good"

        now_utc = datetime.now(timezone.utc)
        last_seen = device.last_seen or device.last_ping_at
        is_stale = False
        if last_seen:
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            is_stale = (now_utc - last_seen) > timedelta(seconds=120)

        conn_status = device.connection_status or ("online" if device.is_online else "offline")
        if is_stale and conn_status == "connected":
            conn_status = "stale"

        return DeviceStatusResponse(
            band_id=device.id,
            device_identifier=device.device_identifier or device.serial_number,
            device_name=device.device_name,
            device_type=device.device_type,
            connection_status=conn_status,
            is_online=device.is_online and not is_stale,
            is_paired=True,
            battery_level=device.battery_level,
            battery_status=bat_status,
            gps_status=device.gps_status or "active",
            last_seen=device.last_seen or device.last_ping_at,
            firmware_version=device.firmware_version,
            is_stale=is_stale,
        )

    def get_child_status(self, child_id: str, current_user: User) -> ChildStatusResponse:
        """Aggregated real-time safety and health status for child."""
        child = self._verify_child_authorization(child_id, current_user)
        loc_resp = self.get_child_location(child_id, current_user)
        dev_resp = self.get_child_device(child_id, current_user)

        # Check separation status
        sep_service = SeparationDomainService(self.db)
        sep_eval = sep_service.evaluate_separation(child_id, current_user)
        is_sep = sep_eval.is_separated

        # Check safe zone status
        sz_status = "no_zones"
        zones = self.db.query(SafeZone).filter(SafeZone.child_id == child.id, SafeZone.is_active == True).all()
        if zones:
            if loc_resp.location_available and loc_resp.latitude is not None and loc_resp.longitude is not None:
                sz_service = SafeZoneService(self.db)
                eval_sz = sz_service.evaluate_child_geofence(
                    child_id=child.id,
                    current_user=current_user,
                    latitude=loc_resp.latitude,
                    longitude=loc_resp.longitude,
                    create_events=False
                )
                sz_status = "inside" if eval_sz.is_inside_safe_zone else "outside"
            else:
                sz_status = "unknown"

        # Check emergency status
        active_emg = (
            self.db.query(EmergencyAlert)
            .filter(EmergencyAlert.child_id == child.id, EmergencyAlert.status == "active")
            .first()
        )
        emg_status = "active" if active_emg else ("resolved" if child.current_status == "safe" else "none")
        active_emg_id = active_emg.id if active_emg else None

        last_loc_dict = None
        if loc_resp.location_available:
            last_loc_dict = {
                "latitude": loc_resp.latitude,
                "longitude": loc_resp.longitude,
                "accuracy": loc_resp.accuracy,
                "timestamp": loc_resp.timestamp.isoformat() if loc_resp.timestamp else None,
                "source": loc_resp.source,
                "status": loc_resp.status,
            }

        return ChildStatusResponse(
            child_id=child.id,
            name=child.name,
            current_status=child.current_status or "safe",
            is_online=dev_resp.is_online or loc_resp.status == "fresh",
            location_available=loc_resp.location_available,
            last_known_location=last_loc_dict,
            gps_status=dev_resp.gps_status if dev_resp.band_id else ("active" if loc_resp.location_available else "inactive"),
            gps_accuracy=loc_resp.accuracy,
            last_location_update=loc_resp.timestamp,
            band_connection_status=dev_resp.connection_status,
            is_separated=is_sep,
            safe_zone_status=sz_status,
            emergency_status=emg_status,
            active_emergency_id=active_emg_id,
        )

    def get_recent_activity(
        self,
        child_id: str,
        limit: int,
        current_user: User
    ) -> List[RecentActivityItem]:
        """Fetch recent chronological safety activity for the child."""
        child = self._verify_child_authorization(child_id, current_user)
        events = (
            self.db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == child.id)
            .order_by(desc(SafetyEvent.created_at))
            .limit(limit)
            .all()
        )
        return [RecentActivityItem.model_validate(ev) for ev in events]

    def get_alert_summary(self, child_id: str, current_user: User) -> AlertSummaryResponse:
        """Calculate alert summary metrics directly from database."""
        child = self._verify_child_authorization(child_id, current_user)
        events = self.db.query(SafetyEvent).filter(SafetyEvent.child_id == child.id).all()

        total = len(events)
        unread = sum(1 for ev in events if not ev.is_acknowledged)
        critical = sum(1 for ev in events if (ev.severity or "").lower() == "critical")
        high = sum(1 for ev in events if (ev.severity or "").lower() == "high")
        warning = sum(1 for ev in events if (ev.severity or "").lower() == "warning")
        info = sum(1 for ev in events if (ev.severity or "").lower() == "info")
        active = sum(1 for ev in events if not ev.is_acknowledged or (ev.severity or "").lower() in ["critical", "high"])

        return AlertSummaryResponse(
            child_id=child.id,
            total_alerts=total,
            unread_alerts=unread,
            active_alerts=active,
            critical_alerts=critical,
            high_alerts=high,
            warning_alerts=warning,
            info_alerts=info,
        )

    def get_safety_overview(self, child_id: str, current_user: User) -> SafetyOverviewResponse:
        """Full aggregated dashboard payload for CaregiverDashboard and SafetyOverviewScreen."""
        child = self._verify_child_authorization(child_id, current_user)
        profile = self.get_child_profile(child_id, current_user)
        location = self.get_child_location(child_id, current_user)
        device = self.get_child_device(child_id, current_user)
        status_info = self.get_child_status(child_id, current_user)
        alert_summary = self.get_alert_summary(child_id, current_user)
        recent_events = self.get_recent_activity(child_id, limit=5, current_user=current_user)

        active_emg = (
            self.db.query(EmergencyAlert)
            .filter(EmergencyAlert.child_id == child.id, EmergencyAlert.status == "active")
            .first()
        )

        return SafetyOverviewResponse(
            child=profile,
            location=location,
            device=device,
            safety={
                "is_separated": status_info.is_separated,
                "safe_zone_status": status_info.safe_zone_status,
                "tracking_enabled": profile.tracking_enabled,
                "current_status": status_info.current_status,
            },
            emergency={
                "has_active_emergency": active_emg is not None,
                "emergency_id": active_emg.id if active_emg else None,
                "severity": active_emg.severity if active_emg else "none",
                "triggered_by": active_emg.triggered_by if active_emg else None,
                "message": active_emg.message if active_emg else None,
                "latitude": active_emg.latitude if active_emg else None,
                "longitude": active_emg.longitude if active_emg else None,
            },
            alerts={
                "total": alert_summary.total_alerts,
                "unread": alert_summary.unread_alerts,
                "active": alert_summary.active_alerts,
                "critical": alert_summary.critical_alerts,
            },
            events=recent_events,
        )
