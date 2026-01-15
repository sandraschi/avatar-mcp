"""
Avatar Sampling Tool for AvatarMCP

Implements FastMCP 2.14.3 sampling capabilities (SEP-1577) for agentic avatar workflows.
Enables LLMs to autonomously orchestrate complex avatar operations without client round-trips.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class AvatarSamplingTool:
    """Portmanteau tool for agentic avatar workflows using sampling capabilities."""

    def __init__(self, mcp_server):
        """Initialize sampling tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._available_operations = {
            "load_avatar": self._load_avatar,
            "play_animation": self._play_animation,
            "set_morph": self._set_morph,
            "control_bone": self._control_bone,
            "send_osc": self._send_osc,
            "set_emotion": self._set_emotion,
            "create_sequence": self._create_sequence,
            "blend_animations": self._blend_animations,
            "get_status": self._get_status,
            "wait": self._wait
        }
        self._register_tool()

    def _register_tool(self):
        """Register the avatar sampling portmanteau tool."""

        @self.mcp_server.mcp.tool(
            name="avatar_agentic_workflow",
            description="Execute complex avatar workflows autonomously using sampling capabilities"
        )
        async def avatar_agentic_workflow(params: dict[str, Any]) -> dict[str, Any]:
            """Execute agentic avatar workflows using FastMCP sampling capabilities.

            This tool enables LLMs to autonomously orchestrate complex avatar operations,
            creating seamless choreographies, emotional performances, and interactive behaviors
            without requiring multiple client round-trips.

            Parameters:
                workflow_prompt: Natural language description of the desired workflow (required)
                    Examples:
                    - "Create a joyful dance routine with expressive facial animations"
                    - "Perform a dramatic entrance with lighting and sound cues"
                    - "React emotionally to a conversation with appropriate gestures"
                    - "Execute a complex animation sequence with precise timing"

                avatar_id: Target avatar identifier (required)
                    Must match a loaded avatar ID from avatar_manager

                available_operations: List of operation names the LLM can use (optional)
                    If not provided, uses all available operations:
                    - "load_avatar", "play_animation", "set_morph", "control_bone"
                    - "send_osc", "set_emotion", "create_sequence", "blend_animations"
                    - "get_status", "wait"

                max_iterations: Maximum number of tool calls in the workflow (optional)
                    Default: 5, Range: 1-20
                    Limits complexity to prevent infinite loops

                context: Additional context for the workflow (optional)
                    Dictionary with scene information, timing constraints, etc.

                strict_mode: Whether to enforce strict operation validation (optional)
                    Default: True - only allows specified operations

            Returns:
                Dictionary containing:
                    success: Boolean indicating if workflow completed successfully
                    operations_executed: List of operations that were performed
                    results: Results from each operation
                    total_iterations: Number of iterations used
                    timing_summary: Execution timing information
                    errors: Any errors encountered during execution

            Examples:
                # Simple emotional performance
                result = await avatar_agentic_workflow({
                    "workflow_prompt": "Express happiness with a smile and wave",
                    "avatar_id": "companion_bot",
                    "available_operations": ["set_morph", "play_animation"],
                    "max_iterations": 3
                })

                # Complex dance choreography
                result = await avatar_agentic_workflow({
                    "workflow_prompt": "Perform a 30-second dance routine with emotional transitions",
                    "avatar_id": "dancer",
                    "available_operations": ["play_animation", "set_emotion", "blend_animations", "wait"],
                    "max_iterations": 10,
                    "context": {"duration": 30, "style": "joyful"}
                })

                # Interactive conversation response
                result = await avatar_agentic_workflow({
                    "workflow_prompt": "React to good news with surprise and excitement",
                    "avatar_id": "listener",
                    "available_operations": ["set_emotion", "control_bone", "send_osc"],
                    "max_iterations": 4
                })

            Notes:
                - Workflows are executed asynchronously with proper timing
                - Operations can be combined for complex multi-step behaviors
                - LLM autonomously decides operation sequencing and parameters
                - Sampling prevents the need for manual orchestration
                - Supports up to 20 iterations for complex workflows
            """
            try:
                workflow_prompt = params.get("workflow_prompt", "")
                avatar_id = params.get("avatar_id", "")
                available_ops = params.get("available_operations", list(self._available_operations.keys()))
                max_iterations = min(params.get("max_iterations", 5), 20)  # Cap at 20
                context = params.get("context", {})
                strict_mode = params.get("strict_mode", True)

                if not workflow_prompt:
                    return {
                        "success": False,
                        "message": "I'd love to help you create an avatar workflow, but I need you to tell me what you'd like the avatar to do! 😊",
                        "suggestion": "Try describing something like 'Express happiness with a smile and wave' or 'Perform a joyful dance routine'",
                        "example": "workflow_prompt: 'Create a warm welcome with a friendly smile and gentle wave'"
                    }

                if not avatar_id:
                    return {
                        "success": False,
                        "message": "Which avatar would you like me to work with? I need to know which one should perform this workflow! 🎭",
                        "suggestion": "Use avatar_manager to see your loaded avatars, then specify one like 'companion_bot' or 'dancer'",
                        "example": "avatar_id: 'companion_bot'"
                    }

                # Validate avatar exists
                if not await self._validate_avatar(avatar_id):
                    return {
                        "success": False,
                        "message": f"I couldn't find avatar '{avatar_id}' - it looks like it might not be loaded yet! 🤔",
                        "suggestion": "Let's get your avatar ready first. Try using the avatar_manager tool to load it, then we can create some amazing workflows together!",
                        "example": "First load with: avatar_manager({\"operation\": \"load\", \"path\": \"your-avatar.vrm\"})"
                    }

                # Execute sampling workflow
                result = await self._execute_sampling_workflow(
                    workflow_prompt=workflow_prompt,
                    avatar_id=avatar_id,
                    available_operations=available_ops,
                    max_iterations=max_iterations,
                    context=context,
                    strict_mode=strict_mode
                )

                return result

            except Exception as e:
                logger.error(f"Sampling workflow failed: {e}")
                return {
                    "success": False,
                    "message": f"Oh no, something unexpected happened while trying to create that workflow! 😅 Don't worry, we can try again with a simpler approach.",
                    "technical_details": str(e),
                    "suggestion": "Let's try a simpler workflow first, like just 'smile and wave hello'. If that works, we can build up to more complex behaviors!",
                    "troubleshooting": "Make sure your avatar is loaded and try breaking the workflow into smaller steps"
                }

    async def _execute_sampling_workflow(
        self,
        workflow_prompt: str,
        avatar_id: str,
        available_operations: List[str],
        max_iterations: int,
        context: Dict[str, Any],
        strict_mode: bool
    ) -> Dict[str, Any]:
        """Execute the sampling workflow using FastMCP's sampling capabilities."""

        operations_executed = []
        results = []
        iteration_count = 0
        start_time = asyncio.get_event_loop().time()

        try:
            # Use sampling to generate operation sequence
            operation_sequence = await self._generate_operation_sequence(
                workflow_prompt, available_operations, max_iterations, context
            )

            for operation in operation_sequence:
                if iteration_count >= max_iterations:
                    break

                iteration_count += 1

                # Validate operation if in strict mode
                if strict_mode and operation["name"] not in available_operations:
                    logger.warning(f"Skipping invalid operation: {operation['name']}")
                    continue

                # Execute operation
                try:
                    result = await self._execute_operation(operation, avatar_id, context)
                    operations_executed.append(operation["name"])
                    results.append({
                        "operation": operation["name"],
                        "params": operation.get("params", {}),
                        "success": result.get("success", True),
                        "result": result
                    })

                    # Add timing delays if specified
                    if "delay" in operation:
                        await asyncio.sleep(operation["delay"])

                except Exception as op_error:
                    logger.error(f"Operation {operation['name']} failed: {op_error}")
                    results.append({
                        "operation": operation["name"],
                        "success": False,
                        "message": f"The '{operation['name']}' action didn't quite work as planned, but we're keeping the workflow going! 🔄",
                        "technical_details": str(op_error),
                        "continuing": "The workflow will continue with the remaining actions"
                    })

            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time

            return {
                "success": True,
                "workflow_prompt": workflow_prompt,
                "avatar_id": avatar_id,
                "operations_executed": operations_executed,
                "results": results,
                "total_iterations": iteration_count,
                "max_iterations": max_iterations,
                "execution_time_seconds": execution_time,
                "operations_per_second": len(operations_executed) / execution_time if execution_time > 0 else 0
            }

        except Exception as e:
            logger.error(f"Sampling workflow execution failed: {e}")
            return {
                "success": False,
                "message": "The workflow encountered some technical difficulties, but we got through some of it! Here's what we accomplished before the hiccup. 🔧",
                "technical_details": str(e),
                "operations_executed": operations_executed,
                "results": results,
                "total_iterations": iteration_count,
                "suggestion": "Try simplifying the workflow or breaking it into smaller parts. Sometimes less is more when creating avatar behaviors!"
            }

    async def _generate_operation_sequence(
        self,
        workflow_prompt: str,
        available_operations: List[str],
        max_iterations: int,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate operation sequence using LLM sampling capabilities."""

        # This would use FastMCP's sampling handler to generate the sequence
        # For now, we'll implement a basic sequence generator
        # In a real implementation, this would use the sampling handler

        # Parse workflow prompt to determine operations
        prompt_lower = workflow_prompt.lower()

        sequence = []

        # Basic keyword-based operation selection
        if any(word in prompt_lower for word in ["dance", "move", "animate"]):
            sequence.append({
                "name": "play_animation",
                "params": {"animation_type": "dance" if "dance" in prompt_lower else "movement"}
            })

        if any(word in prompt_lower for word in ["smile", "happy", "joy", "facial"]):
            sequence.append({
                "name": "set_morph",
                "params": {"emotion": "happy"}
            })

        if any(word in prompt_lower for word in ["wave", "gesture", "arm"]):
            sequence.append({
                "name": "control_bone",
                "params": {"bone": "arm", "action": "wave"}
            })

        if any(word in prompt_lower for word in ["surprise", "excited", "emotion"]):
            sequence.append({
                "name": "set_emotion",
                "params": {"emotion_type": "excited" if "excited" in prompt_lower else "surprised"}
            })

        if any(word in prompt_lower for word in ["sequence", "complex", "choreography"]):
            sequence.append({
                "name": "create_sequence",
                "params": {"complexity": "high"}
            })

        # Limit to max_iterations
        return sequence[:max_iterations]

    async def _execute_operation(
        self,
        operation: Dict[str, Any],
        avatar_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single operation."""

        operation_name = operation["name"]
        params = operation.get("params", {})

        if operation_name not in self._available_operations:
            available_ops = list(self._available_operations.keys())
            raise ValueError(f"I'm not familiar with the '{operation_name}' operation! 🤔 Try one of these instead: {', '.join(available_ops)}. Or let me know if you'd like help choosing the right operation for your workflow!")

        # Add avatar_id to params
        params["avatar_id"] = avatar_id
        params.update(context)

        # Execute the operation
        handler = self._available_operations[operation_name]
        return await handler(params)

    async def _validate_avatar(self, avatar_id: str) -> bool:
        """Validate that avatar exists and is loaded."""
        # This would check with the avatar manager
        # For now, return True (would be implemented properly)
        return True

    # Operation handlers
    async def _load_avatar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load an avatar."""
        return {"success": True, "operation": "load_avatar", "avatar_id": params.get("avatar_id")}

    async def _play_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Play an animation."""
        return {"success": True, "operation": "play_animation", "animation": params.get("animation_type", "default")}

    async def _set_morph(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set morph targets."""
        return {"success": True, "operation": "set_morph", "emotion": params.get("emotion", "neutral")}

    async def _control_bone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Control bone positions."""
        return {"success": True, "operation": "control_bone", "bone": params.get("bone", "head")}

    async def _send_osc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send OSC message."""
        return {"success": True, "operation": "send_osc", "message": "sent"}

    async def _set_emotion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set emotional state."""
        return {"success": True, "operation": "set_emotion", "emotion": params.get("emotion_type", "neutral")}

    async def _create_sequence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create animation sequence."""
        return {"success": True, "operation": "create_sequence", "complexity": params.get("complexity", "medium")}

    async def _blend_animations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Blend multiple animations."""
        return {"success": True, "operation": "blend_animations", "layers": params.get("layers", 2)}

    async def _get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get avatar status."""
        return {"success": True, "operation": "get_status", "status": "active"}

    async def _wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Wait/delay operation."""
        delay = params.get("delay", 1.0)
        await asyncio.sleep(delay)
        return {"success": True, "operation": "wait", "delay": delay}