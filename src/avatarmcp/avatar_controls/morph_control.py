"""
Morph Control Module

Provides functionality for controlling morph targets (blendshapes) in avatars.
"""

import logging
from typing import Dict, List
from pydantic import BaseModel, Field, field_validator

from .base import (
    AvatarControlBase,
    ControlType,
    ControlResult
)
from ..chat_tools.base_tool import ChatTool, ToolResult, ToolParameter, ToolParameterType, ToolExecutionStatus

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
    
    @field_validator('weight')
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")
        return v

class MorphTargetUpdate(BaseModel):
    """Update for a single morph target."""
    name: str = Field(..., description="Name of the morph target")
    weight: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Weight value between 0.0 and 1.0"
    )

class MorphControlTool(AvatarControlBase, ChatTool):
    """Tool for controlling morph targets with FastMCP 2.12 compatibility."""
    
    def __init__(self):
        self._morph_weights: Dict[str, float] = {}
    
    @property
    def control_type(self) -> ControlType:
        return ControlType.MORPH
    
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
    
    async def execute(self, **kwargs) -> ControlResult:
        """Execute morph target updates."""
        try:
            targets = kwargs.get("targets", [])
            reset_others = kwargs.get("reset_others", False)
            
            # Validate and update morph targets
            updated_targets = []
            for target in targets:
                morph = MorphTargetValue(**target)
                self._morph_weights[morph.name] = morph.weight
                updated_targets.append(morph.dict())
            
            if reset_others:
                # Reset all non-specified morphs to zero
                for name in list(self._morph_weights.keys()):
                    if name not in [t["name"] for t in targets]:
                        self._morph_weights[name] = 0.0
            
            # TODO: Implement actual morph target updates
            logger.info(f"Updated morph targets: {self._morph_weights}")
            
            return ControlResult.success(
                f"Updated {len(updated_targets)} morph targets",
                data={
                    "updated_targets": updated_targets,
                    "reset_others": reset_others,
                    "total_active_morphs": len([w for w in self._morph_weights.values() if w > 0])
                }
            )
            
        except Exception as e:
            logger.error(f"Morph target update failed: {str(e)}", exc_info=True)
            return ControlResult.error("Failed to update morph targets", str(e))
    
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
        "morph_control": MorphControlTool()
    }
