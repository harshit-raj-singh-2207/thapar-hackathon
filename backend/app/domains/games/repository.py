from typing import List, Optional
from sqlalchemy.orm import Session
from app.domains.games.models import Game, GameSession, GameProgress, GameAchievement
from app.domains.games.seed_data import SEED_GAMES


class GamesRepository:
    def __init__(self, db: Session):
        self.db = db

    def ensure_seed_games(self):
        """Seed initial game catalog across 8 categories if table is empty or missing seeds."""
        existing_count = self.db.query(Game).count()
        if existing_count == 0:
            for g in SEED_GAMES:
                game_obj = Game(
                    id=g["id"],
                    title=g["title"],
                    category=g["category"],
                    description=g.get("description"),
                    icon=g.get("icon", "🎮"),
                    color=g.get("color", "#3B82F6"),
                    difficulty=g.get("difficulty", "easy"),
                    min_age=g.get("min_age", 4),
                    max_age=g.get("max_age", 14),
                    is_emergency_recommended=g.get("is_emergency_recommended", True),
                    skill_tags=g.get("skill_tags", []),
                    instructions=g.get("instructions", ""),
                    tasks_data=g.get("tasks_data", []),
                )
                self.db.add(game_obj)
            self.db.commit()

    def get_games(
        self,
        category: Optional[str] = None,
        is_emergency_recommended: Optional[bool] = None,
    ) -> List[Game]:
        self.ensure_seed_games()
        query = self.db.query(Game)
        if category and category.lower() != "all":
            query = query.filter(Game.category.ilike(category.strip()))
        if is_emergency_recommended is not None:
            query = query.filter(Game.is_emergency_recommended == is_emergency_recommended)
        return query.order_by(Game.category.asc(), Game.title.asc()).all()

    def get_game_by_id(self, game_id: str) -> Optional[Game]:
        self.ensure_seed_games()
        return self.db.query(Game).filter(Game.id == game_id).first()

    def create_game(self, game: Game) -> Game:
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def create_session(self, session: GameSession) -> GameSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_by_id(self, session_id: str) -> Optional[GameSession]:
        return self.db.query(GameSession).filter(GameSession.id == session_id).first()

    def update_session(self, session: GameSession) -> GameSession:
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_recent_sessions(
        self,
        child_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[GameSession]:
        query = self.db.query(GameSession)
        if child_id:
            query = query.filter(GameSession.child_id == child_id)
        elif user_id:
            query = query.filter((GameSession.user_id == user_id) | (GameSession.user_id == None))
        return query.order_by(GameSession.created_at.desc()).limit(limit).all()

    def get_progress(self, child_id: str, game_id: str) -> Optional[GameProgress]:
        return (
            self.db.query(GameProgress)
            .filter(GameProgress.child_id == child_id, GameProgress.game_id == game_id)
            .first()
        )

    def get_child_progress_list(self, child_id: str) -> List[GameProgress]:
        return (
            self.db.query(GameProgress)
            .filter(GameProgress.child_id == child_id)
            .order_by(GameProgress.total_stars.desc())
            .all()
        )

    def save_progress(self, progress: GameProgress) -> GameProgress:
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_achievements(self, child_id: str) -> List[GameAchievement]:
        return (
            self.db.query(GameAchievement)
            .filter(GameAchievement.child_id == child_id)
            .order_by(GameAchievement.unlocked_at.desc())
            .all()
        )

    def get_achievement_by_key(self, child_id: str, badge_key: str) -> Optional[GameAchievement]:
        return (
            self.db.query(GameAchievement)
            .filter(GameAchievement.child_id == child_id, GameAchievement.badge_key == badge_key)
            .first()
        )

    def create_achievement(self, achievement: GameAchievement) -> GameAchievement:
        self.db.add(achievement)
        self.db.commit()
        self.db.refresh(achievement)
        return achievement

    def count_sessions(self, child_id: Optional[str] = None) -> int:
        query = self.db.query(GameSession).filter(GameSession.status == "completed")
        if child_id:
            query = query.filter(GameSession.child_id == child_id)
        return query.count()

    def count_achievements(self, child_id: Optional[str] = None) -> int:
        query = self.db.query(GameAchievement)
        if child_id:
            query = query.filter(GameAchievement.child_id == child_id)
        return query.count()
