from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.device import Device
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceHeartbeat,
    DeviceResponse,
)
from app.services.device_service import device_service

router = APIRouter(prefix="/devices", tags=["Safety - Wearables & Hardware Devices"])

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def register_device(
    data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register a new safety GPS band or wearable device.
    """
    existing = db.query(Device).filter(Device.serial_number == data.serial_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A device with this serial number is already registered."
        )
    device = device_service.register_device(db, data)
    return device

@router.get("/", response_model=List[DeviceResponse])
def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all paired devices for the current caregiver/user.
    """
    user_child_ids = [c.id for c in current_user.children]
    devices = (
        db.query(Device)
        .filter((Device.child_id.in_(user_child_ids)) | (Device.child_id.is_(None)))
        .all()
    )
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get device status, battery level, and hardware details.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found.")
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: str,
    data: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update device settings, active status, or pair with another child.
    """
    device = device_service.update_device(db, device_id, data)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found.")
    return device

@router.post("/heartbeat", status_code=status.HTTP_200_OK)
def process_device_heartbeat(
    data: DeviceHeartbeat,
    db: Session = Depends(get_db)
):
    """
    Hardware endpoint: Receive telemetry ping from GPS band (battery, connectivity).
    """
    res = device_service.handle_heartbeat(db, data)
    if "error" in res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=res["error"])
    return res
