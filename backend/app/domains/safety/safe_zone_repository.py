import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.safe_zone import SafeZone

class SafeZoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, zone_id: str) -> Optional[SafeZone]:
        return self.db.query(SafeZone).filter(SafeZone.id == zone_id).first()

    def get_by_child_id(self, child_id: str, active_only: bool = False) -> List[SafeZone]:
        query = self.db.query(SafeZone).filter(SafeZone.child_id == child_id)
        if active_only:
            query = query.filter(SafeZone.is_active == True)
        return query.order_by(SafeZone.created_at.desc()).all()

    def create(
        self,
        child_id: str,
        name: str,
        latitude: float,
        longitude: float,
        radius: float,
        is_active: bool = True,
        zone_type: str = "circle",
        polygon_coordinates: Optional[List] = None,
        address: Optional[str] = None,
        alert_on_exit: bool = True,
        alert_on_enter: bool = False,
    ) -> SafeZone:
        polygon_str = json.dumps(polygon_coordinates) if polygon_coordinates else None
        now_utc = datetime.now(timezone.utc)

        safe_zone = SafeZone(
            child_id=child_id,
            name=name,
            zone_type=zone_type or "circle",
            center_latitude=latitude,
            center_longitude=longitude,
            radius_meters=radius,
            polygon_coordinates=polygon_str,
            address=address,
            is_active=is_active,
            alert_on_exit=alert_on_exit,
            alert_on_enter=alert_on_enter,
            created_at=now_utc,
            updated_at=now_utc,
        )
        self.db.add(safe_zone)
        self.db.commit()
        self.db.refresh(safe_zone)
        return safe_zone

    def update(self, safe_zone: SafeZone, **kwargs) -> SafeZone:
        for key, value in kwargs.items():
            if value is not None and hasattr(safe_zone, key):
                setattr(safe_zone, key, value)
        safe_zone.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(safe_zone)
        return safe_zone

    def delete(self, safe_zone: SafeZone) -> None:
        self.db.delete(safe_zone)
        self.db.commit()
