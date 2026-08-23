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
from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent
from app.models.location import Location
from app.models.user import User
from app.domains.safety.emergency_repository import EmergencyRepository
from app.schemas.emergency import (
    SOSTriggerRequest,
    EmergencyResolveRequest,
    EmergencyResponse,
    EmergencyDetailResponse,
    NFCSOSTriggerRequest,
    NFCSOSTriggerResponse,
)
from app.services.notification_service import notification_service

logger = logging.getLogger("safety.emergency_service")

class EmergencyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmergencyRepository(db)

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
                detail="Unauthorized: You do not have permission to manage emergency events for this child."
            )
        return child

    def trigger_sos(self, data: SOSTriggerRequest, current_user: User) -> EmergencyResponse:
        """
        Trigger an SOS emergency:
        1. Verify child authorization
        2. Prevent duplicate active SOS
        3. Capture current GPS location or fall back to last known location
        4. Create EmergencyAlert and SafetyEvent
        5. Dispatch Caregiver Alert
        """
        child = self._verify_caregiver_authorization(data.child_id, current_user)

        # 2. Prevent duplicate active SOS
        active_emg = self.repo.get_active_by_child_id(child.id)
        if active_emg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Child '{child.name}' already has an active emergency (ID: {active_emg.id})."
            )

        now_utc = datetime.now(timezone.utc)

        # 3. Location determination with fallback
        eval_lat = None
        eval_lon = None
        loc_source = None
        loc_timestamp = None

        if data.latitude is not None and data.longitude is not None:
            eval_lat = data.latitude
            eval_lon = data.longitude
            loc_source = "request"
            loc_timestamp = now_utc
        else:
            latest_loc = (
                self.db.query(Location)
                .filter(Location.child_id == child.id)
                .order_by(desc(Location.recorded_at), desc(Location.created_at))
                .first()
            )
            if latest_loc:
                eval_lat = latest_loc.latitude
                eval_lon = latest_loc.longitude
                loc_source = latest_loc.source or "gps"
                loc_timestamp = latest_loc.recorded_at or latest_loc.created_at

        msg = data.message or data.description or f"SOS Emergency activated for {child.name}!"
        if eval_lat is None:
            msg += " [Location Unavailable]"

        # Update child status
        child.current_status = "emergency"

        try:
            # 4. Create EmergencyAlert
            emergency = self.repo.create_emergency(
                child_id=child.id,
                caregiver_id=child.caregiver_id,
                triggered_by=data.triggered_by or "sos_button",
                severity="critical",
                latitude=eval_lat,
                longitude=eval_lon,
                message=msg,
            )

            # Create SafetyEvent
            event = SafetyEvent(
                child_id=child.id,
                event_type="SOS",
                severity="critical",
                title=f"SOS EMERGENCY ACTIVATED FOR {child.name.upper()}",
                description=msg,
                latitude=eval_lat,
                longitude=eval_lon,
                metadata_json=json.dumps({
                    "emergency_id": emergency.id,
                    "triggered_by": data.triggered_by or "sos_button",
                    "location_available": eval_lat is not None,
                    "location_source": loc_source,
                    "location_timestamp": loc_timestamp.isoformat() if loc_timestamp else None,
                }),
                is_acknowledged=False,
                created_at=now_utc,
            )
            self.db.add(event)
            self.db.commit()
            self.db.refresh(emergency)

            # 5. Dispatch Caregiver Alert
            coords = {"latitude": eval_lat, "longitude": eval_lon} if eval_lat is not None else None
            notification_service.send_emergency_alert(
                db=self.db,
                child=child,
                alert_title=f"🚨 SOS EMERGENCY: {child.name}",
                alert_message=msg,
                severity="critical",
                coordinates=coords,
            )

            return EmergencyResponse(
                id=emergency.id,
                child_id=emergency.child_id,
                caregiver_id=emergency.caregiver_id,
                status=emergency.status,
                severity=emergency.severity,
                triggered_by=emergency.triggered_by,
                event_type="SOS",
                latitude=emergency.latitude,
                longitude=emergency.longitude,
                location_available=emergency.latitude is not None and emergency.longitude is not None,
                message=emergency.message,
                description=emergency.message,
                created_at=emergency.created_at,
                triggered_at=emergency.created_at,
            )
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error triggering SOS for child {child.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while triggering SOS emergency."
            )

    def get_child_emergency(self, child_id: str, current_user: User) -> EmergencyDetailResponse:
        """Get active or most recent emergency for child."""
        child = self._verify_caregiver_authorization(child_id, current_user)
        emergency = self.repo.get_latest_by_child_id(child.id)
        if not emergency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No emergency records found for child '{child_id}'."
            )

        loc_avail = emergency.latitude is not None and emergency.longitude is not None
        return EmergencyDetailResponse(
            id=emergency.id,
            child_id=emergency.child_id,
            caregiver_id=emergency.caregiver_id,
            status=emergency.status,
            severity=emergency.severity,
            triggered_by=emergency.triggered_by,
            event_type="SOS",
            latitude=emergency.latitude,
            longitude=emergency.longitude,
            location_available=loc_avail,
            location_timestamp=emergency.created_at if loc_avail else None,
            location_source="gps" if loc_avail else None,
            address=emergency.address,
            message=emergency.message,
            description=emergency.message,
            triggered_at=emergency.created_at,
            created_at=emergency.created_at,
            resolved_at=emergency.resolved_at,
            resolved_by=emergency.resolved_by,
            resolution_notes=emergency.resolution_notes,
        )

    def get_emergency_details(self, event_id: str, current_user: User) -> EmergencyDetailResponse:
        """Get emergency details by event_id."""
        emergency = self.repo.get_by_id(event_id)
        if not emergency:
            # Check if event_id is a SafetyEvent
            event = self.db.query(SafetyEvent).filter(SafetyEvent.id == event_id).first()
            if event:
                child = self._verify_caregiver_authorization(event.child_id, current_user)
                loc_avail = event.latitude is not None and event.longitude is not None
                return EmergencyDetailResponse(
                    id=event.id,
                    child_id=event.child_id,
                    caregiver_id=child.caregiver_id,
                    status="resolved" if event.is_acknowledged else "active",
                    severity=event.severity or "critical",
                    triggered_by="sos_button",
                    event_type="SOS",
                    latitude=event.latitude,
                    longitude=event.longitude,
                    location_available=loc_avail,
                    location_timestamp=event.created_at if loc_avail else None,
                    location_source="gps" if loc_avail else None,
                    message=event.description or event.title,
                    description=event.description,
                    triggered_at=event.created_at,
                    created_at=event.created_at,
                    resolved_at=event.acknowledged_at,
                    resolved_by=event.acknowledged_by,
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emergency with ID '{event_id}' not found."
            )

        self._verify_caregiver_authorization(emergency.child_id, current_user)
        loc_avail = emergency.latitude is not None and emergency.longitude is not None
        return EmergencyDetailResponse(
            id=emergency.id,
            child_id=emergency.child_id,
            caregiver_id=emergency.caregiver_id,
            status=emergency.status,
            severity=emergency.severity,
            triggered_by=emergency.triggered_by,
            event_type="SOS",
            latitude=emergency.latitude,
            longitude=emergency.longitude,
            location_available=loc_avail,
            location_timestamp=emergency.created_at if loc_avail else None,
            location_source="gps" if loc_avail else None,
            address=emergency.address,
            message=emergency.message,
            description=emergency.message,
            triggered_at=emergency.created_at,
            created_at=emergency.created_at,
            resolved_at=emergency.resolved_at,
            resolved_by=emergency.resolved_by,
            resolution_notes=emergency.resolution_notes,
        )

    def resolve_emergency(
        self,
        event_id: str,
        data: Optional[EmergencyResolveRequest],
        current_user: User
    ) -> EmergencyResponse:
        """
        Resolve an active emergency:
        1. Verify caregiver authorization
        2. Prevent re-resolving an already resolved emergency
        3. Transition to resolved and restore child status to safe
        """
        emergency = self.repo.get_by_id(event_id)
        if not emergency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emergency with ID '{event_id}' not found."
            )

        child = self._verify_caregiver_authorization(emergency.child_id, current_user)

        if emergency.status == "resolved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Emergency is already resolved."
            )

        now_utc = datetime.now(timezone.utc)
        res_notes = data.resolution_notes if data else "Resolved by caregiver."

        try:
            emergency.status = "resolved"
            emergency.resolved_at = now_utc
            emergency.resolved_by = current_user.id
            emergency.resolution_notes = res_notes

            # Check if other active emergencies exist
            other_active = (
                self.db.query(EmergencyAlert)
                .filter(
                    EmergencyAlert.child_id == child.id,
                    EmergencyAlert.status == "active",
                    EmergencyAlert.id != emergency.id
                )
                .count()
            )
            if other_active == 0:
                child.current_status = "safe"

            # Acknowledge safety events
            unack_events = (
                self.db.query(SafetyEvent)
                .filter(
                    SafetyEvent.child_id == child.id,
                    SafetyEvent.is_acknowledged == False,
                    SafetyEvent.event_type.in_(["SOS", "sos_triggered"])
                )
                .all()
            )
            for ev in unack_events:
                ev.is_acknowledged = True
                ev.acknowledged_at = now_utc
                ev.acknowledged_by = current_user.id

            self.db.commit()
            self.db.refresh(emergency)

            return EmergencyResponse(
                id=emergency.id,
                child_id=emergency.child_id,
                caregiver_id=emergency.caregiver_id,
                status=emergency.status,
                severity=emergency.severity,
                triggered_by=emergency.triggered_by,
                event_type="SOS",
                latitude=emergency.latitude,
                longitude=emergency.longitude,
                location_available=emergency.latitude is not None and emergency.longitude is not None,
                message=emergency.message,
                description=emergency.message,
                resolved_at=emergency.resolved_at,
                resolved_by=emergency.resolved_by,
                resolution_notes=emergency.resolution_notes,
                created_at=emergency.created_at,
                triggered_at=emergency.created_at,
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error resolving emergency {event_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while resolving emergency."
            )

    def trigger_nfc_sos(self, data: NFCSOSTriggerRequest, current_user: User) -> NFCSOSTriggerResponse:
        """
        NFC Emergency Trigger with Wearable & Device Status Verification:
        1. Validate authenticated user & child access
        2. Validate NFC identifier
        3. Verify wearable existence & child association
        4. Verify wearable online status & battery health
        5. Trigger existing SOS engine & dispatch caregiver alert
        6. Persist NFC_SOS_TRIGGERED / NFC_SOS_REJECTED safety events
        7. Return structured trigger confirmation
        """
        now_utc = datetime.now(timezone.utc)
        nfc_clean = str(data.nfc_identifier).strip() if data.nfc_identifier else ""

        # 1. Verify child existence
        child = self.db.query(Child).filter(Child.id == data.child_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child with ID '{data.child_id}' not found."
            )

        # 2. Verify caregiver authorization
        if child.caregiver_id != current_user.id and getattr(current_user, "role", None) != "admin":
            ev_rej = SafetyEvent(
                child_id=child.id,
                event_type="NFC_SOS_REJECTED",
                severity="warning",
                title="Unauthorized NFC SOS Trigger Attempt",
                description=f"User '{current_user.id}' attempted unauthorized NFC SOS trigger for child '{child.name}'.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata_json=json.dumps({"nfc_identifier": nfc_clean, "child_id": child.id, "user_id": current_user.id}),
                is_acknowledged=False,
                created_at=now_utc,
            )
            self.db.add(ev_rej)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You do not have permission to manage emergency events for this child."
            )

        # 3. Validate NFC identifier format
        if not nfc_clean:
            ev_rej = SafetyEvent(
                child_id=child.id,
                event_type="NFC_SOS_REJECTED",
                severity="warning",
                title="Invalid NFC SOS Trigger Identifier",
                description="NFC identifier was empty during emergency trigger attempt.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata_json=json.dumps({"child_id": child.id}),
                is_acknowledged=False,
                created_at=now_utc,
            )
            self.db.add(ev_rej)
            self.db.commit()
            return NFCSOSTriggerResponse(
                triggered=False,
                status="NFC_INVALID",
                reason="NFC identifier is required and cannot be empty",
                child_id=child.id,
                device_verified=False,
            )

        # 4. Verify Wearable Existence & Association
        band = self.db.query(Device).filter(Device.child_id == child.id, Device.is_active == True).first()
        if not band:
            ev_rej = SafetyEvent(
                child_id=child.id,
                event_type="NFC_SOS_REJECTED",
                severity="warning",
                title="Wearable Device Missing During NFC SOS",
                description="No active wearable device is associated with this child.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata_json=json.dumps({"nfc_identifier": nfc_clean, "child_id": child.id}),
                is_acknowledged=False,
                created_at=now_utc,
            )
            self.db.add(ev_rej)
            self.db.commit()
            return NFCSOSTriggerResponse(
                triggered=False,
                status="DEVICE_NOT_ASSOCIATED",
                reason="No active wearable device is associated with this child",
                child_id=child.id,
                device_verified=False,
            )

        # Check if NFC belongs to another child's wearable
        other_device = self.db.query(Device).filter(Device.nfc_tag_id == nfc_clean).first()
        if other_device and other_device.child_id and other_device.child_id != child.id:
            ev_rej = SafetyEvent(
                child_id=child.id,
                event_type="NFC_SOS_REJECTED",
                severity="warning",
                title="NFC Belongs To Another Child",
                description="NFC identifier belongs to another child's wearable device.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata_json=json.dumps({"nfc_identifier": nfc_clean, "child_id": child.id, "assigned_child": other_device.child_id}),
                is_acknowledged=False,
                created_at=now_utc,
            )
            self.db.add(ev_rej)
            self.db.commit()
            return NFCSOSTriggerResponse(
                triggered=False,
                status="DEVICE_NOT_ASSOCIATED",
                reason="NFC identifier belongs to another child's wearable",
                child_id=child.id,
                device_verified=False,
            )

        # Check NFC match against child wearable or recognized emergency badge
        valid_nfc_ids = {band.nfc_tag_id, "NIVARA-EMERGENCY-001", "NIVARA-EMERGENCY-SOS", band.serial_number, band.id}
        if band.nfc_tag_id and nfc_clean not in valid_nfc_ids:
            ev_rej = SafetyEvent(
                child_id=child.id,
                event_type="NFC_SOS_REJECTED",
                severity="warning",
                title="NFC Identifier Mismatch",
                description=f"NFC identifier '{nfc_clean}' does not match the child's assigned wearable.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata_json=json.dumps({"nfc_identifier": nfc_clean, "child_id": child.id}),
                is_acknowledged=False,
                created_at=now_utc,
            )
            self.db.add(ev_rej)
            self.db.commit()
            return NFCSOSTriggerResponse(
                triggered=False,
                status="NFC_INVALID",
                reason="NFC identifier does not match child wearable",
                child_id=child.id,
                device_verified=False,
            )

        # 5. Verify Wearable / Device Status (Online & Battery)
        is_device_online = (
            band.is_online
            and (band.connection_status in ["online", "connected"] or getattr(band, "bluetooth_connected", True))
            and (getattr(band, "battery_level", 100) > 0)
        )

        if not is_device_online:
            ev_rej = SafetyEvent(
                child_id=child.id,
                event_type="NFC_SOS_REJECTED",
                severity="warning",
                title="Wearable Offline During NFC SOS",
                description="Child wearable device is offline, disconnected, or has a depleted battery.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata_json=json.dumps({"nfc_identifier": nfc_clean, "child_id": child.id}),
                is_acknowledged=False,
                created_at=now_utc,
            )
            self.db.add(ev_rej)
            self.db.commit()
            return NFCSOSTriggerResponse(
                triggered=False,
                status="DEVICE_OFFLINE",
                reason="Wearable device is offline or disconnected",
                child_id=child.id,
                device_verified=False,
            )

        # 6. Determine GPS Location & Fallback to Last Known Location
        eval_lat = None
        eval_lon = None
        if data.latitude is not None and data.longitude is not None:
            eval_lat = data.latitude
            eval_lon = data.longitude
        else:
            latest_loc = (
                self.db.query(Location)
                .filter(Location.child_id == child.id)
                .order_by(desc(Location.recorded_at), desc(Location.created_at))
                .first()
            )
            if latest_loc:
                eval_lat = latest_loc.latitude
                eval_lon = latest_loc.longitude

        # 7. Invoke existing SOS trigger flow (EmergencyAlert + Caregiver Alert dispatch)
        sos_req = SOSTriggerRequest(
            child_id=child.id,
            latitude=eval_lat,
            longitude=eval_lon,
            message=f"Emergency SOS triggered via NFC ({nfc_clean})",
            description=f"Immediate assistance required. Triggered via NFC scan '{nfc_clean}'." + (f" Location: ({eval_lat}, {eval_lon})" if eval_lat is not None else " [Location Unavailable]"),
            triggered_by="nfc_emergency"
        )

        emergency_id = None
        try:
            res_sos = self.trigger_sos(data=sos_req, current_user=current_user)
            emergency_id = res_sos.id
        except HTTPException as e:
            if e.status_code == status.HTTP_409_CONFLICT:
                # Active emergency already in progress, maintain SOS_ACTIVE status
                active_emg = self.repo.get_active_by_child_id(child.id)
                if active_emg:
                    emergency_id = active_emg.id
            else:
                raise e

        # 8. Persist explicit NFC_SOS_TRIGGERED safety event
        nfc_event = SafetyEvent(
            child_id=child.id,
            event_type="NFC_SOS_TRIGGERED",
            severity="critical",
            title=f"NFC SOS TRIGGERED FOR {child.name.upper()}",
            description=f"Emergency SOS activated via NFC scan '{nfc_clean}'." + (f" Coordinates: ({eval_lat}, {eval_lon})" if eval_lat is not None else ""),
            latitude=eval_lat,
            longitude=eval_lon,
            metadata_json=json.dumps({
                "nfc_identifier": nfc_clean,
                "child_id": child.id,
                "caregiver_id": current_user.id,
                "emergency_id": emergency_id,
                "trigger_source": "NFC",
                "latitude": eval_lat,
                "longitude": eval_lon,
                "location_available": eval_lat is not None and eval_lon is not None,
                "timestamp": now_utc.isoformat(),
            }),
            is_acknowledged=False,
            created_at=now_utc,
        )
        self.db.add(nfc_event)
        self.db.commit()

        return NFCSOSTriggerResponse(
            triggered=True,
            status="SOS_ACTIVE",
            trigger_source="NFC",
            child_id=child.id,
            latitude=eval_lat,
            longitude=eval_lon,
            location_available=eval_lat is not None and eval_lon is not None,
            timestamp=now_utc,
            device_verified=True,
        )
