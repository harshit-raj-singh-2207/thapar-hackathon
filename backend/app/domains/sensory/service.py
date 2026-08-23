from typing import Optional

from sqlalchemy.orm import Session

from app.domains.sensory.models import SensoryStateRecord
from app.domains.sensory.calm_strategies import get_calm_strategies
from app.domains.sensory.repository import SensoryStateRepository
from app.domains.sensory.schemas import SensoryStateCreate, SensoryStateResponse


class SensoryStateService:
    """Records and reads explicit sensory self-reports without external calls."""

    def __init__(self, db: Session, repository: Optional[SensoryStateRepository] = None):
        self.repository = repository or SensoryStateRepository(db)

    def record_state(
        self, user_id: str, data: SensoryStateCreate
    ) -> SensoryStateResponse:
        record = SensoryStateRecord(
            user_id=user_id,
            sensory_state=data.sensory_state,
            intensity=data.intensity,
            optional_note=data.optional_note,
        )
        saved = self.repository.create(record)
        response = SensoryStateResponse.model_validate(saved)
        return response.model_copy(
            update={"suggestions": get_calm_strategies(response.sensory_state)}
        )

    def get_latest_state(self, user_id: str) -> Optional[SensoryStateResponse]:
        record = self.repository.get_latest_for_user(user_id)
        if record is None:
            return None
        response = SensoryStateResponse.model_validate(record)
        return response.model_copy(
            update={"suggestions": get_calm_strategies(response.sensory_state)}
        )
