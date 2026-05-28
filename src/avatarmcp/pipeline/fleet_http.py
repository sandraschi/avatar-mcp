"""Cross-fleet HTTP helpers for avatar creative pipeline."""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BLENDER_URL = os.environ.get("BLENDER_MCP_URL", "http://127.0.0.1:10849")
DEFAULT_VROID_URL = os.environ.get("VROIDSTUDIO_MCP_URL", "http://127.0.0.1:10881")


async def call_fleet_tool(
    base_url: str,
    tool: str,
    arguments: dict[str, Any] | None = None,
    *,
    path: str = "/api/v1/control/tool",
    timeout: float = 300.0,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + path
    payload = {"tool": tool, "arguments": arguments or {}}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.warning("Fleet tool call failed base=%s tool=%s error=%s", base_url, tool, exc)
        return {"success": False, "error": str(exc), "tool": tool}

    if isinstance(body, dict):
        if "success" not in body:
            return {**body, "success": True}
        return body
    return {"success": False, "error": "Invalid response", "tool": tool}


async def call_blender_tool(tool: str, params: dict[str, Any] | None = None, *, timeout: float = 300.0) -> dict[str, Any]:
    url = DEFAULT_BLENDER_URL.rstrip("/") + "/tool"
    payload = {"tool": tool, "params": params or {}}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc), "tool": tool}
    if isinstance(body, dict):
        if body.get("success") is False:
            return body
        if "success" not in body:
            return {**body, "success": True}
        return body
    return {"success": False, "error": "Invalid blender response", "tool": tool}


async def call_vroid_tool(tool: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    return await call_fleet_tool(DEFAULT_VROID_URL, tool, arguments)


def parse_json_tool_result(raw: dict[str, Any]) -> dict[str, Any]:
    data = raw.get("data")
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {"output": data}
    if isinstance(data, dict):
        return data
    return raw


async def blender_validate_vrm(vrm_path: str) -> dict[str, Any]:
    script = f"""
import bpy, json
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
try:
    bpy.ops.import_scene.vrm(filepath=r"{vrm_path.replace(chr(92), '/')}")
except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
    raise SystemExit(0)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
print(json.dumps({{
    "success": True,
    "meshes": len(meshes),
    "armatures": len(armatures),
    "objects": [o.name for o in bpy.data.objects],
    "vrm_path": r"{vrm_path.replace(chr(92), '/')}",
}}))
"""
    result = await call_blender_tool("script_execute", {"code": script}, timeout=180)
    if not result.get("success"):
        return result
    payload = parse_json_tool_result(result)
    return payload if isinstance(payload, dict) else {"success": True, "raw": payload}


async def blender_reexport_vrm(vrm_path: str, output_path: str) -> dict[str, Any]:
    src = vrm_path.replace("\\", "/")
    out = output_path.replace("\\", "/")
    script = f"""
import bpy, json, os
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.vrm(filepath=r"{src}")
bpy.ops.object.select_all(action='SELECT')
os.makedirs(os.path.dirname(r"{out}") or ".", exist_ok=True)
bpy.ops.export_scene.vrm(filepath=r"{out}")
print(json.dumps({{"success": True, "export_path": r"{out}"}}))
"""
    result = await call_blender_tool("script_execute", {"code": script}, timeout=240)
    if not result.get("success"):
        return result
    if Path(output_path).is_file():
        return {
            "success": True,
            "source": src,
            "export_path": output_path,
            "size_kb": round(Path(output_path).stat().st_size / 1024, 1),
        }
    return {"success": False, "error": "Re-export file missing", "blender": result}


def stage_vrm_for_vts(vrm_path: str, staging_dir: Path, *, label: str = "pipeline_avatar") -> dict[str, Any]:
    src = Path(vrm_path)
    if not src.is_file():
        return {"success": False, "error": f"VRM not found: {vrm_path}"}
    staging_dir.mkdir(parents=True, exist_ok=True)
    dest = staging_dir / src.name
    shutil.copy2(src, dest)
    manifest = {
        "label": label,
        "vrm_file": dest.name,
        "vts_hint": "Load via VTube Studio UI or pyvts",
        "vts_api": "ws://localhost:8001",
    }
    manifest_path = staging_dir / f"{dest.stem}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {
        "success": True,
        "staged_path": str(dest),
        "manifest": str(manifest_path),
        "size_kb": round(dest.stat().st_size / 1024, 1),
    }
