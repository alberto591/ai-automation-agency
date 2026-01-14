"""
WebSocket Connection Manager for Real-Time Dashboard Updates.

Manages WebSocket connections, room subscriptions, and message broadcasting.
"""

from typing import Any

from fastapi import WebSocket

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and room-based broadcasting."""

    def __init__(self) -> None:
        # Active connections: {connection_id: WebSocket}
        self.active_connections: dict[str, WebSocket] = {}
        # Room subscriptions: {room_id: set of connection_ids}
        self.rooms: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info("WS_CONNECTED", context={"connection_id": connection_id})

    def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection and clean up subscriptions."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from all rooms
        for _room_id, subscribers in self.rooms.items():
            subscribers.discard(connection_id)

        logger.info("WS_DISCONNECTED", context={"connection_id": connection_id})

    def subscribe_to_room(self, connection_id: str, room_id: str) -> None:
        """Subscribe a connection to a specific room (e.g., a lead's phone number)."""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(connection_id)
        logger.info("WS_ROOM_SUBSCRIBED", context={"connection_id": connection_id, "room": room_id})

    def unsubscribe_from_room(self, connection_id: str, room_id: str) -> None:
        """Unsubscribe a connection from a room."""
        if room_id in self.rooms:
            self.rooms[room_id].discard(connection_id)
        logger.info(
            "WS_ROOM_UNSUBSCRIBED", context={"connection_id": connection_id, "room": room_id}
        )

    async def send_personal_message(self, message: dict[str, Any], connection_id: str) -> None:
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(
                    "WS_SEND_ERROR", context={"connection_id": connection_id, "error": str(e)}
                )

    async def broadcast_to_room(self, message: dict[str, Any], room_id: str) -> None:
        """Broadcast a message to all subscribers in a room."""
        if room_id not in self.rooms:
            return

        subscribers = list(self.rooms[room_id])  # Copy to avoid modification during iteration
        for connection_id in subscribers:
            await self.send_personal_message(message, connection_id)

        logger.info("WS_BROADCAST", context={"room": room_id, "subscribers": len(subscribers)})

    async def broadcast_to_all(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all active connections."""
        connection_ids = list(self.active_connections.keys())
        for connection_id in connection_ids:
            await self.send_personal_message(message, connection_id)

        logger.info("WS_BROADCAST_ALL", context={"connections": len(connection_ids)})


# Global singleton instance
manager = ConnectionManager()
