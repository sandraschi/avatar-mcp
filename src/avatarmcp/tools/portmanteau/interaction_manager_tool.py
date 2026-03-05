"""
Interaction Manager Portmanteau Tool for AvatarMCP

Consolidates tools for interactive avatar triggers, gestures, and tactile inputs.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class InteractionManagerTool:
    """Portmanteau tool for managing avatar interactions and tactile inputs."""

    def __init__(self, mcp_server):
        """Initialize interaction manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the interaction manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def interaction_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for avatar interaction and tactile input management.

            Parameters:
                operation: The specific operation to perform (required)
                    - "touch": Trigger a tactile interaction at a specific bone/location
                    - "gesture": Trigger a specific pre-defined interactive gesture

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "touch":
                    return self._handle_touch(params)
                elif operation == "gesture":
                    return self._handle_gesture(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Interaction manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_touch(self, params: dict[str, Any]) -> dict[str, Any]:
        location = params.get("location")
        if not location:
            return {"status": "error", "message": "location parameter is required"}

        osc_address = "/avatar/interactive/avatar/touch"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": f"Touch interaction triggered at '{location}'",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_gesture(self, params: dict[str, Any]) -> dict[str, Any]:
        gesture_name = params.get("gesture_name")
        if not gesture_name:
            return {"status": "error", "message": "gesture_name parameter is required"}

        osc_address = "/avatar/interactive/avatar/gesture"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": f"Gesture '{gesture_name}' triggered",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}
