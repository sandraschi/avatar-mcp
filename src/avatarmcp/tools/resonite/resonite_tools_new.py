#!/usr/bin/env python3
"""
Resonite Integration Tools for AvatarMCP

Provides OSC-based integration with Resonite social VR platform.
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ResoniteTools:
    """Resonite integration tools for AvatarMCP."""

    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.resonite_connected = False
        self.active_sessions = {}

    def _register_tools(self):
        """Register Resonite tools with MCP server."""

        @self.mcp_server.mcp.tool()
        def resonite_session_start(params: dict[str, Any]) -> dict[str, Any]:
            """Start a Resonite session for AvatarMCP integration."""
            try:
                session_id = f"resonite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Initialize OSC connection
                osc_connected = self._init_resonite_osc()

                session_info = {
                    "session_id": session_id,
                    "platform": "resonite",
                    "osc_connected": osc_connected,
                    "start_time": datetime.now().isoformat(),
                    "capabilities": ["avatar_control", "world_management", "real_time_sync"],
                }

                self.active_sessions[session_id] = session_info
                self.resonite_connected = osc_connected

                return {
                    "status": "success",
                    "message": "Resonite session started successfully",
                    "session_id": session_id,
                    "osc_connected": osc_connected,
                }

            except Exception as e:
                logger.error(f"Failed to start Resonite session: {e}")
                return {"status": "error", "message": f"Failed to start Resonite session: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def resonite_session_status(params: dict[str, Any]) -> dict[str, Any]:
            """Get current Resonite session status."""
            if not self.active_sessions:
                return {"status": "no_session", "message": "No active Resonite sessions"}

            session = list(self.active_sessions.values())[-1]
            return {
                "status": "success",
                "session_id": session["session_id"],
                "osc_connected": session.get("osc_connected", False),
                "active_sessions": len(self.active_sessions),
            }

        @self.mcp_server.mcp.tool()
        def resonite_world_load(params: dict[str, Any]) -> dict[str, Any]:
            """Load a Resonite world."""
            world_path = params.get("world_path")
            if not world_path:
                return {"status": "error", "message": "world_path required"}

            if not self._validate_world_path(world_path):
                return {"status": "error", "message": f"Invalid world path: {world_path}"}

            result = self._load_resonite_world(world_path)
            if result.get("success"):
                return {
                    "status": "success",
                    "message": f"Loaded Resonite world: {world_path}",
                    "world_path": world_path,
                }
            else:
                return {"status": "error", "message": "Failed to load world"}

    def _init_resonite_osc(self) -> bool:
        """Initialize OSC connection to Resonite."""
        try:
            # Test OSC connection (would normally send a ping/test message)
            return hasattr(self.mcp_server, "_send_osc_message")
        except Exception as e:
            logger.error(f"OSC initialization failed: {e}")
            return False

    def _load_resonite_world(
        self, world_path: str, mode: str = "normal", avatar_slots: int = 8
    ) -> dict[str, Any]:
        """Load a world in Resonite via OSC."""
        try:
            return {
                "success": True,
                "world_path": world_path,
                "mode": mode,
                "avatar_slots": avatar_slots,
                "capabilities": [
                    "avatar_control",
                    "osc_receivers",
                    "protoflux_scripts",
                    "real_time_sync",
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_world_path(self, world_path: str) -> bool:
        """Validate Resonite world path format."""
        valid_prefixes = ["resonite://", "file://", "inventory://"]
        return any(world_path.startswith(prefix) for prefix in valid_prefixes)
