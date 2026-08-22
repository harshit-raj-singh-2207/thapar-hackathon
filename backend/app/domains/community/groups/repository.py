from typing import List, Optional
from sqlalchemy.orm import Session
from app.domains.community.models import Group, GroupMember

class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, group_id: str) -> Optional[Group]:
        return self.db.query(Group).filter(Group.id == group_id).first()

    def create(self, name: str, description: str, category: str, creator_id: str) -> Group:
        group = Group(name=name, description=description, category=category, creator_id=creator_id)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def add_member(self, group_id: str, user_id: str, role: str = "member") -> GroupMember:
        gm = GroupMember(group_id=group_id, user_id=user_id, role=role)
        self.db.add(gm)
        self.db.commit()
        return gm
