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
            - hub_to_studio: Hub download and/or open .vroid in VRoid Studio (+ optional export)
            - depot_list / depot_register / depot_get / depot_scan: local VRM/.vroid catalog
            - vroid_quick_avatar: pywinauto VRoid export + stage
            - hub_stage_file: copy local VRM into staging (+ model_type detect on import)
            - blender_validate: headless Blender import stats
            - blender_reexport: import + VRM re-export
            - stage_for_vts: VTube Studio folder + manifest
            - full_pipeline: vroid -> validate -> vts (+ registry import)
            - list_staging: list staged files
            - longcat_avatar_status: health of the LongCat-Video-Avatar engine
            - longcat_avatar_generate: audio-driven talking video (source_path=audio, vrm_filename=reference
              image .png/.jpg, label=prompt, output_name)
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
                    project_path=params.get("project_path", ""),
                    save_path=params.get("save_path", ""),
                    depot_id=params.get("depot_id", ""),
                    depot_kind=params.get("depot_kind", ""),
                    open_in_studio=bool(params.get("open_in_studio", True)),
                    export_after=bool(params.get("export_after", False)),
                    studio_template=params.get("studio_template", "open_and_export"),
                    copy_to_depot=bool(params.get("copy_to_depot", True)),
                    scan_depot=bool(params.get("scan_depot", False)),
                )
            except Exception as exc:
                logger.exception("avatar_pipeline failed")
                return {"success": False, "status": "error", "message": str(exc)}
