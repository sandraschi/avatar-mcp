"""
Unity Window Manager Portmanteau Tool for AvatarMCP

Consolidates all Unity desktop avatar window management operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class UnityWindowManagerTool:
    """Portmanteau tool for comprehensive Unity desktop avatar window management."""

    def __init__(self, mcp_server):
        """Initialize Unity window manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _send_unity_osc(self, address: str, *args) -> bool:
        """Send OSC message to Unity desktop avatar."""
        try:
            if not self.mcp_server.osc_manager or not self.mcp_server.osc_manager.osc_client:
                return False

            self.mcp_server.osc_manager.osc_client.send_message(address, *args)
            return True
        except Exception as e:
            logger.error(f"Failed to send OSC to Unity: {e}")
            return False

    def _register_tool(self):
        """Register the Unity window manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def unity_window_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive Unity desktop avatar window management tool.

            Provides unified interface for all Unity desktop avatar window operations
            including positioning, transparency control, visibility management, and
            interaction modes. This portmanteau tool consolidates window management
            functionality into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "position": Set window position and size
                    - "transparency": Control window transparency/opacity
                    - "visibility": Show/hide window
                    - "mode": Set interaction mode (interactive/clickthrough)

                Additional parameters depend on the operation:
                    - For "position": x (optional), y (optional), width (optional),
                      height (optional)
                    - For "transparency": opacity (required, 0.0-1.0)
                    - For "visibility": visible (required, true/false)
                    - For "mode": mode (required, "interactive"/"clickthrough")

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Set window position:
                    result = await unity_window_manager({
                        "operation": "position",
                        "x": 100,
                        "y": 100,
                        "width": 800,
                        "height": 600
                    })

                Set window transparency:
                    result = await unity_window_manager({
                        "operation": "transparency",
                        "opacity": 0.8
                    })

                Hide window:
                    result = await unity_window_manager({
                        "operation": "visibility",
                        "visible": False
                    })

                Set click-through mode:
                    result = await unity_window_manager({
                        "operation": "mode",
                        "mode": "clickthrough"
                    })

            Notes:
                - All operations require server to be initialized
                - Unity desktop avatar application must be running
                - OSC communication is used for Unity control
                - Position coordinates are screen pixels
                - Opacity values are clamped to 0.0-1.0 range
                - Mode changes take effect immediately
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "position":
                    return self._handle_position(params)
                elif operation == "transparency":
                    return self._handle_transparency(params)
                elif operation == "visibility":
                    return self._handle_visibility(params)
                elif operation == "mode":
                    return self._handle_mode(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: "
                        "position, transparency, visibility, mode",
                    }

            except Exception as e:
                logger.error(f"Unity window manager operation failed: {e!s}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Unity window manager operation failed: {e!s}",
                }

    def _handle_position(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window position operation."""
        try:
            x = params.get("x", 100)
            y = params.get("y", 100)
            width = params.get("width", 800)
            height = params.get("height", 600)

            # Validate parameters
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                return {"status": "error", "message": "Position coordinates must be numbers"}
            if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
                return {"status": "error", "message": "Size dimensions must be numbers"}
            if width <= 0 or height <= 0:
                return {"status": "error", "message": "Width and height must be positive"}

            # Send OSC command to Unity to set window position
            success = self._send_unity_osc("/unity/window/position", x, y, width, height)

            if success:
                return {
                    "status": "success",
                    "message": f"Set Unity window position to ({x}, {y}) with size {width}x{height}",
                    "operation": "position",
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "unity_command_sent": True,
                }
            else:
                return {"status": "error", "message": "Failed to send Unity position command"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to set Unity window position: {e!s}"}

    def _handle_transparency(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window transparency operation."""
        try:
            opacity = params.get("opacity")
            if opacity is None:
                return {
                    "status": "error",
                    "message": "Opacity parameter is required for transparency operation",
                }

            # Validate and clamp opacity
            try:
                opacity = float(opacity)
                opacity = max(0.0, min(1.0, opacity))  # Clamp to 0-1 range
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": "Opacity must be a number between 0.0 and 1.0",
                }

            # Send OSC command to Unity to set transparency
            success = self._send_unity_osc("/unity/window/transparency", opacity)

            if success:
                return {
                    "status": "success",
                    "message": f"Set Unity window transparency to {opacity}",
                    "operation": "transparency",
                    "opacity": opacity,
                    "unity_command_sent": True,
                }
            else:
                return {"status": "error", "message": "Failed to send Unity transparency command"}

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to set Unity window transparency: {e!s}",
            }

    def _handle_visibility(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window visibility operation."""
        try:
            visible = params.get("visible")
            if visible is None:
                return {
                    "status": "error",
                    "message": "Visible parameter is required for visibility operation",
                }

            # Convert to boolean
            if isinstance(visible, str):
                visible = visible.lower() in ("true", "1", "yes", "on")
            elif isinstance(visible, (int, float)):
                visible = bool(visible)
            elif not isinstance(visible, bool):
                return {"status": "error", "message": "Visible must be a boolean value"}

            # Send OSC command to Unity to set visibility
            success = self._send_unity_osc("/unity/window/visibility", visible)

            if success:
                return {
                    "status": "success",
                    "message": f"Set Unity window visibility to {visible}",
                    "operation": "visibility",
                    "visible": visible,
                    "unity_command_sent": True,
                }
            else:
                return {"status": "error", "message": "Failed to send Unity visibility command"}

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to set Unity window visibility: {e!s}",
            }

    def _handle_mode(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window interaction mode operation."""
        try:
            mode = params.get("mode")
            if not mode:
                return {
                    "status": "error",
                    "message": "Mode parameter is required for mode operation",
                }

            # Validate mode
            valid_modes = ["interactive", "clickthrough"]
            if mode not in valid_modes:
                return {
                    "status": "error",
                    "message": f"Mode must be one of: {', '.join(valid_modes)}",
                }

            # Send OSC command to Unity to set interaction mode
            success = self._send_unity_osc("/unity/window/mode", mode)

            if success:
                return {
                    "status": "success",
                    "message": f"Set Unity window mode to {mode}",
                    "operation": "mode",
                    "mode": mode,
                    "unity_command_sent": True,
                }
            else:
                return {"status": "error", "message": "Failed to send Unity mode command"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to set Unity window mode: {e!s}"}
