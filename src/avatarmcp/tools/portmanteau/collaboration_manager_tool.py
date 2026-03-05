"""
Collaboration Manager Portmanteau Tool for AvatarMCP

Consolidates tools for multi-user avatar collaboration and synchronization.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CollaborationManagerTool:
    """Portmanteau tool for avatar collaboration and synchronization."""

    def __init__(self, mcp_server):
        """Initialize collaboration manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the collaboration manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def collaboration_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for avatar collaboration and synchronization.

            Parameters:
                operation: The specific operation to perform (required)
                    - "join": Join a collaborative session
                    - "leave": Leave a collaborative session
                    - "sync": Synchronize avatar state across session members

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "join":
                    return self._handle_join(params)
                elif operation == "leave":
                    return self._handle_leave(params)
                elif operation == "sync":
                    return self._handle_sync(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Collaboration manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_join(self, params: dict[str, Any]) -> dict[str, Any]:
        session_id = params.get("session_id")
        if not session_id:
            return {"status": "error", "message": "session_id parameter is required"}

        osc_address = "/avatar/collaboration/join"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": f"Joined collaborative session '{session_id}'",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_leave(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/collaboration/leave"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Left collaborative session",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_sync(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/collaboration/sync"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Collaboration sync command sent",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}
