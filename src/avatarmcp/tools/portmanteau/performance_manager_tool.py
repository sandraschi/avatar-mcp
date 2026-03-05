"""
Performance Manager Portmanteau Tool for AvatarMCP

Consolidates tools for avatar performance optimization and profiling.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PerformanceManagerTool:
    """Portmanteau tool for managing avatar performance and optimization."""

    def __init__(self, mcp_server):
        """Initialize performance manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the performance manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def performance_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for avatar performance optimization and profiling.

            Parameters:
                operation: The specific operation to perform (required)
                    - "optimize": Optimize VRM assets for weight and performance
                    - "profile": Profile real-time avatar performance and resource usage

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "optimize":
                    return self._handle_optimize(params)
                elif operation == "profile":
                    return self._handle_profile(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Performance manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_optimize(self, params: dict[str, Any]) -> dict[str, Any]:
        target = params.get("target")
        if not target:
            return {
                "status": "error",
                "message": "target parameter (avatar_id or file) is required",
            }

        osc_address = "/avatar/performance/vrm/optimize"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Performance optimization command sent",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_profile(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/performance/vrm/profile"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Performance profiling command sent",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}
