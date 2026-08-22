from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.live_state.schemas import LiveStateResponse
from app.domains.live_state.service import LiveStateService
from app.domains.users.models import User


router = APIRouter(prefix="/live-state", tags=["Live State"])


@router.get(
    "/me",
    response_model=LiveStateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user's current Live State",
)
def get_my_live_state(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LiveStateResponse:
    return LiveStateService(db).get_user_live_state(current_user.id)
