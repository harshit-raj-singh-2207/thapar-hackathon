import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.user import User
from app.models.device import Device
from app.models.location import Location
from app.models.safe_zone import SafeZone
from app.models.emergency_contact import EmergencyContact
from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent
from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences
from app.domains.safety.emergency_mode_repository import EmergencyModeRepository
from app.schemas.emergency_mode import (
    EmergencyModeCreate,
    EmergencyModeUpdate,
    EmergencyModeResponse,
    EmergencySupportPreferencesResponse,
    EmergencyDashboardSummaryResponse,
    SupportModuleStatus,
    NFCEmergencyCardResponse,
)

logger = logging.getLogger("safety.emergency_mode")

class EmergencyModeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmergencyModeRepository(db)

    def _verify_child_and_caregiver(self, child_id: str, current_user: User) -> Child:
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
                detail="Unauthorized: You do not have permission to access emergency mode for this child."
            )
        return child

    def _build_mode_response(self, mode: EmergencyMode) -> EmergencyModeResponse:
        """Helper to construct EmergencyModeResponse with dynamic status, expiration, and remaining days."""
        now = datetime.now(timezone.utc)
        start = mode.start_date
        end = mode.end_date

        if start and start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end and end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        is_expired = False
        days_remaining = 0

        if end:
            if now >= end:
                is_expired = True
                days_remaining = 0
            else:
                is_expired = False
                days_remaining = max(0, (end - now).days)

        if not mode.is_active or mode.status == "inactive":
            days_remaining = 0

        pref = (
            self.db.query(EmergencySupportPreferences)
            .filter(EmergencySupportPreferences.emergency_mode_id == mode.id)
            .first()
            or mode.preferences
        )
        if not pref:
            pref = EmergencySupportPreferences(
                emergency_mode_id=mode.id,
                communication_enabled=True,
                learning_enabled=True,
                emotion_support_enabled=True,
                emotional_support_enabled=True,
                games_enabled=True,
                safety_monitoring_enabled=True,
                caregiver_notifications_enabled=True,
            )
            self.db.add(pref)
            self.db.commit()
            self.db.refresh(pref)


        pref_response = EmergencySupportPreferencesResponse(
            id=pref.id,
            emergency_mode_id=pref.emergency_mode_id,
            communication_enabled=pref.communication_enabled,
            learning_enabled=pref.learning_enabled,
            emotional_support_enabled=pref.emotion_support_enabled if hasattr(pref, "emotion_support_enabled") else pref.emotional_support_enabled,
            games_enabled=pref.games_enabled,
            safety_monitoring_enabled=pref.safety_monitoring_enabled,
            caregiver_notifications_enabled=pref.caregiver_notifications_enabled,
            created_at=pref.created_at or now,
            updated_at=pref.updated_at or now,
        )

        return EmergencyModeResponse(
            id=mode.id,
            child_id=mode.child_id,
            caregiver_id=mode.caregiver_id,
            status=mode.status,
            emergency_type=mode.emergency_type or "pandemic_lockdown",
            is_active=mode.is_active and not is_expired and mode.status != "inactive",
            is_expired=is_expired,
            effective_status=mode.effective_status,
            start_date=start or now,
            end_date=end or (now + timedelta(days=mode.duration_days or 90)),
            duration_days=mode.duration_days or 90,
            days_remaining=days_remaining,
            reason=mode.reason or "Worldwide Pandemic Emergency - Physical Gathering Restrictions",
            preferences=pref_response,
            created_at=mode.created_at or now,
            updated_at=mode.updated_at or now,
        )

    def create_emergency_mode(self, data: EmergencyModeCreate, current_user: User) -> EmergencyModeResponse:
        """
        Create or reactivate 90-Day Emergency Support Mode for a child.
        """
        child = self._verify_child_and_caregiver(data.child_id, current_user)
        now = datetime.now(timezone.utc)

        start_date = data.start_date or now
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)

        duration_days = data.duration_days if data.duration_days is not None else 90
        if duration_days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid duration: duration_days must be greater than 0."
            )

        if data.end_date:
            end_date = data.end_date
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
            if end_date < start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid dates: end_date cannot be earlier than start_date."
                )
            duration_days = max(1, (end_date - start_date).days)
        else:
            end_date = start_date + timedelta(days=duration_days)

        pref_dict = data.preferences.model_dump() if data.preferences else {}
        existing = self.repo.get_by_child_id(child.id)

        try:
            if existing:
                update_fields = {
                    "caregiver_id": current_user.id,
                    "is_active": True,
                    "status": data.status or "active",
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_days": duration_days,
                }
                if data.reason:
                    update_fields["reason"] = data.reason
                if data.emergency_type:
                    update_fields["emergency_type"] = data.emergency_type

                updated_mode = self.repo.update(
                    mode=existing,
                    update_data=update_fields,
                    preferences_data=pref_dict,
                )
                return self._build_mode_response(updated_mode)
            else:
                new_mode = self.repo.create(
                    child_id=child.id,
                    caregiver_id=current_user.id,
                    start_date=start_date,
                    end_date=end_date,
                    duration_days=duration_days,
                    status=data.status or "active",
                    emergency_type=data.emergency_type or "pandemic_lockdown",
                    reason=data.reason or "Worldwide Pandemic Emergency - Physical Gathering Restrictions",
                    is_active=True,
                    preferences_data=pref_dict,
                )
                return self._build_mode_response(new_mode)

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating emergency mode: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while creating emergency mode: {str(e)}"
            )

    def get_emergency_mode(self, child_id: str, current_user: User) -> EmergencyModeResponse:
        """
        Retrieve emergency mode for a specific child.
        """
        child = self._verify_child_and_caregiver(child_id, current_user)
        mode = self.repo.get_by_child_id(child.id)
        if not mode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No emergency mode found for child '{child_id}'."
            )
        return self._build_mode_response(mode)

    def update_emergency_mode(self, child_id: str, data: EmergencyModeUpdate, current_user: User) -> EmergencyModeResponse:
        """
        Update emergency mode settings, duration, status or preferences.
        """
        child = self._verify_child_and_caregiver(child_id, current_user)
        mode = self.repo.get_by_child_id(child.id)
        if not mode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No emergency mode found for child '{child_id}'."
            )

        try:
            update_fields: Dict[str, Any] = {}
            if data.is_active is not None:
                update_fields["is_active"] = data.is_active
                if not data.is_active:
                    update_fields["status"] = "inactive"
                elif mode.status == "inactive":
                    update_fields["status"] = "active"

            if data.status is not None:
                update_fields["status"] = data.status
                if data.status == "inactive":
                    update_fields["is_active"] = False

            if data.reason is not None:
                update_fields["reason"] = data.reason

            if data.emergency_type is not None:
                update_fields["emergency_type"] = data.emergency_type

            # Handle date / duration updates
            start_date = data.start_date or mode.start_date
            if start_date and start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)

            if data.start_date:
                update_fields["start_date"] = start_date

            if data.end_date:
                end_date = data.end_date
                if end_date.tzinfo is None:
                    end_date = end_date.replace(tzinfo=timezone.utc)
                if end_date < start_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid dates: end_date cannot be earlier than start_date."
                    )
                update_fields["end_date"] = end_date
                update_fields["duration_days"] = max(1, (end_date - start_date).days)
            elif data.duration_days is not None:
                if data.duration_days <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid duration: duration_days must be greater than 0."
                    )
                update_fields["duration_days"] = data.duration_days
                update_fields["end_date"] = start_date + timedelta(days=data.duration_days)

            pref_data = data.preferences.model_dump(exclude_unset=True) if data.preferences else None
            updated_mode = self.repo.update(
                mode=mode,
                update_data=update_fields,
                preferences_data=pref_data,
            )
            return self._build_mode_response(updated_mode)

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating emergency mode: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error while updating emergency mode: {str(e)}"
            )

    def get_emergency_dashboard(self, child_id: str, current_user: User) -> EmergencyDashboardSummaryResponse:
        """
        Get full unified emergency dashboard summary for remote caregiver supervision.
        """
        child = self._verify_child_and_caregiver(child_id, current_user)
        mode = self.repo.get_by_child_id(child.id)

        mode_response = self._build_mode_response(mode) if mode else None
        is_mode_active = mode_response.is_active if mode_response else False

        contacts_count = (
            self.db.query(EmergencyContact)
            .filter(EmergencyContact.user_id == current_user.id)
            .count()
        )
        active_alerts_count = (
            self.db.query(SafetyEvent)
            .filter(SafetyEvent.child_id == child.id, SafetyEvent.is_acknowledged == False)
            .count()
        )
        active_emergency = (
            self.db.query(EmergencyAlert)
            .filter(EmergencyAlert.child_id == child.id, EmergencyAlert.status == "active")
            .first()
        )
        active_safe_zones = (
            self.db.query(SafeZone)
            .filter(SafeZone.child_id == child.id, SafeZone.is_active == True)
            .count()
        )

        pref = mode_response.preferences if mode_response else None

        comm_enabled = pref.communication_enabled if pref else True
        learning_enabled = pref.learning_enabled if pref else True
        games_enabled = pref.games_enabled if pref else True
        emotional_enabled = pref.emotional_support_enabled if pref else True
        safety_enabled = pref.safety_monitoring_enabled if pref else True
        notif_enabled = pref.caregiver_notifications_enabled if pref else True

        communication_status = SupportModuleStatus(
            status="ACTIVE" if comm_enabled else "DISABLED",
            enabled=comm_enabled,
            available_tools=[
                "High-Contrast AAC Grid",
                "Speech Text-to-Speech Engine",
                "Emotion Distress Express Cards",
                "AI Communication Phrase Predictor",
            ],
            details={"aac_ready": True, "voice_synthesis_ready": True},
        )

        learning_status = SupportModuleStatus(
            status="ACTIVE" if (learning_enabled and games_enabled) else ("PARTIAL" if learning_enabled else "DISABLED"),
            enabled=learning_enabled,
            available_tools=[
                "AI Personalized Tutor",
                "Home-Bound Visual Step Schedules",
                "Gamified Token Economy Rewards",
                "Cognitive Indoor Games",
            ],
            details={"tutor_ready": True, "routines_active": True, "games_enabled": games_enabled},
        )

        emotional_status = SupportModuleStatus(
            status="ACTIVE" if emotional_enabled else "DISABLED",
            enabled=emotional_enabled,
            available_tools=[
                "Real-Time Emotion Spectrum Check-In",
                "Sensory Calming Soundscapes",
                "Visual Guided Breathing Coach",
                "Preemptive Meltdown Detection",
            ],
            details={"soundscapes_active": True, "breathing_coach_ready": True},
        )

        # Query Device and Location telemetry for GPS and NFC status
        device = self.db.query(Device).filter(Device.child_id == child.id).first()
        latest_loc = (
            self.db.query(Location)
            .filter(Location.child_id == child.id)
            .order_by(Location.created_at.desc())
            .first()
        )

        # GPS Status Module
        gps_available = safety_enabled and (device is not None or latest_loc is not None)
        gps_status_module = SupportModuleStatus(
            status="ACTIVE" if (gps_available and device and device.is_online) else ("STANDBY" if gps_available else "OFFLINE"),
            enabled=safety_enabled,
            available_tools=[
                "Real-Time GPS Coordinates",
                "Home Isolation Boundary Monitoring",
                "Historical Location Breadcrumbs",
            ],
            details={
                "has_live_gps": latest_loc is not None,
                "latitude": latest_loc.latitude if latest_loc else None,
                "longitude": latest_loc.longitude if latest_loc else None,
                "accuracy": getattr(latest_loc, "accuracy", 5.0) if latest_loc else None,
                "last_location_time": latest_loc.created_at.isoformat() if latest_loc and latest_loc.created_at else None,
                "active_safe_zones_count": active_safe_zones,
            },
        )


        # NFC Wearable Device Status Module
        nfc_available = device is not None and device.is_active
        nfc_status_module = SupportModuleStatus(
            status="ACTIVE" if (nfc_available and device.is_online) else ("STANDBY" if nfc_available else "UNPAIRED"),
            enabled=nfc_available,
            available_tools=[
                "NFC Emergency Profile Pass",
                "Wearable Heartbeat Telemetry",
                "One-Touch NFC Identification",
            ],
            details={
                "device_id": device.id if device else None,
                "device_name": device.device_name if device else "Smart Safety Wearable",
                "device_identifier": device.device_identifier if device else None,
                "nfc_tag_id": device.nfc_tag_id if device else None,
                "is_online": device.is_online if device else False,
                "battery_level": device.battery_level if device else None,
            },
        )

        # SOS / Emergency Module Status
        sos_status_module = SupportModuleStatus(
            status="ALERT_ACTIVE" if active_emergency else "NORMAL",
            enabled=True,
            available_tools=[
                "Instant Panic SOS Button",
                "Multi-Channel Broadcast Dispatch",
                "Caregiver Acknowledgment Protocol",
            ],
            details={
                "has_active_emergency": active_emergency is not None,
                "active_emergency_id": active_emergency.id if active_emergency else None,
                "emergency_status": active_emergency.status if active_emergency else "normal",
                "emergency_type": getattr(active_emergency, "emergency_type", "sos") if active_emergency else None,
                "unacknowledged_alerts_count": active_alerts_count,
            },
        )

        # Games Status Module
        games_status_module = SupportModuleStatus(
            status="ACTIVE" if games_enabled else "DISABLED",
            enabled=games_enabled,
            available_tools=[
                "Cognitive Pattern Match",
                "Sensory Focus Color Sort",
                "Emotion Express Quiz",
                "Token Economy Star Rewards",
            ],
            details={
                "games_available_count": 8,
                "token_rewards_enabled": True,
                "daily_engagement_ready": games_enabled,
            },
        )

        # General Safety Status Module
        safety_status = SupportModuleStatus(
            status="ACTIVE" if safety_enabled else "DISABLED",
            enabled=safety_enabled,
            available_tools=[
                "SmartBand GPS & Live Location",
                "Home Isolation Perimeter Safe-Zone",
                "Wearable NFC Emergency Profile Pass",
                "Instant Multi-Guardian SOS Dispatch",
            ],
            details={
                "active_safe_zones": active_safe_zones,
                "has_active_emergency": active_emergency is not None,
                "current_child_status": child.current_status,
            },
        )

        # Caregiver Coordination & Notifications Module
        coordination_status = SupportModuleStatus(
            status="CONNECTED" if notif_enabled else "MUTED",
            enabled=notif_enabled,
            available_tools=[
                "Instant Push & Alert Cascades",
                "Emergency Contacts Broadcast",
                "Asynchronous Caregiver Telemetry Stream",
            ],
            details={
                "emergency_contacts_count": contacts_count,
                "unacknowledged_alerts": active_alerts_count,
                "notifications_active": notif_enabled,
            },
        )


        return EmergencyDashboardSummaryResponse(
            child_id=child.id,
            child_name=child.name,
            age=child.age,
            autism_level=child.autism_level,
            avatar_url=child.avatar_url,
            current_status=child.current_status or "safe",
            emergency_mode=mode_response,
            is_emergency_mode_active=is_mode_active,
            communication_support=communication_status,
            learning_support=learning_status,
            emotional_support=emotional_status,
            games_support=games_status_module,
            safety_support=safety_status,
            gps_status=gps_status_module,
            nfc_device_status=nfc_status_module,
            sos_emergency_status=sos_status_module,
            caregiver_coordination=coordination_status,
        )

    def get_nfc_emergency_card(self, nfc_tag_id: str) -> NFCEmergencyCardResponse:
        """
        Public/first-responder safe emergency identification card when child's NFC band is tapped.
        Does not require authentication to allow first responders or good samaritans to help,
        while strictly protecting sensitive GPS breadcrumbs/medical records and alerting the caregiver.
        """
        if not nfc_tag_id or not str(nfc_tag_id).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NFC tag identifier is required.",
            )
        nfc_clean = str(nfc_tag_id).strip()

        # Find device
        device = (
            self.db.query(Device)
            .filter(
                (Device.nfc_tag_id == nfc_clean)
                | (Device.device_identifier == nfc_clean)
                | (Device.serial_number == nfc_clean)
                | (Device.id == nfc_clean)
            )
            .first()
        )
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"NFC tag '{nfc_clean}' is not registered with any device.",
            )

        child = None
        caregiver = None
        emg_mode = None
        contacts_list = []

        if device.child_id:
            child = self.db.query(Child).filter(Child.id == device.child_id).first()
            if child:
                if child.caregiver_id:
                    caregiver = self.db.query(User).filter(User.id == child.caregiver_id).first()
                if child.emergency_mode:
                    emg_mode = child.emergency_mode

                # Fetch emergency contacts
                contacts = (
                    self.db.query(EmergencyContact)
                    .filter(EmergencyContact.child_id == child.id, EmergencyContact.is_active == True)
                    .order_by(EmergencyContact.priority_order.asc())
                    .all()
                )
                for c in contacts:
                    contacts_list.append({
                        "name": c.name,
                        "relationship": c.relationship_type or "Emergency Contact",
                        "phone_number": c.phone_number,
                        "is_primary": (c.priority_order == 1),
                    })

                # Log SafetyEvent to alert the caregiver
                try:
                    event = SafetyEvent(
                        child_id=child.id,
                        event_type="NFC_EMERGENCY_SCAN",
                        severity="info",
                        title="NFC Emergency Pass Scanned",
                        description=f"Child's NFC smart wearable ({device.device_name}) was tapped for emergency identification.",
                        is_acknowledged=False,
                    )
                    self.db.add(event)
                    self.db.commit()
                except Exception as ex:
                    logger.warning(f"Could not log NFC scan safety event: {ex}")
                    self.db.rollback()

        is_emg_active = (emg_mode.effective_status == "active") if emg_mode else False
        emg_status = emg_mode.effective_status if emg_mode else "normal"

        return NFCEmergencyCardResponse(
            nfc_tag_id=nfc_clean,
            band_id=device.device_identifier or device.serial_number or device.id,
            child_id=child.id if child else None,
            child_display_name=child.name if child else "Nivara Child",
            is_emergency_mode_active=is_emg_active,
            emergency_status=emg_status,
            caregiver_name=caregiver.full_name if caregiver else None,
            caregiver_phone=getattr(caregiver, "phone_number", None) or "+1 (555) 019-2834",
            emergency_contacts=contacts_list,
            safety_instructions="Child is autistic and may be sensitive to sensory overload. Please speak calmly, avoid sudden movements or loud noises, and contact the primary guardian immediately.",
            scanned_at=datetime.now(timezone.utc),
        )


