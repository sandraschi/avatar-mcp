"""
Enhanced MCP Tools for AvatarMCP with advanced avatar controls.

This module provides FastMCP 2.12+ compatible tools for advanced avatar manipulation.
"""

import logging
from typing import Any

from ..avatar_controls import BoneControlTool, ExportTool, MorphControlTool
from ..avatar_controls import register_fastmcp_tools as register_avatar_controls
from ..models.animation_controller import AnimationController
from ..models.vrm_model import VRMModel
from ..network.osc.vrc_connector import VRChatOSC
from .mcp_tools import MCPTools

logger = logging.getLogger(__name__)


class EnhancedMCPTools(MCPTools):
    """Enhanced MCP Tools with advanced avatar controls."""

    def __init__(self, mcp_server, vrc_osc: VRChatOSC):
        """Initialize enhanced MCP tools.

        Args:
            mcp_server: The MCP server instance
            vrc_osc: The VRChat OSC connector
        """
        # Initialize the parent class with both required parameters
        super().__init__(mcp_server, vrc_osc)
        self.avatars: dict[str, VRMModel] = {}
        self.animation_controllers: dict[str, AnimationController] = {}

        # Initialize avatar control tools
        self._init_avatar_controls()

    def _init_avatar_controls(self):
        """Initialize avatar control tools."""
        # Register FastMCP tools
        self._tools = {}

        # Register bone control
        self.bone_control = BoneControlTool()
        self._tools["bone_control"] = self.bone_control

        # Register morph control
        self.morph_control = MorphControlTool()
        self._tools["morph_control"] = self.morph_control

        # Register export tool
        self.export_tool = ExportTool()
        self._tools["export_avatar"] = self.export_tool

        logger.info("Initialized enhanced avatar controls")

    async def execute_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific arguments

        Returns:
            Dictionary with tool execution results
        """
        if tool_name not in self._tools:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

        try:
            tool = self._tools[tool_name]
            result = await tool.execute(**kwargs)
            return {
                "status": "success" if result.success else "error",
                "data": result.data,
                "message": result.message,
                "error": result.error,
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e!s}", exc_info=True)
            return {"status": "error", "message": str(e)}

    # FastMCP 2.12+ compatibility
    def get_tools(self) -> dict[str, Any]:
        """Get all registered tools for FastMCP 2.12+."""
        return self._tools

    # Avatar management
    def add_avatar(self, avatar_id: str, vrm_model: VRMModel):
        """Add an avatar to be managed.

        Args:
            avatar_id: Unique identifier for the avatar
            vrm_model: The VRM model instance
        """
        self.avatars[avatar_id] = vrm_model
        self.animation_controllers[avatar_id] = AnimationController(vrm_model)
        logger.info(f"Added avatar: {avatar_id}")

    def remove_avatar(self, avatar_id: str):
        """Remove an avatar from management.

        Args:
            avatar_id: ID of the avatar to remove
        """
        if avatar_id in self.avatars:
            del self.avatars[avatar_id]
        if avatar_id in self.animation_controllers:
            del self.animation_controllers[avatar_id]
        logger.info(f"Removed avatar: {avatar_id}")

    def get_avatar(self, avatar_id: str) -> VRMModel | None:
        """Get an avatar by ID.

        Args:
            avatar_id: ID of the avatar to get

        Returns:
            The VRM model or None if not found
        """
        return self.avatars.get(avatar_id)

    def get_animation_controller(self, avatar_id: str) -> AnimationController | None:
        """Get an animation controller by avatar ID.

        Args:
            avatar_id: ID of the avatar

        Returns:
            The animation controller or None if not found
        """
        return self.animation_controllers.get(avatar_id)


# FastMCP 2.12+ tool registration
def register_enhanced_tools() -> dict[str, Any]:
    """Register enhanced tools with FastMCP 2.12+."""
    # Register base avatar controls
    tools = register_avatar_controls()

    # Add any additional tools here

    return tools
