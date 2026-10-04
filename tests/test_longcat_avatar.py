"""Tests for LongCat-Video-Avatar 1.5 digital human integration in avatar-mcp."""

import pytest
from unittest.mock import AsyncMock, patch

from avatarmcp.digital_human.longcat_avatar_service import LongCatAvatarService
from avatarmcp.digital_human.minimax_h3_avatar_service import MiniMaxH3AvatarService
from avatarmcp.pipeline.service import AvatarPipelineService
from avatarmcp.tools.portmanteau.digital_human_tool import DigitalHumanTool


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


@pytest.mark.asyncio
async def test_pipeline_longcat_generate_requires_audio(tmp_path):
    pipeline = AvatarPipelineService(models_dir=str(tmp_path))
    res = await pipeline.run("longcat_avatar_generate")
    assert res["success"] is False
    assert "source_path" in res["message"]


@pytest.mark.asyncio
async def test_pipeline_longcat_generate_ignores_non_image_reference(tmp_path):
    pipeline = AvatarPipelineService(models_dir=str(tmp_path))
    with patch.object(pipeline.longcat, "generate_avatar_video", new=AsyncMock(return_value={"success": True})) as gen:
        await pipeline.run("longcat_avatar_generate", source_path="speech.wav")  # default vrm_filename is a .vrm
        gen.assert_awaited_once_with(audio_path="speech.wav")


class _FakeMCP:
    """Captures tools registered through @mcp_server.mcp.tool()."""

    def __init__(self) -> None:
        self.tools: dict = {}

    def tool(self):
        def register(fn):
            self.tools[fn.__name__] = fn
            return fn

        return register


class _FakeServer:
    def __init__(self) -> None:
        self.mcp = _FakeMCP()


@pytest.fixture
def digital_human_avatar(tmp_path, monkeypatch):
    import avatarmcp.tools.portmanteau.digital_human_tool as mod

    monkeypatch.setattr(mod, "LongCatAvatarService", lambda: LongCatAvatarService(work_dir=tmp_path))
    monkeypatch.setattr(mod, "MiniMaxH3AvatarService", lambda: MiniMaxH3AvatarService(work_dir=tmp_path / "h3"))
    server = _FakeServer()
    DigitalHumanTool(server)
    return server.mcp.tools["digital_human_avatar"]


@pytest.mark.asyncio
async def test_digital_human_tool_longcat_status(digital_human_avatar):
    res = await digital_human_avatar({"operation": "longcat_status"})
    assert res["service"] == "longcat-video-avatar"


@pytest.mark.asyncio
async def test_digital_human_tool_longcat_generate(digital_human_avatar):
    res = await digital_human_avatar(
        {"operation": "longcat_generate", "audio_path": "speech.wav", "output_name": "tool_test.mp4"}
    )
    assert res["success"] is True
    assert res["fps"] == 30
    assert "tool_test.mp4" in res["output_name"]


@pytest.mark.asyncio
async def test_digital_human_tool_validates_input(digital_human_avatar):
    assert (await digital_human_avatar({"operation": "longcat_generate"}))["success"] is False
    assert "Unknown" in (await digital_human_avatar({"operation": "nope"}))["error"]
