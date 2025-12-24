"""
Base classes for MCP tools.

This module provides base classes for MCP tools and related functionality.
"""

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class MCPTool:
    """Base class for MCP tools."""

    def __init__(self, mcp_server=None):
        """Initialize the MCP tool.

        Args:
            mcp_server: The MCP server instance
        """
        self.mcp_server = mcp_server


class MCPToolsBase(MCPTool):
    """Base class for MCP tools collections."""

    def __init__(self, mcp_server=None):
        """Initialize the MCP tools collection.

        Args:
            mcp_server: The MCP server instance
        """
        super().__init__(mcp_server)
        self.tools: dict[str, dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, func: Callable, **kwargs) -> None:
        """Register a tool with the MCP server.

        Args:
            name: Name of the tool
            description: Description of the tool
            func: The function to call when the tool is invoked
            **kwargs: Additional metadata for the tool
        """
        self.tools[name] = {"description": description, "function": func, **kwargs}

    def register_tools(self) -> None:
        """Register all tools with the MCP server.

        This method should be overridden by subclasses to register their tools.
        """
        # Find all methods with _mcp_tool attribute and register them
        for attr_name in dir(self):
            attr = getattr(self, attr_name, None)
            if callable(attr) and hasattr(attr, "_mcp_tool"):
                self.register_tool(
                    name=getattr(attr, "_mcp_tool_name", attr_name),
                    description=getattr(attr, "_mcp_tool_description", ""),
                    func=attr,
                    **getattr(attr, "_mcp_tool_metadata", {}),
                )
