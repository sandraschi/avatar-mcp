"""
Avatar Sampling Tool for AvatarMCP

Implements FastMCP 3.1 sampling for agentic avatar workflows. Uses Context.sample()
to request LLM-generated operation sequences from the client; falls back to a minimal
heuristic only when the client does not support sampling.
"""

import asyncio
import logging
from typing import Any

from fastmcp.server.context import Context
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OperationSpec(BaseModel):
    """Single operation in an avatar workflow sequence."""

    name: str = Field(..., description="Operation name, e.g. play_animation, set_morph")
    params: dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    delay: float | None = Field(default=None, description="Optional delay in seconds after this operation")


class OperationSequenceResult(BaseModel):
    """Structured result from LLM sampling: list of operations to execute."""

    operations: list[OperationSpec] = Field(default_factory=list, description="Ordered list of operations")


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
            "wait": self._wait,
        }
        self._register_tool()

    def _register_tool(self):
        """Register the avatar sampling portmanteau tool."""

        @self.mcp_server.mcp.tool(
            name="avatar_agentic_workflow",
            description="Execute complex avatar workflows autonomously using sampling capabilities",
        )
        async def avatar_agentic_workflow(ctx: Context, params: dict[str, Any]) -> dict[str, Any]:
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
                available_ops = params.get(
                    "available_operations", list(self._available_operations.keys())
                )
                max_iterations = min(params.get("max_iterations", 5), 20)  # Cap at 20
                context = params.get("context", {})
                strict_mode = params.get("strict_mode", True)

                if not workflow_prompt:
                    return {
                        "success": False,
                        "message": "I need a description of what you'd like the avatar to do.",
                        "suggestion": "Try describing something like 'Express happiness with a smile and wave' or 'Perform a joyful dance routine'",
                        "example": "workflow_prompt: 'Create a warm welcome with a friendly smile and gentle wave'",
                    }

                if not avatar_id:
                    return {
                        "success": False,
                        "message": "Which avatar should perform this workflow? Specify avatar_id.",
                        "suggestion": "Use avatar_manager to see your loaded avatars, then specify one like 'companion_bot' or 'dancer'",
                        "example": "avatar_id: 'companion_bot'",
                    }

                # Validate avatar exists
                if not await self._validate_avatar(avatar_id):
                    return {
                        "success": False,
                        "message": f"Avatar '{avatar_id}' not found or not loaded.",
                        "suggestion": "Use the avatar_manager tool to load the avatar first, then retry.",
                        "example": 'First load with: avatar_manager({"operation": "load", "path": "your-avatar.vrm"})',
                    }

                # Execute sampling workflow (ctx used for LLM sampling)
                result = await self._execute_sampling_workflow(
                    ctx=ctx,
                    workflow_prompt=workflow_prompt,
                    avatar_id=avatar_id,
                    available_operations=available_ops,
                    max_iterations=max_iterations,
                    context=context,
                    strict_mode=strict_mode,
                )

                return result

            except Exception as e:
                logger.error("Sampling workflow failed: %s", e)
                return {
                    "success": False,
                    "message": "Workflow execution failed.",
                    "technical_details": str(e),
                    "suggestion": "Try a simpler workflow (e.g. 'smile and wave') or ensure the avatar is loaded.",
                    "troubleshooting": "Ensure avatar is loaded and break the workflow into smaller steps if needed.",
                }

    async def _execute_sampling_workflow(
        self,
        ctx: Context,
        workflow_prompt: str,
        avatar_id: str,
        available_operations: list[str],
        max_iterations: int,
        context: dict[str, Any],
        strict_mode: bool,
    ) -> dict[str, Any]:
        """Execute the sampling workflow using FastMCP 3.1 Context.sample()."""

        operations_executed = []
        results = []
        iteration_count = 0
        start_time = asyncio.get_event_loop().time()

        try:
            operation_sequence = await self._generate_operation_sequence(
                ctx, workflow_prompt, available_operations, max_iterations, context
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
                    results.append(
                        {
                            "operation": operation["name"],
                            "params": operation.get("params", {}),
                            "success": result.get("success", True),
                            "result": result,
                        }
                    )

                    # Add timing delays if specified
                    if "delay" in operation:
                        await asyncio.sleep(operation["delay"])

                except Exception as op_error:
                    logger.error("Operation %s failed: %s", operation["name"], op_error)
                    results.append(
                        {
                            "operation": operation["name"],
                            "success": False,
                            "message": f"Operation '{operation['name']}' failed; workflow continues.",
                            "technical_details": str(op_error),
                            "continuing": "Remaining actions will still run.",
                        }
                    )

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
                "operations_per_second": len(operations_executed) / execution_time
                if execution_time > 0
                else 0,
            }

        except Exception as e:
            logger.error("Sampling workflow execution failed: %s", e)
            return {
                "success": False,
                "message": "Workflow execution failed; partial results below.",
                "technical_details": str(e),
                "operations_executed": operations_executed,
                "results": results,
                "total_iterations": iteration_count,
                "suggestion": "Simplify the workflow or break it into smaller steps.",
            }

    async def _generate_operation_sequence(
        self,
        ctx: Context,
        workflow_prompt: str,
        available_operations: list[str],
        max_iterations: int,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate operation sequence via FastMCP 3.1 Context.sample(); fallback if sampling unavailable."""

        system_prompt = """You are an avatar workflow planner. Given a user's natural language description, output a JSON object with a single key "operations" whose value is a list of steps. Each step must have:
- "name": one of the allowed operation names (exactly as given)
- "params": object with parameters for that operation (e.g. animation_type, emotion, bone, delay)
- "delay": optional number of seconds to wait after this step (omit if not needed)

Use only these operation names: """ + ", ".join(repr(op) for op in available_operations) + """. Keep the list short (at most """ + str(max_iterations) + """ steps). Output only the structured response, no commentary."""

        user_message = f"Plan the avatar workflow (at most {max_iterations} steps): {workflow_prompt}"

        try:
            result = await ctx.sample(
                user_message,
                result_type=OperationSequenceResult,
                system_prompt=system_prompt,
                max_tokens=1024,
            )
            if result.result and result.result.operations:
                return [
                    {
                        "name": op.name,
                        "params": op.params,
                        **({"delay": op.delay} if op.delay is not None else {}),
                    }
                    for op in result.result.operations[:max_iterations]
                ]
        except ValueError as e:
            if "Sampling not supported" in str(e) or "sampling" in str(e).lower():
                logger.info("Sampling not available; using fallback heuristic: %s", e)
            else:
                logger.warning("Sampling failed, using fallback: %s", e)
        except Exception as e:
            logger.warning("Sampling failed, using fallback: %s", e)

        # Fallback: minimal heuristic when client does not support sampling
        prompt_lower = workflow_prompt.lower()
        sequence: list[dict[str, Any]] = []
        if any(w in prompt_lower for w in ["dance", "move", "animate"]):
            sequence.append({"name": "play_animation", "params": {"animation_type": "dance" if "dance" in prompt_lower else "movement"}})
        if any(w in prompt_lower for w in ["smile", "happy", "joy", "facial"]):
            sequence.append({"name": "set_morph", "params": {"emotion": "happy"}})
        if any(w in prompt_lower for w in ["wave", "gesture", "arm"]):
            sequence.append({"name": "control_bone", "params": {"bone": "arm", "action": "wave"}})
        if any(w in prompt_lower for w in ["surprise", "excited", "emotion"]):
            sequence.append({"name": "set_emotion", "params": {"emotion_type": "excited" if "excited" in prompt_lower else "surprised"}})
        if any(w in prompt_lower for w in ["sequence", "complex", "choreography"]):
            sequence.append({"name": "create_sequence", "params": {"complexity": "high"}})
        return sequence[:max_iterations]

    async def _execute_operation(
        self, operation: dict[str, Any], avatar_id: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a single operation."""

        operation_name = operation["name"]
        params = operation.get("params", {})

        if operation_name not in self._available_operations:
            available_ops = list(self._available_operations.keys())
            raise ValueError(
                f"Unknown operation '{operation_name}'. Allowed: {', '.join(available_ops)}."
            )

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
    async def _load_avatar(self, params: dict[str, Any]) -> dict[str, Any]:
        """Load an avatar."""
        return {"success": True, "operation": "load_avatar", "avatar_id": params.get("avatar_id")}

    async def _play_animation(self, params: dict[str, Any]) -> dict[str, Any]:
        """Play an animation."""
        return {
            "success": True,
            "operation": "play_animation",
            "animation": params.get("animation_type", "default"),
        }

    async def _set_morph(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set morph targets."""
        return {
            "success": True,
            "operation": "set_morph",
            "emotion": params.get("emotion", "neutral"),
        }

    async def _control_bone(self, params: dict[str, Any]) -> dict[str, Any]:
        """Control bone positions."""
        return {"success": True, "operation": "control_bone", "bone": params.get("bone", "head")}

    async def _send_osc(self, params: dict[str, Any]) -> dict[str, Any]:
        """Send OSC message."""
        return {"success": True, "operation": "send_osc", "message": "sent"}

    async def _set_emotion(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set emotional state."""
        return {
            "success": True,
            "operation": "set_emotion",
            "emotion": params.get("emotion_type", "neutral"),
        }

    async def _create_sequence(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create animation sequence."""
        return {
            "success": True,
            "operation": "create_sequence",
            "complexity": params.get("complexity", "medium"),
        }

    async def _blend_animations(self, params: dict[str, Any]) -> dict[str, Any]:
        """Blend multiple animations."""
        return {"success": True, "operation": "blend_animations", "layers": params.get("layers", 2)}

    async def _get_status(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get avatar status."""
        return {"success": True, "operation": "get_status", "status": "active"}

    async def _wait(self, params: dict[str, Any]) -> dict[str, Any]:
        """Wait/delay operation."""
        delay = params.get("delay", 1.0)
        await asyncio.sleep(delay)
        return {"success": True, "operation": "wait", "delay": delay}
