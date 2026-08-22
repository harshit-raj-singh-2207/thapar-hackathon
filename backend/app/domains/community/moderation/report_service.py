from sqlalchemy.orm import Session
from app.domains.caregivers.models import ContentReport

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def submit_report(self, reporter_id: str, target_type: str, target_id: str, reason: str) -> ContentReport:
        existing = self.db.query(ContentReport).filter(
            ContentReport.reporter_id == reporter_id,
            ContentReport.target_type == target_type,
            ContentReport.target_id == target_id,
            ContentReport.status == "pending"
        ).first()
        if existing:
            return existing

        report = ContentReport(reporter_id=reporter_id, target_type=target_type, target_id=target_id, reason=reason)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
