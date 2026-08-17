"""
AvatarMCP Server

FastMCP 2.10+ compliant server implementation for managing VRM avatars.
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Any, TypedDict

import fastmcp
from fastmcp.tools import tool as mcp_tool

# Import animation system
from ..core.animation import AnimationClip, AnimationKeyframe

# Import help system
from ..core.help_system import help_system

# Import MCP help system
from ..core.mcp_help import register_help_command

# Import VRM loader
from ..models.vrm_loader import VRMLoader

# Import standard animations
from . import standard_animations

# Initialize FastMCP at module level
mcp = fastmcp.FastMCP(
    name="avatarmcp",
    version="0.1.0",
    instructions="MCP server for VRM avatar management and animation",
)


class AnimationInfo(TypedDict):
    name: str
    duration: float
    loop: bool
    model_id: str


# Global state
_active_animations: dict[str, AnimationInfo] = {}


def play_standard_animation(
    model_id: str, animation_name: str, loop: bool = False, weight: float = 1.0, speed: float = 1.0
) -> dict[str, Any]:
    """Play a standard animation on a model."""
    try:
        # TODO: Implement actual standard animation logic
        logger.info(f"Playing standard animation '{animation_name}' on model {model_id}")
        return {
            "success": True,
            "message": f"Playing standard animation '{animation_name}'",
            "model_id": model_id,
            "animation_name": animation_name,
            "loop": loop,
            "weight": weight,
            "speed": speed,
        }
    except Exception as e:
        logger.error(f"Failed to play standard animation: {e!s}")
        return {
            "success": False,
            "message": f"Failed to play standard animation: {e!s}",
            "error": str(e),
        }


try:
    # Try importing any optional dependencies here
    pass
except ImportError:
    # Use stderr directly for critical import errors before logging is set up
    sys.stderr.write("ERROR: FastMCP 2.10+ is required. Please install with: pip install 'fastmcp>=2.10.0,<3.0.0'\n")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("avatarmcp")


# Type definitions
class ModelInfo(TypedDict):
    model_id: str
    name: str
    version: str
    bones: list[dict[str, Any]]
    materials: list[dict[str, Any]]


def main():
    """
    Entry point for the AvatarMCP server.
    Uses stdio communication as required by FastMCP 2.10+
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Register the help command first
    register_help_command(mcp)

    # Start the server
    import asyncio

    asyncio.run(mcp.run_stdio_async(show_banner=False))

    return 0


# In-memory storage for loaded models and animations
_models: dict[str, Any] = {}  # model_id -> VRM model data
_animations: dict[str, dict[str, Any]] = {}  # model_id -> {animation_name -> animation_data}
_blend_shapes: dict[str, dict[str, float]] = {}  # model_id -> {blend_shape_name -> weight}
_bone_transforms: dict[str, dict[str, dict[str, Any]]] = {}  # model_id -> {bone_name -> transform}
_animation_controllers: dict[str, Any] = {}  # model_id -> AnimationController


# Register commands
@mcp.tool(name="load_vrm")
@help_system.register(
    name="load_vrm",
    description="Load a VRM model into memory for animation and manipulation.",
    examples=["load_vrm('path/to/model.vrm')", "load_vrm(file_path='C:/models/character.vrm')"],
)
def cmd_load_vrm(file_path: str) -> dict[str, Any]:
    """Load a VRM model.

    Args:
        file_path: Path to the VRM file to load. Must be a valid .vrm file.
                  Can be either an absolute path or relative to the current working directory.

    Returns:
        Dict containing:
        - status: 'success' or 'error'
        - model_id: Unique identifier for the loaded model
        - metadata: Model metadata including name, version, and other VRM-specific data
        - error: Error message if status is 'error'
    """
    return load_vrm(file_path)


@mcp.tool(name="unload_vrm")
@help_system.register(
    name="unload_vrm",
    description="Unload a VRM model from memory to free up resources.",
    examples=["unload_vrm('model_1')", "unload_vrm(model_id='character_01')"],
)
def cmd_unload_vrm(model_id: str) -> dict[str, Any]:
    """Unload a VRM model.

    Args:
        model_id: ID of the model to unload. Must be a valid model ID returned by load_vrm().

    Returns:
        Dict containing:
        - status: 'success' or 'error'
        - model_id: ID of the unloaded model
        - error: Error message if status is 'error'
    """
    return unload_vrm(model_id)


@mcp.tool(name="play_animation")
@help_system.register(
    name="play_animation",
    description="Play an animation on a loaded VRM model.",
    examples=[
        "play_animation('model_1', 'idle')",
        "play_animation(model_id='char1', animation_name='wave', loop=True, weight=0.8, speed=1.2)",
    ],
)
def cmd_play_animation(
    model_id: str, animation_name: str, loop: bool = False, weight: float = 1.0, speed: float = 1.0
) -> dict[str, Any]:
    """Play an animation on a model.

    Args:
        model_id: ID of the model to animate. Must be a loaded model ID.
        animation_name: Name of the animation to play. Can be a VRM animation,
                      standard animation, or custom animation name.
        loop: If True, the animation will loop continuously.
        weight: Blend weight (0.0 to 1.0). Controls the influence of this animation.
        speed: Playback speed multiplier. 1.0 is normal speed, 2.0 is double speed, etc.

    Returns:
        Dict containing:
        - status: 'success' or 'error'
        - model_id: ID of the model
        - animation: Name of the animation
        - duration: Duration of the animation in seconds (if available)
        - loop: Whether the animation is set to loop
        - weight: Blend weight
        - speed: Playback speed
        - error: Error message if status is 'error'
    """
    return play_animation(model_id, animation_name, loop, weight, speed)


@mcp.tool(name="stop_animation")
@help_system.register(
    name="stop_animation",
    description="Stop a currently playing animation on a VRM model.",
    examples=[
        "stop_animation('model_1', 'walk')",
        "stop_animation(model_id='char1', animation_name='wave', fade_out=0.5)",
    ],
)
def cmd_stop_animation(model_id: str, animation_name: str, fade_out: float = 0.0) -> dict[str, Any]:
    """Stop a playing animation.

    Args:
        model_id: ID of the model with the animation to stop.
        animation_name: Name of the animation to stop. Must match the name used to start it.
        fade_out: Optional fade out duration in seconds. If > 0, the animation will
                smoothly transition out over this duration.

    Returns:
        Dict containing:
        - status: 'success' or 'error'
        - model_id: ID of the model
        - animation: Name of the stopped animation
        - fade_out: Fade out duration used
        - error: Error message if status is 'error'
    """
    return stop_animation(model_id, animation_name, fade_out)


@mcp.tool(name="set_blend_shape")
@help_system.register(
    name="set_blend_shape",
    description="Set the weight of a blend shape on a VRM model.",
    examples=[
        "set_blend_shape('model_1', 'blink', 1.0)",
        "set_blend_shape(model_id='char1', blend_shape_name='smile', weight=0.5)",
    ],
)
def cmd_set_blend_shape(model_id: str, blend_shape_name: str, weight: float) -> dict[str, Any]:
    """Set blend shape weight.

    Args:
        model_id: ID of the model containing the blend shape.
        blend_shape_name: Name of the blend shape to modify. Use list_blend_shapes()
                        to get available blend shape names for a model.
        weight: Blend weight (0.0 to 1.0). 0.0 means the blend shape has no effect,
               1.0 means full effect.

    Returns:
        Dict containing:
        - status: 'success' or 'error'
        - model_id: ID of the model
        - blend_shape: Name of the modified blend shape
        - weight: The new weight value
        - error: Error message if status is 'error'
    """
    return set_blend_shape(model_id, blend_shape_name, weight)


@mcp.tool(name="set_bone_transform")
@help_system.register(
    name="set_bone_transform",
    description="Set the transform (position/rotation/scale) of a bone in a VRM model.",
    examples=[
        "set_bone_transform('model_1', 'Head', rotation=(0, 0.7, 0, 0.7))  # 90 degree Y rotation",
        "set_bone_transform(model_id='char1', bone_name='Arm_L', position=(0.1, 0, 0))",
    ],
)
def cmd_set_bone_transform(
    model_id: str,
    bone_name: str,
    position: tuple[float, float, float] | None = None,
    rotation: tuple[float, float, float, float] | None = None,
    scale: tuple[float, float, float] | None = None,
) -> dict[str, Any]:
    """Set bone transform directly.

    Args:
        model_id: ID of the model containing the bone.
        bone_name: Name of the bone to transform. Use list_bones() to get available bone names.
        position: Optional (x, y, z) position in model space. At least one of position,
                rotation, or scale must be provided.
        rotation: Optional (x, y, z, w) quaternion rotation in model space.
        scale: Optional (x, y, z) scale factors.

    Returns:
        Dict containing:
        - status: 'success' or 'error'
        - model_id: ID of the model
        - bone: Name of the transformed bone
        - transform: The new transform values that were set
        - error: Error message if status is 'error'
    """
    return set_bone_transform(model_id, bone_name, position, rotation, scale)


@mcp.tool(name="list_animations")
@help_system.register(
    name="list_animations",
    description="List all available animations for a loaded VRM model.",
    examples=["list_animations('model_1')", "animations = list_animations(model_id='char1')"],
)
def cmd_list_animations(model_id: str) -> dict[str, Any]:
    """List available animations for a model.

    Args:
        model_id: ID of the model to query. Must be a loaded model ID.

    Returns:
        Dict containing:
        - status: 'success' or 'error'
        - model_id: ID of the model
        - animations: List of animation names and metadata
        - counts: Dictionary with counts of different animation types
        - error: Error message if status is 'error'
    """
    return list_animations(model_id)


@mcp.tool(name="list_blend_shapes")
def cmd_list_blend_shapes(model_id: str) -> dict[str, Any]:
    """List available blend shapes for a model.

    Args:
        model_id: ID of the model

    Returns:
        Dict with list of blend shapes
    """
    return list_blend_shapes(model_id)


@mcp.tool(name="list_bones")
def cmd_list_bones(model_id: str) -> dict[str, Any]:
    """List all bones in the model.

    Args:
        model_id: ID of the model

    Returns:
        Dict with list of bones
    """
    return list_bones(model_id)


@mcp.tool(name="list_models")
def cmd_list_models() -> dict[str, Any]:
    """List all loaded models.

    Returns:
        Dict with status and list of models
    """
    return list_models()


def get_model(model_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Get model and its animation controller.

    Args:
        model_id: ID of the model

    Returns:
        Tuple of (model_data, animation_controller)

    Raises:
        ValueError: If model is not found
    """
    if model_id not in _models:
        raise ValueError(f"Model {model_id} not found")
    return _models[model_id], _animation_controllers.get(model_id)


def create_error_response(error: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a standardized error response.

    Args:
        error: Human-readable error message
        details: Optional additional error details

    Returns:
        Dict containing error information
    """
    return {"status": "error", "error": error, "details": details or {}}


@mcp_tool()
def load_vrm(file_path: str) -> dict[str, Any]:
    """Load a VRM model from file.

    Args:
        file_path: Path to the VRM file

    Returns:
        Dict with status and model information
    """
    try:
        # Resolve the full file path
        path = Path(file_path).resolve()

        # Validate file exists and is a VRM file
        if not path.exists():
            return create_error_response("File not found", {"file_path": str(path)})

        if path.suffix.lower() != ".vrm":
            return create_error_response("Invalid file type. Expected .vrm file")

        # Generate a unique model ID
        model_id = f"model_{len(_models) + 1}"

        # Load the VRM model using VRMLoader
        vrm_model = VRMLoader.from_file(str(path))

        # Store the real VRM data
        _models[model_id] = {
            "vrm_model": vrm_model,
            "meshes": vrm_model.meshes,
            "materials": vrm_model.materials,
            "bones": vrm_model.bones,
            "blend_shapes": vrm_model.blend_shapes,
            "metadata": vrm_model.metadata,
        }

        # Initialize animation data
        _animations[model_id] = {}
        _blend_shapes[model_id] = {bs.name: bs.weight for bs in vrm_model.blend_shapes}
        _bone_transforms[model_id] = {}

        # Initialize animation controller with real bone data
        from ..core.animation import AnimationController

        _animation_controllers[model_id] = AnimationController()

        # Get bone and blend shape names for the response
        bone_names = list(vrm_model.bones.keys()) if hasattr(vrm_model, "bones") else []
        blend_shape_names = [bs.name for bs in vrm_model.blend_shapes] if hasattr(vrm_model, "blend_shapes") else []

        return {
            "status": "success",
            "model_id": model_id,
            "metadata": {
                "name": getattr(vrm_model.metadata, "name", path.stem),
                "num_meshes": len(vrm_model.meshes) if hasattr(vrm_model, "meshes") else 0,
                "num_bones": len(bone_names),
                "num_blend_shapes": len(blend_shape_names),
                "num_materials": len(vrm_model.materials) if hasattr(vrm_model, "materials") else 0,
                "bones": bone_names,
                "blend_shapes": blend_shape_names,
            },
        }

    except Exception as e:
        error_id = f"err_{len(_models) + 1}"
        logger.error(f"[{error_id}] Failed to load VRM: {e!s}\n{traceback.format_exc()}")
        return create_error_response("Failed to load VRM model", {"error_id": error_id, "error": str(e)})


@mcp_tool()
def unload_vrm(model_id: str) -> dict[str, Any]:
    """Unload a VRM model.

    Args:
        model_id: ID of the model to unload

    Returns:
        Dict with status information
    """
    try:
        if model_id not in _models:
            return create_error_response(f"Model {model_id} not found")

        # Clean up resources
        del _models[model_id]
        _animations.pop(model_id, None)
        _blend_shapes.pop(model_id, None)
        _bone_transforms.pop(model_id, None)
        _animation_controllers.pop(model_id, None)

        return {"status": "success", "model_id": model_id}

    except Exception as e:
        logger.error(f"Failed to unload VRM: {e!s}", exc_info=True)
        return create_error_response("Failed to unload VRM", {"error": str(e)})


def play_animation(
    model_id: str, animation_name: str, loop: bool = False, weight: float = 1.0, speed: float = 1.0
) -> dict[str, Any]:
    """Play an animation on a model.

    Args:
        model_id: ID of the model
        animation_name: Name of the animation to play
        loop: Whether to loop the animation
        weight: Blend weight (0.0 to 1.0)
        speed: Playback speed multiplier

    Returns:
        Dict with status information
    """
    try:
        model, controller = get_model(model_id)

        # Check if this is a standard animation
        if animation_name in standard_animations.list_standard_animations():
            return play_standard_animation(model_id, animation_name, loop, weight, speed)

        # Check if VRM model has animations
        if not hasattr(model["vrm_model"], "animations"):
            return create_error_response("VRM model has no animations")

        # Find the animation in the VRM model
        animation = next((a for a in model["vrm_model"].animations if a.name == animation_name), None)

        if not animation:
            return create_error_response(f"Animation '{animation_name}' not found in VRM model")

        # Create an animation clip from the VRM animation
        clip = AnimationClip(name=animation_name, duration=animation.duration, loop=loop)

        # Convert VRM animation to our keyframe format
        for channel in animation.channels:
            for keyframe in channel.keyframes:
                kf = AnimationKeyframe(time=keyframe.time, bone_name=channel.target_bone)

                # Set transform based on channel type
                if channel.path == "rotation":
                    kf.rotation = keyframe.rotation
                elif channel.path == "position":
                    kf.position = keyframe.position
                elif channel.path == "scale":
                    kf.scale = keyframe.scale

                clip.keyframes.append(kf)

        # Add to controller if not already present
        if animation_name not in controller.animations:
            controller.animations[animation_name] = clip

        # Play the animation
        controller.play_animation(name=animation_name, weight=weight, loop=loop, speed=speed)

        # Update the VRM model's animation state
        if hasattr(model["vrm_model"], "start_animation"):
            model["vrm_model"].start_animation(animation_name, loop=loop, speed=speed)

        return {
            "status": "success",
            "model_id": model_id,
            "animation": animation_name,
            "duration": animation.duration,
            "loop": loop,
            "weight": weight,
            "speed": speed,
        }

    except Exception as e:
        logger.error(f"Failed to play animation: {e!s}", exc_info=True)
        return create_error_response("Failed to play animation", {"error": str(e)})
    """
    Play an animation on the specified model.

    Args:
        model_id: ID of the loaded model
        animation_name: Name of the animation to play
        loop: Whether to loop the animation (default: False)

    Returns:
        Dict containing status information

    Example:
        >>> play_animation("model_123", "wave", loop=True)
        {
            "status": "success",
            "animation": "wave",
            "model_id": "model_123",
            "loop": true,
            "duration": 2.5
        }
    """
    try:
        # Verify model exists
        if model_id not in _models:
            return create_error_response("Model not found", {"model_id": model_id})

        # TODO: Implement actual animation logic
        # For now, just log and return success
        animation_id = f"anim_{len(_active_animations) + 1}"
        animation_info: AnimationInfo = {
            "name": animation_name,
            "duration": 0.0,  # Will be populated with actual duration
            "loop": loop,
            "model_id": model_id,
        }

        _active_animations[animation_id] = animation_info

        logger.info(f"Playing animation '{animation_name}' on model {model_id} (loop: {loop})")

        return {
            "status": "success",
            "animation": animation_name,
            "model_id": model_id,
            "loop": loop,
            "duration": animation_info["duration"],
        }

    except Exception as e:
        error_id = f"anim_err_{len(_active_animations) + 1}"
        logger.error(f"[{error_id}] Failed to play animation: {e!s}\n{traceback.format_exc()}")
        return create_error_response("Failed to play animation", {"error_id": error_id, "error": str(e)})


@mcp_tool()
def stop_animation(model_id: str, animation_name: str, fade_out: float = 0.0) -> dict[str, Any]:
    """Stop a playing animation.

    Args:
        model_id: ID of the model
        animation_name: Name of the animation to stop
        fade_out: Fade out duration in seconds

    Returns:
        Dict with status information
    """
    try:
        model, controller = get_model(model_id)

        # Stop the animation in the controller
        controller.stop_animation(animation_name, fade_out=fade_out)

        # Update the VRM model's animation state
        if hasattr(model["vrm_model"], "stop_animation"):
            model["vrm_model"].stop_animation(animation_name, fade_out=fade_out)

        return {
            "status": "success",
            "model_id": model_id,
            "animation": animation_name,
            "fade_out": fade_out,
        }

    except Exception as e:
        logger.error(f"Failed to stop animation: {e!s}", exc_info=True)
        return create_error_response("Failed to stop animation", {"error": str(e)})


def set_blend_shape(model_id: str, blend_shape_name: str, weight: float) -> dict[str, Any]:
    """Set blend shape weight.

    Args:
        model_id: ID of the model
        blend_shape_name: Name of the blend shape
        weight: Blend weight (0.0 to 1.0)

    Returns:
        Dict with status information and updated blend shape data
    """
    try:
        model, _ = get_model(model_id)

        # Validate the model has blend shape data
        if "vrm_model" not in model or not hasattr(model["vrm_model"], "blend_shapes"):
            return create_error_response("Model has no blend shape data")

        # Find the blend shape
        blend_shape = next((bs for bs in model["vrm_model"].blend_shapes if bs.name == blend_shape_name), None)

        if not blend_shape:
            return create_error_response(f"Blend shape '{blend_shape_name}' not found in model")

        # Clamp weight between 0.0 and 1.0
        weight = max(0.0, min(1.0, weight))

        # Update the weight in our tracking dictionary
        if model_id not in _blend_shapes:
            _blend_shapes[model_id] = {}
        _blend_shapes[model_id][blend_shape_name] = weight

        # Apply the blend shape to the model if it has a method to do so
        if hasattr(model["vrm_model"], "set_blend_shape_weight"):
            try:
                model["vrm_model"].set_blend_shape_weight(blend_shape_name, weight)
            except Exception as e:
                logger.warning(f"Could not update blend shape on model: {e!s}")

        # Get updated blend shape details for the response
        updated_blend_shape = {
            "name": blend_shape_name,
            "preset": getattr(blend_shape, "preset_name", "Custom"),
            "weight": weight,
            "material_affected": len(blend_shape.material_values) if hasattr(blend_shape, "material_values") else 0,
        }

        return {
            "status": "success",
            "model_id": model_id,
            "blend_shape": blend_shape_name,
            "weight": weight,
            "updated_blend_shape": updated_blend_shape,
        }

    except Exception as e:
        logger.error(f"Failed to set blend shape: {e!s}", exc_info=True)
        return create_error_response("Failed to set blend shape", {"error": str(e)})


def set_bone_transform(
    model_id: str,
    bone_name: str,
    position: tuple[float, float, float] | None = None,
    rotation: tuple[float, float, float, float] | None = None,
    scale: tuple[float, float, float] | None = None,
) -> dict[str, Any]:
    """Set bone transform directly.

    This updates the bone's transform in the VRM model and tracks the override.

    Args:
        model_id: ID of the model
        bone_name: Name of the bone to transform
        position: Optional (x, y, z) position in meters
        rotation: Optional (x, y, z, w) quaternion rotation
        scale: Optional (x, y, z) scale

    Returns:
        Dict with status information and updated transform
    """
    try:
        model, _ = get_model(model_id)

        # Validate the model has bone data
        if "vrm_model" not in model or not hasattr(model["vrm_model"], "bones"):
            return create_error_response("Model has no bone data")

        # Find the bone
        if bone_name not in model["vrm_model"].bones:
            return create_error_response(f"Bone '{bone_name}' not found in model")

        # Initialize bone transforms dict if needed
        if model_id not in _bone_transforms:
            _bone_transforms[model_id] = {}
        if bone_name not in _bone_transforms[model_id]:
            _bone_transforms[model_id][bone_name] = {}

        # Update the transform components
        transform_updates = {}

        if position is not None:
            if len(position) != 3:
                return create_error_response("Position must be a tuple of 3 floats (x, y, z)")
            transform_updates["position"] = tuple(float(x) for x in position)

        if rotation is not None:
            if len(rotation) != 4:
                return create_error_response("Rotation must be a tuple of 4 floats (x, y, z, w)")
            transform_updates["rotation"] = tuple(float(x) for x in rotation)

        if scale is not None:
            if len(scale) != 3:
                return create_error_response("Scale must be a tuple of 3 floats (x, y, z)")
            transform_updates["scale"] = tuple(float(x) for x in scale)

        # Update the bone in the VRM model if it has a method to do so
        if hasattr(model["vrm_model"], "set_bone_transform"):
            try:
                model["vrm_model"].set_bone_transform(
                    bone_name,
                    position=transform_updates.get("position"),
                    rotation=transform_updates.get("rotation"),
                    scale=transform_updates.get("scale"),
                )
            except Exception as e:
                logger.warning(f"Could not update bone transform on model: {e!s}")

        # Update our tracking dictionary
        _bone_transforms[model_id][bone_name].update(transform_updates)

        # Get the current transform state for the response
        current_transform = {
            "position": _bone_transforms[model_id][bone_name].get("position", [0, 0, 0]),
            "rotation": _bone_transforms[model_id][bone_name].get("rotation", [0, 0, 0, 1]),
            "scale": _bone_transforms[model_id][bone_name].get("scale", [1, 1, 1]),
        }

        return {
            "status": "success",
            "model_id": model_id,
            "bone": bone_name,
            "transform": current_transform,
            "transform_updated": transform_updates,
        }

    except Exception as e:
        logger.error(f"Failed to set bone transform: {e!s}", exc_info=True)
        return create_error_response("Failed to set bone transform", {"error": str(e)})


def list_animations(model_id: str) -> dict[str, Any]:
    """List available animations for a model.

    Args:
        model_id: ID of the model

    Returns:
        Dict with list of animations and their details
    """
    try:
        model, _ = get_model(model_id)

        # Get standard animations
        standard_anims = [{"name": name, "type": "standard"} for name in standard_animations.list_standard_animations()]

        # Get VRM animations if available
        vrm_anims = []
        if hasattr(model["vrm_model"], "animations"):
            vrm_anims = [
                {
                    "name": anim.name,
                    "type": "vrm",
                    "duration": getattr(anim, "duration", 0.0),
                    "num_channels": len(getattr(anim, "channels", [])),
                    "num_keyframes": sum(len(ch.keyframes) for ch in getattr(anim, "channels", [])),
                }
                for anim in model["vrm_model"].animations
            ]

        # Get custom animations
        custom_anims = []
        if model_id in _animations:
            custom_anims = [
                {
                    "name": name,
                    "type": "custom",
                    "duration": anim.duration,
                    "num_keyframes": len(anim.keyframes),
                }
                for name, anim in _animations[model_id].items()
            ]

        # Combine all animations
        all_animations = standard_anims + vrm_anims + custom_anims

        return {
            "status": "success",
            "model_id": model_id,
            "animations": all_animations,
            "counts": {
                "standard": len(standard_anims),
                "vrm": len(vrm_anims),
                "custom": len(custom_anims),
                "total": len(all_animations),
            },
        }

    except Exception as e:
        logger.error(f"Failed to list animations: {e!s}", exc_info=True)
        return create_error_response("Failed to list animations", {"error": str(e)})


def list_blend_shapes(model_id: str) -> dict[str, Any]:
    """List available blend shapes for a model.

    Args:
        model_id: ID of the model

    Returns:
        Dict with list of blend shapes, their current weights, and presets
    """
    try:
        model, _ = get_model(model_id)

        if "vrm_model" not in model or not hasattr(model["vrm_model"], "blend_shapes"):
            return create_error_response("Model has no blend shape data")

        # Get detailed blend shape information
        blend_shapes = []
        for bs in model["vrm_model"].blend_shapes:
            blend_shape_info = {
                "name": bs.name,
                "preset": getattr(bs, "preset_name", "Unknown"),
                "current_weight": _blend_shapes.get(model_id, {}).get(bs.name, 0.0),
                "material_values": [
                    {
                        "material_name": val.material_name,
                        "property_name": val.property_name,
                        "target_value": val.target_value,
                    }
                    for val in bs.material_values
                ]
                if hasattr(bs, "material_values")
                else [],
            }
            blend_shapes.append(blend_shape_info)

        return {
            "status": "success",
            "model_id": model_id,
            "blend_shapes": {
                bs.name: _blend_shapes.get(model_id, {}).get(bs.name, 0.0) for bs in model["vrm_model"].blend_shapes
            },
            "blend_shape_details": blend_shapes,
        }

    except Exception as e:
        logger.error(f"Failed to list blend shapes: {e!s}", exc_info=True)
        return create_error_response("Failed to list blend shapes", {"error": str(e)})


def list_bones(model_id: str) -> dict[str, Any]:
    """List all bones in the model.

    Args:
        model_id: ID of the model

    Returns:
        Dict with list of bones and their hierarchy
    """
    try:
        model, _ = get_model(model_id)

        if "vrm_model" not in model or not hasattr(model["vrm_model"], "bones"):
            return create_error_response("Model has no bone data")

        # Get bone hierarchy information
        bones = []
        for bone_name, bone_data in model["vrm_model"].bones.items():
            bone_info = {
                "name": bone_name,
                "parent": bone_data.parent_name if hasattr(bone_data, "parent_name") else None,
                "position": getattr(bone_data, "position", [0, 0, 0]),
                "rotation": getattr(bone_data, "rotation", [0, 0, 0, 1]),
                "children": [],
            }
            bones.append(bone_info)

        # Build hierarchy
        bone_map = {bone["name"]: bone for bone in bones}
        root_bones = []

        for bone in bones:
            if bone["parent"] and bone["parent"] in bone_map:
                bone_map[bone["parent"]]["children"].append(bone["name"])
            else:
                root_bones.append(bone["name"])

        return {
            "status": "success",
            "model_id": model_id,
            "bones": list(model["vrm_model"].bones.keys()),
            "root_bones": root_bones,
            "bone_hierarchy": {bone: bone_map[bone]["children"] for bone in bone_map},
        }

    except Exception as e:
        logger.error(f"Failed to list bones: {e!s}", exc_info=True)
        return create_error_response("Failed to list bones", {"error": str(e)})


@mcp.tool(name="list_standard_animations")
def cmd_list_standard_animations() -> dict[str, Any]:
    """List all available standard animations.

    Returns:
        Dict with status and list of animation names
    """
    try:
        animations = standard_animations.list_standard_animations()
        return {"status": "success", "animations": animations}
    except Exception as e:
        logger.error(f"Failed to list standard animations: {e!s}", exc_info=True)
        return create_error_response("Failed to list standard animations", {"error": str(e)})


@mcp.tool(name="play_standard_animation")
def cmd_play_standard_animation(
    model_id: str,
    animation_name: str,
    loop: bool = False,
    weight: float = 1.0,
    speed: float = 1.0,
    fade_in: float | None = None,
) -> dict[str, Any]:
    """Play a standard animation on a model.

    Args:
        model_id: ID of the model
        animation_name: Name of the standard animation to play
        loop: Whether to loop the animation
        weight: Blend weight (0.0 to 1.0)
        speed: Playback speed multiplier
        fade_in: Optional fade in duration in seconds

    Returns:
        Dict with status information
    """
    try:
        # Get the standard animation
        anim_data = standard_animations.get_standard_animation(animation_name)
        if not anim_data:
            return create_error_response(f"Standard animation '{animation_name}' not found")

        # Get the model and animation controller
        model, controller = get_model(model_id)
        if not controller:
            return create_error_response("Animation controller not initialized")

        # Add the animation to the controller if not already present
        if animation_name not in controller.animations:
            from ..core.animation import AnimationClip, AnimationKeyframe

            # Create animation clip
            clip = AnimationClip(
                name=animation_name,
                duration=anim_data["duration"],
                loop=anim_data.get("loop", False),
            )

            # Add keyframes
            for kf_data in anim_data.get("keyframes", []):
                keyframe = AnimationKeyframe(time=kf_data.get("time", 0.0), bone_name=kf_data.get("bone_name", ""))

                if "rotation" in kf_data:
                    keyframe.rotation = tuple(kf_data["rotation"])
                if "position" in kf_data:
                    keyframe.position = tuple(kf_data["position"])
                if "scale" in kf_data:
                    keyframe.scale = tuple(kf_data["scale"])
                if "blend_shape_name" in kf_data:
                    keyframe.blend_shape_name = kf_data["blend_shape_name"]
                    keyframe.blend_shape_weight = kf_data.get("blend_shape_weight", 1.0)

                clip.keyframes.append(keyframe)

            # Add to controller
            controller.animations[animation_name] = clip

        # Play the animation
        controller.play_animation(name=animation_name, weight=weight, loop=loop, speed=speed, fade_in=fade_in)

        return {
            "status": "success",
            "model_id": model_id,
            "animation": animation_name,
            "loop": loop,
            "weight": weight,
            "speed": speed,
        }

    except Exception as e:
        logger.error(f"Failed to play standard animation: {e!s}", exc_info=True)
        return create_error_response("Failed to play standard animation", {"error": str(e)})


@mcp.tool(name="stop_standard_animation")
def cmd_stop_standard_animation(model_id: str, animation_name: str, fade_out: float | None = None) -> dict[str, Any]:
    """Stop a standard animation.

    Args:
        model_id: ID of the model
        animation_name: Name of the animation to stop
        fade_out: Optional fade out duration in seconds

    Returns:
        Dict with status information
    """
    try:
        _, controller = get_model(model_id)
        if not controller:
            return create_error_response("Animation controller not initialized")

        controller.stop_animation(animation_name, fade_out=fade_out)

        return {
            "status": "success",
            "model_id": model_id,
            "animation": animation_name,
            "fade_out": fade_out,
        }

    except Exception as e:
        logger.error(f"Failed to stop standard animation: {e!s}", exc_info=True)
        return create_error_response("Failed to stop standard animation", {"error": str(e)})


def list_models() -> dict[str, Any]:
    """
    List all loaded VRM models.

    Returns:
        Dict containing status and list of loaded models
    """
    try:
        return {"status": "success", "models": list(_models.values())}
    except Exception as e:
        logger.exception("Failed to list models")
        return create_error_response("Failed to list models", {"error": str(e)})


if __name__ == "__main__":
    sys.exit(main())
