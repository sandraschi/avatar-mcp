"""Digital Human Avatar portmanteau tool for AvatarMCP."""

from __future__ import annotations

import logging
from typing import Any

from avatarmcp.digital_human.longcat_avatar_service import LongCatAvatarService
from avatarmcp.digital_human.minimax_h3_avatar_service import MiniMaxH3AvatarService

logger = logging.getLogger(__name__)


class DigitalHumanTool:
    """Portmanteau tool for audio-driven digital human synthesis (LongCat-Video-Avatar 1.5, MiniMax H3)."""

    def __init__(self, mcp_server) -> None:
        self.mcp_server = mcp_server
        self.service = LongCatAvatarService()
        self.h3_service = MiniMaxH3AvatarService()
        self._register_tool()

    def _register_tool(self) -> None:
        service = self.service
        h3_service = self.h3_service
        mcp_server = self.mcp_server

        @mcp_server.mcp.tool()
        async def digital_human_avatar(params: dict[str, Any]) -> dict[str, Any]:
            """Synthesize photorealistic talking digital human video.

            Operations:
            - longcat_status: Check health & CUDA state of LongCat-Video-Avatar engine.
            - longcat_generate: Generate audio-driven digital human video MP4 via LongCat-Video-Avatar 1.5.
            - lipsync_drive: Drive avatar mouth & facial expressions from audio track (LongCat backend).
            - minimax_h3_status: Check health of the MiniMax H3 Ref2VA backend (EXPERIMENTAL, unconfigured
              by default - see minimax_h3_avatar_service.py for what's actually wired up).
            - minimax_h3_generate: Generate audio-driven digital human video via MiniMax H3 Ref2VA
              (EXPERIMENTAL - no sidecar ships with this repo yet, will return success=False until one
              exists; use comfyops-mcp's minimax-h3-i2v ComfyUI workflow as the working alternative).
            """
            try:
                operation = (params.get("operation") or "longcat_status").strip().lower()

                if operation == "longcat_status":
                    return await service.get_health()

                if operation == "minimax_h3_status":
                    return await h3_service.get_health()

                if operation in ("longcat_generate", "lipsync_drive", "vroid_animate"):
                    audio_path = params.get("audio_path") or params.get("audio") or params.get("project_path", "")
                    if not audio_path:
                        return {
                            "success": False,
                            "error": "audio_path is required for digital human generation.",
                        }

                    return await service.generate_avatar_video(
                        audio_path=audio_path,
                        reference_image_path=params.get("reference_image_path") or params.get("source_path", ""),
                        prompt=params.get(
                            "prompt", "VRoid 3D character animated into photorealistic audio-driven digital human"
                        ),
                        num_frames=int(params.get("num_frames", 81)),
                        guidance_scale=float(params.get("guidance_scale", 4.5)),
                        output_name=params.get("output_name", "digital_human_avatar.mp4"),
                    )

                if operation == "minimax_h3_generate":
                    audio_path = params.get("audio_path") or params.get("audio") or params.get("project_path", "")
                    if not audio_path:
                        return {
                            "success": False,
                            "error": "audio_path is required for digital human generation.",
                        }

                    return await h3_service.generate_avatar_video(
                        audio_path=audio_path,
                        reference_image_path=params.get("reference_image_path") or params.get("source_path", ""),
                        prompt=params.get(
                            "prompt", "A photorealistic talking digital human avatar, natural expressions"
                        ),
                        num_frames=int(params.get("num_frames", 125)),
                        guidance_scale=float(params.get("guidance_scale", 4.5)),
                        output_name=params.get("output_name", "minimax_h3_avatar_render.mp4"),
                    )

                return {
                    "success": False,
                    "error": (
                        f"Unknown digital_human_avatar operation: '{operation}'. Valid: longcat_status, "
                        "longcat_generate, lipsync_drive, vroid_animate, minimax_h3_status, minimax_h3_generate."
                    ),
                }
            except Exception as exc:
                logger.exception("digital_human_avatar failed")
                return {"success": False, "error": str(exc)}
