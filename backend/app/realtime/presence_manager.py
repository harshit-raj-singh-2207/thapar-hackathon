from typing import Dict

class PresenceManager:
    def __init__(self):
        self.online_users: Dict[str, bool] = {}

    def set_online(self, user_id: str):
        self.online_users[user_id] = True

    def set_offline(self, user_id: str):
        self.online_users[user_id] = False

    def is_online(self, user_id: str) -> bool:
        return self.online_users.get(user_id, False)

presence_manager = PresenceManager()
