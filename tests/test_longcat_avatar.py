"""Tests for LongCat-Video-Avatar 1.5 digital human integration in avatar-mcp."""

import pytest
from unittest.mock import AsyncMock, patch

from avatarmcp.digital_human.longcat_avatar_service import LongCatAvatarService
from avatarmcp.pipeline.service import AvatarPipelineService


@pytest.mark.asyncio
async def test_longcat_avatar_service_health():
    service = LongCatAvatarService()
    health = await service.get_health()
    assert health["status"] in ("available", "ok")
    assert health["service"] == "longcat-video-avatar"
    assert health["model_id"] == "meituan-longcat/LongCat-Video-Avatar-1.5"


@pytest.mark.asyncio
async def test_longcat_avatar_service_generate(tmp_path):
    service = LongCatAvatarService(work_dir=tmp_path)
    result = await service.generate_avatar_video(
        audio_path="sample_speech.wav",
        reference_image_path="avatar.png",
        prompt="Photorealistic talking avatar",
        output_name="test_avatar.mp4",
    )
    assert result["success"] is True
    assert result["fps"] == 30
    assert "test_avatar.mp4" in result["output_name"]


@pytest.mark.asyncio
async def test_avatar_pipeline_longcat_operations(tmp_path):
    pipeline = AvatarPipelineService(models_dir=str(tmp_path))
    status_res = await pipeline.run("longcat_avatar_status")
    assert status_res["service"] == "longcat-video-avatar"

    gen_res = await pipeline.run(
        "longcat_avatar_generate",
        source_path="speech.wav",
        vrm_filename="portrait.png",
        label="Talking digital human test",
    )
    assert gen_res["success"] is True
    assert gen_res["fps"] == 30
