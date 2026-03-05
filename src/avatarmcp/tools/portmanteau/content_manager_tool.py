"""
Content Manager Portmanteau Tool for AvatarMCP

Consolidates tools for avatar content creation, listing, and publishing.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContentManagerTool:
    """Portmanteau tool for manages avatar content and cataloging."""

    def __init__(self, mcp_server):
        """Initialize content manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the content manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def content_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for avatar content management.

            Parameters:
                operation: The specific operation to perform (required)
                    - "create": Create new avatar content/assets
                    - "publish": Publish avatar content to a catalog or platform
                    - "list": List available avatar content/assets

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "create":
                    return self._handle_create(params)
                elif operation == "publish":
                    return self._handle_publish(params)
                elif operation == "list":
                    return self._handle_list(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Content manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_create(self, params: dict[str, Any]) -> dict[str, Any]:
        content_name = params.get("name")
        if not content_name:
            return {"status": "error", "message": "name parameter is required"}

        osc_address = "/avatar/content/avatar/create"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": f"Content creation command for '{content_name}' sent",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_publish(self, params: dict[str, Any]) -> dict[str, Any]:
        content_id = params.get("content_id")
        if not content_id:
            return {"status": "error", "message": "content_id parameter is required"}

        osc_address = "/avatar/content/avatar/publish"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": f"Content publication command for '{content_id}' sent",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_list(self, params: dict[str, Any]) -> dict[str, Any]:
        osc_address = "/avatar/content/avatar/list"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Content listing command sent",
                "params": params,
            }
        return {"status": "error", "message": "Failed to send OSC command"}
