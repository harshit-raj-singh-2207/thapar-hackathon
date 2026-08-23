from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences

class EmergencyModeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, mode_id: str) -> Optional[EmergencyMode]:
        """Fetch emergency mode by primary key ID."""
        return self.db.query(EmergencyMode).filter(EmergencyMode.id == mode_id).first()

    def get_by_child_id(self, child_id: str) -> Optional[EmergencyMode]:
        """Fetch emergency mode for a specific child."""
        return self.db.query(EmergencyMode).filter(EmergencyMode.child_id == child_id).first()

    def create(
        self,
        child_id: str,
        caregiver_id: str,
        start_date: datetime,
        end_date: datetime,
        duration_days: int = 90,
        status: str = "active",
        emergency_type: str = "pandemic_lockdown",
        reason: str = "Worldwide Pandemic Emergency - Physical Gathering Restrictions",
        is_active: bool = True,
        preferences_data: Optional[Dict[str, Any]] = None,
    ) -> EmergencyMode:
        """Create new emergency mode and child support preferences."""
        now_utc = datetime.now(timezone.utc)
        mode = EmergencyMode(
            child_id=child_id,
            caregiver_id=caregiver_id,
            status=status,
            emergency_type=emergency_type,
            reason=reason,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            is_active=is_active,
            created_at=now_utc,
            updated_at=now_utc,
        )
        self.db.add(mode)
        self.db.flush()

        pref_kwargs = preferences_data or {}
        pref = EmergencySupportPreferences(
            emergency_mode_id=mode.id,
            communication_enabled=pref_kwargs.get("communication_enabled", True),
            learning_enabled=pref_kwargs.get("learning_enabled", True),
            emotion_support_enabled=pref_kwargs.get(
                "emotion_support_enabled",
                pref_kwargs.get("emotional_support_enabled", True),
            ),
            emotional_support_enabled=pref_kwargs.get(
                "emotional_support_enabled",
                pref_kwargs.get("emotion_support_enabled", True),
            ),
            games_enabled=pref_kwargs.get("games_enabled", True),
            safety_monitoring_enabled=pref_kwargs.get("safety_monitoring_enabled", True),
            caregiver_notifications_enabled=pref_kwargs.get("caregiver_notifications_enabled", True),
            created_at=now_utc,
            updated_at=now_utc,
        )
        self.db.add(pref)
        self.db.commit()
        self.db.refresh(mode)
        return mode

    def update(
        self,
        mode: EmergencyMode,
        update_data: Dict[str, Any],
        preferences_data: Optional[Dict[str, Any]] = None,
    ) -> EmergencyMode:
        """Update existing emergency mode and preferences."""
        now_utc = datetime.now(timezone.utc)
        for key, value in update_data.items():
            if value is not None and hasattr(mode, key):
                setattr(mode, key, value)
        mode.updated_at = now_utc

        if preferences_data:
            pref = (
                self.db.query(EmergencySupportPreferences)
                .filter(EmergencySupportPreferences.emergency_mode_id == mode.id)
                .first()
            )
            if not pref:
                pref = EmergencySupportPreferences(
                    emergency_mode_id=mode.id,
                    created_at=now_utc,
                    updated_at=now_utc,
                )
                self.db.add(pref)

            for p_key, p_val in preferences_data.items():
                if p_val is not None:
                    if hasattr(pref, p_key):
                        setattr(pref, p_key, p_val)
                    if p_key == "emotion_support_enabled":
                        pref.emotional_support_enabled = p_val
                    elif p_key == "emotional_support_enabled":
                        pref.emotion_support_enabled = p_val
            pref.updated_at = now_utc
            self.db.add(pref)
            mode.preferences = pref

        self.db.commit()
        self.db.refresh(mode)
        return mode



    def delete(self, mode: EmergencyMode) -> None:
        """Delete an emergency mode record."""
        self.db.delete(mode)
        self.db.commit()
