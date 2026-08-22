from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.domains.communication.models import AACCategory, AACCard, SavedPhrase, EmotionRecord, CommunicationLog

class CommunicationRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------- Categories ----------------
    def get_categories(self) -> List[AACCategory]:
        return self.db.query(AACCategory).order_by(AACCategory.order.asc(), AACCategory.name.asc()).all()

    def get_category_by_id(self, category_id: str) -> Optional[AACCategory]:
        return self.db.query(AACCategory).filter(AACCategory.id == category_id).first()

    def get_category_by_name(self, name: str) -> Optional[AACCategory]:
        return self.db.query(AACCategory).filter(
            func.lower(AACCategory.name) == name.strip().lower()
        ).first()

    def get_category_by_id_or_name(self, identifier: str) -> Optional[AACCategory]:
        clean = identifier.strip().lower()
        return self.db.query(AACCategory).filter(
            or_(
                func.lower(AACCategory.id) == clean,
                func.lower(AACCategory.name) == clean,
                func.lower(AACCategory.id) == f"cat-{clean}",
            )
        ).first()

    def create_category(self, category: AACCategory) -> AACCategory:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    # ---------------- Cards ----------------
    def get_cards(
        self,
        category_id: Optional[str] = None,
        child_id: Optional[str] = None,
        user_id: Optional[str] = None,
        quick_needs_only: bool = False,
        is_active: Optional[bool] = None,
    ) -> List[AACCard]:
        query = self.db.query(AACCard)

        if category_id:
            query = query.filter(AACCard.category_id == category_id)

        if is_active is not None:
            query = query.filter(AACCard.is_active == is_active)

        if quick_needs_only:
            query = query.filter(AACCard.is_quick_need == True)

        if child_id:
            # Return global cards + cards specifically created for this child
            query = query.filter(
                or_(
                    AACCard.child_id == child_id,
                    and_(AACCard.child_id == None, AACCard.user_id == None),
                )
            )
        elif user_id:
            query = query.filter(
                or_(
                    AACCard.user_id == user_id,
                    and_(AACCard.child_id == None, AACCard.user_id == None),
                )
            )

        return query.order_by(
            AACCard.display_order.asc(),
            AACCard.usage_count.desc(),
            AACCard.created_at.asc()
        ).all()

    def get_card_by_id(self, card_id: str) -> Optional[AACCard]:
        return self.db.query(AACCard).filter(AACCard.id == card_id).first()

    def find_duplicate_card(
        self,
        label: str,
        category_id: Optional[str],
        child_id: Optional[str] = None,
        user_id: Optional[str] = None,
        exclude_card_id: Optional[str] = None
    ) -> Optional[AACCard]:
        query = self.db.query(AACCard).filter(
            func.lower(AACCard.label) == label.strip().lower(),
            AACCard.category_id == category_id,
        )
        if exclude_card_id:
            query = query.filter(AACCard.id != exclude_card_id)

        if child_id:
            query = query.filter(AACCard.child_id == child_id)
        elif user_id:
            query = query.filter(AACCard.user_id == user_id)
        else:
            query = query.filter(AACCard.child_id == None, AACCard.user_id == None)

        return query.first()

    def create_card(self, card: AACCard) -> AACCard:
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card

    def update_card(self, card: AACCard) -> AACCard:
        self.db.commit()
        self.db.refresh(card)
        return card

    def delete_card(self, card_id: str) -> bool:
        card = self.get_card_by_id(card_id)
        if card:
            self.db.delete(card)
            self.db.commit()
            return True
        return False

    def increment_card_usage(self, card_id: str):
        card = self.get_card_by_id(card_id)
        if card:
            card.usage_count = (card.usage_count or 0) + 1
            self.db.commit()

    # ---------------- Saved & Quick Phrases ----------------
    def get_phrase_by_id(self, phrase_id: str) -> Optional[SavedPhrase]:
        return self.db.query(SavedPhrase).filter(SavedPhrase.id == phrase_id).first()

    def find_duplicate_phrase(
        self,
        text: str,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        exclude_id: Optional[str] = None,
    ) -> Optional[SavedPhrase]:
        query = self.db.query(SavedPhrase).filter(
            func.lower(SavedPhrase.text) == text.strip().lower()
        )
        if exclude_id:
            query = query.filter(SavedPhrase.id != exclude_id)
        if child_id:
            query = query.filter(SavedPhrase.child_id == child_id)
        elif user_id:
            query = query.filter(SavedPhrase.user_id == user_id)
        else:
            query = query.filter(SavedPhrase.child_id == None, SavedPhrase.user_id == None)
        return query.first()

    def get_phrases(
        self,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        favorites_only: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> List[SavedPhrase]:
        query = self.db.query(SavedPhrase)
        if child_id:
            query = query.filter(
                (SavedPhrase.child_id == child_id) | 
                ((SavedPhrase.child_id == None) & (SavedPhrase.user_id == None))
            )
        elif user_id:
            query = query.filter((SavedPhrase.user_id == user_id) | (SavedPhrase.user_id == None))

        if favorites_only is not None:
            query = query.filter(SavedPhrase.is_favorite == favorites_only)

        if category:
            query = query.filter(func.lower(SavedPhrase.category) == category.strip().lower())

        return query.order_by(
            SavedPhrase.usage_count.desc(),
            SavedPhrase.use_count.desc(),
            SavedPhrase.created_at.desc()
        ).all()

    def get_saved_phrases(self, user_id: Optional[str] = None) -> List[SavedPhrase]:
        return self.get_phrases(user_id=user_id, favorites_only=True)

    def create_saved_phrase(self, phrase: SavedPhrase) -> SavedPhrase:
        self.db.add(phrase)
        self.db.commit()
        self.db.refresh(phrase)
        return phrase

    def delete_saved_phrase(self, phrase_id: str) -> bool:
        phrase = self.get_phrase_by_id(phrase_id)
        if phrase:
            self.db.delete(phrase)
            self.db.commit()
            return True
        return False

    def increment_phrase_usage(self, phrase_id: str) -> Optional[SavedPhrase]:
        phrase = self.get_phrase_by_id(phrase_id)
        if phrase:
            phrase.usage_count = (phrase.usage_count or 0) + 1
            phrase.use_count = (phrase.use_count or 0) + 1
            phrase.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(phrase)
            return phrase
        return None

    # ---------------- Emotion Records ----------------
    def create_emotion_record(self, record: EmotionRecord) -> EmotionRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_recent_emotions(
        self,
        child_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 20
    ) -> List[EmotionRecord]:
        query = self.db.query(EmotionRecord)
        if child_id:
            query = query.filter(EmotionRecord.child_id == child_id)
        elif user_id:
            query = query.filter((EmotionRecord.user_id == user_id) | (EmotionRecord.user_id == None))
        return query.order_by(EmotionRecord.created_at.desc()).limit(limit).all()


    # ---------------- Communication Logs (History) ----------------
    def create_log(self, log: CommunicationLog) -> CommunicationLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_log_by_id(self, log_id: str) -> Optional[CommunicationLog]:
        return (
            self.db.query(CommunicationLog)
            .filter(CommunicationLog.id == log_id, CommunicationLog.is_deleted == False)
            .first()
        )

    def get_logs(self, user_id: Optional[str] = None, limit: int = 30) -> List[CommunicationLog]:
        """Legacy: simple list for backwards compat."""
        query = self.db.query(CommunicationLog).filter(CommunicationLog.is_deleted == False)
        if user_id:
            query = query.filter(
                (CommunicationLog.user_id == user_id) | (CommunicationLog.user_id == None)
            )
        return query.order_by(CommunicationLog.created_at.desc()).limit(limit).all()

    def get_history_page(
        self,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        source: Optional[str] = None,
        category: Optional[str] = None,
        emotion: Optional[str] = None,
        favorites_only: Optional[bool] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        """
        Paginated, filterable history query.
        Returns (items: List[CommunicationLog], total: int).
        """
        query = self.db.query(CommunicationLog).filter(CommunicationLog.is_deleted == False)

        # Ownership: child scope takes priority, then user scope
        if child_id:
            query = query.filter(CommunicationLog.child_id == child_id)
        elif user_id:
            query = query.filter(
                (CommunicationLog.user_id == user_id) | (CommunicationLog.user_id == None)
            )

        # Filters
        if source:
            query = query.filter(func.lower(CommunicationLog.source) == source.strip().lower())
        if category:
            query = query.filter(func.lower(CommunicationLog.category) == category.strip().lower())
        if emotion:
            query = query.filter(func.lower(CommunicationLog.emotion) == emotion.strip().lower())
        if favorites_only is not None:
            query = query.filter(CommunicationLog.is_favorite == favorites_only)
        if date_from:
            query = query.filter(CommunicationLog.created_at >= date_from)
        if date_to:
            query = query.filter(CommunicationLog.created_at <= date_to)

        # Full-text search on sentence (SQLite: LIKE; PostgreSQL: also LIKE — simple & portable)
        if search and search.strip():
            pattern = f"%{search.strip().lower()}%"
            query = query.filter(func.lower(CommunicationLog.sentence).like(pattern))

        # Total count (before pagination)
        total = query.count()

        # Pagination
        offset = (page - 1) * page_size
        items = (
            query
            .order_by(CommunicationLog.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_recent_logs(
        self,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[CommunicationLog]:
        """Return the N most recent non-deleted history entries."""
        query = self.db.query(CommunicationLog).filter(CommunicationLog.is_deleted == False)
        if child_id:
            query = query.filter(CommunicationLog.child_id == child_id)
        elif user_id:
            query = query.filter(CommunicationLog.user_id == user_id)
        return query.order_by(CommunicationLog.created_at.desc()).limit(limit).all()

    def soft_delete_log(self, log_id: str) -> bool:
        log = self.get_log_by_id(log_id)
        if log:
            log.is_deleted = True
            self.db.commit()
            return True
        return False

    def toggle_log_favorite(self, log_id: str) -> Optional[CommunicationLog]:
        log = self.get_log_by_id(log_id)
        if log:
            log.is_favorite = not log.is_favorite
            self.db.commit()
            self.db.refresh(log)
        return log

