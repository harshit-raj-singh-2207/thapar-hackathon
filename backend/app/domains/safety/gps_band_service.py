import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.device import Device
from app.models.child import Child
from app.models.user import User
from app.schemas.device import (
    BandCreate,
    BandUpdate,
    BandStatusResponse,
    BandPairResponse,
    BandUnpairResponse,
    BandHeartbeatRequest,
    BandHeartbeatResponse,
    BandConnectionResponse,
    BandSyncRequest,
    BandSyncResponse,
)

logger = logging.getLogger("safety.gps_band_service")

class GPSBandService:
    def __init__(self, db: Session):
        self.db = db

    def _verify_caregiver_authorization_for_child(self, child_id: str, current_user: User) -> Child:
        """Verify child exists and current authenticated user is authorized caregiver."""
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child with ID '{child_id}' not found."
            )
        if child.caregiver_id != current_user.id and getattr(current_user, "role", None) != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: You do not have permission to manage devices for this child."
            )
        return child

    def _verify_device_authorization(self, device: Device, current_user: User):
        """Verify user is authorized to view or manage this device."""
        if device.child_id:
            child = self.db.query(Child).filter(Child.id == device.child_id).first()
            if child and child.caregiver_id != current_user.id and getattr(current_user, "role", None) != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized: You do not have permission to manage this band."
                )

    def _get_band_or_404(self, band_id: str) -> Device:
        """Retrieve band by primary key id or serial/device_identifier."""
        band = self.db.query(Device).filter(Device.id == band_id).first()
        if not band:
            band = (
                self.db.query(Device)
                .filter((Device.serial_number == band_id) | (Device.device_identifier == band_id))
                .first()
            )
        if not band:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GPS band with ID '{band_id}' not found."
            )
        return band

    def register_band(self, data: BandCreate, current_user: User) -> Device:
        """
        Register a new GPS band and optionally assign to a child.
        Prevents duplicate serial number/identifier and duplicate child assignment.
        """
        ident = data.device_identifier or data.serial_number
        if not ident:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device identifier or serial number is required."
            )

        # Check for existing device with same identifier
        existing = (
            self.db.query(Device)
            .filter((Device.serial_number == ident) | (Device.device_identifier == ident))
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A band with device identifier '{ident}' is already registered."
            )

        # If child_id provided, verify child ownership & duplicate assignment
        if data.child_id:
            child = self._verify_caregiver_authorization_for_child(data.child_id, current_user)
            # Check if this child already has an active band
            assigned_band = (
                self.db.query(Device)
                .filter(Device.child_id == child.id, Device.is_active == True)
                .first()
            )
            if assigned_band:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Child '{child.name}' already has an active band ({assigned_band.id}) assigned."
                )

        now_utc = datetime.now(timezone.utc)
        conn_status = data.connection_status or ("online" if data.is_online else "offline")
        is_online = data.is_online if data.is_online is not None else (conn_status in ["online", "connected"])

        band = Device(
            child_id=data.child_id,
            device_name=data.device_name or "GPS Safety Band",
            device_type=data.device_type or "gps_band",
            serial_number=ident,
            device_identifier=ident,
            battery_level=data.battery_level if data.battery_level is not None else 100,
            connection_status=conn_status,
            gps_status=data.gps_status or "active",
            is_active=True,
            is_online=is_online,
            firmware_version=data.firmware_version or "v1.2.0",
            last_seen=now_utc,
            last_ping_at=now_utc,
            created_at=now_utc,
            updated_at=now_utc,
        )

        try:
            self.db.add(band)
            self.db.commit()
            self.db.refresh(band)
            return band
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error registering band {ident}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while registering the GPS band."
            )

    def get_band_by_identifier(self, identifier: str, current_user: User) -> Device:
        """
        Retrieve band by band_id or child_id.
        Intelligently resolves identifier to either a band ID or a child's assigned band.
        """
        # 1. Try finding Device by primary key id
        band = self.db.query(Device).filter(Device.id == identifier).first()
        if band:
            self._verify_device_authorization(band, current_user)
            return band

        # 2. Try finding Device by serial_number or device_identifier
        band = (
            self.db.query(Device)
            .filter((Device.serial_number == identifier) | (Device.device_identifier == identifier))
            .first()
        )
        if band:
            self._verify_device_authorization(band, current_user)
            return band

        # 3. Try finding Child by identifier and get child's band
        child = self.db.query(Child).filter(Child.id == identifier).first()
        if child:
            self._verify_caregiver_authorization_for_child(child.id, current_user)
            child_band = (
                self.db.query(Device)
                .filter(Device.child_id == child.id)
                .order_by(Device.created_at.desc())
                .first()
            )
            if not child_band:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No band currently assigned to child '{child.id}'."
                )
            return child_band

        # 4. Not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GPS band or child with ID '{identifier}' not found."
        )

    def get_child_band(self, child_id: str, current_user: User) -> Device:
        """Retrieve band assigned to a specific child."""
        child = self._verify_caregiver_authorization_for_child(child_id, current_user)
        band = (
            self.db.query(Device)
            .filter(Device.child_id == child.id)
            .order_by(Device.created_at.desc())
            .first()
        )
        if not band:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No band found for child '{child_id}'."
            )
        return band

    def get_band_status(self, band_id: str, current_user: User) -> BandStatusResponse:
        """Retrieve status, battery level, connection status, and last seen for a band."""
        band = self.get_band_by_identifier(band_id, current_user)
        conn_status = band.connection_status or ("online" if band.is_online else "offline")
        last_seen_time = band.last_seen or band.last_ping_at or band.created_at

        return BandStatusResponse(
            band_id=band.id,
            device_identifier=band.device_identifier or band.serial_number,
            child_id=band.child_id,
            connection_status=conn_status,
            is_online=band.is_online if band.is_online is not None else (conn_status in ["online", "connected"]),
            battery_level=band.battery_level if band.battery_level is not None else 100,
            gps_status=band.gps_status or "active",
            last_seen=last_seen_time,
            updated_at=band.updated_at or band.created_at,
        )

    def update_band(self, band_id: str, data: BandUpdate, current_user: User) -> Device:
        """
        Update band configuration, status, or child assignment.
        """
        band = self._get_band_or_404(band_id)
        self._verify_device_authorization(band, current_user)

        # Handle child re-assignment
        if data.child_id is not None:
            if data.child_id == "" or data.child_id.lower() == "none":
                band.child_id = None
            elif data.child_id != band.child_id:
                # Verify new child
                new_child = self._verify_caregiver_authorization_for_child(data.child_id, current_user)
                # Check if new child already has another band
                existing_assigned = (
                    self.db.query(Device)
                    .filter(Device.child_id == new_child.id, Device.id != band.id, Device.is_active == True)
                    .first()
                )
                if existing_assigned:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Child '{new_child.name}' already has a band ({existing_assigned.id}) assigned."
                    )
                band.child_id = new_child.id

        if data.device_name is not None:
            band.device_name = data.device_name
        if data.device_type is not None:
            band.device_type = data.device_type
        if data.battery_level is not None:
            band.battery_level = data.battery_level
        if data.connection_status is not None:
            band.connection_status = data.connection_status
            band.is_online = data.connection_status in ["online", "connected"]
        if data.is_online is not None:
            band.is_online = data.is_online
            band.connection_status = "online" if data.is_online else "offline"
        if data.gps_status is not None:
            band.gps_status = data.gps_status
        if data.is_active is not None:
            band.is_active = data.is_active
        if data.firmware_version is not None:
            band.firmware_version = data.firmware_version

        now_utc = datetime.now(timezone.utc)
        band.last_seen = now_utc
        band.last_ping_at = now_utc
        band.updated_at = now_utc

        try:
            self.db.commit()
            self.db.refresh(band)
            return band
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating band {band_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating the GPS band."
            )

    def remove_band(self, band_id: str, current_user: User) -> Dict[str, Any]:
        """Remove/delete a band."""
        band = self._get_band_or_404(band_id)
        self._verify_device_authorization(band, current_user)

        try:
            self.db.delete(band)
            self.db.commit()
            return {"message": "GPS band removed successfully.", "band_id": band_id}
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error removing band {band_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while removing the GPS band."
            )

    # Phone ↔ Band Connection Management Operations

    def pair_band(self, band_id: str, child_id: str, current_user: User) -> BandPairResponse:
        """
        Pair band to a child and mark connection status as connected.
        Validates child authorization and prevents duplicate pairing.
        """
        band = self._get_band_or_404(band_id)
        self._verify_device_authorization(band, current_user)

        child = self._verify_caregiver_authorization_for_child(child_id, current_user)

        # Check if band is already paired to this child
        if band.child_id == child.id and band.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This band is already paired with this child."
            )

        # Check if child is already paired with another band
        existing_band = (
            self.db.query(Device)
            .filter(Device.child_id == child.id, Device.id != band.id, Device.is_active == True)
            .first()
        )
        if existing_band:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Child '{child.name}' is already paired with another band ({existing_band.id}). Unpair it first."
            )

        now_utc = datetime.now(timezone.utc)
        band.child_id = child.id
        band.is_active = True
        band.connection_status = "connected"
        band.is_online = True
        band.last_seen = now_utc
        band.last_ping_at = now_utc
        band.updated_at = now_utc

        try:
            self.db.commit()
            self.db.refresh(band)
            return BandPairResponse(
                band_id=band.id,
                child_id=child.id,
                device_identifier=band.device_identifier or band.serial_number,
                connection_status=band.connection_status,
                is_paired=True,
                paired_at=now_utc,
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error pairing band {band_id} to child {child_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while pairing the band."
            )

    def unpair_band(self, band_id: str, current_user: User) -> BandUnpairResponse:
        """
        Unpair band from its current child and update connection status.
        """
        band = self._get_band_or_404(band_id)
        self._verify_device_authorization(band, current_user)

        now_utc = datetime.now(timezone.utc)
        band.child_id = None
        band.connection_status = "disconnected"
        band.is_online = False
        band.last_seen = now_utc
        band.last_ping_at = now_utc
        band.updated_at = now_utc

        try:
            self.db.commit()
            self.db.refresh(band)
            return BandUnpairResponse(
                band_id=band.id,
                device_identifier=band.device_identifier or band.serial_number,
                connection_status="disconnected",
                is_paired=False,
                unpaired_at=now_utc,
                message="Band successfully unpaired.",
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error unpairing band {band_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while unpairing the band."
            )

    def process_heartbeat(
        self,
        band_id: str,
        data: BandHeartbeatRequest,
        current_user: User,
    ) -> BandHeartbeatResponse:
        """
        Process heartbeat telemetry from mobile app:
        - Updates connection status
        - Updates battery level
        - Updates GPS status
        - Updates last_seen timestamp
        """
        band = self._get_band_or_404(band_id)
        self._verify_device_authorization(band, current_user)

        if data.battery_level < 0 or data.battery_level > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Battery level must be between 0 and 100 percent."
            )

        now_utc = datetime.now(timezone.utc)
        conn_status = data.connection_status or "connected"
        is_online = data.is_online if data.is_online is not None else (conn_status in ["connected", "online"])

        band.battery_level = data.battery_level
        band.connection_status = conn_status
        band.is_online = is_online
        band.gps_status = data.gps_status or "active"
        band.last_seen = now_utc
        band.last_ping_at = now_utc
        band.updated_at = now_utc

        if data.firmware_version:
            band.firmware_version = data.firmware_version

        try:
            self.db.commit()
            self.db.refresh(band)
            return BandHeartbeatResponse(
                band_id=band.id,
                device_identifier=band.device_identifier or band.serial_number,
                child_id=band.child_id,
                connection_status=band.connection_status,
                is_online=band.is_online,
                battery_level=band.battery_level,
                gps_status=band.gps_status,
                last_seen=band.last_seen,
                is_stale=False,
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during heartbeat for band {band_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while processing device heartbeat."
            )

    def get_connection_status(
        self,
        band_id: str,
        current_user: User,
        stale_threshold_seconds: int = 120,
    ) -> BandConnectionResponse:
        """
        Get current connection status, battery, GPS status, and check staleness.
        """
        band = self._get_band_or_404(band_id)
        self._verify_device_authorization(band, current_user)

        now_utc = datetime.now(timezone.utc)
        last_seen_time = band.last_seen or band.last_ping_at or band.created_at

        # Calculate if stale based on time elapsed since last_seen
        diff_sec = (now_utc - (last_seen_time if last_seen_time.tzinfo else last_seen_time.replace(tzinfo=timezone.utc))).total_seconds()
        is_stale = diff_sec > stale_threshold_seconds

        conn_status = band.connection_status or ("online" if band.is_online else "offline")
        if is_stale and conn_status in ["connected", "online"]:
            conn_status = "stale"

        return BandConnectionResponse(
            band_id=band.id,
            device_identifier=band.device_identifier or band.serial_number,
            is_paired=band.child_id is not None and band.is_active,
            child_id=band.child_id,
            connection_status=conn_status,
            is_online=band.is_online and not is_stale,
            battery_level=band.battery_level if band.battery_level is not None else 100,
            gps_status=band.gps_status or "active",
            last_seen=last_seen_time,
            is_stale=is_stale,
            updated_at=band.updated_at or band.created_at,
        )

    def sync_band(
        self,
        band_id: str,
        data: BandSyncRequest,
        current_user: User,
    ) -> BandSyncResponse:
        """
        Synchronize device settings and refresh device synchronization state.
        """
        band = self._get_band_or_404(band_id)
        self._verify_device_authorization(band, current_user)

        now_utc = datetime.now(timezone.utc)
        band.last_seen = now_utc
        band.last_ping_at = now_utc
        band.updated_at = now_utc

        try:
            self.db.commit()
            self.db.refresh(band)
            return BandSyncResponse(
                band_id=band.id,
                synced=True,
                server_timestamp=now_utc,
                connection_status=band.connection_status or "connected",
                battery_level=band.battery_level if band.battery_level is not None else 100,
                gps_status=band.gps_status or "active",
                settings=data.settings,
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error syncing band {band_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while synchronizing band."
            )
