"""
Avatar Controls Package

This package provides advanced controls for manipulating avatars, including:
- Bone manipulation
- Morph target control
- Export functionality
"""

# Re-export all public classes and functions
from .base import BaseControlTool, ControlMode, ControlResult, ControlSpace, Quaternion, Transform
from .bone_control import BoneControlTool, BoneTransform
from .export import ExportFormat, ExportOptions, ExportTool
from .morph_control import MorphControlTool, MorphTargetUpdate

__all__ = [
    "BaseControlTool",
    # Bone control
    "BoneControlTool",
    "BoneTransform",
    "ControlMode",
    # Base classes and types
    "ControlResult",
    "ControlSpace",
    "ExportFormat",
    "ExportOptions",
    # Export
    "ExportTool",
    # Morph control
    "MorphControlTool",
    "MorphTargetUpdate",
    "Quaternion",
    "Transform",
]

# List of available controls
AVAILABLE_CONTROLS = ["bone_control", "morph_control", "export_avatar"]


def get_control_tool(name: str) -> BaseControlTool | None:
    """Get a control tool by name.

    Args:
        name: Name of the control tool to get (e.g., 'bone_control')

    Returns:
        The control tool instance or None if not found
    """
    tools = {
        "bone_control": BoneControlTool,
        "morph_control": MorphControlTool,
        "export_avatar": ExportTool,
    }

    tool_class = tools.get(name)
    return tool_class() if tool_class else None


def register_fastmcp_tools() -> dict[str, BaseControlTool]:
    """Register all FastMCP tools.

    This function initializes and returns all available control tools
    properly configured for use with FastMCP 2.12+.

    Returns:
        Dictionary mapping tool names to tool instances
    """
    return {
        "bone_control": BoneControlTool(),
        "morph_control": MorphControlTool(),
        "export_avatar": ExportTool(),
    }


# For backward compatibility
register_tools = register_fastmcp_tools
