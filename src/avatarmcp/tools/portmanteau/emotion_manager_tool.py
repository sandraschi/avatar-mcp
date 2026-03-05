"""
Emotion Manager Portmanteau Tool for AvatarMCP

Consolidates facial expressions, micro-expressions, and personality profiles.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EmotionManagerTool:
    """Portmanteau tool for avatar emotional state and personality management."""

    def __init__(self, mcp_server):
        """Initialize emotion manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the emotion manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def emotion_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for managing avatar emotions and personality.

            Parameters:
                operation: The specific operation to perform (required)
                    - "state_machine": Define emotional state machine
                    - "micro_expressions": Trigger subtle emotional cues
                    - "create_personality": Create a new personality profile
                    - "apply_personality": Apply a profile to an avatar

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "state_machine":
                    return self._handle_state_machine(params)
                elif operation == "micro_expressions":
                    return self._handle_micro_expressions(params)
                elif operation == "create_personality":
                    return self._handle_create_personality(params)
                elif operation == "apply_personality":
                    return self._handle_apply_personality(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Emotion manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_state_machine(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/emotion/state/machine"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Emotion state machine defined",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_micro_expressions(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/emotion/micro/expressions"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Micro-expressions triggered",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_create_personality(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/avatar/personality/create"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Personality profile created",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_apply_personality(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/avatar/personality/apply"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Personality profile applied",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}
