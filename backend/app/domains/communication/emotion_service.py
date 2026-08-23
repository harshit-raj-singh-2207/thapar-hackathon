from typing import Dict, Any, List, Optional
from collections import Counter
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.communication.repository import CommunicationRepository
from app.domains.communication.models import EmotionRecord, CommunicationLog
from app.domains.communication.schemas import (
    EmotionCheckinRequest,
    EmotionCheckinResponse,
    EmotionSuggestionsResponse,
    CaregiverEmotionReviewResponse,
    EmergencyEmotionSummaryResponse,
)
from app.domains.communication.aac_service import AACService
from app.ai.emotion_ai import EmotionAI
from app.models.user import User
from app.models.child import Child
from app.models.emergency_mode import EmergencyMode

class EmotionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommunicationRepository(db)
        self.aac_service = AACService(db)

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
            pref = emg.preferences
            return bool(
                getattr(pref, "emotion_support_enabled", True) or 
                getattr(pref, "emotional_support_enabled", True)
            )
        return True

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

        is_emg = req.is_emergency_mode if req.is_emergency_mode is not None else self._is_emergency_active(req.child_id)
        rec = EmotionAI.get_emotion_recommendations(clean_emotion, req.intensity, is_emergency_mode=is_emg)

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

        # Cross-log into CommunicationLog so it integrates with full communication history
        primary_phrase = rec.get("recommended_phrases", [f"I feel {clean_emotion}."])[0]
        try:
            log_entry = CommunicationLog(
                user_id=current_user.id if current_user else None,
                child_id=req.child_id,
                sentence=primary_phrase,
                tokens=[clean_emotion.upper()],
                source="emotion",
                category="Emotions",
                emotion=clean_emotion,
                audio_played=True,
            )
            self.repo.create_log(log_entry)
        except Exception:
            pass

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
            suitable_activity=rec.get("suitable_activity"),
            intensity_level=rec.get("intensity_level", "medium"),
            caregiver_alert_recommended=rec.get("caregiver_alert_recommended", False),
            immediate_calming_guidance=rec.get("immediate_calming_guidance"),
            is_emergency_mode=is_emg,
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
        is_emg = self._is_emergency_active(child_id)
        
        result = []
        for r in records:
            rec = EmotionAI.get_emotion_recommendations(r.emotion, r.intensity, is_emergency_mode=is_emg)
            result.append(
                EmotionCheckinResponse(
                    id=r.id,
                    child_id=r.child_id,
                    user_id=r.user_id,
                    emotion=r.emotion,
                    intensity=r.intensity,
                    note=r.note,
                    icon=r.icon or rec.get("icon", "❤️"),
                    calming_strategies=r.calming_strategies or rec.get("calming_strategies", []),
                    sensory_tip=r.sensory_tip or rec.get("sensory_tip"),
                    recommended_phrases=r.recommended_phrases or rec.get("recommended_phrases", []),
                    communication_suggestions=r.recommended_phrases or rec.get("communication_suggestions", []),
                    suitable_activity=rec.get("suitable_activity"),
                    intensity_level=rec.get("intensity_level", "medium"),
                    caregiver_alert_recommended=rec.get("caregiver_alert_recommended", False),
                    immediate_calming_guidance=rec.get("immediate_calming_guidance"),
                    is_emergency_mode=is_emg,
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

        is_emg = self._is_emergency_active(child_id)
        rec = EmotionAI.get_emotion_recommendations(clean_emotion, intensity, is_emergency_mode=is_emg)
        return EmotionSuggestionsResponse(
            emotion=clean_emotion,
            intensity=intensity,
            icon=rec.get("icon", "❤️"),
            calming_strategies=rec.get("calming_strategies", []),
            sensory_tip=rec.get("sensory_tip", ""),
            recommended_phrases=rec.get("recommended_phrases", []),
            communication_suggestions=rec.get("communication_suggestions", []),
            suitable_activity=rec.get("suitable_activity"),
            intensity_level=rec.get("intensity_level", "medium"),
            caregiver_alert_recommended=rec.get("caregiver_alert_recommended", False),
            immediate_calming_guidance=rec.get("immediate_calming_guidance"),
            is_fallback=rec.get("is_fallback", False),
        )

    def get_caregiver_emotion_review(
        self,
        child_id: str,
        current_user: Optional[User] = None
    ) -> CaregiverEmotionReviewResponse:
        """
        Caregiver remote review of child emotional state and distress history.
        Strictly verifies ownership: returns 403 Forbidden for unauthorized caregivers,
        and 404 Not Found if child does not exist.
        """
        self.aac_service._verify_child_access(child_id, current_user)

        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(status_code=404, detail=f"Child '{child_id}' not found.")

        is_emg = False
        emg_status = "inactive"
        if child.emergency_mode:
            emg = child.emergency_mode
            emg_status = emg.effective_status
            is_emg = (emg_status == "active")

        records = self.repo.get_child_emotions(child_id=child_id, limit=50)

        # Convert to response items
        items = []
        high_alerts = []
        all_strategies = []
        activities = []

        for r in records:
            rec = EmotionAI.get_emotion_recommendations(r.emotion, r.intensity, is_emergency_mode=is_emg)
            item = EmotionCheckinResponse(
                id=r.id,
                child_id=r.child_id,
                user_id=r.user_id,
                emotion=r.emotion,
                intensity=r.intensity,
                note=r.note,
                icon=r.icon or rec.get("icon", "❤️"),
                calming_strategies=r.calming_strategies or rec.get("calming_strategies", []),
                sensory_tip=r.sensory_tip or rec.get("sensory_tip"),
                recommended_phrases=r.recommended_phrases or rec.get("recommended_phrases", []),
                communication_suggestions=r.recommended_phrases or rec.get("communication_suggestions", []),
                suitable_activity=rec.get("suitable_activity"),
                intensity_level=rec.get("intensity_level", "medium"),
                caregiver_alert_recommended=rec.get("caregiver_alert_recommended", False),
                immediate_calming_guidance=rec.get("immediate_calming_guidance"),
                is_emergency_mode=is_emg,
                created_at=r.created_at,
                timestamp=r.created_at,
                is_fallback=False,
            )
            items.append(item)
            if r.intensity >= 8:
                high_alerts.append(item)
            for s in (r.calming_strategies or []):
                if s not in all_strategies:
                    all_strategies.append(s)
            if rec.get("suitable_activity") and rec["suitable_activity"] not in activities:
                activities.append(rec["suitable_activity"])

        counts = dict(Counter([r.emotion for r in records]))
        avg_intensity = round(sum(r.intensity for r in records) / len(records), 2) if records else 0.0

        return CaregiverEmotionReviewResponse(
            child_id=child.id,
            child_name=child.name,
            caregiver_id=child.caregiver_id,
            is_emergency_mode=is_emg,
            emergency_status=emg_status,
            recent_checkins=items[:20],
            high_intensity_alerts=high_alerts[:10],
            emotion_breakdown=counts,
            average_intensity=avg_intensity,
            active_calming_strategies=all_strategies[:8],
            recommended_activities=activities[:5],
            total_checkins_count=len(records),
            summary_stats={
                "total_checkins": len(records),
                "high_intensity_count": len(high_alerts),
                "dominant_emotion": max(counts, key=counts.get) if counts else "None",
                "average_intensity": avg_intensity,
                "is_emergency_active": is_emg,
            }
        )

    def get_emergency_emotion_summary(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> EmergencyEmotionSummaryResponse:
        """
        Unified 90-Day Emergency Emotion support summary.
        """
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
                    is_emg = (emg_status == "active")

        recent_checkins = self.get_recent_checkins(child_id=resolved_child_id, current_user=current_user, limit=10)

        # Standard emergency sensory strategies
        sensory_strategies = [
            "5-Minute Box Breathing Pause",
            "Safe Sensory Fort / Quiet Corner",
            "Weighted Lap Pad & Gentle Music",
            "Deep Pressure Squeeze Ball",
            "5-4-3-2-1 Sensory Grounding",
        ]

        activities = [
            EmotionAI.EMOTION_KNOWLEDGE_BASE["anxious"]["suitable_activity"],
            EmotionAI.EMOTION_KNOWLEDGE_BASE["calm"]["suitable_activity"],
            EmotionAI.EMOTION_KNOWLEDGE_BASE["happy"]["suitable_activity"],
        ]

        return EmergencyEmotionSummaryResponse(
            child_id=resolved_child_id,
            child_name=child_name,
            is_emergency_mode=is_emg,
            emergency_status=emg_status,
            emotion_support_enabled=True,
            supported_emotions=EmotionAI.SUPPORTED_EMOTIONS,
            recent_checkins=recent_checkins,
            recommended_sensory_strategies=sensory_strategies,
            recommended_activities=activities,
            summary_stats={
                "total_recent_checkins": len(recent_checkins),
                "is_emergency_active": is_emg,
                "supported_emotions_count": len(EmotionAI.SUPPORTED_EMOTIONS),
            }
        )


