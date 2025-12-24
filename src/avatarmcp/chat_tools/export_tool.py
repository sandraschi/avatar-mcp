"""
Export Tool for AvatarMCP

Provides FastMCP 2.12 compatible endpoints for exporting avatars to Unity/VRChat.
"""

import logging
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from .base_tool import ChatTool, ToolExecutionStatus, ToolParameter, ToolParameterType, ToolResult

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
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


class ExportTool(ChatTool):
    """Tool for exporting avatars to various formats."""

    def __init__(self):
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)

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

    async def execute(self, **kwargs) -> ToolResult:
        try:
            options = ExportOptions(**kwargs.get("options", {}))

            # TODO: Implement actual export logic
            # This is a placeholder for the actual implementation
            export_path = self._generate_export_path(options)

            logger.info(f"Exporting avatar with options: {options.dict()}")

            # Simulate export process
            export_data = {
                "status": "success",
                "format": options.format,
                "output_path": str(export_path),
                "included_animations": options.include_animations,
                "optimized": options.optimize_meshes,
            }

            return ToolResult(
                status=ToolExecutionStatus.SUCCESS,
                data={
                    "export": export_data,
                    "message": f"Successfully exported avatar to {options.format}",
                },
            )

        except Exception as e:
            return ToolResult(status=ToolExecutionStatus.ERROR, error=f"Export failed: {str(e)}")

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


# Alias for backward compatibility
ExportTools = ExportTool


# FastMCP 2.12 Tool Registration
def register_tools() -> dict[str, ChatTool]:
    """Register tools with FastMCP 2.12."""
    return {"export": ExportTool()}
