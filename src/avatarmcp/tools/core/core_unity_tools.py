"""
Core Unity Tools for AvatarMCP

This module contains the core Unity desktop avatar tools that are actually implemented
and working for Unity integration and control.
"""

import logging
import os
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class CoreUnityTools:
    """Core Unity tools with real implementations."""

    def __init__(self, mcp_server):
        """Initialize core Unity tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self.unity_app_process = None
        self._register_tools()

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

    def _register_tools(self):
        """Register core Unity tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        def unity_system_status(params: dict[str, Any]) -> dict[str, Any]:
            """Get Unity desktop avatar system status.

            Returns the current status of the Unity desktop avatar system including
            connection status, loaded avatars, and system health.

            Parameters:
                detailed: Whether to include detailed system information (default: False)

            Returns:
                Dictionary with Unity system status
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

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
                logger.error(f"Failed to get Unity system status: {e!s}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Failed to get Unity system status: {e!s}",
                }

        @self.mcp_server.mcp.tool()
        def unity_avatar_load(params: dict[str, Any]) -> dict[str, Any]:
            """Load a VRM avatar into Unity desktop avatar system.

            Loads a VRM avatar model into the Unity desktop application for display
            and interaction.

            Parameters:
                path: Path to the VRM file to load (required)
                make_active: Whether to make this the active avatar (default: True)

            Returns:
                Dictionary with load status and avatar details
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                path = params.get("path")
                if not path:
                    return {"status": "error", "message": "VRM file path is required"}

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
                        "path": path,
                        "make_active": make_active,
                        "unity_command_sent": True,
                    }
                else:
                    return {"status": "error", "message": "Failed to send Unity load command"}

            except Exception as e:
                logger.error(f"Failed to load Unity avatar: {e!s}", exc_info=True)
                return {"status": "error", "message": f"Failed to load Unity avatar: {e!s}"}

        @self.mcp_server.mcp.tool()
        def unity_avatar_expression(params: dict[str, Any]) -> dict[str, Any]:
            """Control facial expressions on Unity desktop avatar.

            Sets facial expressions on the active Unity desktop avatar using
            blend shapes and morph targets.

            Parameters:
                expression: Name of the expression to set (required)
                strength: Intensity of the expression 0.0-1.0 (default: 1.0)

            Returns:
                Dictionary with expression control status
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                expression = params.get("expression")
                if not expression:
                    return {"status": "error", "message": "Expression name is required"}

                strength = params.get("strength", 1.0)
                strength = max(0.0, min(1.0, strength))  # Clamp to 0-1 range

                # Send OSC command to Unity to set expression
                success = self._send_unity_osc("/unity/avatar/expression", expression, strength)

                if success:
                    return {
                        "status": "success",
                        "message": f"Set Unity avatar expression '{expression}' to {strength}",
                        "expression": expression,
                        "strength": strength,
                        "unity_command_sent": True,
                    }
                else:
                    return {"status": "error", "message": "Failed to send Unity expression command"}

            except Exception as e:
                logger.error(f"Failed to set Unity avatar expression: {e!s}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Failed to set Unity avatar expression: {e!s}",
                }

        @self.mcp_server.mcp.tool()
        def unity_avatar_animation(params: dict[str, Any]) -> dict[str, Any]:
            """Control animations on Unity desktop avatar.

            Plays, stops, or controls animation states on the active Unity desktop avatar.

            Parameters:
                action: Action to perform - "play", "stop", "pause" (required)
                animation_name: Name of animation (required for play action)
                loop: Whether to loop animation (default: False)

            Returns:
                Dictionary with animation control status
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                action = params.get("action")
                if not action:
                    return {"status": "error", "message": "Action is required (play, stop, pause)"}

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
                logger.error(f"Failed to control Unity avatar animation: {e!s}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Failed to control Unity avatar animation: {e!s}",
                }
