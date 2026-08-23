import os
import sys
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.child import Child
from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences, VALID_EMERGENCY_STATUSES

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_emergency_mode_model_creation_and_persistence(db_session: Session):
    # Fetch existing seed user and child
    sarah = db_session.query(User).filter(User.email == "sarah@nivara.app").first()
    child = db_session.query(Child).filter(Child.caregiver_id == sarah.id).first()

    assert sarah is not None
    assert child is not None

    # Clean any existing mode for fresh test
    existing = db_session.query(EmergencyMode).filter(EmergencyMode.child_id == child.id).first()
    if existing:
        db_session.delete(existing)
        db_session.commit()

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=90)

    mode = EmergencyMode(
        child_id=child.id,
        caregiver_id=sarah.id,
        status="active",
        emergency_type="pandemic_lockdown",
        reason="90-Day Nationwide Physical Gathering Restrictions",
        start_date=now,
        end_date=end,
        duration_days=90,
        is_active=True,
    )
    db_session.add(mode)
    db_session.commit()
    db_session.refresh(mode)

    assert mode.id.startswith("emg-mode-")
    assert mode.child_id == child.id
    assert mode.caregiver_id == sarah.id
    assert mode.status == "active"
    assert mode.emergency_type == "pandemic_lockdown"
    assert mode.reason == "90-Day Nationwide Physical Gathering Restrictions"
    assert mode.duration_days == 90
    assert mode.effective_status == "active"
    assert mode.days_remaining >= 89
    assert mode.created_at is not None
    assert mode.updated_at is not None


def test_emergency_mode_statuses_and_validation(db_session: Session):
    sarah = db_session.query(User).filter(User.email == "sarah@nivara.app").first()
    child = db_session.query(Child).filter(Child.caregiver_id == sarah.id).first()

    # Clean existing
    db_session.query(EmergencyMode).filter(EmergencyMode.child_id == child.id).delete()
    db_session.commit()

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=90)

    # Test all 4 valid statuses
    for valid_status in ["scheduled", "active", "expired", "inactive"]:
        mode = EmergencyMode(
            child_id=child.id,
            caregiver_id=sarah.id,
            status=valid_status,
            start_date=now,
            end_date=end,
        )
        db_session.add(mode)
        db_session.commit()
        db_session.refresh(mode)
        assert mode.status == valid_status
        db_session.delete(mode)
        db_session.commit()

    # Test invalid status validation raises ValueError
    with pytest.raises(ValueError) as exc:
        invalid_mode = EmergencyMode(
            child_id=child.id,
            caregiver_id=sarah.id,
            status="invalid_status_xyz",
            start_date=now,
            end_date=end,
        )
    assert "Invalid status" in str(exc.value)


def test_emergency_support_preferences_model(db_session: Session):
    sarah = db_session.query(User).filter(User.email == "sarah@nivara.app").first()
    child = db_session.query(Child).filter(Child.caregiver_id == sarah.id).first()

    db_session.query(EmergencyMode).filter(EmergencyMode.child_id == child.id).delete()
    db_session.commit()

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=90)

    mode = EmergencyMode(
        child_id=child.id,
        caregiver_id=sarah.id,
        status="active",
        start_date=now,
        end_date=end,
    )
    db_session.add(mode)
    db_session.flush()

    pref = EmergencySupportPreferences(
        emergency_mode_id=mode.id,
        communication_enabled=True,
        learning_enabled=True,
        emotion_support_enabled=True,
        games_enabled=False,
        safety_monitoring_enabled=True,
        caregiver_notifications_enabled=True,
    )
    db_session.add(pref)
    db_session.commit()
    db_session.refresh(mode)

    assert mode.preferences is not None
    assert mode.preferences.id.startswith("emg-pref-")
    assert mode.preferences.communication_enabled is True
    assert mode.preferences.learning_enabled is True
    assert mode.preferences.emotion_support_enabled is True
    assert mode.preferences.emotional_support_enabled is True  # Alias check
    assert mode.preferences.games_enabled is False
    assert mode.preferences.safety_monitoring_enabled is True
    assert mode.preferences.caregiver_notifications_enabled is True
    assert mode.preferences.created_at is not None
    assert mode.preferences.updated_at is not None


def test_cascade_delete_behavior(db_session: Session):
    sarah = db_session.query(User).filter(User.email == "sarah@nivara.app").first()
    
    # Create a temporary child
    temp_child = Child(
        caregiver_id=sarah.id,
        name="Temp Test Child",
        age=6,
        current_status="safe",
    )
    db_session.add(temp_child)
    db_session.commit()
    db_session.refresh(temp_child)

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=90)

    mode = EmergencyMode(
        child_id=temp_child.id,
        caregiver_id=sarah.id,
        status="active",
        start_date=now,
        end_date=end,
    )
    pref = EmergencySupportPreferences(
        communication_enabled=True,
        learning_enabled=True,
        emotion_support_enabled=True,
        games_enabled=True,
        safety_monitoring_enabled=True,
        caregiver_notifications_enabled=True,
    )
    mode.preferences = pref
    temp_child.emergency_mode = mode

    db_session.add(mode)
    db_session.commit()

    mode_id = mode.id
    pref_id = pref.id

    # Verify entities exist
    assert db_session.query(EmergencyMode).filter(EmergencyMode.id == mode_id).first() is not None
    assert db_session.query(EmergencySupportPreferences).filter(EmergencySupportPreferences.id == pref_id).first() is not None

    # Delete the child and verify cascade deletion of emergency mode and preferences
    db_session.delete(temp_child)
    db_session.commit()

    assert db_session.query(EmergencyMode).filter(EmergencyMode.id == mode_id).first() is None
    assert db_session.query(EmergencySupportPreferences).filter(EmergencySupportPreferences.id == pref_id).first() is None


