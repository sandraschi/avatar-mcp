"""
OSCMCP Integration for AvatarMCP

This module provides integration between AvatarMCP and OSCMCP for
controlling VRChat avatars through the MCP ecosystem.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from fastmcp import FastMCP

from ..models.vrm_loader import VRMLoader
from ..network.osc.server import VRChatOSCServer

logger = logging.getLogger(__name__)


class AvatarControlMode(Enum):
    """Modes for avatar control."""

    DIRECT = "direct"  # Direct parameter control
    GESTURE = "gesture"  # High-level gesture control
    EXPRESSION = "expression"  # Facial expressions
    AUTOMATED = "automated"  # Automated behavior


@dataclass
class AvatarOSCConfig:
    """Configuration for OSC-based avatar control."""

    receive_port: int = 9000
    send_port: int = 9001
    server_ip: str = "127.0.0.1"
    parameter_mappings: dict[str, str] = field(default_factory=dict)
    gesture_mappings: dict[str, dict] = field(default_factory=dict)
    expression_mappings: dict[str, dict] = field(default_factory=dict)


class AvatarOSCIntegrator:
    """Integrates AvatarMCP with OSCMCP for VRChat control."""

    def __init__(self, mcp_client: FastMCP, config: AvatarOSCConfig | None = None):
        """Initialize the integrator."""
        self.mcp = mcp_client
        self.config = config or AvatarOSCConfig()
        self.osc_server: VRChatOSCServer | None = None
        self.vrm_loader: VRMLoader | None = None
        self._running = False
        self._parameter_callbacks: dict[str, list[Callable]] = {}
        self._current_gestures: dict[str, str] = {"left": "neutral", "right": "neutral"}
        self._current_expressions: dict[str, float] = {}

    async def start(self):
        """Start the OSC server and connect to OSCMCP."""
        if self._running:
            return

        # Initialize OSC server
        self.osc_server = VRChatOSCServer(
            ip=self.config.server_ip,
            receive_port=self.config.receive_port,
            send_port=self.config.send_port,
        )

        # Start the OSC server
        await self.osc_server.start()

        # Register with OSCMCP
        await self._register_with_oscmcp()

        self._running = True
        logger.info("AvatarOSCIntegrator started")

    async def stop(self):
        """Stop the OSC server and clean up."""
        if not self._running or not self.osc_server:
            return

        await self.osc_server.stop()
        self._running = False
        logger.info("AvatarOSCIntegrator stopped")

    async def _register_with_oscmcp(self):
        """Register this instance with OSCMCP."""
        try:
            # Register our OSC endpoints with OSCMCP
            await self.mcp.tools.create_route(
                source="/avatar/parameters/*",
                target=f"osc://{self.config.server_ip}:{self.config.receive_port}/avatar/parameters/{0}",
                transform={"type": "pass_through"},
            )

            # Register parameter mappings
            for param, mapping in self.config.parameter_mappings.items():
                await self.mcp.tools.create_route(
                    source=f"/avatarmcp/{param}",
                    target=f"osc://{self.config.server_ip}:{self.config.send_port}/avatar/parameters/{mapping}",
                    transform={"type": "pass_through"},
                )

            logger.info("Registered with OSCMCP")

        except Exception as e:
            logger.error(f"Failed to register with OSCMCP: {e}")

    def load_vrm(self, file_path: str):
        """Load a VRM model and extract relevant parameters."""
        self.vrm_loader = VRMLoader.from_file(file_path)

        # If we have a VRM loader, update our parameter mappings
        if self.vrm_loader:
            self._update_parameter_mappings()

        return self.vrm_loader

    def _update_parameter_mappings(self):
        """Update parameter mappings based on the loaded VRM model."""
        if not self.vrm_loader:
            return

        # Add blend shape parameters
        for blend_shape in self.vrm_loader.get_blend_shape_names():
            param_name = f"BlendShape.{blend_shape}"
            if param_name not in self.config.parameter_mappings:
                self.config.parameter_mappings[param_name] = blend_shape

        # Add bone parameters (simplified example)
        for bone in self.vrm_loader.get_bone_names():
            for axis in ["X", "Y", "Z"]:
                param_name = f"Bone.{bone}.Rot{axis}"
                if param_name not in self.config.parameter_mappings:
                    self.config.parameter_mappings[param_name] = f"Bone_{bone}_Rot{axis}"

    async def set_gesture(self, hand: str, gesture: str, strength: float = 1.0):
        """Set a gesture for the specified hand."""
        if not self.osc_server:
            logger.warning("OSC server not initialized")
            return

        if hand.lower() not in ["left", "right"]:
            raise ValueError("Hand must be 'left' or 'right'")

        # Update current gesture
        self._current_gestures[hand.lower()] = gesture.lower()

        # Send gesture via OSC
        await self.osc_server.send_gesture(hand, gesture, strength)

        logger.info(f"Set {hand} hand gesture to {gesture} (strength: {strength})")

    async def set_expression(self, expression: str, strength: float = 1.0):
        """Set a facial expression."""
        if not self.osc_server:
            logger.warning("OSC server not initialized")
            return

        # Update current expressions
        self._current_expressions[expression.lower()] = max(0.0, min(1.0, strength))

        # Send expression via OSC
        await self.osc_server.send_expression(expression, strength)

        logger.info(f"Set expression {expression} to {strength}")

    async def set_viseme(self, viseme: str, strength: float = 1.0):
        """Set a viseme for lip sync."""
        if not self.osc_server:
            logger.warning("OSC server not initialized")
            return

        await self.osc_server.send_viseme(viseme, strength)
        logger.info(f"Set viseme {viseme} to {strength}")

    def on_parameter_change(self, parameter: str):
        """Decorator to register a callback for parameter changes."""

        def decorator(callback: Callable[[str, Any], None]):
            if parameter not in self._parameter_callbacks:
                self._parameter_callbacks[parameter] = []
            self._parameter_callbacks[parameter].append(callback)
            return callback

        return decorator

    def _handle_parameter_change(self, parameter: str, value: Any):
        """Handle parameter changes from OSC."""
        # Call registered callbacks
        if parameter in self._parameter_callbacks:
            for callback in self._parameter_callbacks[parameter]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(parameter, value))
                    else:
                        callback(parameter, value)
                except Exception as e:
                    logger.error(f"Error in parameter callback for {parameter}: {e}")

        # Special handling for certain parameters
        if parameter.lower() == "gestureleft" or parameter.lower() == "gestureright":
            hand = parameter[7:].lower()  # Extract "left" or "right"
            self._current_gestures[hand] = value.lower()
        elif parameter.lower().startswith("expressions."):
            expr = parameter[11:]  # Remove "expressions." prefix
            self._current_expressions[expr] = float(value)

    async def get_parameter(self, parameter: str) -> Any | None:
        """Get the current value of a parameter."""
        if not self.osc_server:
            return None

        # Check if it's a gesture parameter
        if parameter.lower() in ["gestureleft", "gestureright"]:
            hand = parameter[7:].lower()
            return self._current_gestures.get(hand)

        # Check if it's an expression parameter
        if parameter.lower().startswith("expressions."):
            expr = parameter[11:]
            return self._current_expressions.get(expr.lower(), 0.0)

        # Default to querying the OSC server
        return self.osc_server.get_parameter(parameter)

    async def send_parameter(self, parameter: str, value: Any):
        """Send a parameter value to the avatar."""
        if not self.osc_server:
            logger.warning("OSC server not initialized")
            return

        await self.osc_server.set_parameter(parameter, value)
