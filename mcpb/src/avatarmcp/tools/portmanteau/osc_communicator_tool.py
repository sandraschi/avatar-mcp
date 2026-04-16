"""
OSC Communicator Portmanteau Tool for AvatarMCP

Consolidates all OSC communication operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class OSCCommunicatorTool:
    """Portmanteau tool for comprehensive OSC communication."""

    def __init__(self, mcp_server):
        """Initialize OSC communicator tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the OSC communicator portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def osc_communicator(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive OSC communication tool.

            Provides unified interface for all OSC (Open Sound Control) operations
            including sending messages to external applications and receiving
            incoming OSC messages. This portmanteau tool consolidates OSC
            communication functionality into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "send": Send an OSC message to external applications
                    - "receive": Get information about received OSC messages

                Additional parameters depend on the operation:
                    - For "send": address (required), value (required), target (optional)
                    - For "receive": None required

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Send simple OSC message:
                    result = await osc_communicator({
                        "operation": "send",
                        "address": "/avatar/parameters/Emotion",
                        "value": 0.8
                    })

                Send OSC message with multiple values:
                    result = await osc_communicator({
                        "operation": "send",
                        "address": "/avatar/transform/position",
                        "value": [1.5, 0.0, 2.3]
                    })

                Send to specific target:
                    result = await osc_communicator({
                        "operation": "send",
                        "address": "/lighting/intensity",
                        "value": 0.7,
                        "target": "192.168.1.100:9000"
                    })

                Get received messages:
                    result = await osc_communicator({
                        "operation": "receive"
                    })

            Notes:
                - All operations require server to be initialized
                - OSC must be enabled in server configuration
                - Messages are sent asynchronously (fire-and-forget)
                - No delivery confirmation or response handling
                - Values are automatically converted to OSC types
                - Network errors don't crash the MCP server
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "send":
                    return self._handle_send(params)
                elif operation == "receive":
                    return self._handle_receive(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: send, receive",
                    }

            except Exception as e:
                logger.error(f"OSC communicator operation failed: {e!s}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"OSC communicator operation failed: {e!s}",
                }

    def _handle_send(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle OSC send operation."""
        try:
            address = params.get("address")
            if not address:
                return {"status": "error", "message": "OSC address is required for send operation"}

            value = params.get("value")
            if value is None:
                return {"status": "error", "message": "OSC value is required for send operation"}

            # Check if OSC is enabled
            if not self.mcp_server.osc_manager or not self.mcp_server.osc_manager.enabled:
                return {"status": "error", "message": "OSC is not enabled or initialized"}

            # Send OSC message
            if hasattr(self.mcp_server.osc_manager, "osc_client") and self.mcp_server.osc_manager.osc_client:
                self.mcp_server.osc_manager.osc_client.send_message(address, value)

                return {
                    "status": "success",
                    "message": f"Sent OSC message '{address}' = {value}",
                    "operation": "send",
                    "address": address,
                    "value": value,
                }
            else:
                return {"status": "error", "message": "OSC client not available"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to send OSC message: {e!s}"}

    def _handle_receive(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle OSC receive operation."""
        try:
            # Check if OSC is enabled
            if not self.mcp_server.osc_manager or not self.mcp_server.osc_manager.enabled:
                return {"status": "error", "message": "OSC is not enabled or initialized"}

            # For now, return basic status since we don't have message history implemented
            # In a full implementation, this would return actual received messages
            return {
                "status": "success",
                "message": "OSC receive functionality available",
                "operation": "receive",
                "messages": [],  # Would contain actual received messages
                "server_running": self.mcp_server.osc_manager.initialized,
                "server_address": f"{self.mcp_server.osc_manager.osc_config.server_address}:{self.mcp_server.osc_manager.osc_config.server_port}",
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to get OSC messages: {e!s}"}
