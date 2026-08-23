from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_optional_user
from app.models.user import User
from app.domains.games.service import GamesService
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
    GameRecommendationsResponse,
    EmergencyGamesHomeResponse,
    CaregiverGamesReviewResponse,
)

router = APIRouter(prefix="/games", tags=["90-Day Emergency Games & Skill Development"])


# ==============================================================================
# 1. Games Home & Catalog APIs
# ==============================================================================

@router.get("/home", response_model=EmergencyGamesHomeResponse, summary="Get Games Home Dashboard")
@router.get("/home/{child_id}", response_model=EmergencyGamesHomeResponse, summary="Get Games Home for Child")
def get_games_home(
    child_id: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve Games Home dashboard including categories, featured games, and recommendations."""
    service = GamesService(db)
    return service.get_games_home(child_id=child_id, current_user=current_user)


@router.get("", response_model=List[GameResponse], summary="Get Games List")
def get_games_list(
    category: Optional[str] = Query(None, description="Filter by category (Communication, Emotion, Memory, Matching, Focus, Learning, Social Skills, Daily Life Skills)"),
    is_emergency_recommended: Optional[bool] = Query(None, description="Filter by emergency recommendation flag"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve list of available cognitive and skill-development games."""
    service = GamesService(db)
    return service.get_games_list(
        category=category,
        is_emergency_recommended=is_emergency_recommended,
        current_user=current_user
    )


@router.get("/details/{game_id}", response_model=GameResponse, summary="Get Game Details")
@router.get("/{game_id}", response_model=GameResponse, summary="Get Game Details (Alias)")
def get_game_details(
    game_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get complete game definition, instructions, and interactive task configurations."""
    service = GamesService(db)
    return service.get_game_details(game_id=game_id, current_user=current_user)


# ==============================================================================
# 2. Interactive Game Session APIs
# ==============================================================================

@router.post("/sessions/start", response_model=GameSessionStartResponse, summary="Start Game Session")
def start_game_session(
    req: GameSessionStartRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Initialize a new game session with interactive question micro-tasks."""
    service = GamesService(db)
    return service.start_game_session(req, current_user=current_user)


@router.post("/sessions/{session_id}/answer", response_model=GameSessionAnswerResponse, summary="Submit Task Answer")
def answer_task(
    session_id: str,
    req: GameSessionAnswerRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Submit an answer to a game task and receive instant encouraging feedback and reinforcement."""
    service = GamesService(db)
    return service.answer_task(session_id=session_id, req=req, current_user=current_user)


@router.post("/sessions/{session_id}/complete", response_model=GameSessionCompleteResponse, summary="Complete Game Session")
def complete_game_session(
    session_id: str,
    req: GameSessionCompleteRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Complete a game session, calculate score and stars (0-3), award badges, and connect to Learning progress."""
    service = GamesService(db)
    return service.complete_game_session(session_id=session_id, req=req, current_user=current_user)


@router.get("/sessions/recent", response_model=List[GameSessionResponse], summary="Get Recent Game Sessions")
def get_recent_sessions(
    child_id: Optional[str] = Query(None, description="Optional child ID"),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve history of recently played game sessions."""
    service = GamesService(db)
    objs = service.repo.get_recent_sessions(child_id=child_id, user_id=current_user.id if current_user else None, limit=limit)
    return [GameSessionResponse.model_validate(s) for s in objs]


# ==============================================================================
# 3. Progress, Achievements & AI Recommendations APIs
# ==============================================================================

@router.get("/progress/{child_id}", response_model=List[GameProgressResponse], summary="Get Child Game Progress")
def get_child_progress(
    child_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get mastery and star accumulation progress across games for a child."""
    service = GamesService(db)
    if current_user:
        service._verify_child_access(child_id, current_user)
    objs = service.repo.get_child_progress_list(child_id=child_id)
    return [GameProgressResponse.model_validate(p) for p in objs]


@router.get("/achievements/{child_id}", response_model=List[GameAchievementResponse], summary="Get Child Badges & Achievements")
def get_child_achievements(
    child_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get unlocked skill badges and milestone achievements for a child."""
    service = GamesService(db)
    if current_user:
        service._verify_child_access(child_id, current_user)
    objs = service.repo.get_achievements(child_id=child_id)
    return [GameAchievementResponse.model_validate(a) for a in objs]


@router.get("/recommendations", response_model=GameRecommendationsResponse, summary="Get AI Game Recommendations")
@router.get("/recommendations/{child_id}", response_model=GameRecommendationsResponse, summary="Get AI Game Recommendations for Child")
def get_recommendations(
    child_id: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get personalized AI skill development game recommendations based on emotional state and learning needs."""
    service = GamesService(db)
    return service.get_recommendations(child_id=child_id, current_user=current_user)


# ==============================================================================
# 4. Caregiver Remote Supervisory Review API
# ==============================================================================

@router.get(
    "/caregiver-review/{child_id}",
    response_model=CaregiverGamesReviewResponse,
    summary="Caregiver Remote Games & Skill Development Review"
)
@router.get(
    "/caregiver-summary/{child_id}",
    response_model=CaregiverGamesReviewResponse,
    summary="Caregiver Remote Games Summary (Alias)"
)
def get_caregiver_review(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caregiver remote supervisory review of child cognitive game sessions,
    total stars earned, skill category mastery breakdown, and unlocked achievements.
    """
    service = GamesService(db)
    return service.get_caregiver_review(child_id=child_id, current_user=current_user)
