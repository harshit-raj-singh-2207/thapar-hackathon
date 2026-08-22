import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger("safety.websocket")

class ConnectionManager:
    def __init__(self):
        # Maps child_id -> set of active WebSockets (caregivers tracking that child)
        self.active_child_trackers: Dict[str, Set[WebSocket]] = {}
        # Maps user_id -> set of active WebSockets
        self.user_connections: Dict[str, Set[WebSocket]] = {}

    async def connect_tracker(self, child_id: str, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        if child_id not in self.active_child_trackers:
            self.active_child_trackers[child_id] = set()
        self.active_child_trackers[child_id].add(websocket)

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)

        logger.info(f"WebSocket connected for child {child_id}, total listeners: {len(self.active_child_trackers[child_id])}")

    def disconnect_tracker(self, child_id: str, websocket: WebSocket, user_id: str = None):
        if child_id in self.active_child_trackers:
            self.active_child_trackers[child_id].discard(websocket)
            if not self.active_child_trackers[child_id]:
                del self.active_child_trackers[child_id]

        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"WebSocket disconnected for child {child_id}")

    async def broadcast_to_child_trackers(self, child_id: str, message: dict):
        if child_id in self.active_child_trackers:
            dead_sockets = set()
            for ws in self.active_child_trackers[child_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_sockets.add(ws)
            for dead in dead_sockets:
                self.active_child_trackers[child_id].discard(dead)

    async def broadcast_to_user(self, user_id: str, message: dict):
        if user_id in self.user_connections:
            dead_sockets = set()
            for ws in self.user_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_sockets.add(ws)
            for dead in dead_sockets:
                self.user_connections[user_id].discard(dead)

ws_manager = ConnectionManager()
