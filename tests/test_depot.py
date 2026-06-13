"""Tests for avatar depot catalog."""

from pathlib import Path

from avatarmcp.pipeline.depot import KIND_VRM, KIND_VROID, SOURCE_HUB, AvatarDepot


def test_depot_register_vrm(tmp_path: Path) -> None:
    depot = AvatarDepot(tmp_path)
    vrm = tmp_path / "staging" / "char.vrm"
    vrm.parent.mkdir(parents=True)
    vrm.write_bytes(b"vrm-test")
    reg = depot.register(vrm, kind=KIND_VRM, source=SOURCE_HUB, character_model_id="abc123")
    assert reg["success"] is True
    entry = reg["entry"]
    assert entry["kind"] == KIND_VRM
    assert entry["character_model_id"] == "abc123"
    listed = depot.list_entries(kind=KIND_VRM)
    assert listed["count"] == 1


def test_depot_register_vroid_copy(tmp_path: Path) -> None:
    depot = AvatarDepot(tmp_path)
    proj = tmp_path / "mychar.vroid"
    proj.write_bytes(b"vroid-project")
    reg = depot.register(proj, kind=KIND_VROID, copy_into_depot=True)
    assert reg["success"] is True
    copied = Path(reg["entry"]["path"])
    assert copied.is_file()
    assert copied.parent.name == "projects"


def test_depot_scan(tmp_path: Path) -> None:
    depot = AvatarDepot(tmp_path)
    staging = tmp_path / "staging"
    hub = tmp_path / "hub"
    output = tmp_path / "output"
    staging.mkdir()
    hub.mkdir()
    output.mkdir()
    (hub / "hub_model.vrm").write_bytes(b"x")
    scan = depot.scan_work_dirs(staging, hub, output)
    assert scan["added_count"] == 1
    assert depot.list_entries()["count"] == 1
