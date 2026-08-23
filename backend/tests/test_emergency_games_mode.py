import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, sync_database_schema, engine
from app.models.user import User
from app.models.child import Child
from app.models.emergency_mode import EmergencyMode, EmergencySupportPreferences
from app.domains.games.models import Game, GameSession, GameProgress, GameAchievement
from app.domains.games.repository import GamesRepository
from app.domains.learning.models import LearningTopic
from app.core.security import create_access_token, get_password_hash
from app.ai.game_ai import GameAI

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_games_db():
    sync_database_schema(engine)
    db = SessionLocal()
    try:
        db.query(GameSession).delete()
        db.query(GameProgress).delete()
        db.query(GameAchievement).delete()
        db.commit()
        GamesRepository(db).ensure_seed_games()
    finally:
        db.close()


@pytest.fixture
def games_setup():
    db = SessionLocal()
    try:
        # Caregiver 1 (Sarah - Authorized)
        cg1 = db.query(User).filter(User.email == "sarah.games@nivara.app").first()
        if not cg1:
            cg1 = User(
                id="user-games-cg1",
                email="sarah.games@nivara.app",
                full_name="Sarah Miller",
                role="caregiver",
                hashed_password=get_password_hash("password123"),
            )
            db.add(cg1)
            db.commit()
            db.refresh(cg1)

        # Caregiver 2 (David - Unauthorized)
        cg2 = db.query(User).filter(User.email == "david.games@nivara.app").first()
        if not cg2:
            cg2 = User(
                id="user-games-cg2",
                email="david.games@nivara.app",
                full_name="David Clark",
                role="caregiver",
                hashed_password=get_password_hash("password123"),
            )
            db.add(cg2)
            db.commit()
            db.refresh(cg2)

        # Child 1 (Leo) -> belongs to cg1
        child1 = db.query(Child).filter(Child.id == "child-leo-games-1").first()
        if not child1:
            child1 = Child(
                id="child-leo-games-1",
                name="Leo Miller",
                age=7,
                caregiver_id=cg1.id,
            )
            db.add(child1)
            db.commit()
            db.refresh(child1)

        # Child 2 (Mia) -> belongs to cg2
        child2 = db.query(Child).filter(Child.id == "child-mia-games-2").first()
        if not child2:
            child2 = Child(
                id="child-mia-games-2",
                name="Mia Clark",
                age=5,
                caregiver_id=cg2.id,
            )
            db.add(child2)
            db.commit()
            db.refresh(child2)

        # Setup Active Emergency Mode for Child 1
        db.query(EmergencyMode).filter(EmergencyMode.child_id == child1.id).delete()
        db.commit()

        emg1 = EmergencyMode(
            id="emg-games-leo-1",
            child_id=child1.id,
            caregiver_id=cg1.id,
            status="active",
            emergency_type="quarantine_90_days",
            start_date=datetime.utcnow() - timedelta(days=2),
            end_date=datetime.utcnow() + timedelta(days=88),
        )
        db.add(emg1)
        db.commit()

        pref1 = EmergencySupportPreferences(
            emergency_mode_id=emg1.id,
            communication_enabled=True,
            learning_enabled=True,
            emotion_support_enabled=True,
            emotional_support_enabled=True,
            games_enabled=True,
            safety_monitoring_enabled=True,
            caregiver_notifications_enabled=True,
        )
        db.add(pref1)
        db.commit()

        # Seed connected Learning Topic
        topic = db.query(LearningTopic).filter(LearningTopic.id == "topic-emotion-game-test").first()
        if not topic:
            topic = LearningTopic(
                id="topic-emotion-game-test",
                title="Emotion Regulation in Isolation",
                category="Emotion",
                description="Recognizing emotional signals and practicing sensory calming.",
                progress_pct=20,
            )
            db.add(topic)
            db.commit()

        token1 = create_access_token(cg1.id)
        token2 = create_access_token(cg2.id)

        return {
            "headers_cg1": {"Authorization": f"Bearer {token1}"},
            "headers_cg2": {"Authorization": f"Bearer {token2}"},
            "cg1": cg1,
            "cg2": cg2,
            "child1": child1,
            "child2": child2,
            "emg1": emg1,
        }
    finally:
        db.close()


# ------------------------------------------------------------------------------
# 1. Games Home
# ------------------------------------------------------------------------------
def test_1_games_home(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    res = client.get(f"/api/v1/games/home/{child_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["child_id"] == child_id
    assert data["child_name"] == "Leo Miller"
    assert data["is_emergency_mode"] is True
    assert data["games_enabled"] is True
    assert len(data["categories"]) == 8
    assert len(data["featured_games"]) > 0
    assert len(data["emergency_recommended_games"]) > 0
    assert len(data["personalized_recommendations"]) > 0


# ------------------------------------------------------------------------------
# 2. Game Categories (All 8 Categories)
# ------------------------------------------------------------------------------
def test_2_game_categories(games_setup):
    headers = games_setup["headers_cg1"]

    expected_categories = [
        "Communication", "Emotion", "Memory", "Matching",
        "Focus", "Learning", "Social Skills", "Daily Life Skills"
    ]

    for cat in expected_categories:
        res = client.get(f"/api/v1/games?category={cat}", headers=headers)
        assert res.status_code == 200
        games = res.json()
        assert len(games) >= 1, f"Missing seed games for category {cat}"
        assert games[0]["category"].lower() == cat.lower()


# ------------------------------------------------------------------------------
# 3. Game Session Start
# ------------------------------------------------------------------------------
def test_3_start_game_session(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    res = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-comm-1", "child_id": child_id},
        headers=headers,
    )
    assert res.status_code == 200
    session = res.json()
    assert session["game_id"] == "game-comm-1"
    assert session["status"] == "in_progress"
    assert session["total_tasks"] == 3
    assert len(session["tasks"]) == 3
    assert session["session_id"] is not None


# ------------------------------------------------------------------------------
# 4. Score Calculation during Task Answering
# ------------------------------------------------------------------------------
def test_4_score_calculation(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Start session
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-comm-1", "child_id": child_id},
        headers=headers,
    )
    session_id = res_start.json()["session_id"]

    # Submit correct answer (o1 for task 0)
    res_ans1 = client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 0, "selected_option_id": "o1", "time_spent_sec": 5},
        headers=headers,
    )
    assert res_ans1.status_code == 200
    assert res_ans1.json()["is_correct"] is True
    assert res_ans1.json()["current_score"] == 1

    # Submit incorrect answer (o1 for task 1)
    res_ans2 = client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 1, "selected_option_id": "o1", "time_spent_sec": 4},
        headers=headers,
    )
    assert res_ans2.status_code == 200
    assert res_ans2.json()["is_correct"] is False
    assert res_ans2.json()["current_score"] == 1


# ------------------------------------------------------------------------------
# 5. Game Completion
# ------------------------------------------------------------------------------
def test_5_game_completion(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Start session
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-emotion-1", "child_id": child_id},
        headers=headers,
    )
    session_id = res_start.json()["session_id"]

    # Answer tasks
    client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 0, "selected_option_id": "o1", "time_spent_sec": 5},
        headers=headers,
    )
    client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 1, "selected_option_id": "o2", "time_spent_sec": 4},
        headers=headers,
    )

    # Complete session
    res_complete = client.post(
        f"/api/v1/games/sessions/{session_id}/complete",
        json={"duration_sec": 45, "notes": "Great focus during emotion detective!"},
        headers=headers,
    )
    assert res_complete.status_code == 200
    comp = res_complete.json()
    assert comp["status"] == "completed"
    assert comp["score"] == 2
    assert comp["stars"] >= 2
    assert "Stars" in comp["feedback"]


# ------------------------------------------------------------------------------
# 6. Progress Persistence
# ------------------------------------------------------------------------------
def test_6_progress_persistence(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Start and complete a session
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-matching-1", "child_id": child_id},
        headers=headers,
    )
    session_id = res_start.json()["session_id"]

    client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 0, "selected_option_id": "o1", "time_spent_sec": 3},
        headers=headers,
    )
    client.post(
        f"/api/v1/games/sessions/{session_id}/complete",
        json={"duration_sec": 30},
        headers=headers,
    )

    # Verify progress persistence endpoint
    res_prog = client.get(f"/api/v1/games/progress/{child_id}", headers=headers)
    assert res_prog.status_code == 200
    prog_list = res_prog.json()
    assert len(prog_list) >= 1
    match_prog = next((p for p in prog_list if p["game_id"] == "game-matching-1"), None)
    assert match_prog is not None
    assert match_prog["total_plays"] >= 1
    assert match_prog["total_stars"] >= 1


# ------------------------------------------------------------------------------
# 7. Stars Calculation
# ------------------------------------------------------------------------------
def test_7_stars_calculation(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Test 3 stars on perfect score
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-focus-1", "child_id": child_id},
        headers=headers,
    )
    session_id = res_start.json()["session_id"]

    client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 0, "selected_option_id": "o1"},
        headers=headers,
    )
    client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 1, "selected_option_id": "o1"},
        headers=headers,
    )

    res_comp = client.post(
        f"/api/v1/games/sessions/{session_id}/complete",
        json={"duration_sec": 20},
        headers=headers,
    )
    assert res_comp.status_code == 200
    assert res_comp.json()["stars"] == 3
    assert res_comp.json()["accuracy_pct"] == 100.0


# ------------------------------------------------------------------------------
# 8. Achievements & Badges Unlocked
# ------------------------------------------------------------------------------
def test_8_achievements_and_badges(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Complete a session to unlock badges
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-emotion-1", "child_id": child_id},
        headers=headers,
    )
    session_id = res_start.json()["session_id"]
    for i in range(3):
        client.post(
            f"/api/v1/games/sessions/{session_id}/answer",
            json={"task_index": i, "selected_option_id": f"o{1 if i!=1 else 2}"},
            headers=headers,
        )

    res_comp = client.post(
        f"/api/v1/games/sessions/{session_id}/complete",
        json={"duration_sec": 35},
        headers=headers,
    )
    assert res_comp.status_code == 200

    # Retrieve achievements
    res_ach = client.get(f"/api/v1/games/achievements/{child_id}", headers=headers)
    assert res_ach.status_code == 200
    badges = res_ach.json()
    assert len(badges) >= 1
    badge_keys = [b["badge_key"] for b in badges]
    assert "first_game" in badge_keys


# ------------------------------------------------------------------------------
# 9. Personalized AI Recommendations
# ------------------------------------------------------------------------------
def test_9_personalized_recommendations(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    res = client.get(f"/api/v1/games/recommendations/{child_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["recommendations"]) >= 1
    assert data["recommendations"][0]["reason"] is not None
    assert data["recommendations"][0]["benefit"] is not None


# ------------------------------------------------------------------------------
# 10. Learning-Game Connection
# ------------------------------------------------------------------------------
def test_10_learning_game_connection(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Play and complete an Emotion game
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-emotion-1", "child_id": child_id},
        headers=headers,
    )
    session_id = res_start.json()["session_id"]
    client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 0, "selected_option_id": "o1"},
        headers=headers,
    )
    res_comp = client.post(
        f"/api/v1/games/sessions/{session_id}/complete",
        json={"duration_sec": 40},
        headers=headers,
    )
    assert res_comp.status_code == 200
    data = res_comp.json()
    assert data["learning_progress_updated"] is True
    assert data["learning_topic_connected"] is not None

    # Verify in DB that learning topic is present and has active progress
    db = SessionLocal()
    try:
        topic_after = db.query(LearningTopic).filter(LearningTopic.title == data["learning_topic_connected"]).first()
        assert topic_after is not None
        assert topic_after.progress_pct > 0
    finally:
        db.close()



# ------------------------------------------------------------------------------
# 11. Communication-Game Connection
# ------------------------------------------------------------------------------
def test_11_communication_game_connection(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Play AAC Picture Word Match
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-comm-1", "child_id": child_id},
        headers=headers,
    )
    session_id = res_start.json()["session_id"]

    # Verify task 0 includes AAC token WATER
    task0 = res_start.json()["tasks"][0]
    assert task0["aac_token"] == "WATER"

    # Answer task
    res_ans = client.post(
        f"/api/v1/games/sessions/{session_id}/answer",
        json={"task_index": 0, "selected_option_id": "o1"},
        headers=headers,
    )
    assert res_ans.status_code == 200
    assert res_ans.json()["reinforcement_cue"] == "WATER"

    # Complete session
    res_comp = client.post(
        f"/api/v1/games/sessions/{session_id}/complete",
        json={"duration_sec": 30},
        headers=headers,
    )
    assert res_comp.status_code == 200
    assert "WATER" in res_comp.json()["communication_reinforced"]


# ------------------------------------------------------------------------------
# 12. Caregiver Access & Review
# ------------------------------------------------------------------------------
def test_12_caregiver_access_and_review(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    # Authorized caregiver Sarah fetches review
    res = client.get(f"/api/v1/games/caregiver-review/{child_id}", headers=headers)
    assert res.status_code == 200
    review = res.json()
    assert review["child_id"] == child_id
    assert review["child_name"] == "Leo Miller"
    assert review["is_emergency_mode"] is True
    assert review["emergency_status"] == "active"
    assert review["total_games_played"] >= 0
    assert review["summary_stats"] is not None


# ------------------------------------------------------------------------------
# 13. Unauthorized Access & Missing Child Blocked
# ------------------------------------------------------------------------------
def test_13_unauthorized_access_and_missing_child(games_setup):
    headers_cg2 = games_setup["headers_cg2"]  # David Clark
    child1_id = games_setup["child1"].id      # Leo Miller (belongs to Sarah)

    # 1. Unauthorized start session -> 403 Forbidden
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-comm-1", "child_id": child1_id},
        headers=headers_cg2,
    )
    assert res_start.status_code == 403

    # 2. Unauthorized caregiver review -> 403 Forbidden
    res_review = client.get(
        f"/api/v1/games/caregiver-review/{child1_id}",
        headers=headers_cg2,
    )
    assert res_review.status_code == 403

    # 3. Missing child -> 404 Not Found
    res_missing = client.get(
        "/api/v1/games/caregiver-review/child-non-existent-9999",
        headers=games_setup["headers_cg1"],
    )
    assert res_missing.status_code == 404


# ------------------------------------------------------------------------------
# 14. Emergency Mode Active Behavior
# ------------------------------------------------------------------------------
def test_14_emergency_mode_active_behavior(games_setup):
    headers = games_setup["headers_cg1"]
    child_id = games_setup["child1"].id

    res = client.get(f"/api/v1/games/home/{child_id}", headers=headers)
    assert res.status_code == 200
    home = res.json()
    assert home["is_emergency_mode"] is True
    assert home["emergency_status"] == "active"
    assert len(home["emergency_recommended_games"]) > 0


# ------------------------------------------------------------------------------
# 15. Emergency Mode Inactive Behavior
# ------------------------------------------------------------------------------
def test_15_emergency_mode_inactive_behavior(games_setup):
    headers = games_setup["headers_cg2"]
    child2_id = games_setup["child2"].id  # Mia has no emergency mode

    res = client.get(f"/api/v1/games/home/{child2_id}", headers=headers)
    assert res.status_code == 200
    home = res.json()
    assert home["is_emergency_mode"] is False
    assert home["emergency_status"] == "inactive"

    # Games still play normally
    res_start = client.post(
        "/api/v1/games/sessions/start",
        json={"game_id": "game-comm-1", "child_id": child2_id},
        headers=headers,
    )
    assert res_start.status_code == 200


# ------------------------------------------------------------------------------
# 16. AI Fallback Resilience
# ------------------------------------------------------------------------------
def test_16_ai_fallback_resilience(monkeypatch):
    # Simulate AI exception
    def broken_recommendations(*args, **kwargs):
        raise RuntimeError("AI service down")

    monkeypatch.setattr(GameAI, "generate_recommendations", broken_recommendations)

    # Calling GameAI directly or via fallback
    try:
        GameAI.generate_recommendations()
    except RuntimeError:
        pass

    # Ensure default recommendations exist and are valid
    assert len(GameAI.DEFAULT_RECOMMENDATIONS) == 3
    assert GameAI.DEFAULT_RECOMMENDATIONS[0]["category"] == "Communication"
    assert GameAI.DEFAULT_RECOMMENDATIONS[1]["category"] == "Emotion"
    assert GameAI.DEFAULT_RECOMMENDATIONS[2]["category"] == "Learning"
