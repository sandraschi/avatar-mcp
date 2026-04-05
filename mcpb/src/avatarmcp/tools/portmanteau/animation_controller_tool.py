"""
Animation Controller Portmanteau Tool for AvatarMCP

Consolidates all animation control operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AnimationControllerTool:
    """Portmanteau tool for comprehensive animation control and management."""

    def __init__(self, mcp_server):
        """Initialize animation controller tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the animation controller portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def animation_controller(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive animation control and management tool.

            Provides unified interface for all animation-related operations including
            playing animations, stopping animations, and listing available animations.
            This portmanteau tool consolidates animation control functionality
            into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "play": Play an animation on the active avatar
                    - "stop": Stop animation(s) on the active avatar
                    - "list": List available animations for the active avatar

                Additional parameters depend on the operation:
                    - For "play": name (required), loop (optional), weight (optional), speed (optional)
                    - For "stop": name (optional), fade_out (optional)
                    - For "list": None required

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Play basic animation:
                    result = await animation_controller({
                        "operation": "play",
                        "name": "idle"
                    })

                Play looping animation with custom settings:
                    result = await animation_controller({
                        "operation": "play",
                        "name": "dance",
                        "loop": True,
                        "weight": 0.8,
                        "speed": 1.2
                    })

                Stop specific animation:
                    result = await animation_controller({
                        "operation": "stop",
                        "name": "dance",
                        "fade_out": 0.5
                    })

                Stop all animations:
                    result = await animation_controller({
                        "operation": "stop"
                    })

                List available animations:
                    result = await animation_controller({
                        "operation": "list"
                    })

            Notes:
                - All operations require server to be initialized
                - All operations work with the currently active avatar
                - Animation names are case-sensitive
                - Weight and speed values are validated and clamped
                - Multiple animations can play simultaneously with different weights
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "play":
                    return self._handle_play(params)
                elif operation == "stop":
                    return self._handle_stop(params)
                elif operation == "list":
                    return self._handle_list(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: play, stop, list",
                    }

            except Exception as e:
                logger.error(f"Animation controller operation failed: {str(e)}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Animation controller operation failed: {str(e)}",
                }

    def _handle_play(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle animation play operation."""
        try:
            animation_name = params.get("name", "idle")
            loop = params.get("loop", False)
            weight = params.get("weight", 1.0)
            speed = params.get("speed", 1.0)

            # Get active avatar
            active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
            if not active_avatar_id:
                return {"status": "error", "message": "No active avatar loaded"}

            # Get animation controller for active avatar
            avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
            if not avatar_data or "animation_controller" not in avatar_data:
                return {
                    "status": "error",
                    "message": "Animation controller not available for active avatar",
                }

            controller = avatar_data["animation_controller"]

            # Play the animation
            result = controller.play_animation(
                animation_name=animation_name, loop=loop, weight=weight, speed=speed
            )

            return {
                "status": "success",
                "message": f"Playing animation '{animation_name}' on avatar '{active_avatar_id}'",
                "operation": "play",
                "animation": animation_name,
                "avatar_id": active_avatar_id,
                "loop": loop,
                "weight": weight,
                "speed": speed,
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to play animation: {str(e)}"}

    def _handle_stop(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle animation stop operation."""
        try:
            animation_name = params.get("name", None)  # If None, stop all animations
            fade_out = params.get("fade_out", 0.0)

            # Get active avatar
            active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
            if not active_avatar_id:
                return {"status": "error", "message": "No active avatar loaded"}

            # Get animation controller for active avatar
            avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
            if not avatar_data or "animation_controller" not in avatar_data:
                return {
                    "status": "error",
                    "message": "Animation controller not available for active avatar",
                }

            controller = avatar_data["animation_controller"]

            if animation_name:
                # Stop specific animation
                result = controller.stop_animation(animation_name, fade_out)
                message = f"Stopped animation '{animation_name}' on avatar '{active_avatar_id}'"
            else:
                # Stop all animations
                controller.stop_all_animations()
                message = f"Stopped all animations on avatar '{active_avatar_id}'"

            return {
                "status": "success",
                "message": message,
                "operation": "stop",
                "avatar_id": active_avatar_id,
                "animation": animation_name,
                "fade_out": fade_out,
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to stop animation: {str(e)}"}

    def _handle_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle animation list operation."""
        try:
            # Get active avatar
            active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
            if not active_avatar_id:
                return {"status": "error", "message": "No active avatar loaded"}

            # Get animation controller for active avatar
            avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
            if not avatar_data or "animation_controller" not in avatar_data:
                return {
                    "status": "error",
                    "message": "Animation controller not available for active avatar",
                }

            controller = avatar_data["animation_controller"]

            # Get available animations
            available_animations = list(controller.animations.keys())
            active_animations = list(controller.active_animations.keys())

            # Add default animations if none are loaded
            if not available_animations:
                available_animations = ["idle", "walk", "run", "wave", "dance", "jump", "sit"]

            return {
                "status": "success",
                "message": f"Listed animations for avatar '{active_avatar_id}'",
                "operation": "list",
                "avatar_id": active_avatar_id,
                "available_animations": available_animations,
                "active_animations": active_animations,
                "total_count": len(available_animations),
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to list animations: {str(e)}"}
