"""Tests for avatar thumbnail API."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_set_model_thumbnail(tmp_path: Path):
    from avatarmcp.models.vrm_manager import VRMManager

    models_dir = tmp_path / "models"
    models_dir.mkdir()
    vrm = models_dir / "TestAvatar.vrm"
    vrm.write_bytes(b"vrm")

    icon = tmp_path / "icon.png"
    icon.write_bytes(b"\x89PNG\r\n\x1a\n")

    manager = VRMManager(models_dir=str(models_dir))
    await manager.scan_models()
    result = await manager.set_model_thumbnail("TestAvatar", str(icon))

    assert result["success"] is True
    thumb = Path(result["thumbnail_path"])
    assert thumb.is_file()
    assert thumb.name == "TestAvatar.thumb.png"
