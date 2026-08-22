from sqlalchemy.orm import Session
from app.domains.community.groups.repository import GroupRepository
from app.domains.community.models import Group

class GroupService:
    def __init__(self, db: Session):
        self.repo = GroupRepository(db)

    def create_group(self, name: str, description: str, category: str, creator_id: str) -> Group:
        group = self.repo.create(name, description, category, creator_id)
        self.repo.add_member(group.id, creator_id, role="admin")
        return group
