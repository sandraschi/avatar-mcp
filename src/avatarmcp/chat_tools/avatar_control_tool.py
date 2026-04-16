"""
Avatar control tool for the Avatar MCP chatbot.

This tool allows the chatbot to control the avatar's appearance and behavior.
"""

import asyncio
import logging

from .base_tool import (
    ChatTool,
    ToolParameter,
    ToolParameterType,
    ToolResult,
)

logger = logging.getLogger(__name__)


class AvatarControlTool(ChatTool):
    """Tool for controlling the avatar's appearance and behavior."""

    @property
    def name(self) -> str:
        return "control_avatar"

    @property
    def description(self) -> str:
        return "Control the avatar's appearance, expressions, and basic behaviors."

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type=ToolParameterType.STRING,
                description="The action to perform on the avatar",
                required=True,
                enum=[
                    "load",
                    "unload",
                    "show",
                    "hide",
                    "set_expression",
                    "reset_pose",
                    "set_visibility",
                    "set_scale",
                ],
            ),
            ToolParameter(
                name="avatar_id",
                type=ToolParameterType.STRING,
                description="ID of the avatar to control (required for load/unload)",
                required=False,
            ),
            ToolParameter(
                name="expression",
                type=ToolParameterType.STRING,
                description="Expression to set (e.g., 'happy', 'sad', 'neutral')",
                required=False,
            ),
            ToolParameter(
                name="intensity",
                type=ToolParameterType.NUMBER,
                description="Intensity of the expression (0.0 to 1.0)",
                required=False,
                min_value=0.0,
                max_value=1.0,
                default=1.0,
            ),
            ToolParameter(
                name="blend_time",
                type=ToolParameterType.NUMBER,
                description="Time in seconds to blend to the new state",
                required=False,
                min_value=0.0,
                default=0.2,
            ),
            ToolParameter(
                name="visible",
                type=ToolParameterType.BOOLEAN,
                description="Whether the avatar should be visible (for set_visibility action)",
                required=False,
            ),
            ToolParameter(
                name="scale",
                type=ToolParameterType.NUMBER,
                description="Scale factor for the avatar (for set_scale action)",
                required=False,
                min_value=0.1,
                default=1.0,
            ),
        ]

    async def execute(
        self,
        action: str,
        avatar_id: str | None = None,
        expression: str | None = None,
        intensity: float = 1.0,
        blend_time: float = 0.2,
        visible: bool | None = None,
        scale: float | None = None,
        **kwargs,
    ) -> ToolResult:
        """
        Control the avatar.

        Args:
            action: The action to perform (load, unload, show, hide, set_expression, etc.)
            avatar_id: ID of the avatar to control (required for load/unload)
            expression: Expression to set (for set_expression action)
            intensity: Intensity of the expression (0.0 to 1.0)
            blend_time: Time in seconds to blend to the new state
            visible: Whether the avatar should be visible (for set_visibility)
            scale: Scale factor for the avatar (for set_scale)

        Returns:
            ToolResult with the result of the operation
        """
        try:
            logger.info(f"Executing avatar control action: {action}")

            # Simulate processing time
            await asyncio.sleep(0.3)

            # In a real implementation, this would interact with the avatar system
            if action == "load":
                if not avatar_id:
                    return ToolResult.error("avatar_id is required for load action")
                return ToolResult.success(
                    content={
                        "status": "loaded",
                        "avatar_id": avatar_id,
                        "message": f"Successfully loaded avatar: {avatar_id}",
                    }
                )

            elif action == "unload":
                if not avatar_id:
                    return ToolResult.error("avatar_id is required for unload action")
                return ToolResult.success(
                    content={
                        "status": "unloaded",
                        "avatar_id": avatar_id,
                        "message": f"Successfully unloaded avatar: {avatar_id}",
                    }
                )

            elif action == "set_expression":
                if not expression:
                    return ToolResult.error("expression is required for set_expression action")
                return ToolResult.success(
                    content={
                        "status": "expression_set",
                        "expression": expression,
                        "intensity": intensity,
                        "blend_time": blend_time,
                        "message": f"Set expression to '{expression}' with intensity {intensity}",
                    }
                )

            elif action == "set_visibility":
                if visible is None:
                    return ToolResult.error("visible parameter is required for set_visibility action")
                return ToolResult.success(
                    content={
                        "status": "visibility_updated",
                        "visible": visible,
                        "message": f"Avatar visibility set to {visible}",
                    }
                )

            elif action == "set_scale":
                if scale is None:
                    return ToolResult.error("scale parameter is required for set_scale action")
                return ToolResult.success(
                    content={
                        "status": "scale_updated",
                        "scale": scale,
                        "message": f"Avatar scale set to {scale}",
                    }
                )

            elif action in ("show", "hide"):
                return ToolResult.success(
                    content={
                        "status": f"{action}n",
                        "visible": action == "show",
                        "message": f"Avatar is now {action}n",
                    }
                )

            elif action == "reset_pose":
                return ToolResult.success(
                    content={
                        "status": "pose_reset",
                        "message": "Avatar pose has been reset to default",
                    }
                )

            else:
                return ToolResult.error(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Error in avatar control: {e}", exc_info=True)
            return ToolResult.error(f"Failed to control avatar: {e!s}")


# Example usage:
# tool = AvatarControlTool()
# result = await tool.execute(
#     action="set_expression",
#     expression="happy",
#     intensity=0.8,
#     blend_time=0.3
# )
# logger.debug(json.dumps(result.to_dict(), indent=2))
