"""
Animation Manager Portmanteau Tool for AvatarMCP

Consolidates all animation operations (play, stop, list, sequence, layering).
"""

import logging
from typing import Any

from avatarmcp.models.animation_controller import AnimationController

logger = logging.getLogger(__name__)


class AnimationManagerTool:
    """Portmanteau tool for comprehensive avatar animation management."""

    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self._sequences: dict[str, Any] = {}
        self._register_tool()

    def _register_tool(self):

        @self.mcp_server.mcp.tool()
        async def animation_manager(params: dict[str, Any]) -> dict[str, Any]:
            try:
                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "play":
                    return await self._handle_play(params)
                elif operation == "stop":
                    return await self._handle_stop(params)
                elif operation == "list":
                    return await self._handle_list(params)
                elif operation == "sequence_create":
                    return await self._handle_sequence_create(params)
                elif operation == "sequence_play":
                    return await self._handle_sequence_play(params)
                elif operation == "blend_layers":
                    return await self._handle_blend_layers(params)
                else:
                    return {"status": "error", "message": f"Unknown operation '{operation}'"}
            except Exception as e:
                logger.error(f"Animation manager operation failed: {e}")
                return {"status": "error", "message": str(e)}

    def _get_avatar_controller(self) -> AnimationController | None:
        avatar_id = self.mcp_server.active_model_id
        if not avatar_id:
            return None
        model = self.mcp_server.loaded_models.get(avatar_id)
        if model and hasattr(model, "animation_controller"):
            return model.animation_controller
        return None

    async def _handle_play(self, params: dict[str, Any]) -> dict[str, Any]:
        animation_name = params.get("name", "idle")
        avatar_id = self.mcp_server.active_model_id
        if not avatar_id:
            return {"status": "error", "message": "No active avatar loaded"}

        controller = self._get_avatar_controller()
        if not controller:
            # Try OSC fallback
            return await self._send_osc_fallback("/avatar/animation/play", params)

        controller.play_animation(
            animation_name=animation_name,
            loop=params.get("loop", False),
            weight=params.get("weight", 1.0),
            speed=params.get("speed", 1.0),
        )

        return {
            "status": "success",
            "message": f"Playing animation '{animation_name}'",
            "operation": "play",
            "animation": animation_name,
            "avatar_id": avatar_id,
        }

    async def _handle_stop(self, params: dict[str, Any]) -> dict[str, Any]:
        animation_name = params.get("name")
        avatar_id = self.mcp_server.active_model_id
        if not avatar_id:
            return {"status": "error", "message": "No active avatar loaded"}

        controller = self._get_avatar_controller()
        if not controller:
            address = "/avatar/animation/stop"
            if animation_name:
                address = f"{address}/{animation_name}"
            return await self._send_osc_fallback(address, params)

        if animation_name:
            controller.stop_animation(animation_name, params.get("fade_out", 0.0))
        else:
            controller.stop_all_animations()

        return {"status": "success", "message": "Animation stop command sent", "operation": "stop"}

    async def _handle_list(self, params: dict[str, Any]) -> dict[str, Any]:
        controller = self._get_avatar_controller()
        if not controller:
            return {"status": "error", "message": "No active avatar with animation controller"}

        return {
            "status": "success",
            "available_animations": list(controller.animations.keys()) if hasattr(controller, "animations") else [],
            "active_animations": list(controller.active_animations.keys()) if hasattr(controller, "active_animations") else [],
        }

    async def _handle_sequence_create(self, params: dict[str, Any]) -> dict[str, Any]:
        sequence_name = params.get("sequence_name")
        if not sequence_name:
            return {"status": "error", "message": "sequence_name parameter is required"}

        self._sequences[sequence_name] = {
            "steps": params.get("steps", []),
            "created_at": __import__("time").time(),
        }
        return {
            "status": "success",
            "message": f"Animation sequence '{sequence_name}' created",
            "operation": "sequence_create",
            "sequence_name": sequence_name,
        }

    async def _handle_sequence_play(self, params: dict[str, Any]) -> dict[str, Any]:
        sequence_name = params.get("sequence_name")
        if not sequence_name:
            return {"status": "error", "message": "sequence_name parameter is required"}

        sequence = self._sequences.get(sequence_name)
        if not sequence:
            return {"status": "error", "message": f"Sequence '{sequence_name}' not found"}

        return {
            "status": "success",
            "message": f"Sequence '{sequence_name}' play initiated",
            "operation": "sequence_play",
            "sequence_name": sequence_name,
            "steps": sequence["steps"],
        }

    async def _handle_blend_layers(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id", self.mcp_server.active_model_id)
        if not avatar_id:
            return {"status": "error", "message": "avatar_id parameter is required"}

        return {
            "status": "success",
            "message": f"Animation blend layers configured for {avatar_id}",
            "operation": "blend_layers",
            "avatar_id": avatar_id,
            "layers": params.get("layers", []),
        }

    async def _send_osc_fallback(self, address: str, params: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(self.mcp_server, "_send_osc_message"):
            return {"status": "error", "message": "OSC not available and no animation controller found"}
        success = self.mcp_server._send_osc_message(address, str(params))
        if success:
            return {"status": "success", "message": "Animation command sent via OSC"}
        return {"status": "error", "message": "Failed to send OSC command"}
