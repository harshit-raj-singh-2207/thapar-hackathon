import sys
import os
import pytest
from datetime import datetime, timedelta, timezone

# Add backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences
from app.models.child import Child
from app.models.user import User
from app.domains.learning.models import Routine, RoutineStep, Task, Reminder, LearningTopic

client = TestClient(app)

def get_auth_tokens():
    """Helper to authenticate test users."""
    res1 = client.post("/api/v1/auth/login", json={"email": "sarah@nivara.app", "password": "password123"})
    sarah_token = res1.json()["access_token"]
    sarah_id = res1.json()["user_id"]

    res2 = client.post("/api/v1/auth/login", json={"email": "david@nivara.app", "password": "password123"})
    david_token = res2.json()["access_token"]
    david_id = res2.json()["user_id"]

    return (sarah_token, sarah_id), (david_token, david_id)


def ensure_emergency_mode_active(child_id: str, caregiver_id: str):
    """Ensure an active 90-day emergency mode exists in test DB."""
    db = next(get_db())
    try:
        emg = db.query(EmergencyMode).filter(EmergencyMode.child_id == child_id).first()
        now = datetime.now(timezone.utc)
        if not emg:
            emg = EmergencyMode(
                child_id=child_id,
                caregiver_id=caregiver_id,
                status="active",
                emergency_type="pandemic_lockdown",
                reason="90-Day Physical Gathering Restriction",
                start_date=now,
                end_date=now + timedelta(days=90),
                duration_days=90,
                is_active=True,
            )
            db.add(emg)
            db.commit()
            db.refresh(emg)

            prefs = EmergencySupportPreferences(
                emergency_mode_id=emg.id,
                learning_enabled=True,
                communication_enabled=True,
                emotion_support_enabled=True,
                games_enabled=True,
                safety_monitoring_enabled=True,
                caregiver_notifications_enabled=True,
            )
            db.add(prefs)
            db.commit()
        else:
            emg.status = "active"
            emg.is_active = True
            emg.start_date = now
            emg.end_date = now + timedelta(days=90)
            if emg.preferences:
                emg.preferences.learning_enabled = True
            db.commit()
    finally:
        db.close()


def test_1_emergency_learning_mode_active():
    """Test 1: Active Emergency Learning Mode retrieves unified home learning plan."""
    (sarah_token, sarah_id), _ = get_auth_tokens()
    child_id = "child-leo-1"
    ensure_emergency_mode_active(child_id, sarah_id)

    res = client.get(
        f"/api/v1/learning/emergency-plan/{child_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res.status_code == 200
    data = res.json()

    assert data["child_id"] == child_id
    assert data["is_emergency_mode"] is True
    assert data["emergency_status"] == "active"
    assert data["learning_enabled"] is True
    assert len(data["daily_routines"]) >= 1
    assert len(data["reminders"]) >= 1
    assert len(data["learning_topics"]) >= 1
    assert len(data["recommended_activities"]) >= 3
    assert data["ai_tutor_hint"] is not None
    assert "total_routines" in data["summary_stats"]


def test_2_daily_routines_lifecycle():
    """Test 2: Daily routines listing, creation, step toggling, and reset."""
    (sarah_token, sarah_id), _ = get_auth_tokens()

    # 1. Get all routines
    res_list = client.get("/api/v1/learning/routines")
    assert res_list.status_code == 200
    routines = res_list.json()
    assert len(routines) >= 1
    morning = next((r for r in routines if r["time_of_day"] == "morning"), routines[0])
    assert len(morning["steps"]) >= 1

    # 2. Toggle a step in the routine
    step_id = morning["steps"][0]["id"]
    res_toggle = client.post(f"/api/v1/learning/routines/steps/{step_id}/toggle")
    assert res_toggle.status_code == 200
    assert "is_completed" in res_toggle.json()

    # 3. Create a customized home study routine
    new_routine = {
        "title": "Afternoon Home Study Routine",
        "time_of_day": "afternoon",
        "icon": "📚",
        "color": "#10B981",
        "is_active": True,
        "steps": [
            {"step_number": 1, "title": "Setup quiet workspace", "instruction": "Clear desk", "icon": "🪑", "duration_sec": 60, "is_completed": False},
            {"step_number": 2, "title": "Open learning app", "instruction": "Check today's story", "icon": "💻", "duration_sec": 120, "is_completed": False},
        ]
    }
    res_create = client.post("/api/v1/learning/routines", json=new_routine)
    assert res_create.status_code == 200
    created_id = res_create.json()["id"]

    # 4. Reset routine
    res_reset = client.post(f"/api/v1/learning/routines/{created_id}/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["message"] == "Routine reset successfully"


def test_3_ai_task_breakdown():
    """Test 3: AI Task breakdown generates micro-steps with icons, timers, and encouragement."""
    req_data = {"task_title": "Clean Desk", "custom_context": "Home study area"}
    res = client.post("/api/v1/learning/breakdown-task", json=req_data)
    assert res.status_code == 200
    data = res.json()

    assert data["task_title"] == "Clean Desk"
    assert len(data["steps"]) >= 3
    assert data["total_estimated_duration_sec"] > 0
    assert "encouragement" in data

    # Verify micro-step structure
    first_step = data["steps"][0]
    assert "step_number" in first_step
    assert "title" in first_step
    assert "instruction" in first_step
    assert "icon" in first_step
    assert "duration_sec" in first_step


def test_4_visual_micro_steps_creation():
    """Test 4: Creating a broken down task with visual micro steps."""
    (sarah_token, _), _ = get_auth_tokens()

    task_payload = {
        "title": "Wash Hands Step-by-Step",
        "description": "Essential hygiene routine for remote health.",
        "category": "Daily Living",
        "icon": "🧼",
        "steps_data": [
            {"step_number": 1, "title": "Turn on warm water", "instruction": "Wet hands under water.", "icon": "🚰", "duration_sec": 10, "is_completed": False},
            {"step_number": 2, "title": "Pump soap into hands", "instruction": "One pump of soap bubbles.", "icon": "🧼", "duration_sec": 10, "is_completed": False},
            {"step_number": 3, "title": "Rub bubbly suds", "instruction": "Sing Happy Birthday twice (20s).", "icon": "🫧", "duration_sec": 20, "is_completed": False},
            {"step_number": 4, "title": "Rinse clean and dry", "instruction": "Pat dry with soft towel.", "icon": "🧺", "duration_sec": 15, "is_completed": False},
        ]
    }
    res = client.post("/api/v1/learning/tasks", json=task_payload)
    assert res.status_code == 200
    data = res.json()

    assert data["title"] == "Wash Hands Step-by-Step"
    assert data["is_completed"] is False
    assert len(data["steps_data"]) == 4


def test_5_task_completion_and_progress():
    """Test 5: Completing task micro-steps updates progress and auto-completes task."""
    task_payload = {
        "title": "Quick Sensory Calming Task",
        "category": "Sensory",
        "icon": "🧘",
        "steps_data": [
            {"step_number": 1, "title": "Deep breath", "is_completed": False},
            {"step_number": 2, "title": "Drink water", "is_completed": False},
        ]
    }
    res_task = client.post("/api/v1/learning/tasks", json=task_payload)
    task_id = res_task.json()["id"]

    # Complete Step 0
    res_step0 = client.post(f"/api/v1/learning/tasks/{task_id}/steps/0?is_completed=true")
    assert res_step0.status_code == 200
    assert res_step0.json()["is_completed"] is False  # Task not fully completed yet

    # Complete Step 1
    res_step1 = client.post(f"/api/v1/learning/tasks/{task_id}/steps/1?is_completed=true")
    assert res_step1.status_code == 200
    assert res_step1.json()["is_completed"] is True  # Task now fully completed!


def test_6_reminders_management():
    """Test 6: Reminders retrieval, creation, and toggle."""
    # 1. Get reminders
    res_list = client.get("/api/v1/learning/reminders")
    assert res_list.status_code == 200
    reminders = res_list.json()
    assert len(reminders) >= 1

    # 2. Create a new reminder
    new_rem = {
        "title": "Afternoon Sensory Calming Break",
        "time_str": "03:00 PM",
        "frequency": "Daily",
        "category": "Sensory Break",
        "icon": "🎧",
        "is_active": True
    }
    res_create = client.post("/api/v1/learning/reminders", json=new_rem)
    assert res_create.status_code == 200
    rem_id = res_create.json()["id"]

    # 3. Toggle reminder
    res_toggle = client.post(f"/api/v1/learning/reminders/{rem_id}/toggle")
    assert res_toggle.status_code == 200
    assert res_toggle.json()["is_active"] is False


def test_7_ai_tutor_nivi_remote_learning():
    """Test 7: AI Tutor Nivi answers with simple language, analogies, follow-ups, and recommended activities."""
    # Ask about germs / hand hygiene
    req_germs = {"question": "Why do we have to wash our hands with soap?"}
    res_germs = client.post("/api/v1/learning/tutor/ask", json=req_germs)
    assert res_germs.status_code == 200
    data_germs = res_germs.json()

    assert "reply" in data_germs
    assert "soap" in data_germs["reply"].lower() or "germ" in data_germs["reply"].lower()
    assert data_germs["simple_analogy"] is not None
    assert len(data_germs["follow_up_questions"]) >= 1
    assert data_germs["recommended_activity"] is not None
    assert "title" in data_germs["recommended_activity"]

    # Ask about staying home / emergency
    req_home = {"question": "Why do I have to stay home from school?"}
    res_home = client.post("/api/v1/learning/tutor/ask", json=req_home)
    assert res_home.status_code == 200
    data_home = res_home.json()
    assert "home" in data_home["reply"].lower() or "protect" in data_home["reply"].lower()
    assert len(data_home["follow_up_questions"]) >= 1


def test_8_personalized_recommendations_in_plan():
    """Test 8: Personalized home learning recommendations in emergency learning plan."""
    (sarah_token, sarah_id), _ = get_auth_tokens()
    child_id = "child-leo-1"
    ensure_emergency_mode_active(child_id, sarah_id)

    res = client.get(
        f"/api/v1/learning/emergency-plan/{child_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res.status_code == 200
    data = res.json()

    recs = data["recommended_activities"]
    assert len(recs) >= 3
    rec_types = [r["type"] for r in recs]
    assert "routine" in rec_types
    assert "task" in rec_types
    assert "break" in rec_types


def test_9_learning_topics_and_progress():
    """Test 9: Learning topics list and progress update."""
    # 1. Get topics
    res_topics = client.get("/api/v1/learning/topics")
    assert res_topics.status_code == 200
    topics = res_topics.json()
    assert len(topics) >= 1
    topic_id = topics[0]["id"]

    # 2. Update progress
    res_prog = client.post(f"/api/v1/learning/topics/{topic_id}/progress?progress_pct=100&is_completed=true")
    assert res_prog.status_code == 200
    assert res_prog.json()["progress_pct"] == 100


def test_10_caregiver_remote_learning_review_authorized():
    """Test 10: Authorized caregiver can access full learning review with stats and recommendations."""
    (sarah_token, sarah_id), _ = get_auth_tokens()
    child_id = "child-leo-1"
    ensure_emergency_mode_active(child_id, sarah_id)

    res = client.get(
        f"/api/v1/learning/caregiver-review/{child_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res.status_code == 200
    data = res.json()

    assert data["child_id"] == child_id
    assert data["caregiver_id"] == sarah_id
    assert "completed_tasks" in data
    assert "in_progress_tasks" in data
    assert "routines" in data
    assert "active_reminders" in data
    assert "learning_topics" in data
    assert "overall_completion_rate" in data
    assert isinstance(data["overall_completion_rate"], (int, float))
    assert "summary_stats" in data


def test_11_unauthorized_caregiver_blocked():
    """Test 11: Unauthorized caregiver accessing another child's learning review returns 403 Forbidden."""
    (sarah_token, _), (david_token, _) = get_auth_tokens()
    sarah_child_id = "child-leo-1"

    # David tries to access Sarah's child -> 403 Forbidden
    res_unauth = client.get(
        f"/api/v1/learning/caregiver-review/{sarah_child_id}",
        headers={"Authorization": f"Bearer {david_token}"}
    )
    assert res_unauth.status_code == 403

    # Nonexistent child -> 404
    res_404 = client.get(
        "/api/v1/learning/caregiver-review/child-nonexistent-999",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res_404.status_code == 404


def test_12_emergency_mode_inactive_behavior():
    """Test 12: Inactive or disabled emergency mode reverts to standard learning view."""
    (sarah_token, sarah_id), _ = get_auth_tokens()
    child_id = "child-leo-1"

    # Deactivate Emergency Mode
    db = next(get_db())
    try:
        emg = db.query(EmergencyMode).filter(EmergencyMode.child_id == child_id).first()
        if emg:
            emg.status = "inactive"
            emg.is_active = False
            db.commit()
    finally:
        db.close()

    res = client.get(
        f"/api/v1/learning/emergency-plan/{child_id}",
        headers={"Authorization": f"Bearer {sarah_token}"}
    )
    assert res.status_code == 200
    data = res.json()

    assert data["is_emergency_mode"] is False
    assert data["emergency_status"] == "inactive"
    assert len(data["daily_routines"]) >= 1  # Standard routines still accessible
    assert len(data["recommended_activities"]) == 0  # Emergency recommendations inactive

    # Restore active emergency mode for other suites
    ensure_emergency_mode_active(child_id, sarah_id)
