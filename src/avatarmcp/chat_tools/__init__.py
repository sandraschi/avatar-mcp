"""
Chat tools for the Avatar MCP server.

This package contains various chat tools that can be used by the chatbot handler
to provide functionality like web search, knowledge base querying, and more.
"""

import logging

logger = logging.getLogger(__name__)

# Re-export commonly used types and classes
# Import base tools
# Import standard tools
from .animation_control_tool import AnimationControlTool
from .avatar_control_tool import AvatarControlTool
from .base_tool import (
    ChatTool,
    ToolError,
    ToolExecutionStatus,
    ToolParameter,
    ToolParameterType,
    ToolResult,
)

# Import new advanced tools
from .bone_control_tool import BoneControlTool
from .export_tool import ExportTools
from .knowledge_base_tool import KnowledgeBaseTool
from .morph_control_tool import MorphControlTool
from .system_info_tool import SystemInfoTool

# Import all tool classes here so they can be accessed directly from the package
from .web_search_tool import WebSearchTool

# List of all available tools
AVAILABLE_TOOLS = [
    WebSearchTool(),
    KnowledgeBaseTool(),
    AvatarControlTool(),
    AnimationControlTool(),
    SystemInfoTool(),
    BoneControlTool(),
    MorphControlTool(),
    ExportTools(),
]


def get_tool_by_name(name: str) -> ChatTool | None:
    """
    Get a chat tool by its name.

    Args:
        name: The name of the tool to retrieve

    Returns:
        The tool instance if found, None otherwise
    """
    for tool in AVAILABLE_TOOLS:
        if tool.name.lower() == name.lower():
            return tool
    return None


# FastMCP 2.12 Tool Registration
def register_fastmcp_tools() -> dict[str, ChatTool]:
    """Register all tools with FastMCP 2.12."""
    from .bone_control_tool import register_tools as register_bone_tools
    from .export_tool import register_tools as register_export_tools
    from .morph_control_tool import register_tools as register_morph_tools

    tools = {}
    tools.update(register_bone_tools())
    tools.update(register_morph_tools())
    tools.update(register_export_tools())
    return tools


__all__ = [
    "AVAILABLE_TOOLS",
    "AnimationControlTool",
    "AvatarControlTool",
    "ChatTool",
    "KnowledgeBaseTool",
    "SystemInfoTool",
    "ToolError",
    "ToolExecutionStatus",
    "ToolParameter",
    "ToolParameterType",
    "ToolResult",
    "WebSearchTool",
    "get_tool_by_name",
]
