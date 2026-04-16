"""
Animation-related commands for AvatarMCP.

This module provides commands for managing animations on VRM models,
including playing, stopping, and querying animation states.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..app import AvatarMCP

# Re-export for easy imports
__all__ = ["register_commands"]


def register_commands(registry):
    """Register all animation-related commands.

    Args:
        registry: Command registry instance to register commands with
    """

    @registry.register(
        name="play_animation",
        description="Play an animation on a model.",
        examples=[
            "play_animation('model_123', 'idle')",
            "play_animation(model_id='model_123', animation_name='wave', loop=True, weight=0.8, speed=1.2)",
        ],
    )
    def play_animation(
        app: AvatarMCP,
        model_id: str,
        animation_name: str,
        loop: bool = False,
        weight: float = 1.0,
        speed: float = 1.0,
    ) -> dict[str, Any]:
        """Play an animation on a model.

        Args:
            model_id: ID of the model to animate
            animation_name: Name of the animation to play
            loop: Whether to loop the animation
            weight: Blend weight (0.0 to 1.0)
            speed: Playback speed multiplier

        Returns:
            Dict with status and animation details
        """
        if model_id not in app.models:
            return {"status": "error", "error": f"Model {model_id} not found", "model_id": model_id}

        try:
            controller = app.animation_controllers[model_id]
            controller.play_animation(animation_name=animation_name, loop=loop, weight=weight, speed=speed)

            return {
                "status": "success",
                "model_id": model_id,
                "animation": animation_name,
                "loop": loop,
                "weight": weight,
                "speed": speed,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_id": model_id,
                "animation": animation_name,
            }

    @registry.register(
        name="stop_animation",
        description="Stop a playing animation on a model.",
        examples=[
            "stop_animation('model_123', 'wave')",
            "stop_animation(model_id='model_123', animation_name='wave', fade_out=0.5)",
        ],
    )
    def stop_animation(app: AvatarMCP, model_id: str, animation_name: str, fade_out: float = 0.0) -> dict[str, Any]:
        """Stop a playing animation on a model.

        Args:
            model_id: ID of the model
            animation_name: Name of the animation to stop
            fade_out: Fade out duration in seconds

        Returns:
            Dict with status information
        """
        if model_id not in app.models:
            return {"status": "error", "error": f"Model {model_id} not found", "model_id": model_id}

        try:
            controller = app.animation_controllers.get(model_id)
            if not controller:
                return {
                    "status": "error",
                    "error": f"No animation controller found for model {model_id}",
                    "model_id": model_id,
                }

            controller.stop_animation(animation_name, fade_out=fade_out)

            return {
                "status": "success",
                "model_id": model_id,
                "animation": animation_name,
                "fade_out": fade_out,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_id": model_id,
                "animation": animation_name,
            }

    @registry.register(
        name="list_animations",
        description="List all animations for a model.",
        examples=["list_animations('model_123')"],
    )
    def list_animations(app: AvatarMCP, model_id: str) -> dict[str, Any]:
        """List all animations for a model.

        Args:
            model_id: ID of the model

        Returns:
            Dict with status and list of animations
        """
        if model_id not in app.models:
            return {"status": "error", "error": f"Model {model_id} not found", "model_id": model_id}

        try:
            controller = app.animation_controllers.get(model_id)
            if not controller:
                return {"status": "success", "model_id": model_id, "animations": []}

            animations = controller.get_animation_list()

            return {"status": "success", "model_id": model_id, "animations": animations}

        except Exception as e:
            return {"status": "error", "error": str(e), "model_id": model_id}

    @registry.register(
        name="get_animation_state",
        description="Get the current state of an animation.",
        examples=["get_animation_state('model_123', 'wave')"],
    )
    def get_animation_state(app: AvatarMCP, model_id: str, animation_name: str) -> dict[str, Any]:
        """Get the current state of an animation.

        Args:
            model_id: ID of the model
            animation_name: Name of the animation

        Returns:
            Dict with animation state information
        """
        if model_id not in app.models:
            return {"status": "error", "error": f"Model {model_id} not found", "model_id": model_id}

        try:
            controller = app.animation_controllers.get(model_id)
            if not controller:
                return {
                    "status": "error",
                    "error": f"No animation controller found for model {model_id}",
                    "model_id": model_id,
                }

            state = controller.get_animation_state(animation_name)
            if not state:
                return {
                    "status": "error",
                    "error": f"Animation {animation_name} not found",
                    "model_id": model_id,
                    "animation": animation_name,
                }

            return {
                "status": "success",
                "model_id": model_id,
                "animation": animation_name,
                "state": state,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_id": model_id,
                "animation": animation_name,
            }
