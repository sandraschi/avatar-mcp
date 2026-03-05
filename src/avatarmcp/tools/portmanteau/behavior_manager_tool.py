"""
Behavior Manager Portmanteau Tool for AvatarMCP

Consolidates AI-powered conversation, adaptation, and learning tools.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BehaviorManagerTool:
    """Portmanteau tool for managing avatar AI behavior and context awareness."""

    def __init__(self, mcp_server):
        """Initialize behavior manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the behavior manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def behavior_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for managing avatar AI behavior and interactions.

            Parameters:
                operation: The specific operation to perform (required)
                    - "respond": Generate AI-powered conversation response
                    - "adapt": Enable behavioral adaptation based on interaction
                    - "predict": Predict user preferences/needs
                    - "analyze": Perform situational context analysis
                    - "learn": Improve behavior based on interaction outcomes

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "respond":
                    return self._handle_respond(params)
                elif operation == "adapt":
                    return self._handle_adapt(params)
                elif operation == "predict":
                    return self._handle_predict(params)
                elif operation == "analyze":
                    return self._handle_analyze(params)
                elif operation == "learn":
                    return self._handle_learn(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Behavior manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_respond(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/ai/conversation/respond"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "AI response generated",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_adapt(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/ai/behavior/adapt"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Behavioral adaptation enabled",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_predict(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/ai/personality/predict"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "User preferences predicted",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_analyze(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/ai/context/analyze"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Context analysis performed",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_learn(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/ai/interaction/learn"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Interaction learning recorded",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}
