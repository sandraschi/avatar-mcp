"""
Animation control tool for the Avatar MCP chatbot.

This tool allows the chatbot to control avatar animations.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Literal

from .base_tool import (
    ChatTool,
    ToolResult,
    ToolParameter,
    ToolParameterType,
    ToolExecutionStatus,
)

logger = logging.getLogger(__name__)

class AnimationControlTool(ChatTool):
    """Tool for controlling avatar animations."""
    
    @property
    def name(self) -> str:
        return "control_animation"
    
    @property
    def description(self) -> str:
        return "Control avatar animations, including playing, stopping, and blending between animations."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type=ToolParameterType.STRING,
                description="The action to perform on the animation",
                required=True,
                enum=["play", "stop", "pause", "resume", "blend"]
            ),
            ToolParameter(
                name="animation_name",
                type=ToolParameterType.STRING,
                description="Name or ID of the animation to play (required for play/blend actions)",
                required=False
            ),
            ToolParameter(
                name="loop",
                type=ToolParameterType.BOOLEAN,
                description="Whether to loop the animation (for play/blend actions)",
                required=False,
                default=False
            ),
            ToolParameter(
                name="speed",
                type=ToolParameterType.NUMBER,
                description="Playback speed multiplier (0.1 to 5.0)",
                required=False,
                min_value=0.1,
                max_value=5.0,
                default=1.0
            ),
            ToolParameter(
                name="blend_time",
                type=ToolParameterType.NUMBER,
                description="Time in seconds to blend between animations (for play/blend actions)",
                required=False,
                min_value=0.0,
                default=0.2
            ),
            ToolParameter(
                name="weight",
                type=ToolParameterType.NUMBER,
                description="Blend weight (0.0 to 1.0, for blend action)",
                required=False,
                min_value=0.0,
                max_value=1.0,
                default=1.0
            ),
            ToolParameter(
                name="layer",
                type=ToolParameterType.INTEGER,
                description="Animation layer (for layered animations)",
                required=False,
                min_value=0,
                default=0
            )
        ]
    
    async def execute(
        self,
        action: str,
        animation_name: Optional[str] = None,
        loop: bool = False,
        speed: float = 1.0,
        blend_time: float = 0.2,
        weight: float = 1.0,
        layer: int = 0,
        **kwargs
    ) -> ToolResult:
        """
        Control avatar animations.
        
        Args:
            action: The action to perform (play, stop, pause, resume, blend)
            animation_name: Name or ID of the animation (required for play/blend)
            loop: Whether to loop the animation
            speed: Playback speed multiplier
            blend_time: Time in seconds to blend between animations
            weight: Blend weight (0.0 to 1.0)
            layer: Animation layer (for layered animations)
            
        Returns:
            ToolResult with the result of the operation
        """
        try:
            logger.info(f"Executing animation control action: {action}")
            
            # Simulate processing time
            await asyncio.sleep(0.2)
            
            # In a real implementation, this would interact with the animation system
            if action == "play":
                if not animation_name:
                    return ToolResult.error("animation_name is required for play action")
                
                return ToolResult.success(
                    content={
                        "status": "playing",
                        "animation": animation_name,
                        "loop": loop,
                        "speed": speed,
                        "blend_time": blend_time,
                        "layer": layer,
                        "message": f"Playing animation '{animation_name}'"
                    }
                )
                
            elif action == "stop":
                return ToolResult.success(
                    content={
                        "status": "stopped",
                        "blend_time": blend_time,
                        "message": "Stopped all animations"
                    }
                )
                
            elif action == "pause":
                return ToolResult.success(
                    content={
                        "status": "paused",
                        "message": "Paused current animation"
                    }
                )
                
            elif action == "resume":
                return ToolResult.success(
                    content={
                        "status": "resumed",
                        "message": "Resumed current animation"
                    }
                )
                
            elif action == "blend":
                if not animation_name:
                    return ToolResult.error("animation_name is required for blend action")
                    
                return ToolResult.success(
                    content={
                        "status": "blending",
                        "animation": animation_name,
                        "weight": weight,
                        "blend_time": blend_time,
                        "layer": layer,
                        "message": f"Blending to animation '{animation_name}' with weight {weight}"
                    }
                )
                
            else:
                return ToolResult.error(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error in animation control: {e}", exc_info=True)
            return ToolResult.error(f"Failed to control animation: {str(e)}")

# Example usage:
# tool = AnimationControlTool()
# result = await tool.execute(
#     action="play",
#     animation_name="wave_hand",
#     loop=False,
#     speed=1.2,
#     blend_time=0.3
# )
# logger.debug(json.dumps(result.to_dict(), indent=2))
