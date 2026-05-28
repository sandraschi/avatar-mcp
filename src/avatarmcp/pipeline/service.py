"""Avatar creative pipeline orchestration service."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any

from avatarmcp.pipeline.fleet_http import (
    DEFAULT_VROID_URL,
    blender_reexport_vrm,
    blender_validate_vrm,
    call_vroid_tool,
    stage_vrm_for_vts,
)
from avatarmcp.pipeline.hub_client import VRoidHubClient
from avatarmcp.pipeline.vrm_type_detect import build_import_metadata

logger = logging.getLogger(__name__)


class AvatarPipelineService:
    """Orchestrates VRoid export, Blender validation, VTube staging."""

    def __init__(self, models_dir: str | None = None) -> None:
        base = Path(models_dir or os.path.join(Path.home(), ".avatarmcp", "models"))
        root = Path(os.environ.get("AVATAR_PIPELINE_WORK_DIR", base.parent / "pipeline"))
        self.work_dir = root
        self.staging_dir = root / "staging"
        self.output_dir = root / "output"
        self.hub_dir = root / "hub"
        self.vts_dir = self.staging_dir / "vts"
        for folder in (self.staging_dir, self.output_dir, self.hub_dir, self.vts_dir):
            folder.mkdir(parents=True, exist_ok=True)
        self.hub_client = VRoidHubClient(self.hub_dir)

    async def run(
        self,
        operation: str,
        *,
        vrm_filename: str = "anime_gal.vrm",
        source_path: str = "",
        output_name: str = "",
        pick_sample: bool = True,
        skip_vroid: bool = False,
        label: str = "pipeline_avatar",
        load_into_registry: bool = True,
        mcp_server: Any | None = None,
        character_model_id: str = "",
        auth_step: str = "status",
        auth_code: str = "",
        oauth_state: str = "",
        access_token: str = "",
        model_type_override: str = "",
    ) -> dict[str, Any]:
        op = operation.strip().lower()

        if op == "status":
            return {
                "success": True,
                "status": "success",
                "work_dir": str(self.work_dir),
                "staging": [p.name for p in self.staging_dir.glob("*.vrm")],
                "outputs": [p.name for p in self.output_dir.glob("*.vrm")],
                "hub": [p.name for p in self.hub_dir.glob("*.vrm")],
                "vroid_url": DEFAULT_VROID_URL,
                "hub_auth": self.hub_client.auth_status(),
                "message": "Avatar pipeline ready",
            }

        if op == "hub_auth":
            step = auth_step.strip().lower() or "status"
            if step == "start":
                return {**self.hub_client.auth_start(), "status": "success" if self.hub_client.client_id else "error"}
            if step == "complete":
                result = await self.hub_client.auth_complete(auth_code, oauth_state)
                return {**result, "status": "success" if result.get("success") else "error"}
            if step == "set_token":
                result = self.hub_client.auth_set_token(access_token)
                return {**result, "status": "success" if result.get("success") else "error"}
            hub_status = self.hub_client.auth_status()
            return {"success": True, "status": "success", **hub_status, "message": "Hub auth status"}

        if op == "hub_download":
            if not character_model_id.strip():
                return {"success": False, "status": "error", "message": "character_model_id required"}
            dl = await self.hub_client.download_character(character_model_id.strip(), self.hub_dir)
            if not dl.get("success"):
                return {**dl, "status": "error", "message": dl.get("error", "Hub download failed")}
            hub_path = Path(dl["download_path"])
            dest_name = vrm_filename or hub_path.name
            staged = self.staging_dir / dest_name
            shutil.copy2(hub_path, staged)
            type_info = build_import_metadata(staged)
            if model_type_override.strip():
                type_info["model_type"] = model_type_override.strip()
                type_info["is_humanoid"] = model_type_override.strip() in ("humanoid", "taur")
            result = {
                "success": True,
                "status": "success",
                "staged_path": str(staged),
                "hub_path": str(hub_path),
                "character_model_id": character_model_id,
                "size_kb": round(staged.stat().st_size / 1024, 1),
                "model_type": type_info.get("model_type"),
                "type_detection": type_info.get("custom_properties", {}).get("type_detection"),
                "message": f"Downloaded Hub model and staged {dest_name}",
            }
            if load_into_registry and mcp_server:
                await self._register_staged(mcp_server, str(staged), metadata=type_info)
            return result

        if op == "vroid_quick_avatar":
            result = await self._vroid_export(vrm_filename, pick_sample=pick_sample)
            if load_into_registry and result.get("success") and mcp_server:
                staged = result.get("staged_path", "")
                meta = build_import_metadata(staged) if staged else None
                await self._register_staged(mcp_server, staged, metadata=meta)
            return result

        if op == "hub_stage_file":
            if not source_path:
                return {"success": False, "status": "error", "message": "source_path required"}
            src = Path(source_path)
            if not src.is_file():
                return {"success": False, "status": "error", "message": f"File not found: {source_path}"}
            dest = self.staging_dir / (vrm_filename or src.name)
            shutil.copy2(src, dest)
            result = {
                "success": True,
                "status": "success",
                "staged_path": str(dest),
                "size_kb": round(dest.stat().st_size / 1024, 1),
                "message": f"Staged {dest.name}",
            }
            if load_into_registry and mcp_server:
                meta = build_import_metadata(dest)
                if model_type_override.strip():
                    meta["model_type"] = model_type_override.strip()
                await self._register_staged(mcp_server, str(dest), metadata=meta)
            return result

        staged_vrm = self._resolve_staged(vrm_filename)
        if op in ("blender_validate", "blender_reexport", "stage_for_vts") and staged_vrm is None:
            return {"success": False, "status": "error", "message": f"VRM not in staging: {vrm_filename}"}

        if op == "blender_validate":
            payload = await blender_validate_vrm(str(staged_vrm))
            return self._wrap(payload, "Blender validation complete")

        if op == "blender_reexport":
            out_name = output_name or vrm_filename.replace(".vrm", "_fixed.vrm")
            out_path = str((self.output_dir / out_name).resolve())
            validate = await blender_validate_vrm(str(staged_vrm))
            if not validate.get("success"):
                return self._wrap(validate, "Validation failed before reexport")
            payload = await blender_reexport_vrm(str(staged_vrm), out_path)
            return self._wrap(payload, "Blender re-export complete")

        if op == "stage_for_vts":
            payload = stage_vrm_for_vts(str(staged_vrm), self.vts_dir, label=label)
            return self._wrap(payload, "Staged for VTube Studio")

        if op == "full_pipeline":
            steps: list[dict[str, Any]] = []
            target = self.staging_dir / vrm_filename
            if not skip_vroid or not target.is_file():
                vroid = await self._vroid_export(vrm_filename, pick_sample=pick_sample)
                steps.append({"step": "vroid_quick_avatar", **vroid})
                if not vroid.get("success"):
                    return {
                        "success": False,
                        "status": "error",
                        "steps": steps,
                        "message": vroid.get("error", "VRoid export failed"),
                    }
            else:
                steps.append({"step": "vroid_quick_avatar", "success": True, "skipped": True})

            validate = await blender_validate_vrm(str(target))
            steps.append({"step": "blender_validate", **validate})
            if not validate.get("success"):
                return {
                    "success": False,
                    "status": "error",
                    "steps": steps,
                    "message": validate.get("error", "validation failed"),
                }

            vts = stage_vrm_for_vts(str(target), self.vts_dir, label=label)
            steps.append({"step": "stage_for_vts", **vts})

            if load_into_registry and mcp_server and target.is_file():
                await self._register_staged(mcp_server, str(target), metadata=build_import_metadata(target))

            return {
                "success": vts.get("success", False),
                "status": "success" if vts.get("success") else "error",
                "vrm_filename": vrm_filename,
                "staged_path": str(target),
                "steps": steps,
                "message": "Full pipeline complete" if vts.get("success") else "Pipeline failed at VTS stage",
            }

        if op == "list_staging":
            files = []
            for folder in (self.staging_dir, self.output_dir, self.vts_dir):
                for path in folder.iterdir():
                    if path.is_file():
                        files.append({"path": str(path), "size_kb": round(path.stat().st_size / 1024, 1)})
            return {"success": True, "status": "success", "files": files, "message": f"{len(files)} staged files"}

        return {"success": False, "status": "error", "message": f"Unknown operation: {operation}"}

    def _resolve_staged(self, vrm_filename: str) -> Path | None:
        primary = self.staging_dir / vrm_filename
        if primary.is_file():
            return primary
        alt = self.output_dir / vrm_filename
        if alt.is_file():
            return alt
        return None

    async def _vroid_export(self, vrm_filename: str, *, pick_sample: bool) -> dict[str, Any]:
        result = await call_vroid_tool(
            "vroid_studio",
            {"operation": "quick_gal_export", "output_name": vrm_filename, "pick_sample": pick_sample},
        )
        if not result.get("success"):
            return {**result, "status": "error", "message": result.get("error", "VRoid export failed")}
        export_path = result.get("export_path", "")
        if export_path and Path(export_path).is_file():
            dest = self.staging_dir / vrm_filename
            shutil.copy2(export_path, dest)
            result["staged_path"] = str(dest)
        return {
            **result,
            "status": "success",
            "message": f"Exported and staged {vrm_filename}",
        }

    async def _register_staged(
        self,
        mcp_server: Any,
        staged_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not staged_path or not Path(staged_path).is_file():
            return
        try:
            meta = metadata or build_import_metadata(staged_path)
            model_id = await mcp_server.vrm_manager.import_model(staged_path, metadata=meta)
            logger.info(
                "Pipeline registered VRM as %s type=%s",
                model_id,
                meta.get("model_type", "humanoid"),
            )
        except Exception as exc:
            logger.warning("Failed to register staged VRM: %s", exc)

    @staticmethod
    def _wrap(payload: dict[str, Any], message: str) -> dict[str, Any]:
        ok = payload.get("success", False)
        return {
            **payload,
            "status": "success" if ok else "error",
            "message": message if ok else payload.get("error", message),
        }
