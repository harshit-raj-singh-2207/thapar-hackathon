from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.location import Location
from app.models.child import Child

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_child_by_id(self, child_id: str) -> Optional[Child]:
        """Fetch child record by unique child_id."""
        return self.db.query(Child).filter(Child.id == child_id).first()

    def create_location(self, location: Location) -> Location:
        """Persist a new location record to the database."""
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def get_latest_location(self, child_id: str) -> Optional[Location]:
        """Fetch the most recent location record for a child based on recorded_at / created_at."""
        return (
            self.db.query(Location)
            .filter(Location.child_id == child_id)
            .order_by(desc(Location.recorded_at), desc(Location.created_at))
            .first()
        )

    def get_last_known_location(self, child_id: str) -> Optional[Location]:
        """Fetch the last known location record for a child."""
        return (
            self.db.query(Location)
            .filter(Location.child_id == child_id)
            .order_by(desc(Location.recorded_at), desc(Location.created_at))
            .first()
        )

    def get_location_history(
        self,
        child_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Location]:
        """Fetch historical GPS location breadcrumbs for a child."""
        query = self.db.query(Location).filter(Location.child_id == child_id)
        if start_time:
            query = query.filter(Location.recorded_at >= start_time)
        if end_time:
            query = query.filter(Location.recorded_at <= end_time)
        return query.order_by(desc(Location.recorded_at), desc(Location.created_at)).limit(limit).all()
