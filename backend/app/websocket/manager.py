import json
import logging
from typing import Dict, List, Any
from fastapi import WebSocket

logger = logging.getLogger("afterflow.websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Any):
        payload = json.dumps({"event": event_type, "data": data})
        stale_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending websocket message: {e}")
                stale_connections.append(connection)
        
        for dead_ws in stale_connections:
            self.disconnect(dead_ws)


ws_manager = ConnectionManager()
