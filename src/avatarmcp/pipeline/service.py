"""Avatar creative pipeline orchestration service."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any

from avatarmcp.pipeline.depot import (
    KIND_VRM,
    KIND_VROID,
    SOURCE_HUB,
    SOURCE_MANUAL,
    SOURCE_STAGING,
    SOURCE_VROID_EXPORT,
    SOURCE_VROID_PROJECT,
    AvatarDepot,
)
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
        self.depot = AvatarDepot(root)

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
        project_path: str = "",
        save_path: str = "",
        depot_id: str = "",
        depot_kind: str = "",
        open_in_studio: bool = True,
        export_after: bool = False,
        studio_template: str = "open_and_export",
        copy_to_depot: bool = True,
        scan_depot: bool = False,
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
                "depot": self.depot.list_entries(limit=20),
                "message": "Avatar pipeline ready",
            }

        if op == "depot_list":
            if scan_depot:
                self.depot.scan_work_dirs(self.staging_dir, self.hub_dir, self.output_dir)
            return self.depot.list_entries(kind=depot_kind.strip())

        if op == "depot_register":
            if not source_path:
                return {"success": False, "status": "error", "message": "source_path required"}
            ext = Path(source_path).suffix.lower()
            kind = KIND_VROID if ext == ".vroid" else KIND_VRM if ext == ".vrm" else ""
            if not kind:
                return {"success": False, "status": "error", "message": "source_path must be .vrm or .vroid"}
            reg = self.depot.register(
                source_path,
                kind=kind,
                source=SOURCE_MANUAL,
                name=Path(source_path).stem,
                character_model_id=character_model_id,
                model_type=model_type_override,
                copy_into_depot=copy_to_depot,
            )
            return {**reg, "status": "success" if reg.get("success") else "error"}

        if op == "depot_get":
            if not depot_id:
                return {"success": False, "status": "error", "message": "depot_id required"}
            got = self.depot.get(depot_id)
            return {**got, "status": "success" if got.get("success") else "error"}

        if op == "depot_scan":
            scanned = self.depot.scan_work_dirs(self.staging_dir, self.hub_dir, self.output_dir)
            return {**scanned, "status": "success", "message": f"Depot scan added {scanned.get('added_count', 0)} entries"}

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
            self.depot.register(
                staged,
                kind=KIND_VRM,
                source=SOURCE_HUB,
                name=dest_name,
                character_model_id=character_model_id.strip(),
                model_type=str(type_info.get("model_type", "")),
                copy_into_depot=copy_to_depot,
                metadata={"hub_path": str(hub_path), "license_id": dl.get("license_id")},
            )
            return result

        if op == "hub_to_studio":
            return await self._hub_to_studio(
                character_model_id=character_model_id,
                vrm_filename=vrm_filename,
                project_path=project_path,
                save_path=save_path,
                depot_id=depot_id,
                output_name=output_name,
                open_in_studio=open_in_studio,
                export_after=export_after,
                studio_template=studio_template,
                copy_to_depot=copy_to_depot,
                load_into_registry=load_into_registry,
                mcp_server=mcp_server,
                model_type_override=model_type_override,
            )

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
            self.depot.register(
                dest,
                kind=KIND_VRM,
                source=SOURCE_STAGING,
                name=dest.name,
                model_type=model_type_override,
                copy_into_depot=copy_to_depot,
            )
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
            self.depot.register(
                dest,
                kind=KIND_VRM,
                source=SOURCE_VROID_EXPORT,
                name=vrm_filename,
                copy_into_depot=False,
            )
        return {
            **result,
            "status": "success",
            "message": f"Exported and staged {vrm_filename}",
        }

    async def _hub_to_studio(
        self,
        *,
        character_model_id: str,
        vrm_filename: str,
        project_path: str,
        save_path: str,
        depot_id: str,
        output_name: str,
        open_in_studio: bool,
        export_after: bool,
        studio_template: str,
        copy_to_depot: bool,
        load_into_registry: bool,
        mcp_server: Any | None,
        model_type_override: str,
    ) -> dict[str, Any]:
        steps: list[dict[str, Any]] = []
        vrm_path: str | None = None
        vroid_path: str | None = None
        depot_entry: dict[str, Any] | None = None

        if character_model_id.strip():
            hub_result = await self.run(
                "hub_download",
                vrm_filename=vrm_filename,
                character_model_id=character_model_id,
                load_into_registry=load_into_registry,
                mcp_server=mcp_server,
                model_type_override=model_type_override,
                copy_to_depot=copy_to_depot,
            )
            steps.append({"step": "hub_download", **hub_result})
            if not hub_result.get("success"):
                return {
                    "success": False,
                    "status": "error",
                    "steps": steps,
                    "message": hub_result.get("message", "Hub download failed"),
                }
            vrm_path = hub_result.get("staged_path")

        if depot_id.strip():
            got = self.depot.get(depot_id.strip())
            if not got.get("success"):
                return {**got, "status": "error", "steps": steps}
            depot_entry = got["entry"]
            if depot_entry.get("kind") == KIND_VROID:
                vroid_path = depot_entry.get("path")
            elif depot_entry.get("kind") == KIND_VRM:
                vrm_path = depot_entry.get("path")

        if project_path.strip():
            proj = Path(project_path.strip())
            if not proj.is_file():
                return {"success": False, "status": "error", "message": f"Project not found: {project_path}"}
            if proj.suffix.lower() != ".vroid":
                return {
                    "success": False,
                    "status": "error",
                    "message": "project_path must be a .vroid VRoid Studio project file",
                }
            vroid_path = str(proj.resolve())
            reg = self.depot.register(
                vroid_path,
                kind=KIND_VROID,
                source=SOURCE_VROID_PROJECT,
                copy_into_depot=copy_to_depot,
            )
            if reg.get("success"):
                depot_entry = reg.get("entry")

        if not vrm_path and vrm_filename:
            staged = self._resolve_staged(vrm_filename)
            if staged:
                vrm_path = str(staged)

        if not vroid_path and not vrm_path:
            return {
                "success": False,
                "status": "error",
                "message": "Provide character_model_id, depot_id (vrm/vroid), project_path (.vroid), or staged vrm_filename",
                "steps": steps,
            }

        studio_result: dict[str, Any] | None = None
        if open_in_studio and vroid_path:
            if export_after:
                out = output_name or Path(vrm_filename or "hub_export.vrm").name
                studio_result = await call_vroid_tool(
                    "vroid_studio",
                    {
                        "operation": "open_and_export",
                        "project_path": vroid_path,
                        "output_name": out,
                    },
                )
            else:
                studio_result = await call_vroid_tool(
                    "vroid_studio",
                    {"operation": "open_project", "project_path": vroid_path},
                )
            steps.append({"step": "vroid_studio", **studio_result})
            if studio_result.get("export_path") and Path(studio_result["export_path"]).is_file():
                staged = self.staging_dir / Path(studio_result["export_path"]).name
                shutil.copy2(studio_result["export_path"], staged)
                vrm_path = str(staged)
                self.depot.register(
                    staged,
                    kind=KIND_VRM,
                    source=SOURCE_VROID_EXPORT,
                    name=staged.name,
                    copy_into_depot=copy_to_depot,
                )
        elif open_in_studio and vrm_path:
            studio_result = await call_vroid_tool("vroid_studio", {"operation": "launch"})
            steps.append({"step": "vroid_launch", **studio_result})
            await call_vroid_tool("vroid_studio", {"operation": "focus"})

        note = ""
        if vrm_path and not vroid_path:
            note = (
                "Hub/staged asset is VRM (runtime export). VRoid Studio edits native .vroid projects. "
                "Use blender_validate/blender_reexport for VRM mesh work, or create a new Studio project "
                "using the downloaded model as visual reference."
            )

        return {
            "success": True,
            "status": "success",
            "steps": steps,
            "vrm_path": vrm_path,
            "vroid_path": vroid_path,
            "depot_entry": depot_entry,
            "studio_result": studio_result,
            "editable_in_studio": bool(vroid_path),
            "note": note,
            "message": "hub_to_studio complete",
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
