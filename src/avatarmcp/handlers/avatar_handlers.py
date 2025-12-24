"""
Avatar management handlers for MCP server.

This module provides handlers for managing VRM avatars, including loading,
unloading, and querying avatar information.
"""

import logging
from typing import Any

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)


class AvatarHandler(BaseHandler):
    """Handles avatar-related MCP requests."""

    def __init__(self, server: Any = None):
        """Initialize the avatar handler.

        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self.loaded_models = {}
        self.active_model_id = None
        self.vrm_manager = None

    async def _initialize(self) -> None:
        """Initialize the VRM manager and load any pre-configured models."""
        if not hasattr(self.server, "vrm_manager"):
            from ..models.vrm_manager import VRMManager

            self.vrm_manager = VRMManager()
            self.server.vrm_manager = self.vrm_manager
        else:
            self.vrm_manager = self.server.vrm_manager

        logger.info("Avatar handler initialized")

    async def handle_avatar_load(self, params: dict[str, Any]) -> dict[str, Any]:
        """Load a VRM model from the specified path.

        Args:
            params: Dictionary containing:
                   - path: Path to the VRM file
                   - model_id: Optional ID of an existing model to load
                   - make_active: Whether to make this the active model (default: True)

        Returns:
            Dictionary with status and model information
        """
        try:
            self._check_initialized()
            source_path = params.get("path")
            model_id = params.get("model_id")
            make_active = params.get("make_active", True)

            if not source_path and not model_id:
                return self._create_error_response("Either path or model_id must be provided")

            if model_id:
                if model_id not in self.vrm_manager.models:
                    return self._create_error_response(f"Model not found: {model_id}")
                model_info = self.vrm_manager.models[model_id]
            else:
                try:
                    model_info = await self.vrm_manager.import_model(source_path)
                    model_id = model_info["id"]
                except Exception as e:
                    return self._create_error_response(f"Failed to import model: {str(e)}")

            try:
                self.loaded_models[model_id] = self.vrm_manager.load_model(model_id)
            except Exception as e:
                return self._create_error_response(f"Failed to load model: {str(e)}")

            if make_active:
                self.active_model_id = model_id

            return self._create_success_response(
                model_id=model_id, active=make_active, metadata=model_info.get("metadata", {})
            )

        except Exception as e:
            logger.error(f"Failed to load avatar: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def handle_avatar_unload(self, params: dict[str, Any]) -> dict[str, Any]:
        """Unload a previously loaded VRM model.

        Args:
            params: Dictionary containing:
                   - id: ID of the model to unload
                   - force: If True, unload even if active (default: False)

        Returns:
            Dictionary with status and unload information
        """
        try:
            self._check_initialized()
            avatar_id = params.get("id")
            force = params.get("force", False)

            if not avatar_id:
                return self._create_error_response("Avatar ID is required")

            if avatar_id not in self.loaded_models:
                return self._create_success_response(
                    message=f"Avatar {avatar_id} is not loaded", was_loaded=False
                )

            if avatar_id == self.active_model_id and not force:
                return self._create_error_response(
                    "Cannot unload active avatar. Set force=True to override."
                )

            del self.loaded_models[avatar_id]

            if avatar_id == self.active_model_id:
                self.active_model_id = next(iter(self.loaded_models), None)

            return self._create_success_response(
                message=f"Unloaded avatar: {avatar_id}",
                was_active=avatar_id == self.active_model_id,
            )

        except Exception as e:
            logger.error(f"Failed to unload avatar: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def handle_avatar_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """List available and loaded avatars.

        Args:
            params: Dictionary containing:
                   - loaded_only: If True, only list loaded models
                   - include_metadata: If True, include model metadata

        Returns:
            Dictionary with lists of loaded and available avatars
        """
        try:
            self._check_initialized()
            loaded_only = params.get("loaded_only", False)
            include_metadata = params.get("include_metadata", False)

            result = {"loaded": {}, "available": {}}

            for model_id, model in self.loaded_models.items():
                result["loaded"][model_id] = {
                    "active": model_id == self.active_model_id,
                    "path": model.path,
                }
                if include_metadata:
                    result["loaded"][model_id]["metadata"] = model.metadata

            if not loaded_only:
                for model_id, model_info in self.vrm_manager.models.items():
                    if model_id not in result["loaded"]:
                        result["available"][model_id] = {
                            "path": model_info.get("path", ""),
                            "metadata": model_info.get("metadata", {})
                            if include_metadata
                            else None,
                        }

            return self._create_success_response(avatars=result)

        except Exception as e:
            logger.error(f"Failed to list avatars: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def handle_avatar_get_metadata(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get metadata for a specific avatar.

        Args:
            params: Dictionary containing:
                   - id: ID of the model
                   - refresh: If True, force refresh metadata from disk

        Returns:
            Dictionary with model metadata
        """
        try:
            self._check_initialized()
            model_id = params.get("id")
            refresh = params.get("refresh", False)

            if not model_id:
                return self._create_error_response("Model ID is required")

            if model_id in self.loaded_models:
                model = self.loaded_models[model_id]
                return self._create_success_response(
                    model_id=model_id, metadata=model.metadata, loaded=True
                )

            if model_id in self.vrm_manager.models:
                if refresh:
                    metadata = await self.vrm_manager.get_model_metadata(model_id, refresh=True)
                    return self._create_success_response(
                        model_id=model_id, metadata=metadata, loaded=False
                    )
                else:
                    model_info = self.vrm_manager.models[model_id]
                    return self._create_success_response(
                        model_id=model_id, metadata=model_info.get("metadata", {}), loaded=False
                    )

            return self._create_error_response(f"Model not found: {model_id}")

        except Exception as e:
            logger.error(f"Failed to get avatar metadata: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def handle_avatar_set_active(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set the active avatar model.

        Args:
            params: Dictionary containing:
                   - id: ID of the model to make active
                   - load_if_needed: If True, load the model if not already loaded

        Returns:
            Dictionary with status and model information
        """
        try:
            self._check_initialized()
            model_id = params.get("id")
            load_if_needed = params.get("load_if_needed", True)

            if not model_id:
                return self._create_error_response("Model ID is required")

            if model_id not in self.loaded_models and load_if_needed:
                load_result = await self.handle_avatar_load(
                    {"model_id": model_id, "make_active": False}
                )
                if load_result.get("status") != "success":
                    return self._create_error_response(
                        f"Failed to load model: {load_result.get('message', 'Unknown error')}"
                    )

            if model_id not in self.loaded_models:
                return self._create_error_response(
                    f"Avatar not loaded: {model_id}. Set load_if_needed=True to load it."
                )

            previous_active = self.active_model_id
            self.active_model_id = model_id

            model_info = self.loaded_models[model_id].to_dict()

            return self._create_success_response(
                model_id=model_id, previous_model_id=previous_active, metadata=model_info
            )

        except Exception as e:
            logger.error(f"Failed to set active avatar: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def handle_avatar_get_active(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get information about the currently active avatar.

        Args:
            params: Dictionary containing:
                   - include_metadata: If True, include full metadata

        Returns:
            Dictionary with active avatar information
        """
        try:
            self._check_initialized()
            include_metadata = params.get("include_metadata", False)

            if not self.active_model_id:
                return self._create_success_response(active=False, message="No active avatar")

            response = {"active": True, "model_id": self.active_model_id, "loaded": True}

            if include_metadata and self.active_model_id in self.loaded_models:
                response["metadata"] = self.loaded_models[self.active_model_id].to_dict()

            return self._create_success_response(**response)

        except Exception as e:
            logger.error(f"Failed to get active avatar: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def shutdown(self) -> None:
        """Clean up resources used by the handler."""
        # Unload all models
        for model_id in list(self.loaded_models.keys()):
            try:
                await self.handle_avatar_unload({"id": model_id, "force": True})
            except Exception as e:
                logger.error(f"Error unloading model {model_id}: {str(e)}")

        self.loaded_models.clear()
        self.active_model_id = None
        self.initialized = False
        logger.info("Avatar handler shutdown complete")
