"""Bone Control Module

Provides functionality for direct bone manipulation in avatars.
"""

import logging

from pydantic import Field

from ..chat_tools.base_tool import (
    ChatTool,
    ToolExecutionStatus,
    ToolParameter,
    ToolParameterType,
    ToolResult,
)
from .base import AvatarControlBase, ControlResult, ControlSpace, ControlType, Transform

logger = logging.getLogger(__name__)


class BoneTransform(Transform):
    """Bone-specific transform with additional properties."""

    bone_name: str = Field(..., description="Name of the bone to transform")
    space: ControlSpace = Field(ControlSpace.LOCAL, description="Coordinate space for the transform")


class BoneControlTool(AvatarControlBase, ChatTool):
    """Tool for controlling avatar bones with FastMCP 2.12 compatibility."""

    def __init__(self):
        self._bone_transforms: dict[str, Transform] = {}

    @property
    def control_type(self) -> ControlType:
        return ControlType.BONE

    @property
    def name(self) -> str:
        return "control_bone"

    @property
    def description(self) -> str:
        return "Control individual avatar bones with transformations"

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="bone_name",
                type=ToolParameterType.STRING,
                description="Name of the bone to transform",
                required=True,
            ),
            ToolParameter(
                name="transform",
                type=ToolParameterType.OBJECT,
                description="Transform data for the bone",
                required=True,
                schema=Transform.schema(),
            ),
        ]

    async def execute(self, **kwargs) -> ControlResult:
        """Execute bone transformation."""
        try:
            bone_name = kwargs.get("bone_name")
            transform_data = kwargs.get("transform", {})

            # Validate input
            if not bone_name:
                return ControlResult.error("Bone name is required")

            transform = Transform(**transform_data)
            self._bone_transforms[bone_name] = transform

            # TODO: Implement actual bone transformation logic
            logger.info(f"Transforming bone {bone_name}: {transform.dict()}")

            return ControlResult.success(
                f"Successfully transformed bone: {bone_name}",
                data={"bone": bone_name, "transform": transform.dict(), "space": transform.space},
            )

        except Exception as e:
            logger.error(f"Bone transform failed: {e!s}", exc_info=True)
            return ControlResult.error("Failed to transform bone", str(e))

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
    return {"bone_control": BoneControlTool()}
