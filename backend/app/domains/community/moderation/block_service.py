from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.domains.caregivers.models import CaregiverBlock

class BlockService:
    def __init__(self, db: Session):
        self.db = db

    def block_user(self, blocker_id: str, blocked_id: str) -> CaregiverBlock:
        existing = self.db.query(CaregiverBlock).filter(
            CaregiverBlock.blocker_id == blocker_id, CaregiverBlock.blocked_id == blocked_id
        ).first()
        if existing:
            return existing
        block = CaregiverBlock(blocker_id=blocker_id, blocked_id=blocked_id)
        self.db.add(block)
        self.db.commit()
        self.db.refresh(block)
        return block

    def unblock_user(self, blocker_id: str, blocked_id: str):
        block = self.db.query(CaregiverBlock).filter(
            CaregiverBlock.blocker_id == blocker_id, CaregiverBlock.blocked_id == blocked_id
        ).first()
        if block:
            self.db.delete(block)
            self.db.commit()

    def is_blocked(self, user1_id: str, user2_id: str) -> bool:
        return self.db.query(CaregiverBlock).filter(
            or_(
                and_(CaregiverBlock.blocker_id == user1_id, CaregiverBlock.blocked_id == user2_id),
                and_(CaregiverBlock.blocker_id == user2_id, CaregiverBlock.blocked_id == user1_id),
            )
        ).first() is not None
