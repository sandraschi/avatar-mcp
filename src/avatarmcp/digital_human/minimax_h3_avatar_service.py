"""MiniMax H3 (Ref2VA) digital human synthesis service - EXPERIMENTAL.

MiniMax H3 (released as open weights 2026-08-03) is a 33B dense omni transformer that
generates video + native synchronized audio in one pass. Its Ref2VA workflow (reference
images + audio + text -> video) is the mode relevant to avatar-mcp: feed a VRoid render or
portrait as the reference and drive it with an audio track, same shape as LongCatAvatarService
but a different underlying model.

STATUS: this is a thin HTTP client against a local sidecar, mirroring longcat_avatar_service.py.
It has NOT been validated against a running H3 sidecar - there is no `minimax_h3_server` shipped
in this repo yet, so `get_health()`/`generate_avatar_video()` will hit the fallback path until
one exists. Treat the "completed_fallback" status honestly: it means no real generation happened.

License note: MiniMax H3 Community License Agreement (2026-08-02) excludes EU/UK/US/South Korea
from "Applicable Territory" for local weights. Not enforced by this code.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_MINIMAX_H3_URL = os.environ.get("MINIMAX_H3_AVATAR_URL", "http://localhost:8190")


class MiniMaxH3AvatarService:
    """Orchestrates MiniMax H3 Ref2VA digital human generation (reference image + audio -> video)."""

    def __init__(self, base_url: str | None = None, work_dir: str | Path | None = None) -> None:
        self.base_url = (base_url or DEFAULT_MINIMAX_H3_URL).rstrip("/")
        self.work_dir = Path(work_dir or os.path.join(Path.home(), ".avatarmcp", "digital_human"))
        self.work_dir.mkdir(parents=True, exist_ok=True)

    async def get_health(self) -> dict[str, Any]:
        """Check status of the local MiniMax H3 sidecar or engine."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/health")
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.debug(f"MiniMax H3 sidecar health check failed: {e}")

        # No sidecar reachable, and no local in-process H3 engine exists yet in this repo.
        # Being explicit rather than pretending readiness: this is NOT running.
        return {
            "status": "not_configured",
            "service": "minimax-h3-avatar",
            "model_id": "MiniMaxAI/MiniMax-H3",
            "workflow": "ref2va",
            "backend": "modular-diffusers",
            "hint": (
                "No MiniMax H3 sidecar found at "
                f"{self.base_url}. This service is wired up but nothing serves it yet - "
                "see videogen-mcp's loader._load_minimax_h3() for the (unverified) load path, "
                "or run H3 via ComfyUI (comfyops-mcp already has minimax-h3-i2v/t2v workflows)."
            ),
        }

    async def generate_avatar_video(
        self,
        audio_path: str,
        *,
        reference_image_path: str = "",
        prompt: str = "A photorealistic talking digital human avatar, natural expressions",
        num_frames: int = 125,  # H3 frame counts follow 17n+5; ~125 = ~5.2s @ 24fps
        guidance_scale: float = 4.5,
        output_name: str = "minimax_h3_avatar_render.mp4",
    ) -> dict[str, Any]:
        """Synthesize an audio-driven digital human MP4 video via MiniMax H3 Ref2VA."""
        output_path = self.work_dir / output_name

        try:
            async with httpx.AsyncClient(timeout=300) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "audio_path": audio_path,
                        "reference_image_path": reference_image_path,
                        "prompt": prompt,
                        "num_frames": num_frames,
                        "guidance_scale": guidance_scale,
                        "workflow": "ref2va",
                    },
                )
                if resp.status_code == 200:
                    output_path.write_bytes(resp.content)
                    return {
                        "success": True,
                        "status": "completed",
                        "output_path": str(output_path),
                        "output_name": output_name,
                        "num_frames": num_frames,
                        "fps": 24,
                        "model_id": "MiniMaxAI/MiniMax-H3",
                    }
        except Exception as e:
            logger.warning(f"MiniMax H3 sidecar HTTP call failed: {e}")

        # Explicit stub - no sidecar exists yet, so this is NOT a real render.
        # Unlike LongCatAvatarService's fallback, this one does not touch a fake output file:
        # returning success=False here is the honest state until a real H3 sidecar is built.
        return {
            "success": False,
            "status": "not_implemented",
            "output_name": output_name,
            "model_id": "MiniMaxAI/MiniMax-H3",
            "message": (
                "No MiniMax H3 sidecar is running - this integration has no working backend yet. "
                "Build a sidecar exposing POST /api/generate (see LongCat's sidecar for the shape "
                "this expects), or use comfyops-mcp's existing minimax-h3-i2v ComfyUI workflow directly."
            ),
        }
