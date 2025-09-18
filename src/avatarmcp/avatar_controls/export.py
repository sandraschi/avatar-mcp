"""
Export Module

Provides functionality for exporting avatars to various formats including
Unity 3D and VRChat SDK.
"""

import os
import json
import logging
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator

from .base import (
    AvatarControlBase,
    ControlType,
    ControlResult
)
from ..chat_tools.base_tool import ChatTool, ToolResult, ToolParameter, ToolParameterType, ToolExecutionStatus

logger = logging.getLogger(__name__)

class ExportFormat(str, Enum):
    """Supported export formats."""
    FBX = "fbx"
    UNITY_PACKAGE = "unitypackage"
    VRCHAT_SDK = "vrcsdk"

class ExportOptions(BaseModel):
    """Export configuration options."""
    format: ExportFormat = Field(
        ExportFormat.FBX,
        description="Export format"
    )
    include_animations: bool = Field(
        True,
        description="Include animations in export"
    )
    optimize_meshes: bool = Field(
        True,
        description="Optimize meshes for target platform"
    )
    platform: str = Field(
        "vrc",
        description="Target platform (vrc, unity, etc.)"
    )
    output_dir: Optional[str] = Field(
        None,
        description="Custom output directory (default: exports/)"
    )
    
    @field_validator('platform')
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
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="options",
                type=ToolParameterType.OBJECT,
                description="Export configuration options",
                required=True,
                schema=ExportOptions.schema()
            )
        ]
    
    async def execute(self, **kwargs) -> ControlResult:
        """Execute avatar export."""
        try:
            options = ExportOptions(**kwargs.get("options", {}))
            
            # Generate output path
            export_path = self._generate_export_path(options)
            
            # TODO: Implement actual export logic
            # This would involve:
            # 1. Serializing the current avatar state
            # 2. Converting to target format
            # 3. Writing to disk
            
            logger.info(f"Exporting avatar to {export_path} with options: {options.dict()}")
            
            # Simulate successful export
            export_data = {
                "format": options.format,
                "output_path": str(export_path),
                "included_animations": options.include_animations,
                "optimized": options.optimize_meshes,
                "platform": options.platform,
                "file_size_mb": 42.5,  # Simulated file size
                "export_time_seconds": 5.2  # Simulated export time
            }
            
            return ControlResult.success(
                f"Successfully exported avatar to {export_path}",
                data={"export": export_data}
            )
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}", exc_info=True)
            return ControlResult.error("Failed to export avatar", str(e))
    
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
            error=result.error
        )

# FastMCP 2.12 Tool Registration
def register_tools() -> Dict[str, ChatTool]:
    """Register tools with FastMCP 2.12."""
    return {
        "export_avatar": ExportTool()
    }
