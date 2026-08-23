from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.games.models import Game, GameSession, GameProgress, GameAchievement
from app.domains.games.repository import GamesRepository
from app.domains.games.schemas import (
    GameResponse,
    GameSessionStartRequest,
    GameSessionStartResponse,
    GameSessionAnswerRequest,
    GameSessionAnswerResponse,
    GameSessionCompleteRequest,
    GameSessionCompleteResponse,
    GameSessionResponse,
    GameProgressResponse,
    GameAchievementResponse,
    GameCategorySummary,
    GameRecommendationItem,
    GameRecommendationsResponse,
    EmergencyGamesHomeResponse,
    CaregiverGamesReviewResponse,
)
from app.domains.communication.repository import CommunicationRepository
from app.domains.learning.repository import LearningRepository
from app.domains.learning.models import LearningTopic
from app.ai.game_ai import GameAI
from app.models.user import User
from app.models.child import Child


CATEGORY_METADATA = {
    "Communication": {
        "display_name": "Communication & AAC",
        "icon": "🗣️",
        "color": "#2563EB",
        "description": "Vocabulary, picture-word association, and AAC sentence reinforcement.",
    },
    "Emotion": {
        "display_name": "Emotion & Regulation",
        "icon": "😊",
        "color": "#EC4899",
        "description": "Identifying feelings, sensory calming tools, and self-regulation.",
    },
    "Memory": {
        "display_name": "Cognitive Memory",
        "icon": "🧠",
        "color": "#8B5CF6",
        "description": "Visual patterns, object recall, and working memory exercises.",
    },
    "Matching": {
        "display_name": "Sensory Matching",
        "icon": "🔷",
        "color": "#F59E0B",
        "description": "Shape, color, texture discrimination, and categorization.",
    },
    "Focus": {
        "display_name": "Quiet Focus",
        "icon": "🎯",
        "color": "#10B981",
        "description": "Sustained attention, visual search, and low-stimulus focus tasks.",
    },
    "Learning": {
        "display_name": "Daily Routines",
        "icon": "📖",
        "color": "#3B82F6",
        "description": "Morning, bedtime, and step-by-step visual routine sorting.",
    },
    "Social Skills": {
        "display_name": "Social Problem Solving",
        "icon": "🤝",
        "color": "#6366F1",
        "description": "Turn-taking, empathy, sharing, and social boundaries.",
    },
    "Daily Life Skills": {
        "display_name": "Home Life Skills",
        "icon": "🧹",
        "color": "#14B8A6",
        "description": "Hygiene, desk organizing, self-care, and task completion.",
    },
}


class GamesService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GamesRepository(db)
        self.comm_repo = CommunicationRepository(db)
        self.learning_repo = LearningRepository(db)

    def _verify_child_access(self, child_id: str, current_user: Optional[User]) -> Child:
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child '{child_id}' not found.",
            )
        if current_user and getattr(current_user, "role", "") != "admin":
            if child.caregiver_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized: You do not have permission to manage games for this child.",
                )
        return child

    def _is_emergency_active(self, child_id: Optional[str]) -> bool:
        if not child_id:
            return False
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child or not child.emergency_mode:
            return False
        emg = child.emergency_mode
        if emg.effective_status != "active":
            return False
        if emg.preferences:
            return bool(emg.preferences.games_enabled)
        return True

    def get_games_home(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> EmergencyGamesHomeResponse:
        resolved_child_id = child_id
        child_name = None
        is_emg = False
        emg_status = "inactive"

        if current_user and not resolved_child_id:
            first_child = self.db.query(Child).filter(Child.caregiver_id == current_user.id).first()
            if first_child:
                resolved_child_id = first_child.id

        if resolved_child_id:
            child = self.db.query(Child).filter(Child.id == resolved_child_id).first()
            if child:
                child_name = child.name
                if child.emergency_mode:
                    emg = child.emergency_mode
                    emg_status = emg.effective_status
                    is_emg = (emg_status == "active" and (not emg.preferences or emg.preferences.games_enabled))

        all_games = self.repo.get_games()

        # Build Category Summaries
        categories_map = {}
        for cat_name, meta in CATEGORY_METADATA.items():
            count = sum(1 for g in all_games if g.category.lower() == cat_name.lower())
            categories_map[cat_name] = GameCategorySummary(
                category=cat_name,
                display_name=meta["display_name"],
                icon=meta["icon"],
                color=meta["color"],
                description=meta["description"],
                games_count=count,
            )

        featured = [GameResponse.model_validate(g) for g in all_games[:4]]
        emergency_recs = [GameResponse.model_validate(g) for g in all_games if g.is_emergency_recommended][:4]

        recent_sessions_objs = self.repo.get_recent_sessions(child_id=resolved_child_id, limit=5)
        recent_sessions = [GameSessionResponse.model_validate(s) for s in recent_sessions_objs]

        achievements_objs = self.repo.get_achievements(child_id=resolved_child_id) if resolved_child_id else []
        achievements = [GameAchievementResponse.model_validate(a) for a in achievements_objs[:6]]

        # AI Recommendations
        personalized = self.get_recommendations(child_id=resolved_child_id, current_user=current_user).recommendations

        return EmergencyGamesHomeResponse(
            child_id=resolved_child_id,
            child_name=child_name,
            is_emergency_mode=is_emg,
            emergency_status=emg_status,
            games_enabled=True,
            categories=list(categories_map.values()),
            featured_games=featured,
            emergency_recommended_games=emergency_recs,
            recent_sessions=recent_sessions,
            recent_achievements=achievements,
            personalized_recommendations=personalized,
            stats={
                "total_games_available": len(all_games),
                "total_categories": len(CATEGORY_METADATA),
                "is_emergency_mode": is_emg,
            },
        )

    def get_games_list(
        self,
        category: Optional[str] = None,
        is_emergency_recommended: Optional[bool] = None,
        current_user: Optional[User] = None
    ) -> List[GameResponse]:
        games = self.repo.get_games(category=category, is_emergency_recommended=is_emergency_recommended)
        return [
            GameResponse(
                id=g.id,
                title=g.title,
                category=g.category,
                description=g.description,
                icon=g.icon,
                color=g.color,
                difficulty=g.difficulty,
                min_age=g.min_age,
                max_age=g.max_age,
                is_emergency_recommended=g.is_emergency_recommended,
                skill_tags=g.skill_tags or [],
                instructions=g.instructions,
                tasks_data=g.tasks_data or [],
                tasks_count=len(g.tasks_data or []),
                created_at=g.created_at,
            )
            for g in games
        ]

    def get_game_details(self, game_id: str, current_user: Optional[User] = None) -> GameResponse:
        g = self.repo.get_game_by_id(game_id)
        if not g:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game '{game_id}' not found.",
            )
        return GameResponse(
            id=g.id,
            title=g.title,
            category=g.category,
            description=g.description,
            icon=g.icon,
            color=g.color,
            difficulty=g.difficulty,
            min_age=g.min_age,
            max_age=g.max_age,
            is_emergency_recommended=g.is_emergency_recommended,
            skill_tags=g.skill_tags or [],
            instructions=g.instructions,
            tasks_data=g.tasks_data or [],
            tasks_count=len(g.tasks_data or []),
            created_at=g.created_at,
        )

    def start_game_session(
        self,
        req: GameSessionStartRequest,
        current_user: Optional[User] = None
    ) -> GameSessionStartResponse:
        game = self.repo.get_game_by_id(req.game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game '{req.game_id}' not found.",
            )

        if req.child_id:
            self._verify_child_access(req.child_id, current_user)

        session = GameSession(
            game_id=game.id,
            child_id=req.child_id,
            user_id=current_user.id if current_user else None,
            status="in_progress",
            score=0,
            max_score=len(game.tasks_data or []),
            stars=0,
            answers_data=[],
        )
        saved = self.repo.create_session(session)

        return GameSessionStartResponse(
            session_id=saved.id,
            game_id=game.id,
            game_title=game.title,
            category=game.category,
            child_id=saved.child_id,
            status=saved.status,
            tasks=game.tasks_data or [],
            total_tasks=len(game.tasks_data or []),
            created_at=saved.created_at,
        )

    def answer_task(
        self,
        session_id: str,
        req: GameSessionAnswerRequest,
        current_user: Optional[User] = None
    ) -> GameSessionAnswerResponse:
        session = self.repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session '{session_id}' not found.",
            )

        game = session.game_rel or self.repo.get_game_by_id(session.game_id)
        tasks = (game.tasks_data if game else []) or []
        if req.task_index < 0 or req.task_index >= len(tasks):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid task_index {req.task_index}. Total tasks: {len(tasks)}",
            )

        current_task = tasks[req.task_index]
        options = current_task.get("options", [])
        chosen = next((o for o in options if o.get("id") == req.selected_option_id), None)
        is_correct = bool(chosen.get("is_correct", False)) if chosen else False

        # Update session score
        if is_correct:
            session.score += current_task.get("points", 1)

        answers = list(session.answers_data or [])
        answers.append({
            "task_index": req.task_index,
            "selected_option_id": req.selected_option_id,
            "is_correct": is_correct,
            "time_spent_sec": req.time_spent_sec,
        })
        session.answers_data = answers
        self.repo.update_session(session)

        cue = current_task.get("aac_token") or current_task.get("emotion_target")
        msg = "Wonderful job! That was correct!" if is_correct else "Good effort! Let's keep going!"

        return GameSessionAnswerResponse(
            session_id=session.id,
            task_index=req.task_index,
            is_correct=is_correct,
            current_score=session.score,
            encouraging_message=msg,
            reinforcement_cue=cue,
        )

    def complete_game_session(
        self,
        session_id: str,
        req: GameSessionCompleteRequest,
        current_user: Optional[User] = None
    ) -> GameSessionCompleteResponse:
        session = self.repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session '{session_id}' not found.",
            )

        game = session.game_rel or self.repo.get_game_by_id(session.game_id)
        max_score = max(session.max_score, 1)
        accuracy = round((session.score / max_score) * 100, 1)

        # Calculate stars (0 to 3)
        if accuracy >= 80:
            stars = 3
            feedback = "Outstanding! You earned 3 Stars! ⭐⭐⭐ Keep up the amazing work!"
        elif accuracy >= 50:
            stars = 2
            feedback = "Great job! You earned 2 Stars! ⭐⭐ You are getting stronger every day!"
        elif accuracy > 0:
            stars = 1
            feedback = "Nice effort! You earned 1 Star! ⭐ Every practice helps you learn!"
        else:
            stars = 0
            feedback = "Thank you for practicing today! Let's try again together soon!"

        session.stars = stars
        session.duration_sec = req.duration_sec or 60
        session.status = "completed"
        session.feedback = feedback
        session.completed_at = datetime.utcnow()
        self.repo.update_session(session)

        new_achievements = []
        child_id = session.child_id
        learning_topic_connected = None
        communication_reinforced = None
        learning_progress_updated = False

        if child_id:
            # 1. Update GameProgress
            prog = self.repo.get_progress(child_id=child_id, game_id=session.game_id)
            if not prog:
                prog = GameProgress(
                    child_id=child_id,
                    game_id=session.game_id,
                    skill_category=game.category if game else "General",
                    total_plays=1,
                    highest_score=session.score,
                    total_stars=stars,
                    mastery_level="mastered" if accuracy >= 80 else "practicing",
                )
            else:
                prog.total_plays += 1
                prog.total_stars += stars
                if session.score > prog.highest_score:
                    prog.highest_score = session.score
                if accuracy >= 80:
                    prog.mastery_level = "mastered"
                elif prog.mastery_level != "mastered":
                    prog.mastery_level = "practicing"
                prog.last_played_at = datetime.utcnow()
            self.repo.save_progress(prog)

            # 2. Award Badges / Achievements
            # First Game
            if not self.repo.get_achievement_by_key(child_id, "first_game"):
                a = self.repo.create_achievement(
                    GameAchievement(
                        child_id=child_id,
                        badge_key="first_game",
                        title="First Game Explorer",
                        description="Completed your first cognitive skill-building game!",
                        icon="🌟",
                        category="Explorer",
                    )
                )
                new_achievements.append(GameAchievementResponse.model_validate(a))

            # 3-Star Mastery
            if stars == 3 and not self.repo.get_achievement_by_key(child_id, "three_stars_master"):
                a = self.repo.create_achievement(
                    GameAchievement(
                        child_id=child_id,
                        badge_key="three_stars_master",
                        title="Three Star Champion",
                        description="Earned a perfect 3-star score in a cognitive game!",
                        icon="⭐⭐⭐",
                        category="Mastery",
                    )
                )
                new_achievements.append(GameAchievementResponse.model_validate(a))

            # Category-specific achievements
            if game:
                cat = game.category.lower()
                if cat == "emotion" and accuracy >= 80 and not self.repo.get_achievement_by_key(child_id, "emotion_detective"):
                    a = self.repo.create_achievement(
                        GameAchievement(
                            child_id=child_id,
                            badge_key="emotion_detective",
                            title="Emotion Detective Badge",
                            description="Mastered feeling identification and self-regulation tools!",
                            icon="😊",
                            category="Emotion",
                        )
                    )
                    new_achievements.append(GameAchievementResponse.model_validate(a))

                if cat == "communication" and accuracy >= 80 and not self.repo.get_achievement_by_key(child_id, "communication_hero"):
                    a = self.repo.create_achievement(
                        GameAchievement(
                            child_id=child_id,
                            badge_key="communication_hero",
                            title="Communication Hero Badge",
                            description="Successfully matched AAC vocabulary for clear expression!",
                            icon="🗣️",
                            category="Communication",
                        )
                    )
                    new_achievements.append(GameAchievementResponse.model_validate(a))

            # 3. Connect to Learning Module Progress
            if game and game.category in ["Learning", "Emotion", "Social Skills"]:
                # Look for matching LearningTopic
                target_topic = self.db.query(LearningTopic).filter(
                    LearningTopic.category.ilike(f"%{game.category}%")
                ).first()
                if target_topic:
                    target_topic.progress_pct = min(100, target_topic.progress_pct + 10)
                    if target_topic.progress_pct == 100:
                        target_topic.is_completed = True
                    self.db.commit()
                    learning_progress_updated = True
                    learning_topic_connected = target_topic.title

            # 4. Connect to Communication Reinforcement
            if game and game.category == "Communication":
                communication_reinforced = "AAC Request Tokens: WATER, FOOD, HELP"

        return GameSessionCompleteResponse(
            session_id=session.id,
            game_id=session.game_id,
            game_title=game.title if game else "Game",
            category=game.category if game else "General",
            child_id=session.child_id,
            score=session.score,
            max_score=max_score,
            accuracy_pct=accuracy,
            stars=stars,
            duration_sec=session.duration_sec,
            status="completed",
            feedback=feedback,
            learning_progress_updated=learning_progress_updated,
            learning_topic_connected=learning_topic_connected,
            communication_reinforced=communication_reinforced,
            new_achievements=new_achievements,
            completed_at=session.completed_at or datetime.utcnow(),
        )

    def get_recommendations(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> GameRecommendationsResponse:
        resolved_child_id = child_id
        if current_user and not resolved_child_id:
            first_child = self.db.query(Child).filter(Child.caregiver_id == current_user.id).first()
            if first_child:
                resolved_child_id = first_child.id

        is_emg = self._is_emergency_active(resolved_child_id)

        # Collect behavioral signals
        recent_emotions = []
        if resolved_child_id:
            em_records = self.comm_repo.get_child_emotions(resolved_child_id, limit=5)
            recent_emotions = [r.emotion for r in em_records]

        rec_items = GameAI.generate_recommendations(
            child_id=resolved_child_id,
            recent_emotions=recent_emotions,
            is_emergency_mode=is_emg,
        )

        return GameRecommendationsResponse(
            child_id=resolved_child_id,
            recommendations=[GameRecommendationItem.model_validate(r) for r in rec_items],
            is_emergency_mode=is_emg,
            summary="Personalized game recommendations based on emotional state and daily home learning priorities.",
            is_fallback=False,
        )

    def get_caregiver_review(
        self,
        child_id: str,
        current_user: Optional[User] = None
    ) -> CaregiverGamesReviewResponse:
        """
        Caregiver remote supervisory review of child cognitive game sessions,
        stars earned, skill mastery breakdown, and unlocked achievements.
        Strictly returns 403 Forbidden for unauthorized caregivers, 404 for missing child.
        """
        child = self._verify_child_access(child_id, current_user)

        is_emg = False
        emg_status = "inactive"
        if child.emergency_mode:
            emg = child.emergency_mode
            emg_status = emg.effective_status
            is_emg = (emg_status == "active")

        sessions_objs = self.repo.get_recent_sessions(child_id=child_id, limit=20)
        progress_objs = self.repo.get_child_progress_list(child_id=child_id)
        achievements_objs = self.repo.get_achievements(child_id=child_id)

        total_games = len(sessions_objs)
        total_stars = sum(s.stars for s in sessions_objs)

        # Skill mastery breakdown
        mastery_map = {}
        for p in progress_objs:
            mastery_map[p.skill_category] = {
                "plays": p.total_plays,
                "highest_score": p.highest_score,
                "stars": p.total_stars,
                "mastery_level": p.mastery_level,
            }

        recs = self.get_recommendations(child_id=child_id, current_user=current_user).recommendations

        return CaregiverGamesReviewResponse(
            child_id=child.id,
            child_name=child.name,
            caregiver_id=child.caregiver_id,
            is_emergency_mode=is_emg,
            emergency_status=emg_status,
            total_games_played=total_games,
            total_stars_earned=total_stars,
            total_achievements_unlocked=len(achievements_objs),
            skill_mastery_breakdown=mastery_map,
            recent_sessions=[GameSessionResponse.model_validate(s) for s in sessions_objs[:10]],
            achievements=[GameAchievementResponse.model_validate(a) for a in achievements_objs],
            recommended_activities=recs,
            summary_stats={
                "total_completed_sessions": total_games,
                "total_stars": total_stars,
                "achievements_count": len(achievements_objs),
                "is_emergency_active": is_emg,
            },
        )
