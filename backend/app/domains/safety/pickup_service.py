import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.child import Child
from app.models.caregiver_nfc import CaregiverNFC
from app.models.safe_zone import SafeZone
from app.models.device import Device
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.schemas.pickup import (
    CaregiverNFCRegisterRequest,
    CaregiverNFCResponse,
    PickupVerifyRequest,
    PickupVerifyResponse,
)
from app.utils.distance import calculate_haversine_distance

logger = logging.getLogger("safety.pickup_service")

class CaregiverPickupService:
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
                detail="Unauthorized: You do not have permission for this child."
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

    def register_caregiver_nfc(self, data: CaregiverNFCRegisterRequest, current_user: User) -> CaregiverNFC:
        """
        Register a unique NFC badge identifier for an authorized caregiver & child pair.
        """
        child = self._verify_caregiver_authorization_for_child(data.child_id, current_user)
        nfc_clean = str(data.nfc_identifier).strip()
        if not nfc_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Caregiver NFC identifier is required and cannot be empty."
            )

        # Check uniqueness across existing caregiver NFC registrations
        existing = self.db.query(CaregiverNFC).filter(CaregiverNFC.nfc_identifier == nfc_clean).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A caregiver NFC credential with identifier '{nfc_clean}' is already registered."
            )

        now_utc = datetime.now(timezone.utc)
        record = CaregiverNFC(
            caregiver_id=current_user.id,
            child_id=child.id,
            nfc_identifier=nfc_clean,
            status=data.status or "active",
            created_at=now_utc,
            updated_at=now_utc,
        )

        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error registering caregiver NFC: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while registering caregiver NFC."
            )

    def verify_pickup(self, data: PickupVerifyRequest, current_user: User) -> PickupVerifyResponse:
        """
        Verify caregiver pickup combining:
        1. NFC identity & credential validity
        2. Authorized caregiver check
        3. Correct child association
        4. GPS proximity to allowed pickup zone
        5. Wearable / semiconductor status
        """
        now_utc = datetime.now(timezone.utc)

        # 1. Verify Child & Caregiver Authorization
        child = self._verify_caregiver_authorization_for_child(data.child_id, current_user)

        # 2. Verify NFC Credential
        nfc_clean = str(data.nfc_identifier).strip()
        nfc_auth = self.db.query(CaregiverNFC).filter(CaregiverNFC.nfc_identifier == nfc_clean).first()

        if not nfc_auth:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="UNKNOWN_CAREGIVER_NFC",
                severity="warning",
                title="Unknown Caregiver NFC Scanned",
                description=f"NFC credential '{nfc_clean}' is not registered.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={"nfc_identifier": nfc_clean, "child_id": child.id}
            )
            return PickupVerifyResponse(
                verified=False,
                status="PICKUP_REJECTED",
                reason="NFC identifier not registered",
                child_id=child.id,
                child_name=child.name,
                caregiver_id=current_user.id,
                caregiver_name=current_user.full_name,
                nfc_identifier=nfc_clean,
                timestamp=now_utc,
                safety_event_id=ev.id,
            )

        if nfc_auth.caregiver_id != current_user.id:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="PICKUP_REJECTED",
                severity="warning",
                title="Unauthorized Caregiver NFC Attempt",
                description=f"NFC credential '{nfc_clean}' belongs to another caregiver.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={"nfc_identifier": nfc_clean, "child_id": child.id}
            )
            return PickupVerifyResponse(
                verified=False,
                status="PICKUP_REJECTED",
                reason="Caregiver is not authorized",
                child_id=child.id,
                child_name=child.name,
                caregiver_id=current_user.id,
                caregiver_name=current_user.full_name,
                nfc_identifier=nfc_clean,
                timestamp=now_utc,
                safety_event_id=ev.id,
            )

        if nfc_auth.child_id != child.id:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="PICKUP_REJECTED",
                severity="warning",
                title="Wrong Child Pickup Attempt",
                description=f"NFC credential is not authorized for child '{child.name}'.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={"nfc_identifier": nfc_clean, "child_id": child.id}
            )
            return PickupVerifyResponse(
                verified=False,
                status="PICKUP_REJECTED",
                reason="NFC identifier is not authorized for this child",
                child_id=child.id,
                child_name=child.name,
                caregiver_id=current_user.id,
                caregiver_name=current_user.full_name,
                nfc_identifier=nfc_clean,
                timestamp=now_utc,
                safety_event_id=ev.id,
            )

        if nfc_auth.status != "active":
            return PickupVerifyResponse(
                verified=False,
                status="PICKUP_REJECTED",
                reason="Caregiver NFC credential is not active",
                child_id=child.id,
                child_name=child.name,
                caregiver_id=current_user.id,
                caregiver_name=current_user.full_name,
                nfc_identifier=nfc_clean,
                timestamp=now_utc,
            )

        # 3. GPS Proximity Check (against active safe zones or checkpoints)
        safe_zones = self.db.query(SafeZone).filter(
            (SafeZone.child_id == child.id) | (SafeZone.child_id.is_(None)),
            SafeZone.is_active == True
        ).all()

        within_pickup_zone = False
        min_dist = float("inf")

        for zone in safe_zones:
            d = calculate_haversine_distance(
                data.latitude,
                data.longitude,
                zone.center_latitude,
                zone.center_longitude,
            )
            if d < min_dist:
                min_dist = d
            if d <= max(zone.radius_meters, 250.0):
                within_pickup_zone = True
                break

        if not within_pickup_zone and safe_zones:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="LOCATION_MISMATCH",
                severity="warning",
                title="Caregiver Pickup Location Mismatch",
                description=f"Caregiver GPS position is {round(min_dist, 1)}m away from authorized pickup zones.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={
                    "nfc_identifier": nfc_clean,
                    "child_id": child.id,
                    "distance_meters": round(min_dist, 1),
                }
            )
            return PickupVerifyResponse(
                verified=False,
                status="LOCATION_MISMATCH",
                reason="Caregiver GPS is outside the allowed pickup location",
                child_id=child.id,
                child_name=child.name,
                caregiver_id=current_user.id,
                caregiver_name=current_user.full_name,
                nfc_identifier=nfc_clean,
                location_verified=False,
                timestamp=now_utc,
                safety_event_id=ev.id,
            )

        # 4. Wearable / Semiconductor Status Check
        band = self.db.query(Device).filter(Device.child_id == child.id, Device.is_active == True).first()
        is_device_online = (
            (band is not None)
            and band.is_online
            and (band.connection_status in ["online", "connected"] or getattr(band, "bluetooth_connected", True))
            and (getattr(band, "battery_level", 100) > 0)
        )

        if not is_device_online:
            ev = self._record_safety_event(
                child_id=child.id,
                event_type="DEVICE_OFFLINE",
                severity="warning",
                title="Child Device Offline During Pickup",
                description=f"Child wearable is offline or disconnected during pickup verification.",
                latitude=data.latitude,
                longitude=data.longitude,
                metadata={"nfc_identifier": nfc_clean, "child_id": child.id}
            )
            return PickupVerifyResponse(
                verified=False,
                status="DEVICE_OFFLINE",
                reason="Child wearable is offline or disconnected",
                child_id=child.id,
                child_name=child.name,
                caregiver_id=current_user.id,
                caregiver_name=current_user.full_name,
                nfc_identifier=nfc_clean,
                location_verified=True,
                device_verified=False,
                timestamp=now_utc,
                safety_event_id=ev.id,
            )

        # 5. Success: Verified
        nfc_auth.last_pickup_at = now_utc
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()

        ev = self._record_safety_event(
            child_id=child.id,
            event_type="PICKUP_VERIFIED",
            severity="info",
            title="Caregiver Pickup Verified",
            description=f"Caregiver {current_user.full_name} successfully verified pickup for {child.name}.",
            latitude=data.latitude,
            longitude=data.longitude,
            metadata={
                "nfc_identifier": nfc_clean,
                "child_id": child.id,
                "caregiver_id": current_user.id,
            }
        )

        return PickupVerifyResponse(
            verified=True,
            status="PICKUP_VERIFIED",
            child_id=child.id,
            child_name=child.name,
            caregiver_id=current_user.id,
            caregiver_name=current_user.full_name,
            nfc_identifier=nfc_clean,
            location_verified=True,
            device_verified=True,
            reason=None,
            timestamp=now_utc,
            safety_event_id=ev.id,
        )
