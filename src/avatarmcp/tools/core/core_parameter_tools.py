"""
Core Parameter Tools for AvatarMCP

This module contains the core parameter control tools that are actually implemented
and working for setting and getting avatar parameters.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CoreParameterTools:
    """Core parameter tools with real implementations."""

    def __init__(self, mcp_server):
        """Initialize core parameter tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register core parameter tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        def parameter_set(params: dict[str, Any]) -> dict[str, Any]:
            """Set a parameter value on the active avatar.
            
            Sets a custom parameter value on the currently active avatar. Parameters
            can control animations, expressions, or other avatar behaviors.
            
            Parameters:
                name: Name of the parameter to set (required)
                value: Value to set (boolean, integer, float, or string)
                
            Returns:
                Dictionary with status and parameter details
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                name = params.get("name")
                if not name:
                    return {"status": "error", "message": "Parameter name is required"}
                
                value = params.get("value")
                if value is None:
                    return {"status": "error", "message": "Parameter value is required"}
                
                # Get active avatar
                active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
                if not active_avatar_id:
                    return {"status": "error", "message": "No active avatar loaded"}
                
                # Get animation controller for active avatar
                avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
                if not avatar_data or "animation_controller" not in avatar_data:
                    return {"status": "error", "message": "Animation controller not available for active avatar"}
                
                controller = avatar_data["animation_controller"]
                
                # Set the parameter
                controller.set_parameter(name, value)
                
                return {
                    "status": "success",
                    "message": f"Set parameter '{name}' = {value} on avatar '{active_avatar_id}'",
                    "parameter_name": name,
                    "value": value,
                    "avatar_id": active_avatar_id
                }
                
            except Exception as e:
                logger.error(f"Failed to set parameter: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to set parameter: {str(e)}"}

        @self.mcp_server.mcp.tool()
        def parameter_get(params: dict[str, Any]) -> dict[str, Any]:
            """Get a parameter value from the active avatar.
            
            Retrieves the current value of a parameter from the currently active avatar.
            
            Parameters:
                name: Name of the parameter to get (required)
                
            Returns:
                Dictionary with status and parameter value
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                name = params.get("name")
                if not name:
                    return {"status": "error", "message": "Parameter name is required"}
                
                # Get active avatar
                active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
                if not active_avatar_id:
                    return {"status": "error", "message": "No active avatar loaded"}
                
                # Get animation controller for active avatar
                avatar_data = self.mcp_server.vrm_manager.get_avatar(active_avatar_id)
                if not avatar_data or "animation_controller" not in avatar_data:
                    return {"status": "error", "message": "Animation controller not available for active avatar"}
                
                controller = avatar_data["animation_controller"]
                
                # Get the parameter value
                value = controller.get_parameter(name)
                
                return {
                    "status": "success",
                    "message": f"Retrieved parameter '{name}' = {value} from avatar '{active_avatar_id}'",
                    "parameter_name": name,
                    "value": value,
                    "avatar_id": active_avatar_id
                }
                
            except Exception as e:
                logger.error(f"Failed to get parameter: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Failed to get parameter: {str(e)}"}



