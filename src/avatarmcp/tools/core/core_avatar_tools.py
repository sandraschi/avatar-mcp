"""
Core Avatar Tools for AvatarMCP

This module contains the core avatar lifecycle tools migrated from the monolithic server.
"""

import logging
import os
import time
from typing import Any

from ...models.vrm import VRMModel

logger = logging.getLogger(__name__)


class CoreAvatarTools:
    """Core avatar tools for lifecycle management."""

    def __init__(self, mcp_server):
        """Initialize core avatar tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all core avatar tools with the MCP server."""

        @self.mcp_server.mcp.tool()
        async def avatar_load(
            path: str,
            make_active: bool = True,
            metadata: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Load a VRM avatar into the system.

            Loads a specified VRM avatar file and prepares it for animation,
            expression control, and interaction.

            Parameters:
                path: Identifier or file path of the avatar to load (required)
                make_active: Whether to set this avatar as active immediately (default: True)
                metadata: Optional additional metadata for the model

            Returns:
                Dictionary with status, model ID, and metadata
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                source_path = path
                if not source_path:
                    raise ValueError("No avatar path or model ID provided")

                metadata = metadata or {}

                # Check if it's a file path or model ID
                if os.path.isfile(source_path):
                    # Import the VRM file
                    model_id = await self.mcp_server.vrm_manager.import_model(source_path, metadata)
                    logger.info(f"Imported VRM model: {model_id} from {source_path}")
                else:
                    # Treat as model ID
                    model_id = source_path

                # Load the model
                model_info = await self.mcp_server.vrm_manager.load_model(model_id)
                if (
                    not model_info
                    or "status" not in model_info
                    or model_info["status"] != "success"
                ):
                    raise RuntimeError(f"Failed to load model {model_id}")

                # Create VRMModel instance
                vrm_model = VRMModel(model_info["path"])
                self.mcp_server.loaded_models[model_id] = vrm_model

                # Set as active if requested
                if make_active:
                    self.mcp_server.active_model_id = model_id

                return {
                    "status": "success",
                    "model_id": model_id,
                    "active": make_active,
                    "metadata": model_info.get("metadata", {}),
                }

            except Exception as e:
                error_msg = f"Failed to load avatar: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {"status": "error", "message": error_msg}

        @self.mcp_server.mcp.tool()
        async def avatar_unload(avatar_id: str, force: bool = False) -> dict[str, Any]:
            """Unload an avatar from the system.

            Removes a loaded avatar from memory. Active avatars cannot be unloaded
            unless force is set to True.

            Parameters:
                avatar_id: ID of the avatar to unload (required)
                force: Whether to force unloading even if active (default: False)

            Returns:
                Dictionary with status and message
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                if not avatar_id:
                    raise ValueError("No avatar ID provided")

                if avatar_id not in self.mcp_server.loaded_models:
                    raise ValueError(f"Avatar not found: {avatar_id}")

                # Don't unload active model unless forced
                if avatar_id == self.mcp_server.active_model_id and not force:
                    raise RuntimeError("Cannot unload active model. Set force=True to override.")

                # Remove from loaded models
                del self.mcp_server.loaded_models[avatar_id]

                # Update active model if needed
                if avatar_id == self.mcp_server.active_model_id:
                    self.mcp_server.active_model_id = next(
                        iter(self.mcp_server.loaded_models), None
                    )

                return {
                    "status": "success",
                    "message": f"Unloaded avatar: {avatar_id}",
                    "was_active": avatar_id == self.mcp_server.active_model_id,
                }

            except Exception as e:
                error_msg = f"Failed to unload avatar: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {"status": "error", "message": error_msg}

        @self.mcp_server.mcp.tool()
        async def avatar_list(
            loaded_only: bool = False, include_metadata: bool = False
        ) -> dict[str, Any]:
            """List available or loaded avatars.

            Returns a list of avatars currently in the system.

            Parameters:
                loaded_only: Only return avatars currently in memory (default: False)
                include_metadata: Include full metadata for each avatar (default: False)

            Returns:
                Dictionary with list of avatars and counts
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                avatars = []

                # Get loaded models
                for model_id in self.mcp_server.loaded_models.keys():
                    avatar_info = {
                        "id": model_id,
                        "name": model_id,
                        "status": "loaded",
                        "is_active": model_id == self.mcp_server.active_model_id,
                    }

                    if include_metadata and model_id in self.mcp_server.loaded_models:
                        avatar_info["metadata"] = self.mcp_server.loaded_models[model_id].to_dict()

                    avatars.append(avatar_info)

                return {
                    "status": "success",
                    "count": len(avatars),
                    "active_model": self.mcp_server.active_model_id,
                    "avatars": avatars,
                }

            except Exception as e:
                error_msg = f"Failed to list avatars: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {"status": "error", "message": error_msg}

        @self.mcp_server.mcp.tool()
        async def avatar_set_active(avatar_id: str) -> dict[str, Any]:
            """Set the specified loaded avatar as the active model.

            Parameters:
                avatar_id: ID of the avatar to make active (required)

            Returns:
                Dictionary with status and message
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                if not avatar_id:
                    raise ValueError("No avatar ID provided")

                # Check if the model is loaded
                if avatar_id not in self.mcp_server.loaded_models:
                    return {
                        "status": "error",
                        "message": f"Avatar with ID '{avatar_id}' is not loaded",
                    }

                # Set the active model
                self.mcp_server.active_model_id = avatar_id

                return {
                    "status": "success",
                    "message": f"Set active avatar to: {avatar_id}",
                    "active_avatar_id": avatar_id,
                }

            except Exception as e:
                logger.error(f"Failed to set active avatar: {str(e)}", exc_info=True)
                return {"status": "error", "message": str(e)}

        @self.mcp_server.mcp.tool()
        async def avatar_get_active() -> dict[str, Any]:
            """Get information about the currently active avatar model.

            Returns:
                Dictionary with active avatar ID and status
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                if not self.mcp_server.active_model_id:
                    return {
                        "status": "success",
                        "active_avatar_id": None,
                        "message": "No active avatar",
                    }

                return {
                    "status": "success",
                    "active_avatar_id": self.mcp_server.active_model_id,
                    "loaded": self.mcp_server.active_model_id in self.mcp_server.loaded_models,
                    "message": f"Active avatar: {self.mcp_server.active_model_id}",
                }

            except Exception as e:
                logger.error(f"Failed to get active avatar: {str(e)}", exc_info=True)
                return {"status": "error", "message": str(e)}

        @self.mcp_server.mcp.tool()
        async def avatar_get_metadata(avatar_id: str | None = None) -> dict[str, Any]:
            """Get detailed metadata for a specific or active avatar.

            Parameters:
                avatar_id: ID of the avatar (optional, defaults to active)

            Returns:
                Dictionary with avatar metadata
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                avatar_id = avatar_id or self.mcp_server.active_model_id

                if not avatar_id:
                    raise ValueError("No avatar ID provided and no active model")

                # Check if the model is loaded
                if avatar_id in self.mcp_server.loaded_models:
                    return {
                        "status": "success",
                        "id": avatar_id,
                        "loaded": True,
                        "active": avatar_id == self.mcp_server.active_model_id,
                        "metadata": self.mcp_server.loaded_models[avatar_id].to_dict(),
                    }

                raise ValueError(f"Avatar not found: {avatar_id}")

            except Exception as e:
                error_msg = f"Failed to get avatar metadata: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {"status": "error", "message": error_msg}
