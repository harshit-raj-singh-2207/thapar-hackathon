from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.domains.safety.caregiver_dashboard_service import CaregiverDashboardService
from app.schemas.caregiver_dashboard import (
    ChildProfileResponse,
    ChildStatusResponse,
    ChildLocationResponse,
    DeviceStatusResponse,
    SafetyOverviewResponse,
    RecentActivityItem,
    AlertSummaryResponse,
)

router = APIRouter(prefix="/caregiver", tags=["Caregiver Dashboard"])

@router.get(
    "/{child_id}/profile",
    response_model=ChildProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Child Profile for Caregiver"
)
def get_child_profile(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CaregiverDashboardService(db)
    return service.get_child_profile(child_id, current_user)

@router.get(
    "/{child_id}/status",
    response_model=ChildStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Aggregated Child Safety Status"
)
def get_child_status(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CaregiverDashboardService(db)
    return service.get_child_status(child_id, current_user)

@router.get(
    "/{child_id}/location",
    response_model=ChildLocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Child Location and Freshness"
)
def get_child_location(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CaregiverDashboardService(db)
    return service.get_child_location(child_id, current_user)

@router.get(
    "/{child_id}/device",
    response_model=DeviceStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Child GPS Band / Device Telemetry"
)
def get_child_device(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CaregiverDashboardService(db)
    return service.get_child_device(child_id, current_user)

@router.get(
    "/{child_id}/safety-overview",
    response_model=SafetyOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Comprehensive Aggregated Safety Overview"
)
def get_safety_overview(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CaregiverDashboardService(db)
    return service.get_safety_overview(child_id, current_user)

@router.get(
    "/{child_id}/recent-activity",
    response_model=List[RecentActivityItem],
    status_code=status.HTTP_200_OK,
    summary="Get Recent Safety Events / Activities"
)
def get_recent_activity(
    child_id: str,
    limit: int = Query(20, ge=1, le=100, description="Max number of recent events to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CaregiverDashboardService(db)
    return service.get_recent_activity(child_id, limit, current_user)

@router.get(
    "/{child_id}/alerts/summary",
    response_model=AlertSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Caregiver Alert Summary and Metrics"
)
def get_alert_summary(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CaregiverDashboardService(db)
    return service.get_alert_summary(child_id, current_user)
