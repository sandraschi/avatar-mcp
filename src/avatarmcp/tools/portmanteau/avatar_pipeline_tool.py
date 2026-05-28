"""Avatar creative pipeline portmanteau tool."""

from __future__ import annotations

import logging
from typing import Any

from avatarmcp.pipeline.service import AvatarPipelineService

logger = logging.getLogger(__name__)


class AvatarPipelineTool:
    """Fleet orchestrator: VRoid brute-force, Blender validate, VTube staging."""

    def __init__(self, mcp_server) -> None:
        self.mcp_server = mcp_server
        models_dir = getattr(mcp_server.vrm_manager, "models_dir", None)
        self.service = AvatarPipelineService(models_dir=models_dir)
        self._register_tool()

    def _register_tool(self) -> None:
        service = self.service
        mcp_server = self.mcp_server

        @mcp_server.mcp.tool()
        async def avatar_pipeline(params: dict[str, Any]) -> dict[str, Any]:
            """Orchestrate VRM creative pipeline across fleet MCP servers.

            Operations:
            - status: pipeline dirs, fleet URLs, hub auth status
            - hub_auth: VRoid Hub OAuth (auth_step: status|start|complete|set_token)
            - hub_download: fetch VRM from Hub by character_model_id, stage, detect model_type
            - vroid_quick_avatar: pywinauto VRoid export + stage
            - hub_stage_file: copy local VRM into staging (+ model_type detect on import)
            - blender_validate: headless Blender import stats
            - blender_reexport: import + VRM re-export
            - stage_for_vts: VTube Studio folder + manifest
            - full_pipeline: vroid -> validate -> vts (+ registry import)
            - list_staging: list staged files
            """
            try:
                operation = (params.get("operation") or "status").strip().lower()
                return await service.run(
                    operation,
                    vrm_filename=params.get("vrm_filename", "anime_gal.vrm"),
                    source_path=params.get("source_path", ""),
                    output_name=params.get("output_name", ""),
                    pick_sample=bool(params.get("pick_sample", True)),
                    skip_vroid=bool(params.get("skip_vroid", False)),
                    label=params.get("label", "pipeline_avatar"),
                    load_into_registry=bool(params.get("load_into_registry", True)),
                    mcp_server=mcp_server,
                    character_model_id=params.get("character_model_id", ""),
                    auth_step=params.get("auth_step", "status"),
                    auth_code=params.get("auth_code", ""),
                    oauth_state=params.get("oauth_state", ""),
                    access_token=params.get("access_token", ""),
                    model_type_override=params.get("model_type_override", ""),
                )
            except Exception as exc:
                logger.exception("avatar_pipeline failed")
                return {"success": False, "status": "error", "message": str(exc)}
