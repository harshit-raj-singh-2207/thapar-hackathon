from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.communication.repository import CommunicationRepository
from app.domains.communication.models import AACCategory, AACCard, SavedPhrase, CommunicationLog
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
    EmergencyCommunicationModeResponse,
    CaregiverCommunicationReviewResponse,
    CaregiverEmotionReviewResponse,
    EmergencyEmotionSummaryResponse,
)
from app.domains.communication.aac_service import AACService
from app.domains.communication.emotion_service import EmotionService
from app.domains.communication.speech_service import SpeechService
from app.ai.communication_ai import CommunicationAI
from app.ai.gateway import SmartAIGateway
from app.models.user import User

class CommunicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommunicationRepository(db)
        self.aac_service = AACService(db)
        self.emotion_service = EmotionService(db)

    # ---------------- AAC Categories & Cards ----------------
    def get_categories(self) -> List[AACCategory]:
        return self.aac_service.get_categories()

    def get_category_by_id(self, category_id: str) -> AACCategory:
        return self.aac_service.get_category_by_id(category_id)

    def get_cards(
        self,
        category: Optional[str] = None,
        child_id: Optional[str] = None,
        user: Optional[User] = None,
        quick_needs_only: bool = False,
        is_active: Optional[bool] = None,
    ) -> List[AACCardResponse]:
        return self.aac_service.get_cards(
            category=category,
            child_id=child_id,
            user=user,
            quick_needs_only=quick_needs_only,
            is_active=is_active,
        )

    def get_card_by_id(self, card_id: str, user: Optional[User] = None) -> AACCardResponse:
        return self.aac_service.get_card_by_id(card_id, user=user)

    def create_card(self, req: AACCardCreate, current_user: User) -> AACCardResponse:
        return self.aac_service.create_card(req, current_user=current_user)

    def update_card(self, card_id: str, req: AACCardUpdate, current_user: User) -> AACCardResponse:
        return self.aac_service.update_card(card_id, req, current_user=current_user)

    def delete_card(self, card_id: str, current_user: User) -> Dict[str, Any]:
        return self.aac_service.delete_card(card_id, current_user=current_user)

    def get_aac_board(self) -> List[Dict[str, Any]]:
        return self.aac_service.get_categories_with_cards()

    # ---------------- AI Sentence Building & NLP ----------------
    def build_aac_sentence(
        self,
        req: AACSentenceBuildRequest,
        current_user: Optional[User] = None
    ) -> AACSentenceBuildResponse:
        return self.aac_service.build_aac_sentence(req, current_user=current_user)

    def build_sentence(
        self,
        req: SentenceBuildRequest,
        current_user: Optional[User] = None
    ) -> SentenceBuildResponse:
        # Verify child authorization if child_id provided
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        res = CommunicationAI.generate_sentence_from_tokens(
            tokens=req.tokens,
            sentence=req.sentence,
            emotion=req.emotion,
            context=req.context,
            style=req.style or "natural"
        )
        gateway_result = SmartAIGateway(self.db).build_aac_sentence(
            tokens=req.tokens,
            sentence=req.sentence,
            user_id=current_user.id if current_user else None,
            fallback=lambda: res["generated_sentence"],
            context={"emotion": req.emotion, "style": req.style, "context": req.context},
        )
        res["generated_sentence"] = gateway_result.text
        
        # Log communication attempt
        saved_log_id = None
        if res.get("generated_sentence"):
            log = CommunicationLog(
                user_id=current_user.id if current_user else None,
                sentence=res["generated_sentence"],
                source="ai_sentence",
                emotion=req.emotion,
                audio_played=True,
            )
            saved_log = self.repo.create_log(log)
            saved_log_id = saved_log.id

        return SentenceBuildResponse(
            raw_tokens=res.get("raw_tokens", []),
            generated_sentence=res["generated_sentence"],
            suggested_alternatives=res.get("suggested_alternatives", []),
            simplified_sentence=res.get("simplified_sentence"),
            suggestions=res.get("suggestions", []),
            is_fallback=res.get("is_fallback", False),
            audio_hint=res.get("audio_hint"),
            timestamp=datetime.utcnow(),
            log_id=saved_log_id,
        )

    def simplify_text(
        self,
        req: SimplifyTextRequest,
        current_user: Optional[User] = None
    ) -> SimplifyTextResponse:
        # Verify child authorization if child_id provided
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        target_text = req.text if req.text is not None else (req.sentence or "")
        res = CommunicationAI.simplify_complex_text(
            text=target_text,
            target_level=req.target_level or "easy",
            context=req.context
        )
        gateway_result = SmartAIGateway(self.db).simplify_message(
            text=target_text,
            user_id=current_user.id if current_user else None,
            fallback=lambda: res.get("simplified_text", target_text),
            context={"target_level": req.target_level, "context": req.context},
        )
        res["simplified_text"] = gateway_result.text
        res["simplified_sentence"] = gateway_result.text
        return SimplifyTextResponse(
            original_text=res.get("original_text", target_text),
            simplified_text=res.get("simplified_text", ""),
            simplified_sentence=res.get("simplified_sentence", ""),
            key_points=res.get("key_points", []),
            matching_aac_tokens=res.get("matching_aac_tokens", []),
            suggestions=res.get("suggestions", []),
            is_fallback=res.get("is_fallback", False),
        )

    def synthesize_speech(
        self,
        req: TextToSpeechRequest,
        current_user: Optional[User] = None
    ) -> TextToSpeechResponse:
        # Validate text up front
        if not req.text or not req.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text must not be empty for speech synthesis."
            )
        if len(req.text.strip()) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long. Maximum 500 characters allowed."
            )

        # Verify child authorization if provided
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        res = SpeechService.synthesize_speech_metadata(req, child_id=req.child_id)
        return TextToSpeechResponse(
            text=res.get("text", req.text or ""),
            audio_url=res.get("audio_url"),
            phonetic_guide=res.get("phonetic_guide"),
            ssml_hint=res.get("ssml_hint"),
            web_speech_config=res.get("web_speech_config"),
            duration_estimate_sec=res.get("duration_estimate_sec", 1.5),
            voice_used=res.get("voice_used", "friendly_child"),
            is_fallback=res.get("is_fallback", False),
            provider=res.get("provider", "web_speech_api"),
        )

    def synthesize_aac_speech(
        self,
        req: AACSpeechRequest,
        current_user: Optional[User] = None
    ) -> TextToSpeechResponse:
        # Validate tokens up front
        if not req.tokens or not [t for t in req.tokens if str(t).strip()]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tokens must not be empty for AAC speech synthesis."
            )

        # Verify child authorization if provided
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        try:
            res = SpeechService.synthesize_aac_tokens(
                tokens=req.tokens,
                voice=req.voice,
                speed=req.speed or 1.0,
                pitch=req.pitch or 1.0,
                language=req.language or "en-US",
                emotion=req.emotion,
                child_id=req.child_id,
            )
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )

        return TextToSpeechResponse(
            text=res.get("text", ""),
            audio_url=res.get("audio_url"),
            phonetic_guide=res.get("phonetic_guide"),
            ssml_hint=res.get("ssml_hint"),
            web_speech_config=res.get("web_speech_config"),
            duration_estimate_sec=res.get("duration_estimate_sec", 1.5),
            voice_used=res.get("voice_used", "friendly_child"),
            is_fallback=res.get("is_fallback", False),
            provider=res.get("provider", "web_speech_api"),
        )

    def synthesize_ai_sentence_speech(
        self,
        req: AISentenceSpeechRequest,
        current_user: Optional[User] = None
    ) -> TextToSpeechResponse:
        # Validate sentence up front
        if not req.sentence or not req.sentence.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sentence must not be empty for AI speech synthesis."
            )
        if len(req.sentence.strip()) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sentence too long. Maximum 500 characters allowed."
            )

        # Verify child authorization if provided
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        try:
            res = SpeechService.synthesize_ai_sentence(
                sentence=req.sentence,
                emotion=req.emotion,
                voice=req.voice,
                speed=req.speed or 1.0,
                pitch=req.pitch or 1.0,
                language=req.language or "en-US",
                child_id=req.child_id,
            )
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )

        return TextToSpeechResponse(
            text=res.get("text", req.sentence or ""),
            audio_url=res.get("audio_url"),
            phonetic_guide=res.get("phonetic_guide"),
            ssml_hint=res.get("ssml_hint"),
            web_speech_config=res.get("web_speech_config"),
            duration_estimate_sec=res.get("duration_estimate_sec", 1.5),
            voice_used=res.get("voice_used", "friendly_child"),
            is_fallback=res.get("is_fallback", False),
            provider=res.get("provider", "web_speech_api"),
        )


    # ---------------- Emotion Check-in & Suggestions ----------------
    def checkin_emotion(
        self,
        req: EmotionCheckinRequest,
        current_user: Optional[User] = None
    ) -> EmotionCheckinResponse:
        return self.emotion_service.record_emotion_checkin(req, current_user=current_user)

    def get_emotion_history(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None,
        limit: int = 20
    ) -> List[EmotionCheckinResponse]:
        return self.emotion_service.get_recent_checkins(child_id=child_id, current_user=current_user, limit=limit)

    def get_emotion_suggestions(
        self,
        emotion: str,
        intensity: int = 5,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> EmotionSuggestionsResponse:
        return self.emotion_service.get_emotion_suggestions(
            emotion=emotion,
            intensity=intensity,
            child_id=child_id,
            current_user=current_user
        )

    def get_caregiver_emotion_review(
        self,
        child_id: str,
        current_user: Optional[User] = None
    ) -> CaregiverEmotionReviewResponse:
        return self.emotion_service.get_caregiver_emotion_review(child_id=child_id, current_user=current_user)

    def get_emergency_emotion_summary(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> EmergencyEmotionSummaryResponse:
        return self.emotion_service.get_emergency_emotion_summary(child_id=child_id, current_user=current_user)

    # ---------------- Quick Communication & Favorite Phrases ----------------
    def get_common_phrases(
        self,
        category: Optional[str] = None,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> List[SavedPhrase]:
        if child_id:
            self.aac_service._verify_child_access(child_id, current_user)

        # Ensure all standard default emergency items are present in DB
        default_items = [
            ("I need help", "Emergency & Help", "🆘"),
            ("I don't feel well", "Emergency & Health", "🤒"),
            ("I am scared", "Emergency & Feelings", "😨"),
            ("I am hungry", "Food & Drink", "🍽️"),
            ("I need water", "Food & Drink", "🥤"),
            ("I want to talk", "Communication", "💬"),
            ("I need quiet", "Comfort & Calm", "🤫"),
            ("I want my caregiver", "Caregiver & Family", "🫂"),
            ("I need a break", "Comfort & Calm", "⏸️"),
            ("I feel sick", "Emergency & Health", "🤢"),
            ("Please help me", "Emergency & Help", "🙏"),
            ("Yes, please", "Quick Responses", "👍"),
            ("No, thank you", "Quick Responses", "✋"),
            ("I want to play", "Activities", "🧸"),
            ("I need the toilet", "Daily Needs", "🚻"),
            ("I feel uncomfortable", "Feelings", "😣"),
        ]
        for text, cat, icon in default_items:
            existing = self.repo.find_duplicate_phrase(
                text=text,
                user_id=None,
                child_id=None,
            )
            if not existing:
                p = SavedPhrase(
                    text=text,
                    category=cat,
                    icon=icon,
                    is_favorite=False,
                    usage_count=10,
                    use_count=10,
                )
                self.repo.create_saved_phrase(p)

        phrases = self.repo.get_phrases(
            user_id=current_user.id if current_user else None,
            child_id=child_id,
            favorites_only=False,
            category=category
        )
        return phrases



    def get_favorite_phrases(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None,
        category: Optional[str] = None
    ) -> List[SavedPhrase]:
        if child_id:
            self.aac_service._verify_child_access(child_id, current_user)
        return self.repo.get_phrases(
            user_id=current_user.id if current_user else None,
            child_id=child_id,
            favorites_only=True,
            category=category
        )

    def save_favorite_phrase(
        self,
        req: SavedPhraseCreate,
        current_user: Optional[User] = None
    ) -> SavedPhrase:
        if not req.text or not req.text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Phrase text cannot be empty."
            )
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        user_id = current_user.id if current_user else None

        # Check duplicate favorite
        existing = self.repo.find_duplicate_phrase(
            text=req.text,
            user_id=user_id,
            child_id=req.child_id
        )
        if existing and existing.is_favorite:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Favorite phrase '{req.text}' already exists."
            )

        phrase = SavedPhrase(
            child_id=req.child_id,
            user_id=user_id,
            text=req.text.strip(),
            tokens=req.tokens or [],
            category=req.category or "Quick Communication",
            icon=req.icon or "⭐",
            is_favorite=req.is_favorite,
            usage_count=0,
            use_count=0,
        )
        return self.repo.create_saved_phrase(phrase)

    def delete_favorite_phrase(
        self,
        phrase_id: str,
        current_user: Optional[User] = None
    ) -> Dict[str, str]:
        phrase = self.repo.get_phrase_by_id(phrase_id)
        if not phrase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phrase not found."
            )

        # Authorization check
        if current_user:
            if phrase.child_id:
                self.aac_service._verify_child_access(phrase.child_id, current_user)
            elif phrase.user_id and phrase.user_id != current_user.id and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this phrase."
                )

        self.repo.delete_saved_phrase(phrase_id)
        return {"message": "Favorite phrase deleted successfully"}

    def record_phrase_usage(
        self,
        req: PhraseUsageRequest,
        current_user: Optional[User] = None
    ) -> PhraseUsageResponse:
        phrase = None
        spoken_text = ""
        usage_count = 1

        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        if req.phrase_id:
            phrase = self.repo.get_phrase_by_id(req.phrase_id)
            if not phrase:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Phrase with ID '{req.phrase_id}' not found."
                )
            if phrase.child_id and current_user:
                self.aac_service._verify_child_access(phrase.child_id, current_user)
            updated_phrase = self.repo.increment_phrase_usage(req.phrase_id)
            spoken_text = updated_phrase.text if updated_phrase else phrase.text
            usage_count = updated_phrase.usage_count if updated_phrase else phrase.usage_count
        elif req.text and req.text.strip():
            spoken_text = req.text.strip()
            # Try to match existing phrase by text
            existing = self.repo.find_duplicate_phrase(
                text=spoken_text,
                user_id=current_user.id if current_user else None,
                child_id=req.child_id
            )
            if existing:
                updated = self.repo.increment_phrase_usage(existing.id)
                usage_count = updated.usage_count if updated else 1
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Either phrase_id or text must be provided."
            )

        # Log spoken communication
        log = CommunicationLog(
            user_id=current_user.id if current_user else None,
            sentence=spoken_text,
            source="quick_phrase",
            emotion=req.emotion,
            audio_played=True,
        )
        saved_log = self.repo.create_log(log)

        return PhraseUsageResponse(
            phrase_id=phrase.id if phrase else None,
            text=spoken_text,
            usage_count=usage_count,
            spoken_sentence=spoken_text,
            timestamp=datetime.utcnow(),
            log_id=saved_log.id,
        )

    # Aliases for backward compatibility
    def get_saved_phrases(self, user_id: Optional[str] = None) -> List[SavedPhrase]:
        return self.get_favorite_phrases(current_user=User(id=user_id, email="", full_name="", role="caregiver") if user_id else None)

    def save_phrase(self, req: SavedPhraseCreate, user_id: Optional[str] = None) -> SavedPhrase:
        user = User(id=user_id, email="", full_name="", role="caregiver") if user_id else None
        return self.save_favorite_phrase(req, current_user=user)

    def delete_saved_phrase(self, phrase_id: str) -> bool:
        phrase = self.repo.get_phrase_by_id(phrase_id)
        if not phrase:
            return False
        return self.repo.delete_saved_phrase(phrase_id)

    def log_communication(
        self,
        req: CommunicationLogCreate,
        user_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> CommunicationLog:
        uid = user_id or (current_user.id if current_user else None)
        # Verify child access if provided
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)
        log = CommunicationLog(
            user_id=uid,
            child_id=req.child_id,
            sentence=req.sentence,
            tokens=req.tokens or [],
            source=req.source,
            category=req.category,
            emotion=req.emotion,
            audio_played=req.audio_played,
            is_favorite=req.is_favorite,
        )
        return self.repo.create_log(log)

    def get_communication_logs(self, user_id: Optional[str] = None, limit: int = 30) -> List[CommunicationLog]:
        """Legacy: returns simple list."""
        return self.repo.get_logs(user_id=user_id, limit=limit)

    # ---- Full history with pagination, search, filter ----

    def get_history(
        self,
        filters: CommunicationHistoryFilter,
        current_user: Optional[User] = None,
    ) -> CommunicationHistoryPage:
        if filters.child_id:
            self.aac_service._verify_child_access(filters.child_id, current_user)
        user_id = current_user.id if current_user else None
        items, total = self.repo.get_history_page(
            user_id=user_id,
            child_id=filters.child_id,
            source=filters.source,
            category=filters.category,
            emotion=filters.emotion,
            favorites_only=filters.favorites_only,
            search=filters.search,
            date_from=filters.date_from,
            date_to=filters.date_to,
            page=filters.page,
            page_size=filters.page_size,
        )
        pages = max(1, -(-total // filters.page_size))  # ceiling division
        return CommunicationHistoryPage(
            items=items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            pages=pages,
            has_next=filters.page < pages,
            has_prev=filters.page > 1,
        )

    def get_history_entry(
        self,
        log_id: str,
        current_user: Optional[User] = None,
    ) -> CommunicationLog:
        log = self.repo.get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found.")
        # Ownership check: if user_id set, verify it matches
        if log.user_id and current_user and log.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        return log

    def get_recent_history(
        self,
        child_id: Optional[str] = None,
        limit: int = 10,
        current_user: Optional[User] = None,
    ) -> List[CommunicationLog]:
        if child_id:
            self.aac_service._verify_child_access(child_id, current_user)
        user_id = current_user.id if current_user else None
        return self.repo.get_recent_logs(user_id=user_id, child_id=child_id, limit=limit)

    def delete_history_entry(
        self,
        log_id: str,
        current_user: Optional[User] = None,
    ) -> dict:
        log = self.repo.get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found.")
        if log.user_id and current_user and log.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        self.repo.soft_delete_log(log_id)
        return {"deleted": True, "id": log_id}

    def toggle_history_favorite(
        self,
        log_id: str,
        current_user: Optional[User] = None,
    ) -> CommunicationLog:
        log = self.repo.get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found.")
        if log.user_id and current_user and log.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        result = self.repo.toggle_log_favorite(log_id)
        return result

    def replay_history_entry(
        self,
        log_id: str,
        current_user: Optional[User] = None,
    ) -> CommunicationLog:
        """
        Replay: fetch the original entry and create a new log entry
        stamped with the current timestamp so it appears in history again.
        """
        original = self.get_history_entry(log_id, current_user=current_user)
        replayed = CommunicationLog(
            user_id=original.user_id,
            child_id=original.child_id,
            sentence=original.sentence,
            tokens=original.tokens or [],
            source=original.source,
            category=original.category,
            emotion=original.emotion,
            audio_played=True,
            is_favorite=False,
        )
        return self.repo.create_log(replayed)

    # ---------------- Emergency Communication Mode & Caregiver Review ----------------

    def get_emergency_communication_mode(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> EmergencyCommunicationModeResponse:
        """
        Provides unified Emergency Communication Mode bundle for remote child independence.
        Aggregates common emergency phrases, AAC quick-needs, favorites, top phrases,
        recent history, calming strategies, and speech synthesis configuration.
        """
        child_name = None
        if child_id:
            child = self.aac_service._verify_child_access(child_id, current_user)
            child_name = getattr(child, "name", None) or getattr(child, "full_name", None)
        elif current_user:
            if getattr(current_user, "children", None):
                c = current_user.children[0]
                child_id = c.id
                child_name = getattr(c, "name", None) or getattr(c, "full_name", None)

        # 1. Fetch common/emergency phrases
        phrases = self.get_common_phrases(child_id=child_id, current_user=current_user)
        phrase_responses = [SavedPhraseResponse.model_validate(p) for p in phrases]

        # 2. Fetch quick-needs AAC cards
        quick_cards = self.get_cards(child_id=child_id, user=current_user, quick_needs_only=True)
        if not quick_cards:
            quick_cards = self.get_cards(child_id=child_id, user=current_user)

        # 3. Favorite phrases
        favorites = self.get_favorite_phrases(child_id=child_id, current_user=current_user)
        favorite_responses = [SavedPhraseResponse.model_validate(f) for f in favorites]

        # 4. Frequently used phrases
        top_phrases = self.repo.get_top_used_phrases(
            child_id=child_id,
            user_id=current_user.id if current_user else None,
            limit=10
        )
        top_responses = [SavedPhraseResponse.model_validate(tp) for tp in top_phrases]

        # 5. Recent communication logs
        recent_logs = self.get_recent_history(child_id=child_id, current_user=current_user, limit=10)
        log_responses = [CommunicationLogResponse.model_validate(l) for l in recent_logs]

        # 6. Calming strategies
        calming_strategies = [
            "Take 3 deep breaths with the visual balloon coach.",
            "Listen to calming rain or ocean waves in Sensory audio.",
            "Use the quiet corner symbol strip if sounds are too loud.",
            "Drink a sip of cool water.",
            "Ask caregiver for a comforting hug or squeeze toy.",
        ]

        # 7. Speech configuration
        speech_config = {
            "rate": 0.9,
            "pitch": 1.0,
            "lang": "en-US",
            "voice": "friendly_child",
            "volume": 1.0,
        }

        return EmergencyCommunicationModeResponse(
            child_id=child_id,
            child_name=child_name,
            status="active",
            is_emergency_mode=True,
            emergency_phrases=phrase_responses,
            quick_needs_cards=quick_cards,
            favorite_phrases=favorite_responses,
            frequently_used_phrases=top_responses,
            recent_history=log_responses,
            calming_strategies=calming_strategies,
            speech_config=speech_config,
        )

    def get_caregiver_communication_review(
        self,
        child_id: str,
        current_user: User
    ) -> CaregiverCommunicationReviewResponse:
        """
        Caregiver remote supervision view for reviewing child's communication activity
        during isolation/remote emergency.
        """
        child = self.aac_service._verify_child_access(child_id, current_user)
        child_name = getattr(child, "name", None) or getattr(child, "full_name", None) or "Child"

        recent_logs = self.repo.get_recent_logs(child_id=child_id, limit=20)
        top_phrases = self.repo.get_top_used_phrases(child_id=child_id, limit=10)
        emotion_logs = self.repo.get_emotion_logs(child_id=child_id, limit=20)
        favorites = self.get_favorite_phrases(child_id=child_id, current_user=current_user)
        emergency_logs = self.repo.get_emergency_logs(child_id=child_id, limit=20)
        total_logs = self.repo.count_logs(child_id=child_id)

        return CaregiverCommunicationReviewResponse(
            child_id=child.id,
            child_name=child_name,
            caregiver_id=current_user.id,
            recent_communications=[CommunicationLogResponse.model_validate(l) for l in recent_logs],
            frequently_used_phrases=[SavedPhraseResponse.model_validate(p) for p in top_phrases],
            emotion_communications=[CommunicationLogResponse.model_validate(l) for l in emotion_logs],
            saved_favorite_phrases=[SavedPhraseResponse.model_validate(f) for f in favorites],
            emergency_communications=[CommunicationLogResponse.model_validate(l) for l in emergency_logs],
            emergency_phrases_count=len(emergency_logs),
            total_logs_count=total_logs,
        )

