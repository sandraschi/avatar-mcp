"""
AvatarMCP Server

FastMCP 2.10.1+ compliant server implementation for AvatarMCP with structured logging,
error handling, and VRM model management.
"""
import json
import logging
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypedDict

# Import FastMCP 2.10.1+
try:
    import fastmcp
except ImportError as e:
    print("ERROR: FastMCP 2.10.1+ is required. Please install with: pip install 'fastmcp>=2.10.1,<3.0.0'",
          file=sys.stderr)
    sys.exit(1)

# Configure structured logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)],
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("avatarmcp")

# Type definitions for better code completion and documentation
class ModelInfo(TypedDict):
    model_id: str
    name: str
    version: str
    bones: List[Dict[str, Any]]
    materials: List[Dict[str, Any]]

class AnimationInfo(TypedDict):
    name: str
    duration: float
    loop: bool
    model_id: str

# Initialize FastMCP 2.10.1+
mcp = fastmcp.mcp(
    name="avatarmcp",
    version="0.1.0",
    description="MCP server for managing and animating VRM avatars with stdio communication"
)

# In-memory storage for loaded models and animations
_models: Dict[str, ModelInfo] = {}
_active_animations: Dict[str, AnimationInfo] = {}

# Register commands
@mcp.command("load_vrm")
def cmd_load_vrm(file_path: str) -> Dict[str, Any]:
    """Load a VRM model.
    
    Args:
        file_path: Path to the VRM file
        
    Returns:
        Dict with status and model information
    """
    return load_vrm(file_path)

@mcp.command("play_animation")
def cmd_play_animation(model_id: str, animation_name: str, loop: bool = False) -> Dict[str, Any]:
    """Play an animation on a model.
    
    Args:
        model_id: ID of the model
        animation_name: Name of the animation to play
        loop: Whether to loop the animation
        
    Returns:
        Dict with status information
    """
    return play_animation(model_id, animation_name, loop)

@mcp.command("list_models")
def cmd_list_models() -> Dict[str, Any]:
    """List all loaded models.
    
    Returns:
        Dict with status and list of models
    """
    return list_models()

def create_error_response(error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized error response.

    Args:
        error: Human-readable error message
        details: Optional additional error details

    Returns:
        Dict containing error information
    """
    return {
        "status": "error",
        "error": error,
        "details": details or {}
    }

@mcp.tool()
def load_vrm(file_path: str) -> Dict[str, Any]:
    """
    Load a VRM model from the specified file path.

    Args:
        file_path: Path to the .vrm file

    Returns:
        Dict containing status and model information

    Example:
        >>> load_vrm("path/to/model.vrm")
        {
            "status": "success",
            "model_id": "model_123",
            "metadata": {...}
        }
    """
    try:
        path = Path(file_path).resolve()

        # Validate file exists and is a VRM file
        if not path.exists():
            return create_error_response("File not found", {"file_path": str(path)})

        if path.suffix.lower() != '.vrm':
            return create_error_response("Invalid file type. Expected .vrm file")

        # Generate a unique model ID
        model_id = f"model_{len(_models) + 1}"

        # TODO: Replace with actual VRM loading logic
        # For now, create a mock model
        model_info: ModelInfo = {
            "model_id": model_id,
            "name": path.stem,
            "version": "1.0",
            "bones": [],  # Will be populated with actual VRM bone data
            "materials": []  # Will be populated with actual VRM material data
        }

        # Store the model
        _models[model_id] = model_info

        logger.info(f"Successfully loaded VRM model: {model_id}")

        return {
            "status": "success",
            "model_id": model_id,
            "metadata": model_info
        }

    except Exception as e:
        error_id = f"err_{len(_models) + 1}"
        logger.error(f"[{error_id}] Failed to load VRM: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            "Failed to load VRM model",
            {"error_id": error_id, "error": str(e)}
        )

@mcp.tool()
def play_animation(model_id: str, animation_name: str, loop: bool = False) -> Dict[str, Any]:
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
            "model_id": model_id
        }

        _active_animations[animation_id] = animation_info

        logger.info(f"Playing animation '{animation_name}' on model {model_id} (loop: {loop})")

        return {
            "status": "success",
            "animation": animation_name,
            "model_id": model_id,
            "loop": loop,
            "duration": animation_info["duration"]
        }

    except Exception as e:
        error_id = f"anim_err_{len(_active_animations) + 1}"
        logger.error(f"[{error_id}] Failed to play animation: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            "Failed to play animation",
            {"error_id": error_id, "error": str(e)}
        )

@mcp.tool()
def list_models() -> Dict[str, Any]:
    """
    List all loaded VRM models.

    Returns:
        Dict containing status and list of loaded models
    """
    try:
        return {
            "status": "success",
            "models": list(_models.values())
        }
    except Exception as e:
        logger.exception("Failed to list models")
        return create_error_response("Failed to list models", {"error": str(e)})

def main() -> int:
    """
    Entry point for the AvatarMCP server.
    Uses stdio communication as required by FastMCP 2.10.1+
    """
    try:
        logger.info("Starting AvatarMCP server...")
        logger.info("Using stdio communication (FastMCP 2.10.1+)")
        logger.info("Press Ctrl+C to stop the server")
        
        # Start the MCP server with stdio communication
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Error in server: %s", str(e))
        logger.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
