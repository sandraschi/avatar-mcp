"""
OSC (Open Sound Control) handlers for MCP server.

This module provides handlers for OSC communication, allowing control of avatars
and animations via OSC messages.
"""

import asyncio
import logging
import socket
from collections.abc import Callable
from typing import Any

from pythonosc import dispatcher, udp_client
from pythonosc.osc_server import AsyncIOOSCUDPServer

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)


class OSCConfig:
    """Configuration for OSC communication."""

    def __init__(
        self,
        server_ip: str = "127.0.0.1",
        server_port: int = 9001,
        client_ip: str = "127.0.0.1",
        client_port: int = 9000,
    ):
        """Initialize OSC configuration.

        Args:
            server_ip: IP address to listen for OSC messages
            server_port: Port to listen for OSC messages
            client_ip: IP address to send OSC messages to
            client_port: Port to send OSC messages to
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_ip = client_ip
        self.client_port = client_port

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "client_ip": self.client_ip,
            "client_port": self.client_port,
        }


class OSCManager:
    """Manages OSC client and server for bidirectional communication."""

    def __init__(self, config: OSCConfig):
        """Initialize the OSC manager.

        Args:
            config: OSC configuration
        """
        self.config = config
        self.client = None
        self.server = None
        self.dispatcher = dispatcher.Dispatcher()
        self.message_queue = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        """Start the OSC client and server."""
        if self._running:
            return

        # Setup OSC client
        self.client = udp_client.SimpleUDPClient(self.config.client_ip, self.config.client_port)

        # Setup OSC server
        try:
            # Create server with reuse port
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.config.server_ip, self.config.server_port))

            server = AsyncIOOSCUDPServer(
                (self.config.server_ip, self.config.server_port),
                self.dispatcher,
                asyncio.get_event_loop(),
            )

            # Start server
            transport, _ = await server.create_serve_endpoint()
            self.server = server
            self._transport = transport
            self._running = True

            logger.info(f"OSC server started on {self.config.server_ip}:{self.config.server_port}")
            logger.info(f"OSC client sending to {self.config.client_ip}:{self.config.client_port}")

        except OSError as e:
            logger.error(f"Failed to start OSC server: {str(e)}")
            raise

    async def stop(self) -> None:
        """Stop the OSC client and server."""
        if not self._running:
            return

        if self.server and hasattr(self, "_transport"):
            self._transport.close()

        self.client = None
        self.server = None
        self._running = False
        logger.info("OSC server stopped")

    def send_message(self, address: str, *args, ip: str = None, port: int = None) -> None:
        """Send an OSC message.

        Args:
            address: OSC address pattern
            *args: Arguments to send
            ip: Override destination IP
            port: Override destination port
        """
        if not self._running or not self.client:
            logger.warning("OSC client not running, cannot send message")
            return

        try:
            target_ip = ip or self.config.client_ip
            target_port = port or self.config.client_port

            # Update client if target changed
            if (ip and ip != self.config.client_ip) or (port and port != self.config.client_port):
                self.client = udp_client.SimpleUDPClient(target_ip, target_port)

            self.client.send_message(address, args)
            logger.debug(f"Sent OSC: {address} {args}")

        except Exception as e:
            logger.error(f"Failed to send OSC message: {str(e)}")

    def add_handler(self, address: str, handler: Callable) -> None:
        """Add a handler for an OSC address pattern.

        Args:
            address: OSC address pattern to match
            handler: Callback function to handle the message
        """
        self.dispatcher.map(address, handler)

    def remove_handler(self, address: str) -> None:
        """Remove a handler for an OSC address pattern.

        Args:
            address: OSC address pattern to remove
        """
        if address in self.dispatcher._map:
            del self.dispatcher._map[address]


class OSCHandler(BaseHandler):
    """Handles OSC communication for the MCP server."""

    def __init__(self, server: Any = None):
        """Initialize the OSC handler.

        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self.osc_manager = None
        self.config = None
        self._message_handlers = {}

    async def _initialize(self) -> None:
        """Initialize the OSC manager and register handlers."""
        # Load configuration from server or use defaults
        self.config = OSCConfig(
            server_ip=self.server.config.get("osc_server_ip", "127.0.0.1"),
            server_port=self.server.config.get("osc_server_port", 9001),
            client_ip=self.server.config.get("osc_client_ip", "127.0.0.1"),
            client_port=self.server.config.get("osc_client_port", 9000),
        )

        # Initialize OSC manager
        self.osc_manager = OSCManager(self.config)

        # Register default handlers
        self._register_default_handlers()

        # Start OSC server
        await self.osc_manager.start()

        logger.info("OSC handler initialized")

    def _register_default_handlers(self) -> None:
        """Register default OSC message handlers."""
        # Avatar control
        self.register_handler("/avatar/load", self._handle_avatar_load)
        self.register_handler("/avatar/unload", self._handle_avatar_unload)
        self.register_handler("/avatar/set_active", self._handle_avatar_set_active)

        # Animation control
        self.register_handler("/animation/play", self._handle_animation_play)
        self.register_handler("/animation/stop", self._handle_animation_stop)
        self.register_handler("/animation/list", self._handle_animation_list)

    def register_handler(self, address: str, handler: Callable) -> None:
        """Register a custom OSC message handler.

        Args:
            address: OSC address pattern to match
            handler: Callback function to handle the message
        """
        if not self.osc_manager:
            raise RuntimeError("OSC manager not initialized")

        self._message_handlers[address] = handler
        self.osc_manager.add_handler(address, self._create_osc_handler(handler))

    def _create_osc_handler(self, handler: Callable) -> Callable:
        """Create a wrapper for OSC message handlers.

        Args:
            handler: The actual handler function

        Returns:
            Wrapped handler function
        """

        async def wrapper(osc_addr: str, *args) -> None:
            try:
                # Convert OSC arguments to Python types
                py_args = []
                for arg in args:
                    if hasattr(arg, "__dict__"):
                        py_args.append(vars(arg))
                    else:
                        py_args.append(arg)

                # Call the handler with unpacked arguments
                await handler(*py_args)

            except Exception as e:
                logger.error(f"Error in OSC handler for {osc_addr}: {str(e)}", exc_info=True)

        return wrapper

    async def send_message(self, address: str, *args, ip: str = None, port: int = None) -> None:
        """Send an OSC message.

        Args:
            address: OSC address pattern
            *args: Arguments to send
            ip: Override destination IP
            port: Override destination port
        """
        if not self.osc_manager:
            logger.warning("OSC manager not initialized, cannot send message")
            return

        self.osc_manager.send_message(address, *args, ip=ip, port=port)

    # OSC Message Handlers

    async def _handle_avatar_load(self, *args) -> None:
        """Handle /avatar/load OSC message."""
        if not hasattr(self.server, "avatar_handler"):
            return

        # Parse arguments: /avatar/load <path> [model_id] [make_active]
        path = str(args[0]) if args else None
        model_id = str(args[1]) if len(args) > 1 else None
        make_active = bool(args[2]) if len(args) > 2 else True

        params = {"path": path, "model_id": model_id, "make_active": make_active}

        # Call avatar handler
        response = await self.server.avatar_handler.handle_avatar_load(params)

        # Send response back via OSC
        if response.get("status") == "success":
            self.send_message("/avatar/loaded", response.get("model_id"))
        else:
            self.send_message("/avatar/load_failed", response.get("message", "Unknown error"))

    async def _handle_avatar_unload(self, *args) -> None:
        """Handle /avatar/unload OSC message."""
        if not hasattr(self.server, "avatar_handler"):
            return

        # Parse arguments: /avatar/unload [model_id] [force]
        model_id = str(args[0]) if args else None
        force = bool(args[1]) if len(args) > 1 else False

        # If no model_id provided, unload active avatar
        if not model_id and hasattr(self.server.avatar_handler, "active_model_id"):
            model_id = self.server.avatar_handler.active_model_id

        if not model_id:
            self.send_message("/avatar/unload_failed", "No model ID provided and no active model")
            return

        params = {"id": model_id, "force": force}

        # Call avatar handler
        response = await self.server.avatar_handler.handle_avatar_unload(params)

        # Send response back via OSC
        if response.get("status") == "success":
            self.send_message("/avatar/unloaded", model_id)
        else:
            self.send_message(
                "/avatar/unload_failed", response.get("message", "Unknown error"), model_id
            )

    async def _handle_avatar_set_active(self, *args) -> None:
        """Handle /avatar/set_active OSC message."""
        if not hasattr(self.server, "avatar_handler"):
            return

        # Parse arguments: /avatar/set_active <model_id> [load_if_needed]
        if not args:
            self.send_message("/avatar/set_active_failed", "No model ID provided")
            return

        model_id = str(args[0])
        load_if_needed = bool(args[1]) if len(args) > 1 else True

        params = {"id": model_id, "load_if_needed": load_if_needed}

        # Call avatar handler
        response = await self.server.avatar_handler.handle_avatar_set_active(params)

        # Send response back via OSC
        if response.get("status") == "success":
            self.send_message("/avatar/active", model_id)
        else:
            self.send_message(
                "/avatar/set_active_failed", response.get("message", "Unknown error"), model_id
            )

    async def _handle_animation_play(self, *args) -> None:
        """Handle /animation/play OSC message."""
        if not hasattr(self.server, "animation_handler"):
            return

        # Parse arguments: /animation/play <name> [loop] [speed] [blend_time]
        if not args:
            self.send_message("/animation/play_failed", "No animation name provided")
            return

        name = str(args[0])
        loop = bool(args[1]) if len(args) > 1 else False
        speed = float(args[2]) if len(args) > 2 else 1.0
        blend_time = float(args[3]) if len(args) > 3 else 0.2

        params = {"name": name, "loop": loop, "speed": speed, "blend_time": blend_time}

        # Call animation handler
        response = await self.server.animation_handler.handle_animation_play(params)

        # Send response back via OSC
        if response.get("status") == "success":
            self.send_message("/animation/playing", name)
        else:
            self.send_message(
                "/animation/play_failed", response.get("message", "Unknown error"), name
            )

    async def _handle_animation_stop(self, *args) -> None:
        """Handle /animation/stop OSC message."""
        if not hasattr(self.server, "animation_handler"):
            return

        # Parse arguments: /animation/stop [blend_time]
        blend_time = float(args[0]) if args else 0.2

        params = {"blend_time": blend_time}

        # Call animation handler
        response = await self.server.animation_handler.handle_animation_stop(params)

        # Send response back via OSC
        if response.get("status") == "success":
            self.send_message("/animation/stopped")

    async def _handle_animation_list(self, *args) -> None:
        """Handle /animation/list OSC message."""
        if not hasattr(self.server, "animation_handler"):
            return

        # Call animation handler
        response = await self.server.animation_handler.handle_animation_list({})

        # Send response back via OSC
        if response.get("status") == "success":
            animations = response.get("animations", [])
            current = response.get("current_animation")

            # Send each animation as a separate message
            for _i, anim in enumerate(animations):
                self.send_message(
                    "/animation/item",
                    anim.get("name", ""),
                    anim.get("display_name", ""),
                    anim.get("loop", False),
                    anim.get("default_speed", 1.0),
                    anim.get("description", ""),
                    anim.get("category", ""),
                    anim == current,  # Is this the current animation?
                )

            # Send end of list marker
            self.send_message("/animation/end_of_list", len(animations))

    async def shutdown(self) -> None:
        """Clean up resources used by the handler."""
        if self.osc_manager:
            await self.osc_manager.stop()

        self._message_handlers.clear()
        self.initialized = False
        logger.info("OSC handler shutdown complete")
