from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.communication.repository import CommunicationRepository
from app.domains.communication.models import AACCategory, AACCard, CommunicationLog
from app.domains.communication.schemas import (
    AACCategoryResponse,
    AACCardCreate,
    AACCardUpdate,
    AACCardResponse,
    AACSentenceBuildRequest,
    AACSentenceBuildResponse,
)
from app.models.child import Child
from app.models.user import User
from app.ai.communication_ai import CommunicationAI

class AACService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommunicationRepository(db)

    def _verify_child_access(self, child_id: str, user: Optional[User]) -> Child:
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Child with ID '{child_id}' not found."
            )
        if user and user.role != "admin" and child.caregiver_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access or modify this child's communication resources."
            )
        return child

    def get_categories(self) -> List[AACCategory]:
        return self.repo.get_categories()

    def get_category_by_id(self, category_id: str) -> AACCategory:
        category = self.repo.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID '{category_id}' not found."
            )
        return category

    def get_cards(
        self,
        category: Optional[str] = None,
        child_id: Optional[str] = None,
        user: Optional[User] = None,
        quick_needs_only: bool = False,
        is_active: Optional[bool] = None,
    ) -> List[AACCardResponse]:
        category_id = None
        if category:
            cat_obj = self.repo.get_category_by_id_or_name(category)
            if not cat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category '{category}' not found."
                )
            category_id = cat_obj.id

        if child_id:
            self._verify_child_access(child_id, user)

        cards = self.repo.get_cards(
            category_id=category_id,
            child_id=child_id,
            user_id=user.id if user and not child_id else None,
            quick_needs_only=quick_needs_only,
            is_active=is_active,
        )

        # Build responses with category_name
        categories_map = {c.id: c.name for c in self.repo.get_categories()}
        result = []
        for card in cards:
            resp = AACCardResponse(
                id=card.id,
                category_id=card.category_id,
                category_name=categories_map.get(card.category_id, "General"),
                label=card.label,
                title=card.label,
                spoken_text=card.spoken_text or card.label,
                keyword=card.keyword or card.label.lower(),
                icon=card.icon,
                image_url=card.image_url,
                part_of_speech=card.part_of_speech or "noun",
                bg_color=card.bg_color or "#FFFFFF",
                text_color=card.text_color or "#0F172A",
                usage_count=card.usage_count or 0,
                is_quick_need=card.is_quick_need or False,
                is_active=card.is_active if card.is_active is not None else True,
                display_order=card.display_order or 0,
                child_id=card.child_id,
                user_id=card.user_id,
                created_at=card.created_at,
                updated_at=card.updated_at,
            )
            result.append(resp)
        return result

    def get_card_by_id(self, card_id: str, user: Optional[User] = None) -> AACCardResponse:
        card = self.repo.get_card_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID '{card_id}' not found."
            )
        if card.child_id and user:
            self._verify_child_access(card.child_id, user)

        cat_obj = self.repo.get_category_by_id(card.category_id) if card.category_id else None
        return AACCardResponse(
            id=card.id,
            category_id=card.category_id,
            category_name=cat_obj.name if cat_obj else "General",
            label=card.label,
            title=card.label,
            spoken_text=card.spoken_text or card.label,
            keyword=card.keyword or card.label.lower(),
            icon=card.icon,
            image_url=card.image_url,
            part_of_speech=card.part_of_speech or "noun",
            bg_color=card.bg_color or "#FFFFFF",
            text_color=card.text_color or "#0F172A",
            usage_count=card.usage_count or 0,
            is_quick_need=card.is_quick_need or False,
            is_active=card.is_active if card.is_active is not None else True,
            display_order=card.display_order or 0,
            child_id=card.child_id,
            user_id=card.user_id,
            created_at=card.created_at,
            updated_at=card.updated_at,
        )

    def create_card(self, card_in: AACCardCreate, current_user: User) -> AACCardResponse:
        label = (card_in.title or card_in.label or "").strip()
        if not label:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Card label cannot be empty."
            )

        # Resolve category
        category_id = card_in.category_id
        if not category_id and card_in.category:
            cat_obj = self.repo.get_category_by_id_or_name(card_in.category)
            if not cat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category '{card_in.category}' not found."
                )
            category_id = cat_obj.id
        elif category_id:
            cat_obj = self.repo.get_category_by_id(category_id)
            if not cat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID '{category_id}' not found."
                )

        # Verify child if provided
        if card_in.child_id:
            self._verify_child_access(card_in.child_id, current_user)

        # Check duplicate
        dup = self.repo.find_duplicate_card(
            label=label,
            category_id=category_id,
            child_id=card_in.child_id,
            user_id=current_user.id if not card_in.child_id else None
        )
        if dup:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A card with label '{label}' already exists in this category."
            )

        new_card = AACCard(
            category_id=category_id,
            label=label,
            spoken_text=card_in.spoken_text or label,
            keyword=card_in.keyword or label.lower(),
            icon=card_in.icon or "💬",
            image_url=card_in.image_url,
            part_of_speech=card_in.part_of_speech or "noun",
            bg_color=card_in.bg_color or "#FFFFFF",
            text_color=card_in.text_color or "#0F172A",
            is_quick_need=card_in.is_quick_need or False,
            is_active=card_in.is_active if card_in.is_active is not None else True,
            display_order=card_in.display_order or 0,
            child_id=card_in.child_id,
            user_id=current_user.id,
        )

        saved = self.repo.create_card(new_card)
        cat_obj = self.repo.get_category_by_id(saved.category_id) if saved.category_id else None

        return AACCardResponse(
            id=saved.id,
            category_id=saved.category_id,
            category_name=cat_obj.name if cat_obj else "General",
            label=saved.label,
            title=saved.label,
            spoken_text=saved.spoken_text or saved.label,
            keyword=saved.keyword or saved.label.lower(),
            icon=saved.icon,
            image_url=saved.image_url,
            part_of_speech=saved.part_of_speech,
            bg_color=saved.bg_color,
            text_color=saved.text_color,
            usage_count=saved.usage_count or 0,
            is_quick_need=saved.is_quick_need or False,
            is_active=saved.is_active,
            display_order=saved.display_order,
            child_id=saved.child_id,
            user_id=saved.user_id,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    def update_card(self, card_id: str, card_in: AACCardUpdate, current_user: User) -> AACCardResponse:
        card = self.repo.get_card_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID '{card_id}' not found."
            )

        # Check authorization
        if card.child_id:
            self._verify_child_access(card.child_id, current_user)
        elif card.user_id:
            if current_user.role != "admin" and card.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to modify this card."
                )
        else:
            # System global card
            if current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="System cards cannot be modified by non-admin users."
                )

        # Check category change
        target_category_id = card.category_id
        if card_in.category_id:
            cat_obj = self.repo.get_category_by_id(card_in.category_id)
            if not cat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID '{card_in.category_id}' not found."
                )
            target_category_id = cat_obj.id
            card.category_id = target_category_id
        elif card_in.category:
            cat_obj = self.repo.get_category_by_id_or_name(card_in.category)
            if not cat_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category '{card_in.category}' not found."
                )
            target_category_id = cat_obj.id
            card.category_id = target_category_id

        # Update fields
        new_label = card_in.title or card_in.label
        if new_label is not None:
            clean_label = new_label.strip()
            if not clean_label:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Card label cannot be empty."
                )
            # Check duplicate
            dup = self.repo.find_duplicate_card(
                label=clean_label,
                category_id=target_category_id,
                child_id=card.child_id,
                user_id=card.user_id,
                exclude_card_id=card.id
            )
            if dup:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A card with label '{clean_label}' already exists in this category."
                )
            card.label = clean_label

        if card_in.spoken_text is not None:
            card.spoken_text = card_in.spoken_text
        if card_in.keyword is not None:
            card.keyword = card_in.keyword
        if card_in.icon is not None:
            card.icon = card_in.icon
        if card_in.image_url is not None:
            card.image_url = card_in.image_url
        if card_in.part_of_speech is not None:
            card.part_of_speech = card_in.part_of_speech
        if card_in.bg_color is not None:
            card.bg_color = card_in.bg_color
        if card_in.text_color is not None:
            card.text_color = card_in.text_color
        if card_in.is_quick_need is not None:
            card.is_quick_need = card_in.is_quick_need
        if card_in.is_active is not None:
            card.is_active = card_in.is_active
        if card_in.display_order is not None:
            card.display_order = card_in.display_order

        updated = self.repo.update_card(card)
        cat_obj = self.repo.get_category_by_id(updated.category_id) if updated.category_id else None

        return AACCardResponse(
            id=updated.id,
            category_id=updated.category_id,
            category_name=cat_obj.name if cat_obj else "General",
            label=updated.label,
            title=updated.label,
            spoken_text=updated.spoken_text or updated.label,
            keyword=updated.keyword or updated.label.lower(),
            icon=updated.icon,
            image_url=updated.image_url,
            part_of_speech=updated.part_of_speech,
            bg_color=updated.bg_color,
            text_color=updated.text_color,
            usage_count=updated.usage_count or 0,
            is_quick_need=updated.is_quick_need or False,
            is_active=updated.is_active,
            display_order=updated.display_order,
            child_id=updated.child_id,
            user_id=updated.user_id,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    def delete_card(self, card_id: str, current_user: User) -> Dict[str, Any]:
        card = self.repo.get_card_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID '{card_id}' not found."
            )

        if card.child_id:
            self._verify_child_access(card.child_id, current_user)
        elif card.user_id:
            if current_user.role != "admin" and card.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this card."
                )
        else:
            if current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="System cards cannot be deleted by non-admin users."
                )

        self.repo.delete_card(card_id)
        return {"success": True, "message": "Card deleted successfully", "deleted_id": card_id}

    def get_categories_with_cards(self) -> List[Dict[str, Any]]:
        categories = self.repo.get_categories()
        result = []
        for cat in categories:
            cards = self.repo.get_cards(category_id=cat.id)
            result.append({
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "order": cat.order,
                "cards": [
                    {
                        "id": c.id,
                        "label": c.label,
                        "spoken_text": c.spoken_text or c.label,
                        "icon": c.icon,
                        "part_of_speech": c.part_of_speech,
                        "bg_color": c.bg_color,
                        "text_color": c.text_color,
                        "is_quick_need": c.is_quick_need,
                        "usage_count": c.usage_count,
                    }
                    for c in cards
                ]
            })
        return result

    def get_quick_needs(self) -> List[AACCard]:
        return self.repo.get_cards(quick_needs_only=True)

    def assemble_sentence(self, tokens: List[str], emotion: Optional[str] = None, style: str = "natural") -> Dict[str, Any]:
        # Track usage of cards matching tokens
        for t in tokens:
            card = self.db.query(AACCard).filter(AACCard.label.ilike(t.strip())).first()
            if card:
                self.repo.increment_card_usage(card.id)

        ai_res = CommunicationAI.generate_sentence_from_tokens(tokens, emotion=emotion, style=style)
        return {
            "raw_tokens": tokens,
            "generated_sentence": ai_res["generated_sentence"],
            "suggested_alternatives": ai_res["suggested_alternatives"],
            "simplified_sentence": ai_res["simplified_sentence"],
            "audio_hint": ai_res["audio_hint"],
        }

    def build_aac_sentence(
        self,
        req: AACSentenceBuildRequest,
        current_user: Optional[User] = None
    ) -> AACSentenceBuildResponse:
        # 1. Verify child access if child_id provided
        if req.child_id:
            self._verify_child_access(req.child_id, current_user)

        # 2. Extract inputs
        card_id_list = req.card_ids if req.card_ids is not None else req.token_ids
        raw_tokens_list = req.tokens

        if card_id_list is None and raw_tokens_list is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Token or card list cannot be empty."
            )

        if card_id_list is not None and len(card_id_list) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Card IDs sequence cannot be empty."
            )

        if raw_tokens_list is not None and card_id_list is None and len(raw_tokens_list) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tokens sequence cannot be empty."
            )

        resolved_labels: List[str] = []
        resolved_tokens: List[str] = []
        resolved_card_ids: List[str] = []

        if card_id_list is not None:
            for cid in card_id_list:
                card = self.repo.get_card_by_id(cid)
                if not card:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Card with ID '{cid}' not found."
                    )
                if card.is_active is False:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Card '{card.label}' ({card.id}) is inactive."
                    )
                if card.child_id and current_user:
                    self._verify_child_access(card.child_id, current_user)
                self.repo.increment_card_usage(card.id)
                resolved_labels.append(card.label)
                resolved_tokens.append(card.keyword.upper() if card.keyword else card.label.upper())
                resolved_card_ids.append(card.id)
        else:
            for t in raw_tokens_list:
                clean_t = t.strip()
                if not clean_t:
                    continue
                # Try finding matching card by id or label
                card = self.repo.get_card_by_id(clean_t)
                if not card:
                    card = self.db.query(AACCard).filter(AACCard.label.ilike(clean_t)).first()

                if card:
                    if card.is_active is False:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Card '{card.label}' ({card.id}) is inactive."
                        )
                    if card.child_id and current_user:
                        self._verify_child_access(card.child_id, current_user)
                    self.repo.increment_card_usage(card.id)
                    resolved_labels.append(card.label)
                    resolved_tokens.append(card.keyword.upper() if card.keyword else card.label.upper())
                    resolved_card_ids.append(card.id)
                else:
                    resolved_labels.append(clean_t)
                    resolved_tokens.append(clean_t.upper())

        if not resolved_labels:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No valid tokens found to construct a sentence."
            )

        # 3. Assemble structured sentence preserving input order
        ai_res = CommunicationAI.generate_sentence_from_tokens(
            resolved_labels, emotion=req.emotion, style=req.style or "natural"
        )
        constructed_sentence = ai_res["generated_sentence"]

        # 4. Persistence into CommunicationLog
        log_id = None
        if req.save_log:
            log = CommunicationLog(
                user_id=current_user.id if current_user else None,
                child_id=req.child_id,
                sentence=constructed_sentence,
                tokens=resolved_tokens,
                source="aac",
                emotion=req.emotion,
                audio_played=True,
            )
            saved_log = self.repo.create_log(log)
            log_id = saved_log.id

        now = datetime.utcnow()
        return AACSentenceBuildResponse(
            tokens=resolved_tokens,
            labels=resolved_labels,
            card_ids=resolved_card_ids,
            constructed_sentence=constructed_sentence,
            sentence=constructed_sentence,
            generated_sentence=constructed_sentence,
            simplified_sentence=ai_res.get("simplified_sentence"),
            suggested_alternatives=ai_res.get("suggested_alternatives", []),
            audio_hint=ai_res.get("audio_hint"),
            timestamp=now,
            log_id=log_id,
        )

