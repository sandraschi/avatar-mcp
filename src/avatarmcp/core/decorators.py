"""
Custom decorators for AvatarMCP.

This module provides decorators for MCP tools and other functionality.
"""
from typing import Any, Callable, Optional, TypeVar, cast
from functools import wraps

F = TypeVar('F', bound=Callable[..., Any])

def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs: Any
) -> Callable[[F], F]:
    """
    Decorator to mark a method as an MCP tool.
    
    Args:
        name: Optional name for the tool (defaults to method name)
        description: Optional description for the tool
        **kwargs: Additional metadata for the tool
        
    Returns:
        Decorated function with MCP tool metadata
    """
    def decorator(func: F) -> F:
        # Add MCP tool metadata to the function
        func._mcp_tool = True  # type: ignore
        func._mcp_tool_name = name or func.__name__  # type: ignore
        func._mcp_tool_description = description or func.__doc__ or ""  # type: ignore
        func._mcp_tool_metadata = kwargs  # type: ignore
        
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)
            
        return cast(F, wrapper)
    return decorator
