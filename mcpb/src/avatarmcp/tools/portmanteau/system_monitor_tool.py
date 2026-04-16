"""
System Monitor Portmanteau Tool for AvatarMCP

Consolidates all system monitoring and diagnostics operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class SystemMonitorTool:
    """Portmanteau tool for comprehensive system monitoring and diagnostics."""

    def __init__(self, mcp_server):
        """Initialize system monitor tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the system monitor portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def system_monitor(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive system monitoring and diagnostics tool.

            Provides unified interface for all system monitoring operations including
            server status, health metrics, performance monitoring, and diagnostic
            information. This portmanteau tool consolidates system monitoring
            functionality into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "get_status": Get comprehensive system status and health information
                    - "get_health": Get system health metrics and diagnostics
                    - "get_metrics": Get detailed performance metrics

                Additional parameters depend on the operation:
                    - For "get_status": detailed (optional)
                    - For "get_health": include_memory (optional), include_cpu (optional)
                    - For "get_metrics": metric_type (optional)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Get basic system status:
                    result = await system_monitor({
                        "operation": "get_status"
                    })

                Get detailed system status:
                    result = await system_monitor({
                        "operation": "get_status",
                        "detailed": True
                    })

                Get system health metrics:
                    result = await system_monitor({
                        "operation": "get_health",
                        "include_memory": True,
                        "include_cpu": True
                    })

                Get performance metrics:
                    result = await system_monitor({
                        "operation": "get_metrics",
                        "metric_type": "performance"
                    })

            Notes:
                - All operations require server to be initialized
                - Health metrics may require additional dependencies (psutil)
                - Performance metrics are collected in real-time
                - System load information is platform-dependent
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "get_status":
                    return self._handle_get_status(params)
                elif operation == "get_health":
                    return self._handle_get_health(params)
                elif operation == "get_metrics":
                    return self._handle_get_metrics(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: get_status, get_health, get_metrics",
                    }

            except Exception as e:
                logger.error(f"System monitor operation failed: {e!s}", exc_info=True)
                return {"status": "error", "message": f"System monitor operation failed: {e!s}"}

    def _handle_get_status(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle system status get operation."""
        try:
            detailed = params.get("detailed", False)

            # Get basic status
            status = {
                "status": "success",
                "message": "System status retrieved",
                "operation": "get_status",
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
                        "osc_enabled": self.mcp_server.osc_manager.enabled if self.mcp_server.osc_manager else False,
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
            return {"status": "error", "message": f"Failed to get system status: {e!s}"}

    def _handle_get_health(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle system health get operation."""
        try:
            include_memory = params.get("include_memory", True)
            include_cpu = params.get("include_cpu", True)

            health = {
                "status": "success",
                "message": "System health metrics retrieved",
                "operation": "get_health",
                "timestamp": time.time(),
            }

            if include_memory:
                health["memory_health"] = self._get_memory_usage()

            if include_cpu:
                health["cpu_health"] = self._get_system_load()

            # Add server health indicators
            health.update(
                {
                    "server_health": "healthy"
                    if self.mcp_server.initialized and self.mcp_server.running
                    else "unhealthy",
                    "vrm_manager_health": "healthy"
                    if hasattr(self.mcp_server, "vrm_manager") and self.mcp_server.vrm_manager
                    else "unhealthy",
                    "osc_health": "healthy"
                    if hasattr(self.mcp_server, "osc_manager")
                    and self.mcp_server.osc_manager
                    and self.mcp_server.osc_manager.enabled
                    else "disabled",
                }
            )

            return health

        except Exception as e:
            return {"status": "error", "message": f"Failed to get system health: {e!s}"}

    def _handle_get_metrics(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle system metrics get operation."""
        try:
            metric_type = params.get("metric_type", "all")

            metrics = {
                "status": "success",
                "message": "System metrics retrieved",
                "operation": "get_metrics",
                "timestamp": time.time(),
            }

            if metric_type in ["all", "performance"]:
                metrics["performance"] = {
                    "uptime": time.time() - self.mcp_server.start_time if hasattr(self.mcp_server, "start_time") else 0,
                    "active_tools": self._count_active_tools(),
                    "memory_usage": self._get_memory_usage(),
                    "system_load": self._get_system_load(),
                }

            if metric_type in ["all", "avatar"]:
                if hasattr(self.mcp_server, "vrm_manager") and self.mcp_server.vrm_manager:
                    metrics["avatar"] = {
                        "loaded_count": len(self.mcp_server.vrm_manager.avatars),
                        "active_avatar": self.mcp_server.vrm_manager.get_active_avatar_id(),
                    }

            if metric_type in ["all", "network"]:
                if hasattr(self.mcp_server, "osc_manager") and self.mcp_server.osc_manager:
                    metrics["network"] = {
                        "osc_enabled": self.mcp_server.osc_manager.enabled,
                        "osc_initialized": self.mcp_server.osc_manager.initialized,
                    }

            return metrics

        except Exception as e:
            return {"status": "error", "message": f"Failed to get system metrics: {e!s}"}

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
