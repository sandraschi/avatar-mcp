"""
Core System Tools for AvatarMCP

This module contains the core system monitoring and status tools that are actually
implemented and working for system health and diagnostics.
"""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class CoreSystemTools:
    """Core system tools with real implementations."""

    def __init__(self, mcp_server):
        """Initialize core system tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register core system tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        def system_status(params: dict[str, Any]) -> dict[str, Any]:
            """Get comprehensive system status and health information.

            Returns detailed information about the AvatarMCP server status,
            loaded resources, active connections, and system health metrics.

            Parameters:
                detailed: Whether to include detailed system metrics (default: False)

            Returns:
                Dictionary with comprehensive system status
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                detailed = params.get("detailed", False)

                # Get basic status
                status = {
                    "status": "success",
                    "server_initialized": self.mcp_server.initialized,
                    "server_running": self.mcp_server.running,
                    "uptime_seconds": time.time() - self.mcp_server.start_time
                    if hasattr(self.mcp_server, "start_time")
                    else 0,
                    "timestamp": time.time(),
                }

                # Add VRM manager status
                if hasattr(self.mcp_server, "vrm_manager"):
                    status.update(
                        {
                            "vrm_manager_active": self.mcp_server.vrm_manager is not None,
                            "loaded_avatars": len(self.mcp_server.vrm_manager.avatars)
                            if self.mcp_server.vrm_manager
                            else 0,
                            "active_avatar_id": self.mcp_server.vrm_manager.get_active_avatar_id()
                            if self.mcp_server.vrm_manager
                            else None,
                        }
                    )

                # Add OSC status
                if hasattr(self.mcp_server, "osc_manager"):
                    status.update(
                        {
                            "osc_enabled": self.mcp_server.osc_manager.enabled
                            if self.mcp_server.osc_manager
                            else False,
                            "osc_initialized": self.mcp_server.osc_manager.initialized
                            if self.mcp_server.osc_manager
                            else False,
                        }
                    )

                # Add detailed metrics if requested
                if detailed:
                    status.update(
                        {
                            "memory_usage": self._get_memory_usage(),
                            "active_tools": self._count_active_tools(),
                            "system_load": self._get_system_load(),
                        }
                    )

                return status

            except Exception as e:
                logger.error(f"Failed to get system status: {e!s}", exc_info=True)
                return {"status": "error", "message": f"Failed to get system status: {e!s}"}

    def _get_memory_usage(self) -> dict[str, Any]:
        """Get memory usage information."""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                "percent": process.memory_percent(),
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}

    def _count_active_tools(self) -> int:
        """Count the number of active tools."""
        try:
            if hasattr(self.mcp_server, "mcp") and hasattr(self.mcp_server.mcp, "_tools"):
                return len(self.mcp_server.mcp._tools)
            return 0
        except Exception:
            return 0

    def _get_system_load(self) -> dict[str, Any]:
        """Get system load information."""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(),
                "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
                "disk_usage": psutil.disk_usage("/").percent if hasattr(psutil, "disk_usage") else None,
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
