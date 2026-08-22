from app.realtime.connection_manager import manager

class ChatManager:
    async def send_dm(self, sender_id: str, recipient_id: str, message_data: dict):
        await manager.send_personal_message(message_data, recipient_id)
        await manager.send_personal_message(message_data, sender_id)

chat_manager = ChatManager()
