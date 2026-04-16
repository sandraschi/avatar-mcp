"""
Unity Integration Portmanteau Tool for AvatarMCP

Consolidates all Unity desktop avatar operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import logging
import os
import subprocess
import sys
from typing import Any

logger = logging.getLogger(__name__)


class UnityIntegrationTool:
    """Portmanteau tool for comprehensive Unity desktop avatar integration."""

    def __init__(self, mcp_server):
        """Initialize Unity integration tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self.unity_app_process = None
        self._register_tool()

    def _ensure_unity_app_running(self) -> bool:
        """Ensure the Unity desktop avatar application is running."""
        try:
            # Check if OSC client is available
            if not hasattr(self.mcp_server, "osc_manager") or not self.mcp_server.osc_manager:
                logger.warning("OSC manager not available - cannot communicate with Unity")
                return False

            # Check if process is still running
            if self.unity_app_process and self.unity_app_process.poll() is None:
                return True

            # Try to launch the Unity desktop avatar viewer
            viewer_paths = [
                os.path.join(os.getcwd(), "desktop_avatar_viewer.py"),
                os.path.join(os.getcwd(), "src", "desktop_avatar_viewer.py"),
                os.path.join(os.getcwd(), "unity-desktop-avatar", "DesktopAvatarViewer.exe"),
            ]

            for viewer_path in viewer_paths:
                if os.path.exists(viewer_path):
                    try:
                        if viewer_path.endswith(".exe"):
                            self.unity_app_process = subprocess.Popen([viewer_path])
                        else:
                            self.unity_app_process = subprocess.Popen([sys.executable, viewer_path])

                        logger.info(f"Launched Unity desktop avatar viewer: {viewer_path}")
                        return True
                    except Exception as e:
                        logger.error(f"Failed to launch {viewer_path}: {e}")
                        continue

            logger.warning("No Unity desktop avatar viewer found")
            return False

        except Exception as e:
            logger.error(f"Error checking Unity app status: {e}")
            return False

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
        """Register the Unity integration portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def unity_integration(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive Unity desktop avatar integration tool.

            Provides unified interface for all Unity desktop avatar operations including
            system status monitoring, avatar loading, expression control, and animation
            management. This portmanteau tool consolidates Unity integration functionality
            into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "status": Get Unity desktop avatar system status
                    - "load_avatar": Load a VRM avatar into Unity desktop system
                    - "set_expression": Control facial expressions on Unity avatar
                    - "control_animation": Control animations on Unity avatar

                Additional parameters depend on the operation:
                    - For "status": detailed (optional)
                    - For "load_avatar": path (required), make_active (optional)
                    - For "set_expression": expression (required), strength (optional)
                    - For "control_animation": action (required), animation_name (optional), loop (optional)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Get Unity system status:
                    result = await unity_integration({
                        "operation": "status",
                        "detailed": True
                    })

                Load avatar into Unity:
                    result = await unity_integration({
                        "operation": "load_avatar",
                        "path": "models/my_avatar.vrm",
                        "make_active": True
                    })

                Set facial expression:
                    result = await unity_integration({
                        "operation": "set_expression",
                        "expression": "Happy",
                        "strength": 0.8
                    })

                Control animation:
                    result = await unity_integration({
                        "operation": "control_animation",
                        "action": "play",
                        "animation_name": "wave",
                        "loop": False
                    })

            Notes:
                - All operations require server to be initialized
                - Unity desktop avatar application must be running
                - OSC communication is used for Unity control
                - Avatar loading may take several seconds for complex models
                - Expression strength is clamped to 0.0-1.0 range
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "status":
                    return self._handle_status(params)
                elif operation == "load_avatar":
                    return self._handle_load_avatar(params)
                elif operation == "set_expression":
                    return self._handle_set_expression(params)
                elif operation == "control_animation":
                    return self._handle_control_animation(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: status, load_avatar, set_expression, control_animation",
                    }

            except Exception as e:
                logger.error(f"Unity integration operation failed: {e!s}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Unity integration operation failed: {e!s}",
                }

    def _handle_status(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity system status operation."""
        try:
            detailed = params.get("detailed", False)

            # Check Unity app status
            unity_running = self._ensure_unity_app_running()

            # Check OSC connection
            osc_connected = (
                self.mcp_server.osc_manager is not None
                and self.mcp_server.osc_manager.enabled
                and self.mcp_server.osc_manager.osc_client is not None
            )

            status = {
                "status": "success",
                "message": "Unity system status retrieved",
                "operation": "status",
                "unity_running": unity_running,
                "osc_connected": osc_connected,
                "osc_enabled": self.mcp_server.osc_manager.enabled if self.mcp_server.osc_manager else False,
                "timestamp": __import__("time").time(),
            }

            if detailed:
                status.update(
                    {
                        "osc_server_address": self.mcp_server.osc_manager.osc_config.server_address
                        if self.mcp_server.osc_manager
                        else None,
                        "osc_server_port": self.mcp_server.osc_manager.osc_config.server_port
                        if self.mcp_server.osc_manager
                        else None,
                        "osc_client_address": self.mcp_server.osc_manager.osc_config.client_address
                        if self.mcp_server.osc_manager
                        else None,
                        "osc_client_port": self.mcp_server.osc_manager.osc_config.client_port
                        if self.mcp_server.osc_manager
                        else None,
                    }
                )

            return status

        except Exception as e:
            return {"status": "error", "message": f"Failed to get Unity system status: {e!s}"}

    def _handle_load_avatar(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity avatar load operation."""
        try:
            path = params.get("path")
            if not path:
                return {
                    "status": "error",
                    "message": "VRM file path is required for load_avatar operation",
                }

            make_active = params.get("make_active", True)

            # Ensure Unity app is running
            if not self._ensure_unity_app_running():
                return {
                    "status": "error",
                    "message": "Unity desktop avatar application is not running",
                }

            # Send OSC command to Unity to load avatar
            success = self._send_unity_osc("/unity/avatar/load", path, make_active)

            if success:
                return {
                    "status": "success",
                    "message": f"Loading VRM avatar from {path}",
                    "operation": "load_avatar",
                    "path": path,
                    "make_active": make_active,
                    "unity_command_sent": True,
                }
            else:
                return {"status": "error", "message": "Failed to send Unity load command"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to load Unity avatar: {e!s}"}

    def _handle_set_expression(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity avatar expression operation."""
        try:
            expression = params.get("expression")
            if not expression:
                return {
                    "status": "error",
                    "message": "Expression name is required for set_expression operation",
                }

            strength = params.get("strength", 1.0)
            strength = max(0.0, min(1.0, strength))  # Clamp to 0-1 range

            # Send OSC command to Unity to set expression
            success = self._send_unity_osc("/unity/avatar/expression", expression, strength)

            if success:
                return {
                    "status": "success",
                    "message": f"Set Unity avatar expression '{expression}' to {strength}",
                    "operation": "set_expression",
                    "expression": expression,
                    "strength": strength,
                    "unity_command_sent": True,
                }
            else:
                return {"status": "error", "message": "Failed to send Unity expression command"}

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to set Unity avatar expression: {e!s}",
            }

    def _handle_control_animation(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity avatar animation control operation."""
        try:
            action = params.get("action")
            if not action:
                return {
                    "status": "error",
                    "message": "Action is required for control_animation operation",
                }

            animation_name = params.get("animation_name", "")
            loop = params.get("loop", False)

            # Send OSC command to Unity based on action
            if action == "play":
                if not animation_name:
                    return {
                        "status": "error",
                        "message": "Animation name is required for play action",
                    }
                success = self._send_unity_osc("/unity/avatar/animation/play", animation_name, loop)
            elif action == "stop":
                success = self._send_unity_osc("/unity/avatar/animation/stop")
            elif action == "pause":
                success = self._send_unity_osc("/unity/avatar/animation/pause")
            else:
                return {
                    "status": "error",
                    "message": f"Invalid action '{action}'. Use 'play', 'stop', or 'pause'",
                }

            if success:
                return {
                    "status": "success",
                    "message": f"Unity avatar animation {action} command sent",
                    "operation": "control_animation",
                    "action": action,
                    "animation_name": animation_name,
                    "loop": loop,
                    "unity_command_sent": True,
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to send Unity animation {action} command",
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to control Unity avatar animation: {e!s}",
            }
