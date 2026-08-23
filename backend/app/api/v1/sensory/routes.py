from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.sensory.schemas import SensoryStateCreate, SensoryStateResponse
from app.domains.sensory.service import SensoryStateService
from app.domains.users.models import User


router = APIRouter(prefix="/sensory", tags=["Sensory State"])


@router.post(
    "/state",
    response_model=SensoryStateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report current sensory state",
)
def report_sensory_state(
    request: SensoryStateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SensoryStateResponse:
    return SensoryStateService(db).record_state(current_user.id, request)


@router.get(
    "/latest",
    response_model=Optional[SensoryStateResponse],
    status_code=status.HTTP_200_OK,
    summary="Get latest sensory state",
)
def get_latest_sensory_state(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[SensoryStateResponse]:
    return SensoryStateService(db).get_latest_state(current_user.id)
