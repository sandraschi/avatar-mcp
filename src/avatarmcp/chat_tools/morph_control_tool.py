"""
Morph Target Control Tool for AvatarMCP

Provides FastMCP 2.12 compatible endpoints for morph target control.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from pydantic import BaseModel, Field, validator
from .base_tool import ChatTool, ToolResult, ToolParameter, ToolParameterType, ToolExecutionStatus

logger = logging.getLogger(__name__)

class MorphTargetValue(BaseModel):
    """Morph target value definition."""
    name: str = Field(..., description="Name of the morph target")
    weight: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Weight value between 0.0 and 1.0"
    )

class MorphControlTool(ChatTool):
    """Tool for controlling morph targets through FastMCP 2.12 compatible API."""
    
    @property
    def name(self) -> str:
        return "control_morph"
    
    @property
    def description(self) -> str:
        return "Control avatar morph targets (blendshapes)"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="targets",
                type=ToolParameterType.ARRAY,
                description="List of morph targets to update",
                required=True,
                items={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "weight": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    },
                    "required": ["name", "weight"]
                }
            ),
            ToolParameter(
                name="reset_others",
                type=ToolParameterType.BOOLEAN,
                description="Reset other morph targets to zero",
                required=False,
                default=False
            )
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            targets = kwargs.get("targets", [])
            reset_others = kwargs.get("reset_others", False)
            
            # Validate targets
            morph_targets = [MorphTargetValue(**t) for t in targets]
            
            # TODO: Implement actual morph target control logic
            logger.info(f"Updating morph targets: {morph_targets}, reset_others: {reset_others}")
            
            return ToolResult(
                status=ToolExecutionStatus.SUCCESS,
                data={
                    "updated_targets": [t.dict() for t in morph_targets],
                    "reset_others": reset_others,
                    "message": f"Updated {len(morph_targets)} morph targets"
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolExecutionStatus.ERROR,
                error=f"Failed to update morph targets: {str(e)}"
            )

# FastMCP 2.12 Tool Registration
def register_tools():
    """Register tools with FastMCP 2.12."""
    return {
        "morph_control": MorphControlTool()
    }
