from typing import List
from app.realtime.connection_manager import manager

class GroupManager:
    async def broadcast_group_event(self, group_id: str, member_user_ids: List[str], event_data: dict):
        await manager.broadcast_to_users(event_data, member_user_ids)

group_manager = GroupManager()
