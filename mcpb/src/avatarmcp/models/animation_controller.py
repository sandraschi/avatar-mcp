"""
Animation Controller for managing VRM model animations.
"""

import time
from typing import Any


class AnimationController:
    """Controller for managing VRM model animations."""

    def __init__(self):
        """Initialize the animation controller."""
        self.animations: dict[str, dict[str, Any]] = {}
        self.active_animations: dict[str, dict[str, Any]] = {}

    def play_animation(
        self, animation_name: str, loop: bool = False, weight: float = 1.0, speed: float = 1.0
    ) -> dict[str, Any]:
        """Play an animation.

        Args:
            animation_name: Name of the animation to play
            loop: Whether to loop the animation
            weight: Blend weight (0.0 to 1.0)
            speed: Playback speed multiplier

        Returns:
            Dict with animation status
        """
        if animation_name not in self.animations:
            self.animations[animation_name] = {
                "name": animation_name,
                "start_time": time.time(),
                "loop": loop,
                "weight": max(0.0, min(1.0, weight)),
                "speed": max(0.1, speed),
                "paused": False,
            }

        self.active_animations[animation_name] = self.animations[animation_name]

        return {
            "status": "success",
            "animation": animation_name,
            "loop": loop,
            "weight": weight,
            "speed": speed,
        }

    def stop_animation(self, animation_name: str, fade_out: float = 0.0) -> dict[str, Any]:
        """Stop a playing animation.

        Args:
            animation_name: Name of the animation to stop
            fade_out: Fade out duration in seconds

        Returns:
            Dict with stop status
        """
        if animation_name in self.active_animations:
            if fade_out > 0:
                # Schedule fade out
                self.active_animations[animation_name]["fade_out"] = {
                    "start_time": time.time(),
                    "duration": fade_out,
                    "initial_weight": self.active_animations[animation_name]["weight"],
                }
            else:
                # Immediate stop
                self.active_animations.pop(animation_name, None)

        return {"status": "success", "animation": animation_name, "fade_out": fade_out}

    def update(self, delta_time: float):
        """Update all active animations.

        Args:
            delta_time: Time since last update in seconds
        """
        current_time = time.time()
        to_remove = []

        for name, anim in list(self.active_animations.items()):
            # Handle fade out
            if "fade_out" in anim:
                fade = anim["fade_out"]
                elapsed = current_time - fade["start_time"]

                if elapsed >= fade["duration"]:
                    to_remove.append(name)
                    continue

                # Update weight based on fade out progress
                progress = elapsed / fade["duration"]
                anim["weight"] = fade["initial_weight"] * (1.0 - progress)

            # Update animation state
            if not anim.get("paused", False):
                anim["elapsed"] = anim.get("elapsed", 0) + (delta_time * anim["speed"])

        # Remove completed animations
        for name in to_remove:
            self.active_animations.pop(name, None)

    def get_active_animations(self) -> list[dict[str, Any]]:
        """Get a list of all active animations."""
        return [
            {
                "name": anim["name"],
                "weight": anim["weight"],
                "speed": anim["speed"],
                "loop": anim["loop"],
                "paused": anim.get("paused", False),
            }
            for anim in self.active_animations.values()
        ]

    def clear(self):
        """Clear all animations."""
        self.animations.clear()
        self.active_animations.clear()
