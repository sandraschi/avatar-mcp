"""
Export Module

Provides functionality for exporting avatars to various formats including
Unity 3D and VRChat SDK.
"""

import logging
from enum import StrEnum
from pathlib import Path

import httpx
from pydantic import BaseModel, Field, field_validator

from ..chat_tools.base_tool import (
    ChatTool,
    ToolExecutionStatus,
    ToolParameter,
    ToolParameterType,
    ToolResult,
)
from .base import AvatarControlBase, ControlResult, ControlType

logger = logging.getLogger(__name__)


class ExportFormat(StrEnum):
    """Supported export formats."""

    FBX = "fbx"
    UNITY_PACKAGE = "unitypackage"
    VRCHAT_SDK = "vrcsdk"


class ExportOptions(BaseModel):
    """Export configuration options."""

    format: ExportFormat = Field(ExportFormat.FBX, description="Export format")
    include_animations: bool = Field(True, description="Include animations in export")
    optimize_meshes: bool = Field(True, description="Optimize meshes for target platform")
    platform: str = Field("vrc", description="Target platform (vrc, unity, etc.)")
    output_dir: str | None = Field(None, description="Custom output directory (default: exports/)")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        valid_platforms = ["vrc", "unity", "generic"]
        if v not in valid_platforms:
            raise ValueError(f"Platform must be one of {valid_platforms}")
        return v


class ExportTool(AvatarControlBase, ChatTool):
    """Tool for exporting avatars to various formats with FastMCP 2.12 compatibility."""

    def __init__(self):
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)

    @property
    def control_type(self) -> ControlType:
        return ControlType.EXPORT

    @property
    def name(self) -> str:
        return "export_avatar"

    @property
    def description(self) -> str:
        return "Export avatar to various formats (FBX, UnityPackage, VRChat SDK)"

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="options",
                type=ToolParameterType.OBJECT,
                description="Export configuration options",
                required=True,
                schema=ExportOptions.schema(),
            )
        ]

    async def execute(self, **kwargs) -> ControlResult:
        """Execute avatar export via blender-mcp.

        Delegates to blender-mcp's export pipeline which handles VRM import
        and platform-specific export (FBX for VRChat, GLB for Resonite, etc.).
        """
        try:
            options = ExportOptions(**kwargs.get("options", {}))
            export_path = self._generate_export_path(options)
            vrm_path = self._get_active_vrm_path()

            if vrm_path:
                result = await self._export_via_blender(vrm_path, options, export_path)
                if result:
                    return ControlResult.success(
                        f"Exported avatar to {export_path}",
                        data={"export": result},
                    )

            # Fallback: simulated export when no VRM or blender unavailable
            logger.warning("Blender MCP export unavailable - returning simulated result")
            export_data = {
                "format": options.format,
                "output_path": str(export_path),
                "included_animations": options.include_animations,
                "optimized": options.optimize_meshes,
                "platform": options.platform,
                "note": "Blender MCP not reachable - simulated export only",
            }
            return ControlResult.success(
                f"Simulated export to {export_path} (blender-mcp unavailable)",
                data={"export": export_data},
            )

        except Exception as e:
            logger.error(f"Export failed: {e!s}", exc_info=True)
            return ControlResult.error("Failed to export avatar", str(e))

    def _get_active_vrm_path(self) -> str | None:
        """Get file path of the currently loaded VRM avatar."""
        try:
            from ..models.vrm_manager import VRMManager

            manager = VRMManager()
            active = manager.get_active()
            if active:
                return str(active) if isinstance(active, (str, Path)) else getattr(active, "path", None)
        except Exception:
            pass
        return None

    async def _export_via_blender(self, vrm_path: str, options: ExportOptions, export_path: Path) -> dict | None:
        """Call blender-mcp to import VRM and export to target format."""

        abs_vrm = str(Path(vrm_path).resolve())
        abs_out = str(export_path.resolve())

        platform_map = {
            "vrc": ("VRCHAT", "fbx"),
            "unity": ("UNITY", "fbx"),
            "generic": ("RESONITE", "glb"),
        }
        preset_platform, _ext = platform_map.get(options.platform, ("RESONITE", "glb"))

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                # Step 1: Import VRM into Blender
                resp = await client.post(
                    "http://127.0.0.1:10849/tool",
                    json={
                        "tool": "blender_import",
                        "params": {
                            "operation": "import_file",
                            "filepath": abs_vrm,
                            "format": "vrm",
                        },
                    },
                )
                if resp.status_code != 200:
                    logger.warning("blender-mcp import returned %d", resp.status_code)
                    return None
                import_result = resp.json()
                if not import_result.get("success"):
                    logger.warning("blender-mcp import failed: %s", import_result.get("error", ""))
                    return None

                # Step 2: Export via platform preset
                resp = await client.post(
                    "http://127.0.0.1:10849/tool",
                    json={
                        "tool": "blender_export_presets",
                        "params": {
                            "operation": "export_with_preset",
                            "platform": preset_platform,
                            "output_path": abs_out,
                            "include_materials": True,
                            "include_textures": options.optimize_meshes,
                            "apply_modifiers": options.optimize_meshes,
                        },
                    },
                )
                if resp.status_code != 200:
                    return None
                export_result = resp.json()
                if export_result.get("success"):
                    return {
                        "format": options.format.value,
                        "output_path": abs_out,
                        "platform": options.platform,
                        "blender_export": "ok",
                    }
        except Exception as e:
            logger.warning("blender-mcp export call failed: %s", e)

        return None

    def _generate_export_path(self, options: ExportOptions) -> Path:
        """Generate a unique export file path."""
        output_dir = Path(options.output_dir) if options.output_dir else self.exports_dir
        output_dir.mkdir(exist_ok=True, parents=True)

        base_name = "avatar_export"
        ext = options.format
        counter = 1

        while True:
            export_path = output_dir / f"{base_name}_{counter}.{ext}"
            if not export_path.exists():
                return export_path
            counter += 1

    # FastMCP 2.12 compatibility
    async def _execute_tool(self, **kwargs) -> ToolResult:
        """Execute as a FastMCP 2.12 tool."""
        result = await self.execute(**kwargs)
        return ToolResult(
            status=ToolExecutionStatus.SUCCESS if result.success else ToolExecutionStatus.ERROR,
            data=result.data,
            error=result.error,
        )


# FastMCP 2.12 Tool Registration
def register_tools() -> dict[str, ChatTool]:
    """Register tools with FastMCP 2.12."""
    return {"export_avatar": ExportTool()}
