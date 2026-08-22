import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.child import Child
from app.models.safety_event import SafetyEvent
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceHeartbeat
from app.config.settings import settings

logger = logging.getLogger("safety.device")

class DeviceService:
    @staticmethod
    def register_device(db: Session, data: DeviceCreate) -> Device:
        device = Device(
            child_id=data.child_id,
            device_name=data.device_name,
            device_type=data.device_type,
            serial_number=data.serial_number,
            battery_level=data.battery_level or 100,
            firmware_version=data.firmware_version or "v1.2.0",
            is_active=True,
            is_online=True,
            last_ping_at=datetime.now(timezone.utc),
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def update_device(db: Session, device_id: str, data: DeviceUpdate) -> Optional[Device]:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            return None
        if data.child_id is not None:
            device.child_id = data.child_id
        if data.device_name is not None:
            device.device_name = data.device_name
        if data.device_type is not None:
            device.device_type = data.device_type
        if data.is_active is not None:
            device.is_active = data.is_active
        if data.firmware_version is not None:
            device.firmware_version = data.firmware_version
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def handle_heartbeat(db: Session, heartbeat: DeviceHeartbeat) -> Dict[str, Any]:
        device = db.query(Device).filter(Device.serial_number == heartbeat.serial_number).first()
        if not device:
            return {"error": "Device not recognized with given serial number"}

        device.battery_level = heartbeat.battery_level
        device.last_ping_at = datetime.now(timezone.utc)
        device.is_online = True
        if heartbeat.firmware_version:
            device.firmware_version = heartbeat.firmware_version

        events_created = []
        # Check low battery
        if heartbeat.battery_level <= settings.LOW_BATTERY_ALERT_THRESHOLD and device.child_id:
            event = SafetyEvent(
                child_id=device.child_id,
                event_type="low_battery",
                severity="warning",
                title=f"Low Battery on {device.device_name}",
                description=f"Device battery dropped to {heartbeat.battery_level}%. Please charge immediately.",
                latitude=heartbeat.latitude,
                longitude=heartbeat.longitude,
                metadata_json=json.dumps({"battery_level": heartbeat.battery_level}),
            )
            db.add(event)
            events_created.append("low_battery")

        db.commit()
        db.refresh(device)

        return {
            "device_id": device.id,
            "serial_number": device.serial_number,
            "status": "online",
            "battery_level": device.battery_level,
            "last_ping_at": device.last_ping_at.isoformat(),
            "events_triggered": events_created,
        }

device_service = DeviceService()
