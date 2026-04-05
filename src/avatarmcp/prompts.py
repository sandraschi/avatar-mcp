"""
FastMCP 3.1 prompts for AvatarMCP.

Register with the server by calling register_prompts(mcp) from server __init__.
"""

from typing import Any


def register_prompts(mcp: Any) -> None:
    """Register prompt templates with the FastMCP instance."""

    @mcp.prompt(
        name="avatar_workflow_guide",
        description="Guidance for using the avatar agentic workflow tool: when to use it, allowed operations, and examples.",
    )
    def avatar_workflow_guide() -> str:
        return """Use the avatar_agentic_workflow tool when you need the avatar to perform a multi-step sequence (e.g. "dance then smile", "wave and say hello with expression").

Required arguments:
- workflow_prompt: Natural language description of what the avatar should do (e.g. "Perform a joyful dance with a smile and wave").
- avatar_id: The loaded avatar's ID (from avatar_manager).

Optional:
- available_operations: Subset of operations to allow. If omitted, all are allowed: load_avatar, play_animation, set_morph, control_bone, send_osc, set_emotion, create_sequence, blend_animations, get_status, wait.
- max_iterations: Max steps (1-20, default 5).
- context: Extra dict (e.g. duration, style) for the workflow.
- strict_mode: If true (default), only allowed operation names are executed.

The client's LLM is used via sampling to plan the sequence when the client supports it; otherwise a simple keyword-based fallback is used."""

    @mcp.prompt(
        name="animation_assistant",
        description="Short prompt to help an AI act as an animation assistant for avatar operations.",
    )
    def animation_assistant() -> str:
        return """You are an avatar animation assistant. You have access to tools that load VRM avatars, play animations, set morph targets (facial expressions), control bones, send OSC messages, and manage emotions and sequences. Prefer avatar_agentic_workflow for multi-step behaviors; use single-operation tools for one-off actions. Always confirm the avatar is loaded (avatar_manager) before animating."""
