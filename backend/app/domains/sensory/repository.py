from typing import Optional

from sqlalchemy.orm import Session

from app.domains.sensory.models import SensoryStateRecord


class SensoryStateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: SensoryStateRecord) -> SensoryStateRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_for_user(self, user_id: str) -> Optional[SensoryStateRecord]:
        return (
            self.db.query(SensoryStateRecord)
            .filter(SensoryStateRecord.user_id == user_id)
            .order_by(
                SensoryStateRecord.created_at.desc(),
                SensoryStateRecord.id.desc(),
            )
            .first()
        )
