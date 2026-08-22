from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.communication.repository import CommunicationRepository
from app.domains.communication.models import EmotionRecord
from app.domains.communication.schemas import EmotionCheckinRequest, EmotionCheckinResponse, EmotionSuggestionsResponse
from app.domains.communication.aac_service import AACService
from app.ai.emotion_ai import EmotionAI
from app.models.user import User

class EmotionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommunicationRepository(db)
        self.aac_service = AACService(db)

    def record_emotion_checkin(
        self,
        req: EmotionCheckinRequest,
        current_user: Optional[User] = None
    ) -> EmotionCheckinResponse:
        # Validate emotion
        clean_emotion = req.emotion.strip().lower() if req.emotion else ""
        if not clean_emotion or clean_emotion not in EmotionAI.SUPPORTED_EMOTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid emotion '{req.emotion}'. Supported emotions: {', '.join(EmotionAI.SUPPORTED_EMOTIONS)}"
            )

        # Validate intensity
        if req.intensity < 1 or req.intensity > 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Emotion intensity must be between 1 and 10."
            )

        # Child authorization check
        if req.child_id:
            self.aac_service._verify_child_access(req.child_id, current_user)

        rec = EmotionAI.get_emotion_recommendations(clean_emotion, req.intensity)

        record = EmotionRecord(
            child_id=req.child_id,
            user_id=current_user.id if current_user else None,
            emotion=clean_emotion,
            intensity=req.intensity,
            note=req.note,
            icon=rec.get("icon", "❤️"),
            calming_strategies=rec.get("calming_strategies", []),
            sensory_tip=rec.get("sensory_tip"),
            recommended_phrases=rec.get("recommended_phrases", []),
        )
        saved = self.repo.create_emotion_record(record)

        return EmotionCheckinResponse(
            id=saved.id,
            child_id=saved.child_id,
            user_id=saved.user_id,
            emotion=saved.emotion,
            intensity=saved.intensity,
            note=saved.note,
            icon=saved.icon,
            calming_strategies=saved.calming_strategies or [],
            sensory_tip=saved.sensory_tip,
            recommended_phrases=saved.recommended_phrases or [],
            communication_suggestions=saved.recommended_phrases or [],
            created_at=saved.created_at,
            timestamp=saved.created_at,
            is_fallback=rec.get("is_fallback", False),
        )

    def get_recent_checkins(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None,
        limit: int = 20
    ) -> List[EmotionCheckinResponse]:
        if child_id:
            self.aac_service._verify_child_access(child_id, current_user)

        user_id = current_user.id if current_user else None
        records = self.repo.get_recent_emotions(child_id=child_id, user_id=user_id, limit=limit)
        
        result = []
        for r in records:
            result.append(
                EmotionCheckinResponse(
                    id=r.id,
                    child_id=r.child_id,
                    user_id=r.user_id,
                    emotion=r.emotion,
                    intensity=r.intensity,
                    note=r.note,
                    icon=r.icon or "❤️",
                    calming_strategies=r.calming_strategies or [],
                    sensory_tip=r.sensory_tip,
                    recommended_phrases=r.recommended_phrases or [],
                    communication_suggestions=r.recommended_phrases or [],
                    created_at=r.created_at,
                    timestamp=r.created_at,
                    is_fallback=False,
                )
            )
        return result

    def get_emotion_suggestions(
        self,
        emotion: str,
        intensity: int = 5,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> EmotionSuggestionsResponse:
        clean_emotion = emotion.strip().lower() if emotion else ""
        if not clean_emotion or clean_emotion not in EmotionAI.SUPPORTED_EMOTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid emotion '{emotion}'. Supported emotions: {', '.join(EmotionAI.SUPPORTED_EMOTIONS)}"
            )

        if intensity < 1 or intensity > 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Emotion intensity must be between 1 and 10."
            )

        if child_id:
            self.aac_service._verify_child_access(child_id, current_user)

        rec = EmotionAI.get_emotion_recommendations(clean_emotion, intensity)
        return EmotionSuggestionsResponse(
            emotion=clean_emotion,
            intensity=intensity,
            icon=rec.get("icon", "❤️"),
            calming_strategies=rec.get("calming_strategies", []),
            sensory_tip=rec.get("sensory_tip", ""),
            recommended_phrases=rec.get("recommended_phrases", []),
            communication_suggestions=rec.get("communication_suggestions", []),
            is_fallback=rec.get("is_fallback", False),
        )

