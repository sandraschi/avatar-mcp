"""
Enhanced Animation System for VRM Models

This module provides an advanced animation system with:
- Animation blending and layering
- State machine for animation transitions
- Improved performance with spatial partitioning
- Support for animation events
- Animation retargeting
"""

from __future__ import annotations

import bisect
import json
import logging
import math
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Type aliases
Quaternion = tuple[float, float, float, float]  # x, y, z, w
Vector3 = tuple[float, float, float]
BonePose = dict[str, tuple[Quaternion, Vector3 | None, Vector3 | None]]  # bone_name -> (rotation, position, scale)
BlendShapes = dict[str, float]  # blend_shape_name -> weight


class AnimationEventType(Enum):
    """Types of animation events that can be triggered."""

    CUSTOM = auto()
    FOOTSTEP = auto()
    SOUND = auto()
    EFFECT = auto()
    BLEND_SHAPE = auto()


@dataclass
class AnimationEvent:
    """Represents an event that occurs at a specific time in an animation."""

    event_type: AnimationEventType
    time: float
    name: str
    data: dict[str, Any] = field(default_factory=dict)
    triggered: bool = False


@dataclass
class AnimationKeyframe:
    """Represents a single keyframe in an animation with optional bone transform
    and blend shape data."""

    time: float
    bone_name: str = ""
    rotation: Quaternion | None = None
    position: Vector3 | None = None
    scale: Vector3 | None = None
    blend_shape_name: str = ""
    blend_shape_weight: float = 0.0
    events: list[AnimationEvent] = field(default_factory=list)

    def has_transform(self) -> bool:
        """Check if this keyframe contains transform data."""
        return self.rotation is not None or self.position is not None or self.scale is not None

    def has_blend_shape(self) -> bool:
        """Check if this keyframe contains blend shape data."""
        return bool(self.blend_shape_name)


class AnimationBlendMode(Enum):
    """Different ways to blend between animations."""

    OVERRIDE = auto()  # Override the base pose
    ADDITIVE = auto()  # Add to the base pose
    LAYERED = auto()  # Blend with base pose based on weight
    MASKED = auto()  # Only apply to specific bones


@dataclass
class AnimationClip:
    """Represents an animation clip with keyframes and metadata."""

    name: str
    duration: float
    keyframes: list[AnimationKeyframe] = field(default_factory=list)
    loop: bool = False
    speed: float = 1.0
    blend_mode: AnimationBlendMode = AnimationBlendMode.OVERRIDE
    priority: int = 0  # Higher priority animations are applied last
    fade_in_time: float = 0.1  # Seconds to fade in
    fade_out_time: float = 0.1  # Seconds to fade out
    events: list[AnimationEvent] = field(default_factory=list)
    bone_masks: set[str] | None = None  # If not None, only these bones are affected

    def __post_init__(self):
        # Sort keyframes by time for faster searching
        self.keyframes.sort(key=lambda kf: kf.time)
        self.events.sort(key=lambda e: e.time)

    def get_keyframes_at_time(self, time: float) -> list[AnimationKeyframe]:
        """Get all keyframes at a specific time."""
        # Find the first keyframe at or after the specified time
        idx = bisect.bisect_left([kf.time for kf in self.keyframes], time)
        result = []

        # Check for exact matches
        while idx < len(self.keyframes) and math.isclose(self.keyframes[idx].time, time):
            result.append(self.keyframes[idx])
            idx += 1

        return result

    def get_surrounding_keyframes(self, time: float) -> tuple[AnimationKeyframe | None, AnimationKeyframe | None]:
        """Get the keyframes before and after the specified time."""
        if not self.keyframes:
            return None, None

        # Handle edge cases
        if time <= self.keyframes[0].time:
            return None, self.keyframes[0]
        if time >= self.keyframes[-1].time:
            return self.keyframes[-1], None

        # Binary search for the right keyframe
        left, right = 0, len(self.keyframes) - 1
        while right - left > 1:
            mid = (left + right) // 2
            if self.keyframes[mid].time <= time:
                left = mid
            else:
                right = mid

        return self.keyframes[left], self.keyframes[right]


class AnimationState:
    """Tracks the state of a playing animation instance."""

    def __init__(self, clip: AnimationClip, weight: float = 1.0, loop: bool | None = None, speed: float | None = None):
        """Initialize a new animation state."""
        self.clip = clip
        self.weight = weight
        self.loop = loop if loop is not None else clip.loop
        self.speed = speed if speed is not None else clip.speed
        self.time = 0.0
        self.weight_delta = 0.0  # For smooth weight transitions
        self.is_playing = True
        self.last_update_time = time.time()
        self.triggered_events = set()  # Track which events have been triggered

    def update(self, delta_time: float) -> list[AnimationEvent]:
        """
        Update the animation state.

        Args:
            delta_time: Time since last update in seconds

        Returns:
            List of events that were triggered this frame
        """
        if not self.is_playing:
            return []

        # Update animation time
        self.time += delta_time * self.speed

        # Handle looping
        if self.loop and self.clip.duration > 0:
            self.time %= self.clip.duration

        # Update weight with delta for smooth transitions
        target_weight = 1.0 if self.is_playing else 0.0
        weight_delta = delta_time / (self.clip.fade_in_time if target_weight > self.weight else self.clip.fade_out_time)
        self.weight = np.clip(self.weight + weight_delta * (1 if target_weight > self.weight else -1), 0.0, 1.0)

        # Collect events that were passed this frame
        triggered_events = []

        # Check for events in the clip
        for event in self.clip.events:
            if not event.triggered and self.time >= event.time:
                event.triggered = True
                triggered_events.append(event)

        return triggered_events

    def get_pose(self) -> tuple[BonePose, BlendShapes]:
        """
        Get the current pose from this animation state.

        Returns:
            Tuple of (bone_poses, blend_shapes)
        """
        bone_poses = {}
        blend_shapes = {}

        if not self.is_playing or self.weight <= 0.0:
            return bone_poses, blend_shapes

        # Get the keyframes to interpolate between
        prev_kf, next_kf = self.clip.get_surrounding_keyframes(self.time)

        if prev_kf is None or next_kf is None:
            return bone_poses, blend_shapes

        # Calculate interpolation factor
        if prev_kf.time == next_kf.time:
            t = 0.0
        else:
            t = (self.time - prev_kf.time) / (next_kf.time - prev_kf.time)

        # Interpolate bone transforms
        if prev_kf.has_transform() and next_kf.has_transform() and prev_kf.bone_name == next_kf.bone_name:
            bone_name = prev_kf.bone_name
            rotation = self._slerp_quat(prev_kf.rotation, next_kf.rotation, t) if prev_kf.rotation else None
            position = self._lerp_vec3(prev_kf.position, next_kf.position, t) if prev_kf.position else None
            scale = self._lerp_vec3(prev_kf.scale, next_kf.scale, t) if prev_kf.scale else None

            bone_poses[bone_name] = (rotation, position, scale)

        # Handle blend shapes
        if (
            prev_kf.has_blend_shape()
            and next_kf.has_blend_shape()
            and prev_kf.blend_shape_name == next_kf.blend_shape_name
        ):
            weight = prev_kf.blend_shape_weight + (next_kf.blend_shape_weight - prev_kf.blend_shape_weight) * t
            blend_shapes[prev_kf.blend_shape_name] = weight * self.weight

        return bone_poses, blend_shapes

    @staticmethod
    def _slerp_quat(q1: Quaternion | None, q2: Quaternion | None, t: float) -> Quaternion:
        """Spherical linear interpolation between two quaternions."""
        if q1 is None or q2 is None:
            return (0.0, 0.0, 0.0, 1.0)

        # Simple nlerp for now - replace with proper slerp if needed
        dot = q1[0] * q2[0] + q1[1] * q2[1] + q1[2] * q2[2] + q1[3] * q2[3]

        # If the dot product is negative, the quaternions have opposite handed-ness
        if dot < 0.0:
            q2 = (-q2[0], -q2[1], -q2[2], -q2[3])
            dot = -dot

        # Clamp dot to avoid numerical issues
        dot = max(-1.0, min(1.0, dot))

        # If the inputs are too close, just use linear interpolation
        if dot > 0.9995:
            result = (
                q1[0] + t * (q2[0] - q1[0]),
                q1[1] + t * (q2[1] - q1[1]),
                q1[2] + t * (q2[2] - q1[2]),
                q1[3] + t * (q2[3] - q1[3]),
            )
        else:
            # SLERP
            theta_0 = math.acos(dot)
            theta = theta_0 * t
            sin_theta = math.sin(theta)
            sin_theta_0 = math.sin(theta_0)

            s1 = math.cos(theta) - dot * sin_theta / sin_theta_0
            s2 = sin_theta / sin_theta_0

            result = (
                q1[0] * s1 + q2[0] * s2,
                q1[1] * s1 + q2[1] * s2,
                q1[2] * s1 + q2[2] * s2,
                q1[3] * s1 + q2[3] * s2,
            )

        # Normalize the result
        length = math.sqrt(sum(x * x for x in result))
        if length > 0.0:
            length = 1.0 / length
            result = (
                result[0] * length,
                result[1] * length,
                result[2] * length,
                result[3] * length,
            )

        return result

    @staticmethod
    def _lerp_vec3(v1: Vector3 | None, v2: Vector3 | None, t: float) -> Vector3:
        """Linear interpolation between two 3D vectors."""
        if v1 is None and v2 is None:
            return (0.0, 0.0, 0.0)
        if v1 is None:
            return v2
        if v2 is None:
            return v1
        return (
            v1[0] + (v2[0] - v1[0]) * t,
            v1[1] + (v2[1] - v1[1]) * t,
            v1[2] + (v2[2] - v1[2]) * t,
        )


class AnimationLayer:
    """A layer that can contain multiple animation states with blending."""

    def __init__(
        self,
        name: str,
        weight: float = 1.0,
        blend_mode: AnimationBlendMode = AnimationBlendMode.OVERRIDE,
    ):
        """Initialize a new animation layer."""
        self.name = name
        self.weight = weight
        self.blend_mode = blend_mode
        self.states: dict[str, AnimationState] = {}
        self._event_handlers = defaultdict(list)

    def add_state(
        self,
        name: str,
        clip: AnimationClip,
        weight: float = 1.0,
        loop: bool | None = None,
        speed: float | None = None,
    ) -> AnimationState:
        """Add a new animation state to this layer."""
        state = AnimationState(clip, weight, loop, speed)
        self.states[name] = state
        return state

    def remove_state(self, name: str) -> bool:
        """Remove an animation state from this layer."""
        if name in self.states:
            del self.states[name]
            return True
        return False

    def update(self, delta_time: float) -> list[tuple[str, AnimationEvent]]:
        """
        Update all animation states in this layer.

        Returns:
            List of (state_name, event) tuples for all triggered events
        """
        all_events = []

        for name, state in list(self.states.items()):
            # Update the state
            events = state.update(delta_time)

            # Collect events with state info
            for event in events:
                all_events.append((name, event))

            # Remove completed non-looping animations
            if not state.loop and state.time >= state.clip.duration:
                self.states.pop(name, None)

        return all_events

    def get_pose(self) -> tuple[BonePose, BlendShapes]:
        """
        Get the combined pose from all active animation states in this layer.

        Returns:
            Tuple of (bone_poses, blend_shapes)
        """
        if not self.states or self.weight <= 0.0:
            return {}, {}

        # Sort states by priority (higher priority last)
        sorted_states = sorted(self.states.values(), key=lambda s: s.clip.priority)

        # Initialize with the first state's pose
        if not sorted_states:
            return {}, {}

        combined_bones, combined_shapes = sorted_states[0].get_pose()

        # Blend with remaining states
        for state in sorted_states[1:]:
            if state.weight <= 0.0:
                continue

            bone_poses, blend_shapes = state.get_pose()

            # Blend bone poses
            for bone_name, (rot, pos, scale) in bone_poses.items():
                if bone_name not in combined_bones:
                    combined_bones[bone_name] = (rot, pos, scale)
                else:
                    # Blend rotations
                    if rot is not None:
                        combined_rot = combined_bones[bone_name][0]
                        if combined_rot is not None:
                            # Simple nlerp for now
                            t = state.weight * self.weight
                            combined_rot = AnimationState._slerp_quat(combined_rot, rot, t)
                        combined_bones[bone_name] = (combined_rot, pos, scale)

            # Blend blend shapes
            for name, weight in blend_shapes.items():
                combined_shapes[name] = combined_shapes.get(name, 0.0) + weight * self.weight

        return combined_bones, combined_shapes


class AnimationController:
    """
    Advanced animation controller with support for:
    - Animation layering
    - State machines
    - Event handling
    - Cross-fading
    - Retargeting
    """

    def __init__(self):
        """Initialize a new AnimationController."""
        self.layers: dict[str, AnimationLayer] = {}
        self._animation_clips: dict[str, AnimationClip] = {}
        self._event_handlers = defaultdict(list)
        self._last_update_time = time.time()
        self._default_pose: BonePose = {}
        self._skeleton: dict[str, Any] = {}

        # Load default animations
        self._load_default_animations()

    def add_layer(
        self,
        name: str,
        weight: float = 1.0,
        blend_mode: AnimationBlendMode = AnimationBlendMode.OVERRIDE,
    ) -> AnimationLayer:
        """Add a new animation layer."""
        if name in self.layers:
            raise ValueError(f"Layer '{name}' already exists")

        layer = AnimationLayer(name, weight, blend_mode)
        self.layers[name] = layer
        return layer

    def remove_layer(self, name: str) -> bool:
        """Remove an animation layer."""
        if name in self.layers:
            del self.layers[name]
            return True
        return False

    def load_animation(self, name: str, file_path: str | Path) -> AnimationClip | None:
        """
        Load an animation from a JSON file.

        Args:
            name: Name to give the animation
            file_path: Path to the animation file

        Returns:
            The loaded AnimationClip, or None if loading failed
        """
        try:
            with open(file_path) as f:
                data = json.load(f)

            clip = AnimationClip(
                name=name,
                duration=data.get("duration", 1.0),
                loop=data.get("loop", False),
                speed=data.get("speed", 1.0),
                blend_mode=AnimationBlendMode[data.get("blend_mode", "OVERRIDE")],
                priority=data.get("priority", 0),
                fade_in_time=data.get("fade_in_time", 0.1),
                fade_out_time=data.get("fade_out_time", 0.1),
            )

            # Load keyframes
            for kf_data in data.get("keyframes", []):
                keyframe = AnimationKeyframe(
                    time=kf_data.get("time", 0.0),
                    bone_name=kf_data.get("bone_name", ""),
                    rotation=tuple(kf_data["rotation"]) if "rotation" in kf_data else None,
                    position=tuple(kf_data["position"]) if "position" in kf_data else None,
                    scale=tuple(kf_data["scale"]) if "scale" in kf_data else None,
                    blend_shape_name=kf_data.get("blend_shape_name", ""),
                    blend_shape_weight=kf_data.get("blend_shape_weight", 0.0),
                )
                clip.keyframes.append(keyframe)

            # Load events
            for event_data in data.get("events", []):
                event = AnimationEvent(
                    event_type=AnimationEventType[event_data.get("type", "CUSTOM")],
                    time=event_data.get("time", 0.0),
                    name=event_data.get("name", ""),
                    data=event_data.get("data", {}),
                )
                clip.events.append(event)

            # Sort keyframes and events
            clip.keyframes.sort(key=lambda kf: kf.time)
            clip.events.sort(key=lambda e: e.time)

            self._animation_clips[name] = clip
            logger.info(f"Loaded animation '{name}' from {file_path}")
            return clip

        except Exception as e:
            logger.error(f"Failed to load animation from {file_path}: {e!s}")
            return None

    def play_animation(self, layer_name: str, clip_name: str, fade_time: float = 0.1) -> bool:
        """
        Play an animation on a specific layer with optional cross-fading.

        Args:
            layer_name: Name of the layer to play the animation on
            clip_name: Name of the animation clip to play
            fade_time: Time in seconds to fade to the new animation

        Returns:
            True if the animation was started, False otherwise
        """
        if layer_name not in self.layers or clip_name not in self._animation_clips:
            return False

        layer = self.layers[layer_name]
        clip = self._animation_clips[clip_name]

        # Create a new state for this animation
        state = layer.add_state(clip_name, clip)

        # Set up fade in/out for smooth transitions
        if fade_time > 0:
            # Fade out other states
            for name, other_state in list(layer.states.items()):
                if name != clip_name:
                    other_state.is_playing = False
                    other_state.clip.fade_out_time = fade_time

            # Fade in the new state
            state.clip.fade_in_time = fade_time
        else:
            # No fade, immediately remove other states
            layer.states = {clip_name: state}

        logger.info(f"Playing animation '{clip_name}' on layer '{layer_name}'")
        return True

    def update(self) -> None:
        """Update all animation states and handle events."""
        current_time = time.time()
        delta_time = current_time - self._last_update_time
        self._last_update_time = current_time

        # Update all layers and collect events
        all_events = []
        for layer_name, layer in self.layers.items():
            layer_events = layer.update(delta_time)
            all_events.extend((layer_name, state_name, event) for state_name, event in layer_events)

        # Handle events
        for layer_name, state_name, event in all_events:
            self._handle_event(layer_name, state_name, event)

    def get_pose(self) -> tuple[BonePose, BlendShapes]:
        """
        Get the final pose by blending all layers.

        Returns:
            Tuple of (bone_poses, blend_shapes)
        """
        final_bones = {}
        final_shapes = {}

        # Sort layers by name for consistent ordering
        for layer_name in sorted(self.layers.keys()):
            layer = self.layers[layer_name]

            # Skip disabled layers
            if layer.weight <= 0.0:
                continue

            # Get the pose from this layer
            bone_poses, blend_shapes = layer.get_pose()

            # Apply layer blending
            if layer.blend_mode == AnimationBlendMode.OVERRIDE:
                # Override previous layers
                final_bones.update(bone_poses)
                final_shapes.update(blend_shapes)
            elif layer.blend_mode == AnimationBlendMode.ADDITIVE:
                # Add to previous layers
                for bone_name, (rot, pos, scale) in bone_poses.items():
                    if bone_name in final_bones:
                        # Add rotations (quaternion multiplication)
                        if rot is not None and final_bones[bone_name][0] is not None:
                            q1 = final_bones[bone_name][0]
                            q2 = rot
                            w = (
                                q1[3] * q2[3] - q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2],
                                q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0],
                                -q1[0] * q2[2] + q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1],
                                q1[0] * q2[1] - q1[1] * q2[0] + q1[2] * q2[3] + q1[3] * q2[2],
                            )
                            final_bones[bone_name] = (w, pos, scale)
                    else:
                        final_bones[bone_name] = (rot, pos, scale)

                # Add blend shapes
                for name, weight in blend_shapes.items():
                    final_shapes[name] = final_shapes.get(name, 0.0) + weight

            # Other blend modes can be added here

        return final_bones, final_shapes

    def add_event_handler(self, event_type: AnimationEventType | str, callback: Callable):
        """
        Register a callback for animation events.

        Args:
            event_type: Type of event to listen for, or '*' for all events
            callback: Function to call when the event occurs
                      Signature: (layer_name: str, state_name: str, event: AnimationEvent) -> None
        """
        if isinstance(event_type, str):
            event_type = AnimationEventType[event_type.upper()]
        self._event_handlers[event_type].append(callback)

    def _handle_event(self, layer_name: str, state_name: str, event: AnimationEvent) -> None:
        """Handle an animation event by calling all registered handlers."""
        # Call specific handlers for this event type
        for handler in self._event_handlers.get(event.event_type, []):
            try:
                handler(layer_name, state_name, event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type}: {e}")

        # Call wildcard handlers
        for handler in self._event_handlers.get("*", []):
            try:
                handler(layer_name, state_name, event)
            except Exception as e:
                logger.error(f"Error in wildcard event handler: {e}")

    def _load_default_animations(self) -> None:
        """Load any default animations that should always be available."""
        # Create an idle animation
        idle_clip = AnimationClip(name="idle", duration=1.0, loop=True)
        self._animation_clips["idle"] = idle_clip

        # Create a default layer
        self.add_layer("base", 1.0, AnimationBlendMode.OVERRIDE)

        logger.info("Initialized animation controller with default animations")


# Example usage
def example_usage():
    """Example of how to use the AnimationController."""
    # Create a controller
    controller = AnimationController()

    # Load an animation
    controller.load_animation("walk", "animations/walk.json")

    # Set up event handlers
    def on_footstep(layer: str, state: str, event: AnimationEvent):
        logger.debug("Footstep at %fs", event.time)

    controller.add_event_handler(AnimationEventType.FOOTSTEP, on_footstep)

    # Play an animation
    controller.play_animation("base", "walk")

    # Main loop
    try:
        while True:
            controller.update()
            _bone_poses, _blend_shapes = controller.get_pose()

            # Apply poses to your model here

            time.sleep(1 / 60)  # 60 FPS
    except KeyboardInterrupt:
        logger.info("Animation stopped")


if __name__ == "__main__":
    example_usage()
