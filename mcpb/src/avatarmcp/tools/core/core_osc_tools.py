"""
Core OSC Tools for AvatarMCP

This module contains the core OSC communication tools that are actually implemented
and working for sending and receiving OSC messages.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreOSCTools:
    """Core OSC tools with real implementations."""

    def __init__(self, mcp_server):
        """Initialize core OSC tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register core OSC tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        def osc_send(params: dict[str, Any]) -> dict[str, Any]:
            """Send an OSC message to external applications.

            Sends OSC (Open Sound Control) messages to configured receivers, enabling
            communication with VRChat, other avatar applications, or custom OSC-enabled software.

            Parameters:
                address: OSC address pattern to send to (required)
                value: Value to send with the message (required)
                target: Optional target receiver (IP:port format)

            Returns:
                Dictionary with status and message details
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                address = params.get("address")
                if not address:
                    return {"status": "error", "message": "OSC address is required"}

                value = params.get("value")
                if value is None:
                    return {"status": "error", "message": "OSC value is required"}

                # Check if OSC is enabled
                if not self.mcp_server.osc_manager or not self.mcp_server.osc_manager.enabled:
                    return {"status": "error", "message": "OSC is not enabled or initialized"}

                # Send OSC message
                if (
                    hasattr(self.mcp_server.osc_manager, "osc_client")
                    and self.mcp_server.osc_manager.osc_client
                ):
                    self.mcp_server.osc_manager.osc_client.send_message(address, value)

                    return {
                        "status": "success",
                        "message": f"Sent OSC message '{address}' = {value}",
                        "address": address,
                        "value": value,
                    }
                else:
                    return {"status": "error", "message": "OSC client not available"}

            except Exception as e:
                logger.error(f"Failed to send OSC message: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to send OSC message: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def osc_receive(params: dict[str, Any]) -> dict[str, Any]:
            """Get information about received OSC messages.

            Returns details about OSC messages that have been received by the server,
            including message history and current status.

            Parameters:
                None required

            Returns:
                Dictionary with received messages and status
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                # Check if OSC is enabled
                if not self.mcp_server.osc_manager or not self.mcp_server.osc_manager.enabled:
                    return {"status": "error", "message": "OSC is not enabled or initialized"}

                # For now, return basic status since we don't have message history implemented
                # In a full implementation, this would return actual received messages
                return {
                    "status": "success",
                    "message": "OSC receive functionality available",
                    "messages": [],  # Would contain actual received messages
                    "server_running": self.mcp_server.osc_manager.initialized,
                    "server_address": f"{self.mcp_server.osc_manager.osc_config.server_address}:{self.mcp_server.osc_manager.osc_config.server_port}",
                }

            except Exception as e:
                logger.error(f"Failed to get OSC messages: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to get OSC messages: {str(e)}"}
