"""
Avatar Manager Portmanteau Tool for AvatarMCP

Consolidates all avatar lifecycle management operations into a single tool.
"""

import logging
import os
from typing import Any

from avatarmcp.models.vrm_model import VRMModel

logger = logging.getLogger(__name__)


class AvatarManagerTool:
    """Portmanteau tool for comprehensive avatar lifecycle management."""

    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self._register_tool()

    def _register_tool(self):

        @self.mcp_server.mcp.tool()
        async def avatar_manager(params: dict[str, Any]) -> dict[str, Any]:
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "load":
                    return await self._handle_load(params)
                elif operation == "unload":
                    return await self._handle_unload(params)
                elif operation == "list":
                    return await self._handle_list(params)
                elif operation == "set_active":
                    return await self._handle_set_active(params)
                elif operation == "get_active":
                    return await self._handle_get_active(params)
                elif operation == "get_metadata":
                    return await self._handle_get_metadata(params)
                elif operation == "set_thumbnail":
                    return await self._handle_set_thumbnail(params)
                elif operation == "get_thumbnail_path":
                    return await self._handle_get_thumbnail_path(params)
                else:
                    return {
                        "status": "error",
                        "message": (
                            "Unknown operation. Valid: load, unload, list, set_active, "
                            "get_active, get_metadata, set_thumbnail, get_thumbnail_path"
                        ),
                    }

            except Exception as e:
                logger.error(f"Avatar manager operation failed: {e!s}", exc_info=True)
                return {"status": "error", "message": f"Avatar manager operation failed: {e!s}"}

    async def _handle_load(self, params: dict[str, Any]) -> dict[str, Any]:
        file_path = params.get("path")
        if not file_path:
            return {"status": "error", "message": "Path parameter is required for load operation"}

        make_active = params.get("make_active", True)

        try:
            # Import model to VRM manager for file tracking
            model_id = await self.mcp_server.vrm_manager.import_model(file_path)

            # Load VRM model into memory
            try:
                vrm_model = VRMModel(file_path)
            except Exception as e:
                # Model file may not be valid VRM; register in loaded_models anyway
                # for models scanned from the models directory
                self.mcp_server.loaded_models[model_id] = {"id": model_id, "path": file_path}
                if make_active:
                    self.mcp_server.active_model_id = model_id
                return {
                    "status": "success",
                    "message": f"Imported avatar from {file_path} (model data deferred)",
                    "operation": "load",
                    "avatar_id": model_id,
                    "path": file_path,
                    "make_active": make_active,
                    "note": "VRM model data will be loaded on first access",
                }

            self.mcp_server.loaded_models[model_id] = vrm_model

            if make_active:
                self.mcp_server.active_model_id = model_id

            return {
                "status": "success",
                "message": f"Loaded avatar from {file_path}",
                "operation": "load",
                "avatar_id": model_id,
                "path": file_path,
                "make_active": make_active,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to load avatar: {e!s}"}

    async def _handle_unload(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id")
        if not avatar_id:
            return {"status": "error", "message": "Avatar ID is required for unload operation"}

        try:
            if avatar_id in self.mcp_server.loaded_models:
                del self.mcp_server.loaded_models[avatar_id]
                if self.mcp_server.active_model_id == avatar_id:
                    self.mcp_server.active_model_id = None
                return {
                    "status": "success",
                    "message": f"Unloaded avatar {avatar_id}",
                    "operation": "unload",
                    "avatar_id": avatar_id,
                }
            return {"status": "error", "message": f"Avatar {avatar_id} not found"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to unload avatar: {e!s}"}

    async def _handle_list(self, params: dict[str, Any]) -> dict[str, Any]:
        try:
            avatars = []
            for model_id, model in self.mcp_server.loaded_models.items():
                name = model_id
                path = ""
                if hasattr(model, "metadata"):
                    name = model.metadata.get("name", model_id)
                if hasattr(model, "file_path"):
                    path = model.file_path
                elif isinstance(model, dict):
                    name = model.get("name", model_id)
                    path = model.get("path", "")
                avatars.append({
                    "id": model_id,
                    "name": name,
                    "path": path,
                    "active": model_id == self.mcp_server.active_model_id,
                })

            return {
                "status": "success",
                "message": f"Found {len(avatars)} loaded avatars",
                "operation": "list",
                "avatars": avatars,
                "active_avatar_id": self.mcp_server.active_model_id,
                "count": len(avatars),
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to list avatars: {e!s}"}

    async def _handle_set_active(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id")
        if not avatar_id:
            return {"status": "error", "message": "Avatar ID is required for set_active operation"}

        try:
            if avatar_id in self.mcp_server.loaded_models:
                self.mcp_server.active_model_id = avatar_id
                return {
                    "status": "success",
                    "message": f"Set active avatar to {avatar_id}",
                    "operation": "set_active",
                    "avatar_id": avatar_id,
                }
            return {"status": "error", "message": f"Avatar {avatar_id} not found"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set active avatar: {e!s}"}

    async def _handle_get_active(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = self.mcp_server.active_model_id
        if avatar_id:
            return {
                "status": "success",
                "message": f"Active avatar is {avatar_id}",
                "operation": "get_active",
                "avatar_id": avatar_id,
            }
        return {
            "status": "success",
            "message": "No active avatar",
            "operation": "get_active",
            "avatar_id": None,
        }

    async def _handle_get_metadata(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id")
        if not avatar_id:
            avatar_id = self.mcp_server.active_model_id
            if not avatar_id:
                return {"status": "error", "message": "No avatar ID provided and no active avatar"}

        try:
            model = self.mcp_server.loaded_models.get(avatar_id)
            if model:
                metadata = model.to_dict()
                metadata["bones"] = model.get_bone_names()
                metadata["blend_shapes"] = model.get_blend_shape_names()
                return {
                    "status": "success",
                    "message": f"Retrieved metadata for avatar {avatar_id}",
                    "operation": "get_metadata",
                    "avatar_id": avatar_id,
                    "metadata": metadata,
                }

            # Fall back to VRM manager info
            model_info = await self.mcp_server.vrm_manager.get_model_info(avatar_id)
            if model_info:
                return {
                    "status": "success",
                    "message": f"Retrieved metadata for avatar {avatar_id}",
                    "operation": "get_metadata",
                    "avatar_id": avatar_id,
                    "metadata": model_info,
                }

            return {"status": "error", "message": f"No metadata found for avatar {avatar_id}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get avatar metadata: {e!s}"}

    async def _handle_set_thumbnail(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id") or params.get("model_id")
        icon_path = params.get("icon_path")
        if not avatar_id or not icon_path:
            return {"status": "error", "message": "avatar_id and icon_path required for set_thumbnail"}

        result = await self.mcp_server.vrm_manager.set_model_thumbnail(str(avatar_id), str(icon_path))
        if not result.get("success"):
            return {"status": "error", "message": result.get("error", "Thumbnail import failed"), **result}
        return {
            "status": "success",
            "message": f"Thumbnail set for avatar {avatar_id}",
            "operation": "set_thumbnail",
            "avatar_id": avatar_id,
            **result,
        }

    async def _handle_get_thumbnail_path(self, params: dict[str, Any]) -> dict[str, Any]:
        avatar_id = params.get("avatar_id") or params.get("model_id")
        if not avatar_id:
            return {"status": "error", "message": "avatar_id required for get_thumbnail_path"}

        model_info = await self.mcp_server.vrm_manager.get_model_info(str(avatar_id))
        if not model_info:
            return {"status": "error", "message": f"Avatar {avatar_id} not found"}

        thumb = os.path.join(model_info["directory"], f"{avatar_id}.thumb.png")
        return {
            "status": "success",
            "operation": "get_thumbnail_path",
            "avatar_id": avatar_id,
            "thumbnail_path": thumb,
            "exists": os.path.isfile(thumb),
        }
