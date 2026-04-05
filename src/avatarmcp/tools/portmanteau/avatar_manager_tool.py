"""
Avatar Manager Portmanteau Tool for AvatarMCP

Consolidates all avatar lifecycle management operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AvatarManagerTool:
    """Portmanteau tool for comprehensive avatar lifecycle management."""

    def __init__(self, mcp_server):
        """Initialize avatar manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):
        """Register the avatar manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def avatar_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive avatar lifecycle management tool.

            Provides unified interface for all avatar-related operations including
            loading, unloading, listing, activation control, and metadata retrieval.
            This portmanteau tool consolidates multiple individual avatar tools
            into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "load": Load a VRM avatar model
                    - "unload": Unload an avatar model
                    - "list": List all loaded avatars
                    - "set_active": Set the active avatar
                    - "get_active": Get the currently active avatar
                    - "get_metadata": Get avatar metadata

                Additional parameters depend on the operation:
                    - For "load": path (required), make_active (optional)
                    - For "unload": avatar_id (required)
                    - For "set_active": avatar_id (required)
                    - For "get_metadata": avatar_id (optional, defaults to active)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Load a new avatar:
                    result = await avatar_manager({
                        "operation": "load",
                        "path": "models/my_avatar.vrm",
                        "make_active": True
                    })

                List all loaded avatars:
                    result = await avatar_manager({
                        "operation": "list"
                    })

                Set active avatar:
                    result = await avatar_manager({
                        "operation": "set_active",
                        "avatar_id": "avatar_123"
                    })

                Get avatar metadata:
                    result = await avatar_manager({
                        "operation": "get_metadata",
                        "avatar_id": "avatar_123"
                    })

            Notes:
                - All operations require server to be initialized
                - Avatar IDs are generated automatically on load
                - Only one avatar can be active at a time
                - Metadata includes blend shapes, bones, animations
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "load":
                    return self._handle_load(params)
                elif operation == "unload":
                    return self._handle_unload(params)
                elif operation == "list":
                    return self._handle_list(params)
                elif operation == "set_active":
                    return self._handle_set_active(params)
                elif operation == "get_active":
                    return self._handle_get_active(params)
                elif operation == "get_metadata":
                    return self._handle_get_metadata(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: load, unload, list, set_active, get_active, get_metadata",
                    }

            except Exception as e:
                logger.error(f"Avatar manager operation failed: {str(e)}", exc_info=True)
                return {"status": "error", "message": f"Avatar manager operation failed: {str(e)}"}

    def _handle_load(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle avatar load operation."""
        try:
            path = params.get("path")
            if not path:
                return {
                    "status": "error",
                    "message": "Path parameter is required for load operation",
                }

            make_active = params.get("make_active", True)

            # Use existing VRM manager to load avatar
            avatar_id = self.mcp_server.vrm_manager.load_vrm(path)

            if make_active:
                self.mcp_server.vrm_manager.set_active_avatar(avatar_id)

            return {
                "status": "success",
                "message": f"Loaded avatar from {path}",
                "operation": "load",
                "avatar_id": avatar_id,
                "path": path,
                "make_active": make_active,
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to load avatar: {str(e)}"}

    def _handle_unload(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle avatar unload operation."""
        try:
            avatar_id = params.get("avatar_id")
            if not avatar_id:
                return {
                    "status": "error",
                    "message": "Avatar ID parameter is required for unload operation",
                }

            # Use existing VRM manager to unload avatar
            success = self.mcp_server.vrm_manager.unload_vrm(avatar_id)

            if success:
                return {
                    "status": "success",
                    "message": f"Unloaded avatar {avatar_id}",
                    "operation": "unload",
                    "avatar_id": avatar_id,
                }
            else:
                return {"status": "error", "message": f"Failed to unload avatar {avatar_id}"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to unload avatar: {str(e)}"}

    def _handle_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle avatar list operation."""
        try:
            # Get list of loaded avatars from VRM manager
            avatars = self.mcp_server.vrm_manager.list_avatars()
            active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()

            return {
                "status": "success",
                "message": f"Found {len(avatars)} loaded avatars",
                "operation": "list",
                "avatars": avatars,
                "active_avatar_id": active_avatar_id,
                "count": len(avatars),
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to list avatars: {str(e)}"}

    def _handle_set_active(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle set active avatar operation."""
        try:
            avatar_id = params.get("avatar_id")
            if not avatar_id:
                return {
                    "status": "error",
                    "message": "Avatar ID parameter is required for set_active operation",
                }

            # Use existing VRM manager to set active avatar
            success = self.mcp_server.vrm_manager.set_active_avatar(avatar_id)

            if success:
                return {
                    "status": "success",
                    "message": f"Set active avatar to {avatar_id}",
                    "operation": "set_active",
                    "avatar_id": avatar_id,
                }
            else:
                return {"status": "error", "message": f"Failed to set active avatar to {avatar_id}"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to set active avatar: {str(e)}"}

    def _handle_get_active(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle get active avatar operation."""
        try:
            # Get active avatar from VRM manager
            active_avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()

            if active_avatar_id:
                return {
                    "status": "success",
                    "message": f"Active avatar is {active_avatar_id}",
                    "operation": "get_active",
                    "avatar_id": active_avatar_id,
                }
            else:
                return {
                    "status": "success",
                    "message": "No active avatar",
                    "operation": "get_active",
                    "avatar_id": None,
                }

        except Exception as e:
            return {"status": "error", "message": f"Failed to get active avatar: {str(e)}"}

    def _handle_get_metadata(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle get avatar metadata operation."""
        try:
            avatar_id = params.get("avatar_id")
            if not avatar_id:
                # Default to active avatar
                avatar_id = self.mcp_server.vrm_manager.get_active_avatar_id()
                if not avatar_id:
                    return {
                        "status": "error",
                        "message": "No avatar ID provided and no active avatar",
                    }

            # Get avatar metadata from VRM manager
            metadata = self.mcp_server.vrm_manager.get_avatar_metadata(avatar_id)

            if metadata:
                return {
                    "status": "success",
                    "message": f"Retrieved metadata for avatar {avatar_id}",
                    "operation": "get_metadata",
                    "avatar_id": avatar_id,
                    "metadata": metadata,
                }
            else:
                return {"status": "error", "message": f"No metadata found for avatar {avatar_id}"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to get avatar metadata: {str(e)}"}
