from sqlalchemy.orm import Session
from app.domains.community.moderation.block_service import BlockService
from app.domains.community.moderation.report_service import ReportService

class ModerationService:
    def __init__(self, db: Session):
        self.block_service = BlockService(db)
        self.report_service = ReportService(db)
