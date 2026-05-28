"""Tests for avatar pipeline staging."""

from pathlib import Path

from avatarmcp.pipeline.fleet_http import stage_vrm_for_vts


def test_stage_vrm_for_vts(tmp_path: Path) -> None:
    src = tmp_path / "test.vrm"
    src.write_bytes(b"vrm-bytes")
    staging = tmp_path / "vts"
    result = stage_vrm_for_vts(str(src), staging, label="test")
    assert result["success"] is True
    assert Path(result["staged_path"]).is_file()
    assert Path(result["manifest"]).is_file()
