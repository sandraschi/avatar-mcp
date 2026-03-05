"""
Animation Manager Portmanteau Tool for AvatarMCP

Consolidates all animation operations (play, stop, list, sequence, layering).
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AnimationManagerTool:
    """Portmanteau tool for comprehensive avatar animation management."""

    def __init__(self, mcp_server):
        """Initialize animation manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the animation manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def animation_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Unified tool for all avatar animation and layering operations.

            Parameters:
                operation: The specific operation to perform (required)
                    - "play": Play an animation on the active avatar
                    - "stop": Stop animation(s) on the active avatar
                    - "list": List available animations for the active avatar
                    - "sequence_create": Create a complex multi-step animation sequence
                    - "sequence_play": Play a saved animation sequence
                    - "blend_layers": Layer multiple animations with weights and priorities

                Additional parameters depend on the operation.
            """
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "play":
                    return self._handle_play(params)
                elif operation == "stop":
                    return self._handle_stop(params)
                elif operation == "list":
                    return self._handle_list(params)
                elif operation == "sequence_create":
                    return self._handle_sequence_create(params)
                elif operation == "sequence_play":
                    return self._handle_sequence_play(params)
                elif operation == "blend_layers":
                    return self._handle_blend_layers(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'",
                    }
            except Exception as e:
                logger.error(f"Animation manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _handle_play(self, params: dict[str, Any]) -> dict[str, Any]:
        animation_name = params.get("name", "idle")
        active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
        if not active_avatar_id:
            return {"status": "error", "message": "No active avatar loaded"}

        avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
        if not avatar_data or "animation_controller" not in avatar_data:
            return {"status": "error", "message": "Animation controller not available"}

        controller = avatar_data["animation_controller"]
        controller.play_animation(
            animation_name=animation_name,
            loop=params.get("loop", False),
            weight=params.get("weight", 1.0),
            speed=params.get("speed", 1.0),
        )

        return {
            "status": "success",
            "message": f"Playing animation '{animation_name}' on avatar '{active_avatar_id}'",
            "operation": "play",
            "animation": animation_name,
            "avatar_id": active_avatar_id,
        }

    def _handle_stop(self, params: dict[str, Any]) -> dict[str, Any]:
        animation_name = params.get("name")
        fade_out = params.get("fade_out", 0.0)
        active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
        if not active_avatar_id:
            return {"status": "error", "message": "No active avatar loaded"}

        avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
        if not avatar_data or "animation_controller" not in avatar_data:
            return {"status": "error", "message": "Animation controller not available"}

        controller = avatar_data["animation_controller"]
        if animation_name:
            controller.stop_animation(animation_name, fade_out)
        else:
            controller.stop_all_animations()

        return {
            "status": "success",
            "message": "Animation stop command sent",
            "operation": "stop",
            "avatar_id": active_avatar_id,
        }

    def _handle_list(self, params: dict[str, Any]) -> dict[str, Any]:
        active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
        if not active_avatar_id:
            return {"status": "error", "message": "No active avatar loaded"}

        avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
        if not avatar_data or "animation_controller" not in avatar_data:
            return {"status": "error", "message": "Animation controller not available"}

        controller = avatar_data["animation_controller"]
        return {
            "status": "success",
            "available_animations": list(controller.animations.keys()),
            "active_animations": list(controller.active_animations.keys()),
        }

    def _handle_sequence_create(self, params: dict[str, Any]) -> dict[str, Any]:
        sequence_name = params.get("sequence_name")
        if not sequence_name:
            return {"status": "error", "message": "sequence_name parameter is required"}

        osc_address = "/avatar/animation/sequence/create"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": f"Animation sequence '{sequence_name}' creation command sent",
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_sequence_play(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id")
        sequence_name = params.get("sequence_name")
        if not avatar_id or not sequence_name:
            return {
                "status": "error",
                "message": "Both avatar_id and sequence_name parameters are required",
            }

        osc_address = "/avatar/animation/sequence/play"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": f"Sequence '{sequence_name}' play command sent for '{avatar_id}'",
            }
        return {"status": "error", "message": "Failed to send OSC command"}

    def _handle_blend_layers(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id")
        if not avatar_id:
            return {"status": "error", "message": "avatar_id parameter is required"}

        osc_address = "/avatar/animation/blend/layers"
        if self.mcp_server._send_osc_message(osc_address, str(params)):
            return {
                "status": "success",
                "message": "Animation blend layers command sent",
            }
        return {"status": "error", "message": "Failed to send OSC command"}
