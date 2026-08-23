import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.child import Child
from app.models.safe_zone import SafeZone
from app.models.device import Device
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.schemas.safe_zone import (
    CheckpointCreate,
    CheckpointResponse,
    NFCGPSVerifyRequest,
    NFCGPSVerifyResponse,
)
from app.utils.distance import calculate_haversine_distance

logger = logging.getLogger("safety.smart_verification_service")

class SmartVerificationService:
    def __init__(self, db: Session):
        self.db = db

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
                detail="Unauthorized: You do not have permission to access or verify this child."
            )
        return child

    def _record_safety_event(
        self,
        child_id: str,
        event_type: str,
        title: str,
        description: str,
        severity: str = "info",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SafetyEvent:
        """Persist a safety event using the existing SafetyEvent model."""
        now_utc = datetime.now(timezone.utc)
        meta_str = json.dumps(metadata) if metadata else None

        event = SafetyEvent(
            child_id=child_id,
            event_type=event_type,
            severity=severity,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            metadata_json=meta_str,
            is_acknowledged=False,
            created_at=now_utc,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def create_checkpoint(self, data: CheckpointCreate, current_user: User) -> SafeZone:
        """
        Create a new NFC-enabled checkpoint / safe zone.
        Validates NFC uniqueness, coordinates, radius, and caregiver authorization.
        """
        nfc_clean = str(data.nfc_tag_id).strip()
        if not nfc_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NFC tag identifier is required and cannot be empty."
            )

        # Validate NFC ID uniqueness across checkpoints
        existing_nfc = self.db.query(SafeZone).filter(SafeZone.nfc_tag_id == nfc_clean).first()
        if existing_nfc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A checkpoint with NFC ID '{nfc_clean}' is already registered."
            )

        # Validate coordinates & radius
        if data.latitude < -90.0 or data.latitude > 90.0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Latitude must be between -90 and 90."
            )
        if data.longitude < -180.0 or data.longitude > 180.0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Longitude must be between -180 and 180."
            )
        if data.radius <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Radius must be greater than 0."
            )

        # If child_id provided, verify caregiver ownership
        child_id = None
        if data.child_id:
            child = self._verify_caregiver_authorization_for_child(data.child_id, current_user)
            child_id = child.id
        elif current_user.children:
            child_id = current_user.children[0].id

        now_utc = datetime.now(timezone.utc)
        checkpoint = SafeZone(
            child_id=child_id,
            name=data.name,
            nfc_tag_id=nfc_clean,
            status=data.status or "active",
            zone_type="circle",
            center_latitude=data.latitude,
            center_longitude=data.longitude,
            radius_meters=data.radius,
            address=data.address,
            is_active=data.is_active if data.is_active is not None else True,
            alert_on_exit=True,
            alert_on_enter=False,
            created_at=now_utc,
            updated_at=now_utc,
        )

        try:
            self.db.add(checkpoint)
            self.db.commit()
            self.db.refresh(checkpoint)
            return checkpoint
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating checkpoint: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating checkpoint."
            )

    def get_checkpoint(self, identifier: str, current_user: User) -> SafeZone:
        """Get a single checkpoint by ID or NFC tag."""
        checkpoint = (
            self.db.query(SafeZone)
            .filter((SafeZone.id == identifier) | (SafeZone.nfc_tag_id == identifier))
            .first()
        )
        if not checkpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Checkpoint with identifier '{identifier}' not found."
            )
        if checkpoint.child_id:
            self._verify_caregiver_authorization_for_child(checkpoint.child_id, current_user)
        return checkpoint

    def list_checkpoints(self, current_user: User) -> List[SafeZone]:
        """List all accessible checkpoints."""
        user_child_ids = [c.id for c in current_user.children]
        query = self.db.query(SafeZone).filter(SafeZone.nfc_tag_id.isnot(None))
        if user_child_ids and getattr(current_user, "role", None) != "admin":
            query = query.filter((SafeZone.child_id.in_(user_child_ids)) | (SafeZone.child_id.is_(None)))
        return query.order_by(SafeZone.created_at.desc()).all()

    def verify_nfc_gps(self, data: NFCGPSVerifyRequest, current_user: User) -> NFCGPSVerifyResponse:
        """
        Multi-signal Smart Safety Verification:
        Combines:
        1. NFC Checkpoint Identity
        2. Live GPS Coordinates & Distance Check
        3. Wearable Semiconductor Status (Battery, BLE, Online state)
        Generates: VERIFIED (SAFE) / LOCATION_MISMATCH / DEVICE_OFFLINE / UNKNOWN_NFC / FAILED
        """
        now_utc = datetime.now(timezone.utc)

        # 1. Verify Child & Caregiver Authorization
        child = self._verify_caregiver_authorization_for_child(data.child_id, current_user)

        # 2. Verify Wearable Band Existence & Association
        band = (
            self.db.query(Device)
            .filter(
                (Device.id == data.band_id)
                | (Device.serial_number == data.band_id)
                | (Device.device_identifier == data.band_id)
            )
            .first()
        )
        if not band:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wearable band with identifier '{data.band_id}' not found."
            )

        if band.child_id != child.id:
            # Band belongs to a different child
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="NFC_GPS_MISMATCH",
                severity="warning",
                title="Wearable Mismatch During Checkpoint Scan",
                description=f"Band '{data.band_id}' is not assigned to child '{child.name}'.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={"band_id": data.band_id, "child_id": child.id, "nfc_tag_id": data.nfc_tag_id}
            )
            return NFCGPSVerifyResponse(
                verified=False,
                status="FAILED",
                verification_type="NFC_GPS",
                child_id=child.id,
                child_name=child.name,
                band_id=data.band_id,
                reason=f"Band '{data.band_id}' does not belong to child '{child.name}'",
                safety_event_id=ev.id,
                timestamp=now_utc,
            )

        # 3. Verify NFC Checkpoint
        nfc_clean = str(data.nfc_tag_id).strip()
        checkpoint = self.db.query(SafeZone).filter(SafeZone.nfc_tag_id == nfc_clean).first()
        if not checkpoint:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="UNKNOWN_NFC",
                severity="warning",
                title="Unknown NFC Checkpoint Scanned",
                description=f"NFC tag '{nfc_clean}' is not recognized as a registered safety checkpoint.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={"band_id": data.band_id, "child_id": child.id, "nfc_tag_id": nfc_clean}
            )
            return NFCGPSVerifyResponse(
                verified=False,
                status="UNKNOWN_NFC",
                verification_type="NFC_GPS",
                child_id=child.id,
                child_name=child.name,
                band_id=band.device_identifier or band.serial_number or band.id,
                reason=f"NFC checkpoint '{nfc_clean}' is not registered",
                safety_event_id=ev.id,
                timestamp=now_utc,
            )

        # 4. Calculate Distance via Haversine formula
        dist_meters = calculate_haversine_distance(
            data.latitude,
            data.longitude,
            checkpoint.center_latitude,
            checkpoint.center_longitude,
        )
        is_inside_checkpoint = dist_meters <= checkpoint.radius_meters

        # 5. Device / Semiconductor State Verification
        is_device_online = band.is_online and (band.connection_status in ["online", "connected"] or band.bluetooth_connected)
        battery = band.battery_level if band.battery_level is not None else 100
        gps_enabled = band.gps_enabled if band.gps_enabled is not None else True
        bluetooth_connected = band.bluetooth_connected if band.bluetooth_connected is not None else True

        # Check Device Offline / Disconnected
        if not is_device_online or battery <= 0:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="DEVICE_OFFLINE",
                severity="warning",
                title="Device Offline During Checkpoint Scan",
                description=f"Wearable for child '{child.name}' is offline/disconnected during checkpoint scan at '{checkpoint.name}'.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={
                    "band_id": band.device_identifier or band.serial_number or band.id,
                    "checkpoint_id": checkpoint.id,
                    "distance_meters": round(dist_meters, 2),
                    "battery_level": battery,
                    "connection_status": band.connection_status,
                }
            )
            return NFCGPSVerifyResponse(
                verified=False,
                status="DEVICE_OFFLINE",
                verification_type="NFC_GPS",
                checkpoint_id=checkpoint.id,
                checkpoint_name=checkpoint.name,
                child_id=child.id,
                child_name=child.name,
                band_id=band.device_identifier or band.serial_number or band.id,
                distance_meters=round(dist_meters, 2),
                radius_meters=checkpoint.radius_meters,
                device_connected=False,
                battery_level=battery,
                gps_enabled=gps_enabled,
                bluetooth_connected=bluetooth_connected,
                reason="Wearable is offline or disconnected",
                safety_event_id=ev.id,
                timestamp=now_utc,
            )

        # Check GPS Proximity Mismatch
        if not is_inside_checkpoint:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="NFC_GPS_MISMATCH",
                severity="warning",
                title=f"NFC + GPS Location Mismatch: {checkpoint.name}",
                description=f"NFC scanned at {checkpoint.name}, but GPS position is {round(dist_meters, 1)}m away (outside {checkpoint.radius_meters}m radius).",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={
                    "band_id": band.device_identifier or band.serial_number or band.id,
                    "checkpoint_id": checkpoint.id,
                    "distance_meters": round(dist_meters, 2),
                    "radius_meters": checkpoint.radius_meters,
                    "battery_level": battery,
                }
            )
            return NFCGPSVerifyResponse(
                verified=False,
                status="LOCATION_MISMATCH",
                verification_type="NFC_GPS",
                checkpoint_id=checkpoint.id,
                checkpoint_name=checkpoint.name,
                child_id=child.id,
                child_name=child.name,
                band_id=band.device_identifier or band.serial_number or band.id,
                distance_meters=round(dist_meters, 2),
                radius_meters=checkpoint.radius_meters,
                device_connected=True,
                battery_level=battery,
                gps_enabled=gps_enabled,
                bluetooth_connected=bluetooth_connected,
                reason="NFC checkpoint and GPS location do not match",
                safety_event_id=ev.id,
                timestamp=now_utc,
            )

        # 6. Success: All 3 signals (NFC + Proximity + Device Status) Verified
        ev = self._record_safety_event(
            child_id=child.id,
            event_type="NFC_GPS_VERIFIED",
            severity="info",
            title=f"NFC Checkpoint Verified: {checkpoint.name}",
            description=f"Child {child.name} safely verified at {checkpoint.name} ({round(dist_meters, 1)}m away). Wearable is active with {battery}% battery.",
            latitude=data.latitude,
            longitude=data.longitude,
            metadata={
                "band_id": band.device_identifier or band.serial_number or band.id,
                "checkpoint_id": checkpoint.id,
                "distance_meters": round(dist_meters, 2),
                "battery_level": battery,
            }
        )

        return NFCGPSVerifyResponse(
            verified=True,
            status="SAFE",
            verification_type="NFC_GPS",
            checkpoint_id=checkpoint.id,
            checkpoint_name=checkpoint.name,
            child_id=child.id,
            child_name=child.name,
            band_id=band.device_identifier or band.serial_number or band.id,
            distance_meters=round(dist_meters, 2),
            radius_meters=checkpoint.radius_meters,
            device_connected=True,
            battery_level=battery,
            gps_enabled=gps_enabled,
            bluetooth_connected=bluetooth_connected,
            reason=None,
            safety_event_id=ev.id,
            timestamp=now_utc,
        )
