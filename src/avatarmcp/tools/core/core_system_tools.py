"""
Core System Tools for AvatarMCP

This module contains the core system tools migrated from the monolithic server.
"""

import logging
import time
from typing import Any

from ...models.vrm_manager import VRMManager

logger = logging.getLogger(__name__)


class CoreSystemTools:
    """Core system tools for server management."""

    def __init__(self, mcp_server):
        """Initialize core system tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all core system tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        async def initialize(models_dir: str | None = None) -> dict[str, Any]:
            """Initialize the AvatarMCP server and scan for models.

            Parameters:
                models_dir: Directory containing VRM models (optional)

            Returns:
                Dictionary with initialization status and model count
            """
            try:
                logger.info("Initializing AvatarMCP server via tool")

                # Update models directory if specified
                if models_dir:
                    self.mcp_server.vrm_manager = VRMManager(models_dir)

                # Scan for available models
                await self.mcp_server.vrm_manager.scan_models()

                self.mcp_server.initialized = True
                return {
                    "status": "success",
                    "message": "AvatarMCP initialized",
                    "version": "1.0.0",
                    "models_dir": str(self.mcp_server.vrm_manager.models_dir),
                    "num_models": len(self.mcp_server.vrm_manager.models),
                }
            except Exception as e:
                error_msg = f"Initialization failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {"status": "error", "message": error_msg}

        @self.mcp_server.mcp.tool()
        async def shutdown() -> dict[str, Any]:
            """Shut down the AvatarMCP server.

            Returns:
                Dictionary confirming shutdown initiation
            """
            logger.info("Shutdown requested via tool")
            self.mcp_server.running = False
            return {"status": "success", "message": "Shutdown initiated"}

        @self.mcp_server.mcp.tool()
        async def system_status() -> dict[str, Any]:
            """Get the current status of the AvatarMCP server.

            Returns:
                Dictionary with server health and uptime information
            """
            return {
                "status": "success",
                "system": {
                    "name": "AvatarMCP",
                    "version": "1.0.0",
                    "status": "running",
                    "uptime": time.time() - self.mcp_server.start_time,
                    "initialized": self.mcp_server.initialized,
                },
            }

        @self.mcp_server.mcp.tool()
        async def debug_echo(params: dict[str, Any]) -> dict[str, Any]:
            """Echo back the parameters for debugging purposes.

            Parameters:
                params: Dictionary of parameters to echo back (required)

            Returns:
                Dictionary with status and echoed parameters
            """
            return {"status": "success", "echo": params}
