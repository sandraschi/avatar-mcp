"""
Core Animation Tools for AvatarMCP

This module contains the core animation control tools that are actually implemented
and working, as opposed to the advanced animation tools which are more experimental.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreAnimationTools:
    """Core animation tools with real implementations."""

    def __init__(self, mcp_server):
        """Initialize core animation tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register core animation tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        def animation_play(params: dict[str, Any]) -> dict[str, Any]:
            """Play an animation on the active avatar.

            Plays a specified animation on the currently active avatar with support
            for looping, weight blending, and speed control.

            Parameters:
                name: Name of the animation to play (default: "idle")
                loop: Whether to loop the animation (default: False)
                weight: Blend weight 0.0-1.0 (default: 1.0)
                speed: Playback speed multiplier (default: 1.0)

            Returns:
                Dictionary with status, animation details, and avatar info
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

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
                    "animation": animation_name,
                    "avatar_id": active_avatar_id,
                    "loop": loop,
                    "weight": weight,
                    "speed": speed,
                }

            except Exception as e:
                logger.error(f"Failed to play animation: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to play animation: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def animation_stop(params: dict[str, Any]) -> dict[str, Any]:
            """Stop animation(s) on the active avatar.

            Stops either a specific animation or all animations on the active avatar.

            Parameters:
                name: Name of animation to stop (optional, stops all if not provided)
                fade_out: Fade out time in seconds (default: 0.0)

            Returns:
                Dictionary with status and stop details
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

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
                    "avatar_id": active_avatar_id,
                    "animation": animation_name,
                    "fade_out": fade_out,
                }

            except Exception as e:
                logger.error(f"Failed to stop animation: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to stop animation: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def animation_list(params: dict[str, Any]) -> dict[str, Any]:
            """List available animations for the active avatar.

            Returns all animations available for the currently active avatar,
            including both loaded animations and default animations.

            Parameters:
                None required

            Returns:
                Dictionary with available animations, active animations, and counts
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

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
                    "avatar_id": active_avatar_id,
                    "available_animations": available_animations,
                    "active_animations": active_animations,
                    "total_count": len(available_animations),
                }

            except Exception as e:
                logger.error(f"Failed to list animations: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to list animations: {str(e)}"}
