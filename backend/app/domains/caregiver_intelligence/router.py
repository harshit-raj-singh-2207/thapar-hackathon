from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.caregiver_intelligence.schemas import CaregiverInsightsResponse
from app.domains.caregiver_intelligence.service import CaregiverIntelligenceService
from app.models.user import User


router = APIRouter(prefix="/caregiver/users", tags=["Caregiver Intelligence"])


@router.get("/{user_id}/insights", response_model=CaregiverInsightsResponse)
def get_user_insights(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaregiverInsightsResponse:
    return CaregiverIntelligenceService(db).get_insights(user_id, current_user)
