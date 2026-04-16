"""
WebSocket handler for real-time communication with clients.

This module provides a WebSocket handler for bidirectional communication
with web-based clients, enabling real-time updates and control.
"""

import asyncio
import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)


@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client."""

    id: str
    websocket: WebSocket
    authenticated: bool = False
    subscriptions: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


class WebSocketHandler(BaseHandler):
    """Handles WebSocket connections and message routing."""

    def __init__(self, server: Any = None):
        """Initialize the WebSocket handler.

        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self.active_connections: dict[str, WebSocketClient] = {}
        self.message_handlers: dict[str, Callable] = {}
        self.subscription_handlers: dict[str, Callable] = {}
        self.heartbeat_task: asyncio.Task | None = None

    async def _initialize(self) -> None:
        """Initialize the WebSocket handler and register default handlers."""
        # Register default message handlers
        self._register_default_handlers()

        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat())

        logger.info("WebSocket handler initialized")

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        # Connection management
        self.register_message_handler("ping", self._handle_ping)
        self.register_message_handler("auth", self._handle_auth)
        self.register_message_handler("subscribe", self._handle_subscribe)
        self.register_message_handler("unsubscribe", self._handle_unsubscribe)

        # Avatar control
        self.register_message_handler("avatar/load", self._forward_to_avatar_handler)
        self.register_message_handler("avatar/unload", self._forward_to_avatar_handler)
        self.register_message_handler("avatar/list", self._forward_to_avatar_handler)

        # Animation control
        self.register_message_handler("animation/play", self._forward_to_animation_handler)
        self.register_message_handler("animation/stop", self._forward_to_animation_handler)
        self.register_message_handler("animation/list", self._forward_to_animation_handler)

    async def accept_connection(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to accept
        """
        client_id = str(uuid.uuid4())
        client = WebSocketClient(id=client_id, websocket=websocket)

        try:
            await websocket.accept()
            self.active_connections[client_id] = client

            # Send connection established message
            await self._send_to_client(client, {"type": "connection_established", "client_id": client_id})

            logger.info(f"New WebSocket connection: {client_id}")

            # Keep connection alive and process messages
            while True:
                try:
                    data = await websocket.receive_text()
                    await self._handle_message(client, data)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e!s}", exc_info=True)
                    await self._send_error(client, "internal_error", str(e))

        except Exception as e:
            logger.error(f"WebSocket connection error: {e!s}", exc_info=True)

        finally:
            await self._handle_disconnect(client_id)

    async def _handle_disconnect(self, client_id: str) -> None:
        """Handle client disconnection.

        Args:
            client_id: ID of the disconnected client
        """
        if client_id in self.active_connections:
            client = self.active_connections[client_id]

            # Clean up subscriptions
            for topic in list(client.subscriptions):
                await self._unsubscribe_client(client_id, topic)

            # Close the WebSocket if it's still open
            if client.websocket.client_state != WebSocketState.DISCONNECTED:
                try:
                    await client.websocket.close()
                except Exception as e:
                    logger.warning(f"Error closing WebSocket: {e!s}")

            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")

    async def _handle_message(self, client: WebSocketClient, message: str) -> None:
        """Handle an incoming WebSocket message.

        Args:
            client: The client that sent the message
            message: The raw message string (should be JSON)
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if not message_type:
                raise ValueError("Missing 'type' field in message")

            # Find and call the appropriate handler
            handler = self.message_handlers.get(message_type)
            if not handler:
                raise ValueError(f"Unknown message type: {message_type}")

            await handler(client, data.get("data", {}))

        except json.JSONDecodeError:
            await self._send_error(client, "invalid_message", "Invalid JSON format")
        except Exception as e:
            await self._send_error(client, "processing_error", str(e))

    async def _send_to_client(self, client: WebSocketClient, data: dict[str, Any]) -> None:
        """Send a message to a specific client.

        Args:
            client: The client to send the message to
            data: The data to send (will be JSON-serialized)
        """
        try:
            if client.websocket.client_state == WebSocketState.CONNECTED:
                await client.websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error sending message to client {client.id}: {e!s}")

    async def broadcast(self, data: dict[str, Any], topic: str = None) -> None:
        """Broadcast a message to all connected clients.

        Args:
            data: The data to broadcast (will be JSON-serialized)
            topic: Optional topic to filter subscribers
        """
        for client in list(self.active_connections.values()):
            if not topic or topic in client.subscriptions:
                await self._send_to_client(client, data)

    async def _send_error(self, client: WebSocketClient, error_type: str, message: str) -> None:
        """Send an error message to a client.

        Args:
            client: The client to send the error to
            error_type: Type of error
            message: Error message
        """
        await self._send_to_client(client, {"type": "error", "error": {"type": error_type, "message": message}})

    # Message Handlers

    async def _handle_ping(self, client: WebSocketClient, data: dict[str, Any]) -> None:
        """Handle ping message (heartbeat)."""
        await self._send_to_client(client, {"type": "pong", "timestamp": data.get("timestamp")})

    async def _handle_auth(self, client: WebSocketClient, data: dict[str, Any]) -> None:
        """Handle authentication."""
        # Simple token-based authentication
        auth_token = data.get("token")

        # In a real application, validate the token here
        if auth_token:
            client.authenticated = True
            client.metadata["auth_method"] = "token"

            await self._send_to_client(
                client,
                {
                    "type": "auth_success",
                    "client_id": client.id,
                    "permissions": ["read", "write"],  # Example permissions
                },
            )
        else:
            client.authenticated = False
            await self._send_error(client, "auth_failed", "Invalid or missing token")

    async def _handle_subscribe(self, client: WebSocketClient, data: dict[str, Any]) -> None:
        """Handle subscription request."""
        if not client.authenticated:
            await self._send_error(client, "unauthorized", "Authentication required")
            return

        topic = data.get("topic")
        if not topic:
            await self._send_error(client, "invalid_request", "Missing topic")
            return

        # Check if there's a specific handler for this subscription
        handler = self.subscription_handlers.get(topic)
        if handler:
            try:
                result = await handler(client, data.get("params", {}))
                if result is not None:
                    await self._send_to_client(client, {"type": "subscription_update", "topic": topic, "data": result})
            except Exception as e:
                await self._send_error(client, "subscription_error", str(e))
                return

        # Add to subscriptions
        client.subscriptions.add(topic)

        await self._send_to_client(client, {"type": "subscription_success", "topic": topic})

    async def _handle_unsubscribe(self, client: WebSocketClient, data: dict[str, Any]) -> None:
        """Handle unsubscription request."""
        topic = data.get("topic")
        if not topic:
            await self._send_error(client, "invalid_request", "Missing topic")
            return

        await self._unsubscribe_client(client.id, topic)

    async def _unsubscribe_client(self, client_id: str, topic: str) -> None:
        """Unsubscribe a client from a topic."""
        if client_id in self.active_connections and topic in self.active_connections[client_id].subscriptions:
            self.active_connections[client_id].subscriptions.remove(topic)

            # Notify the client
            try:
                await self._send_to_client(self.active_connections[client_id], {"type": "unsubscribed", "topic": topic})
            except Exception as e:
                logger.warning(f"Error sending unsubscribed message: {e!s}")

    # Forwarding to other handlers

    async def _forward_to_avatar_handler(self, client: WebSocketClient, data: dict[str, Any]) -> None:
        """Forward message to the avatar handler."""
        if not hasattr(self.server, "avatar_handler"):
            await self._send_error(client, "service_unavailable", "Avatar handler not available")
            return

        # Extract the command from the message type (e.g., "avatar/load" -> "load")
        command = data.get("type", "").split("/")[-1] if "/" in data.get("type", "") else ""
        handler_name = f"handle_avatar_{command}"

        if not hasattr(self.server.avatar_handler, handler_name):
            await self._send_error(client, "invalid_request", f"Unknown avatar command: {command}")
            return

        try:
            handler = getattr(self.server.avatar_handler, handler_name)
            response = await handler(data.get("params", {}))

            # Send the response back to the client
            await self._send_to_client(client, {"type": f"avatar/{command}_response", "data": response})

        except Exception as e:
            await self._send_error(client, "handler_error", f"Error processing avatar command: {e!s}")

    async def _forward_to_animation_handler(self, client: WebSocketClient, data: dict[str, Any]) -> None:
        """Forward message to the animation handler."""
        if not hasattr(self.server, "animation_handler"):
            await self._send_error(client, "service_unavailable", "Animation handler not available")
            return

        # Extract the command from the message type (e.g., "animation/play" -> "play")
        command = data.get("type", "").split("/")[-1] if "/" in data.get("type", "") else ""
        handler_name = f"handle_animation_{command}"

        if not hasattr(self.server.animation_handler, handler_name):
            await self._send_error(client, "invalid_request", f"Unknown animation command: {command}")
            return

        try:
            handler = getattr(self.server.animation_handler, handler_name)
            response = await handler(data.get("params", {}))

            # Send the response back to the client
            await self._send_to_client(client, {"type": f"animation/{command}_response", "data": response})

        except Exception as e:
            await self._send_error(client, "handler_error", f"Error processing animation command: {e!s}")

    # Public API

    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a specific message type.

        Args:
            message_type: The message type to handle
            handler: The handler function (async)
        """
        self.message_handlers[message_type] = handler

    def register_subscription_handler(self, topic: str, handler: Callable) -> None:
        """Register a handler for a subscription topic.

        Args:
            topic: The topic to handle
            handler: The handler function (async)
        """
        self.subscription_handlers[topic] = handler

    async def publish(self, topic: str, data: Any) -> None:
        """Publish data to all subscribers of a topic.

        Args:
            topic: The topic to publish to
            data: The data to publish
        """
        for client in self.active_connections.values():
            if topic in client.subscriptions:
                await self._send_to_client(client, {"type": "subscription_update", "topic": topic, "data": data})

    # Heartbeat and maintenance

    async def _heartbeat(self) -> None:
        """Send periodic heartbeat messages to all connected clients."""
        try:
            while True:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

                # Send ping to all connected clients
                current_time = asyncio.get_event_loop().time()
                for client in list(self.active_connections.values()):
                    try:
                        await self._send_to_client(client, {"type": "ping", "timestamp": current_time})
                    except Exception as e:
                        logger.warning(f"Error sending heartbeat to {client.id}: {e!s}")

        except asyncio.CancelledError:
            # Shutdown requested
            pass
        except Exception as e:
            logger.error(f"Heartbeat task error: {e!s}", exc_info=True)

    async def shutdown(self) -> None:
        """Clean up resources used by the handler."""
        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None

        # Close all active connections
        for client_id in list(self.active_connections.keys()):
            await self._handle_disconnect(client_id)

        self.active_connections.clear()
        self.message_handlers.clear()
        self.subscription_handlers.clear()

        logger.info("WebSocket handler shutdown complete")
