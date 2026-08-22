from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_optional_user
from app.models.user import User
from app.domains.communication.service import CommunicationService
from app.domains.communication.schemas import (
    AACCategoryResponse,
    AACCardCreate,
    AACCardUpdate,
    AACCardResponse,
    AACSentenceBuildRequest,
    AACSentenceBuildResponse,
    SentenceBuildRequest,
    SentenceBuildResponse,
    SimplifyTextRequest,
    SimplifyTextResponse,
    TextToSpeechRequest,
    AACSpeechRequest,
    AISentenceSpeechRequest,
    TextToSpeechResponse,
    EmotionCheckinRequest,
    EmotionCheckinResponse,
    EmotionSuggestionsResponse,
    SavedPhraseCreate,
    SavedPhraseResponse,
    PhraseUsageRequest,
    PhraseUsageResponse,
    CommunicationLogCreate,
    CommunicationLogResponse,
    CommunicationHistoryFilter,
    CommunicationHistoryPage,
)

router = APIRouter(prefix="/communication", tags=["AI Communication & AAC Foundation"])

# ==============================================================================
# AAC Categories & Picture Cards Foundation APIs
# ==============================================================================

@router.get("/categories", response_model=List[AACCategoryResponse], summary="Get AAC Categories")
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all available AAC categories (Quick Needs, Food, Drink, Feelings, Actions, Play)."""
    service = CommunicationService(db)
    return service.get_categories()


@router.get("/cards", response_model=List[AACCardResponse], summary="Get AAC Picture Communication Cards")
def get_cards(
    category: Optional[str] = Query(None, description="Category name or ID filter"),
    category_id: Optional[str] = Query(None, description="Category ID filter"),
    child_id: Optional[str] = Query(None, description="Filter for cards accessible to specific child"),
    is_quick_need: Optional[bool] = Query(None, description="Filter quick need cards"),
    is_active: Optional[bool] = Query(None, description="Filter active cards"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve picture communication cards with optional category, child, and active filtering."""
    service = CommunicationService(db)
    target_category = category_id or category
    return service.get_cards(
        category=target_category,
        child_id=child_id,
        user=current_user,
        quick_needs_only=bool(is_quick_need),
        is_active=is_active,
    )


@router.get("/cards/{category_or_card_id}", summary="Get AAC Cards by Category or Card ID")
def get_cards_by_category_or_id(
    category_or_card_id: str,
    child_id: Optional[str] = Query(None, description="Child ID filter if querying category"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve cards under a specific category (by category id/name) OR retrieve a specific single card by card_id.
    """
    service = CommunicationService(db)

    # 1. Check if category matches identifier
    category_obj = service.repo.get_category_by_id_or_name(category_or_card_id)
    if category_obj:
        return service.get_cards(
            category=category_obj.id,
            child_id=child_id,
            user=current_user,
        )

    # 2. Otherwise try looking up by card_id
    try:
        return service.get_card_by_id(category_or_card_id, user=current_user)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category or Card '{category_or_card_id}' not found."
        )


@router.post(
    "/cards",
    response_model=AACCardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Custom AAC Picture Card"
)
def create_card(
    req: AACCardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AAC picture communication card associated with authenticated user/child."""
    service = CommunicationService(db)
    return service.create_card(req, current_user=current_user)


@router.patch(
    "/cards/{card_id}",
    response_model=AACCardResponse,
    summary="Update AAC Picture Card"
)
def update_card(
    card_id: str,
    req: AACCardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing AAC communication card."""
    service = CommunicationService(db)
    return service.update_card(card_id, req, current_user=current_user)


@router.delete(
    "/cards/{card_id}",
    summary="Delete AAC Picture Card"
)
def delete_card(
    card_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a custom AAC communication card."""
    service = CommunicationService(db)
    return service.delete_card(card_id, current_user=current_user)


# ==============================================================================
# Full AAC Board & AI Natural Sentence Building
# ==============================================================================

@router.get("/aac-board", summary="Get Full AAC Board Hierarchy")
def get_aac_board(db: Session = Depends(get_db)):
    """Retrieve full AAC category & picture card communication board."""
    service = CommunicationService(db)
    return service.get_aac_board()


@router.post(
    "/aac/sentence",
    response_model=AACSentenceBuildResponse,
    summary="Construct Structured Sentence from AAC Tokens"
)
def build_aac_sentence(
    req: AACSentenceBuildRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Validate AAC token sequence, preserve token order, construct structured natural sentence,
    and persist communication event.
    """
    service = CommunicationService(db)
    return service.build_aac_sentence(req, current_user=current_user)


# ==============================================================================
# AI Sentence Generation & Communication Simplification APIs
# ==============================================================================

@router.post("/sentence/generate", response_model=SentenceBuildResponse, summary="AI Sentence Generation from AAC Tokens")
@router.post("/generate-sentence", response_model=SentenceBuildResponse, summary="AI Sentence Generation (Alias)")
@router.post("/build-sentence", response_model=SentenceBuildResponse, summary="Build Natural Sentence from AAC Tokens (Legacy)")
def generate_ai_sentence(
    req: SentenceBuildRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Generate grammatically complete natural, child-friendly sentence and suggestions from AAC tokens."""
    service = CommunicationService(db)
    return service.build_sentence(req, current_user=current_user)


@router.post("/sentence/simplify", response_model=SimplifyTextResponse, summary="Simplify Complex Text")
@router.post("/simplify-text", response_model=SimplifyTextResponse, summary="Simplify Complex Text (Alias)")
@router.post("/simplify", response_model=SimplifyTextResponse, summary="Simplify Text (Alias)")
def simplify_ai_text(
    req: SimplifyTextRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Simplify complex sentences into concise, visual-friendly bullet points and matching AAC tokens."""
    service = CommunicationService(db)
    return service.simplify_text(req, current_user=current_user)




# ==============================================================================
# Text-to-Speech APIs
# ==============================================================================

@router.post("/speech/synthesize", response_model=TextToSpeechResponse, summary="Synthesize Speech from Text")
@router.post("/text-to-speech", response_model=TextToSpeechResponse, summary="Synthesize AAC Speech (Alias)")
@router.post("/tts", response_model=TextToSpeechResponse, summary="TTS Shorthand Alias")
def synthesize_speech(
    req: TextToSpeechRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Convert communication text to speech metadata.
    Returns phonetic guide, SSML hint, and Web Speech API configuration.
    Child authorization enforced when child_id is provided.
    No API keys or provider credentials are ever exposed in the response.
    """
    service = CommunicationService(db)
    return service.synthesize_speech(req, current_user=current_user)


@router.post("/speech/aac", response_model=TextToSpeechResponse, summary="Synthesize Speech from AAC Tokens")
@router.post("/speech/aac-sentence", response_model=TextToSpeechResponse, summary="Synthesize AAC Sentence Speech (Alias)")
def synthesize_aac_speech(
    req: AACSpeechRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Synthesize speech directly from a list of AAC tokens or card labels.
    Child authorization enforced when child_id is provided.
    """
    service = CommunicationService(db)
    return service.synthesize_aac_speech(req, current_user=current_user)


@router.post("/speech/ai-sentence", response_model=TextToSpeechResponse, summary="Synthesize Speech for AI-Generated Sentence")
def synthesize_ai_sentence_speech(
    req: AISentenceSpeechRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Synthesize speech for an AI-generated sentence with emotion tone inflection.
    Child authorization enforced when child_id is provided.
    """
    service = CommunicationService(db)
    return service.synthesize_ai_sentence_speech(req, current_user=current_user)



# ==============================================================================
# Emotion-Aware Communication APIs
# ==============================================================================

@router.post("/emotions/checkin", response_model=EmotionCheckinResponse, summary="Record Emotion Check-in")
@router.post("/emotion-checkin", response_model=EmotionCheckinResponse, summary="Record Emotion Check-in (Alias)")
def emotion_checkin(
    req: EmotionCheckinRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Record an emotion check-in, save state, and receive AI calming suggestions and phrases."""
    service = CommunicationService(db)
    return service.checkin_emotion(req, current_user=current_user)


@router.get("/emotions/history", response_model=List[EmotionCheckinResponse], summary="Get Emotion Check-in History")
@router.get("/emotion-history", response_model=List[EmotionCheckinResponse], summary="Get Emotion Check-in History (Alias)")
def get_emotion_history(
    child_id: Optional[str] = Query(None, description="Optional child ID to filter history"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve history of recorded emotion check-ins."""
    service = CommunicationService(db)
    return service.get_emotion_history(child_id=child_id, current_user=current_user, limit=limit)


@router.get("/emotions/suggestions", response_model=EmotionSuggestionsResponse, summary="Get Emotion Suggestions & Calming Tips")
@router.get("/emotion-suggestions", response_model=EmotionSuggestionsResponse, summary="Get Emotion Suggestions (Alias)")
def get_emotion_suggestions(
    emotion: str = Query(..., description="Emotion name (e.g. happy, sad, angry, anxious, calm, scared, frustrated, overwhelmed)"),
    intensity: int = Query(5, ge=1, le=10, description="Emotion intensity from 1 to 10"),
    child_id: Optional[str] = Query(None, description="Optional child ID"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get real-time emotion calming strategies, sensory grounding tips, and communication phrases."""
    service = CommunicationService(db)
    return service.get_emotion_suggestions(
        emotion=emotion,
        intensity=intensity,
        child_id=child_id,
        current_user=current_user
    )



# ==============================================================================
# Quick Communication & Favorite Phrases APIs
# ==============================================================================

@router.get("/phrases/common", response_model=List[SavedPhraseResponse], summary="Get Common Communication Phrases")
@router.get("/common-phrases", response_model=List[SavedPhraseResponse], summary="Get Common Communication Phrases (Alias)")
def get_common_phrases(
    category: Optional[str] = Query(None, description="Filter common phrases by category"),
    child_id: Optional[str] = Query(None, description="Optional child ID"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve pre-defined and common everyday communication phrases."""
    service = CommunicationService(db)
    return service.get_common_phrases(category=category, child_id=child_id, current_user=current_user)


@router.get("/phrases/favorites", response_model=List[SavedPhraseResponse], summary="Get Favorite Phrases")
@router.get("/favorite-phrases", response_model=List[SavedPhraseResponse], summary="Get Favorite Phrases (Alias)")
@router.get("/saved-phrases", response_model=List[SavedPhraseResponse], summary="Get Saved Favorite Phrases (Legacy)")
def get_favorite_phrases(
    child_id: Optional[str] = Query(None, description="Filter favorites by child ID"),
    category: Optional[str] = Query(None, description="Filter favorites by category"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve saved favorite communication phrases for user or child."""
    service = CommunicationService(db)
    return service.get_favorite_phrases(child_id=child_id, current_user=current_user, category=category)


@router.post("/phrases/favorites", response_model=SavedPhraseResponse, summary="Save Favorite Phrase")
@router.post("/phrases", response_model=SavedPhraseResponse, summary="Save Phrase")
@router.post("/saved-phrases", response_model=SavedPhraseResponse, summary="Save Favorite Phrase (Legacy)")
def save_favorite_phrase(
    req: SavedPhraseCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Save a favorite communication phrase or sentence strip with duplicate prevention."""
    service = CommunicationService(db)
    return service.save_favorite_phrase(req, current_user=current_user)


@router.delete("/phrases/favorites/{phrase_id}", summary="Remove Favorite Phrase")
@router.delete("/phrases/{phrase_id}", summary="Remove Phrase")
@router.delete("/saved-phrases/{phrase_id}", summary="Delete Saved Phrase (Legacy)")
def remove_favorite_phrase(
    phrase_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Remove a saved favorite phrase with ownership validation."""
    service = CommunicationService(db)
    return service.delete_favorite_phrase(phrase_id, current_user=current_user)


@router.post("/phrases/{phrase_id}/usage", response_model=PhraseUsageResponse, summary="Record Phrase Usage By ID")
def record_phrase_usage_by_id(
    phrase_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Record spoken usage of a specific phrase by ID."""
    service = CommunicationService(db)
    req = PhraseUsageRequest(phrase_id=phrase_id)
    return service.record_phrase_usage(req, current_user=current_user)


@router.post("/phrases/usage", response_model=PhraseUsageResponse, summary="Record Phrase Usage")
def record_phrase_usage(
    req: PhraseUsageRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Record spoken usage of a phrase and update usage metrics."""
    service = CommunicationService(db)
    return service.record_phrase_usage(req, current_user=current_user)



# ==============================================================================
# Communication History APIs
# ==============================================================================

@router.get("/history", response_model=CommunicationHistoryPage, summary="Get Paginated Communication History")
def get_communication_history(
    child_id: Optional[str] = Query(None, description="Filter by child ID"),
    source: Optional[str] = Query(None, description="Filter by source: aac, quick_need, ai_sentence, emotion, speech"),
    category: Optional[str] = Query(None, description="Filter by category"),
    emotion: Optional[str] = Query(None, description="Filter by emotion"),
    favorites_only: Optional[bool] = Query(None, description="Return only favorited entries"),
    search: Optional[str] = Query(None, description="Search in sentence text"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO 8601)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO 8601)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Paginated, filterable, searchable communication history."""
    from datetime import datetime as dt
    service = CommunicationService(db)
    filters = CommunicationHistoryFilter(
        child_id=child_id,
        source=source,
        category=category,
        emotion=emotion,
        favorites_only=favorites_only,
        search=search,
        date_from=dt.fromisoformat(date_from) if date_from else None,
        date_to=dt.fromisoformat(date_to) if date_to else None,
        page=page,
        page_size=page_size,
    )
    return service.get_history(filters, current_user=current_user)


@router.get("/history/recent", response_model=List[CommunicationLogResponse], summary="Get Recent Communications")
def get_recent_history(
    child_id: Optional[str] = Query(None, description="Filter by child ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of recent entries to return"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Return the N most recent communication history entries."""
    service = CommunicationService(db)
    return service.get_recent_history(child_id=child_id, limit=limit, current_user=current_user)


@router.get("/history/{log_id}", response_model=CommunicationLogResponse, summary="Get History Entry by ID")
def get_history_entry(
    log_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Retrieve a specific communication history entry by ID."""
    service = CommunicationService(db)
    return service.get_history_entry(log_id, current_user=current_user)


@router.post("/history/{log_id}/replay", response_model=CommunicationLogResponse, summary="Replay a Previous Communication")
def replay_history_entry(
    log_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Replay a previous communication: creates a new log entry with the same sentence/tokens."""
    service = CommunicationService(db)
    return service.replay_history_entry(log_id, current_user=current_user)


@router.post("/history/{log_id}/favorite", response_model=CommunicationLogResponse, summary="Toggle History Favorite")
def toggle_history_favorite(
    log_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Toggle the favorite flag on a communication history entry."""
    service = CommunicationService(db)
    return service.toggle_history_favorite(log_id, current_user=current_user)


@router.delete("/history/{log_id}", summary="Delete History Entry")
def delete_history_entry(
    log_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Soft-delete a communication history entry. Ownership enforced."""
    service = CommunicationService(db)
    return service.delete_history_entry(log_id, current_user=current_user)


@router.post("/log", response_model=CommunicationLogResponse, summary="Log Communication Event")
def log_communication(
    req: CommunicationLogCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Log an AAC or voice communication event to history."""
    service = CommunicationService(db)
    return service.log_communication(req, current_user=current_user)
