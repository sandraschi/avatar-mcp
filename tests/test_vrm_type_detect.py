"""Tests for VRM model_type detection."""

import json
import struct
from pathlib import Path

from avatarmcp.pipeline.vrm_type_detect import build_import_metadata, classify_vrm_model_type


def _make_minimal_glb(title: str, node_names: list[str]) -> bytes:
    gltf = {
        "asset": {"version": "2.0"},
        "nodes": [{"name": n} for n in node_names],
        "extensions": {
            "VRM": {
                "title": title,
                "author": "test",
                "humanoid": {
                    "humanBones": [{"bone": f"bone_{i}"} for i in range(10)],
                },
            }
        },
    }
    json_bytes = json.dumps(gltf).encode("utf-8")
    json_pad = (4 - (len(json_bytes) % 4)) % 4
    json_chunk = json_bytes + b" " * json_pad
    total_len = 12 + 8 + len(json_chunk)
    header = struct.pack("<III", 0x46546C67, 2, total_len)
    chunk_header = struct.pack("<I4s", len(json_chunk), b"JSON")
    return header + chunk_header + json_chunk


def test_classify_humanoid_default(tmp_path: Path) -> None:
    path = tmp_path / "girl.vrm"
    path.write_bytes(_make_minimal_glb("Anime Girl", ["Hips", "Head"]))
    result = classify_vrm_model_type(path)
    assert result["model_type"] == "humanoid"
    assert result["is_humanoid"] is True


def test_classify_quadruped_keywords(tmp_path: Path) -> None:
    path = tmp_path / "wolf.vrm"
    path.write_bytes(_make_minimal_glb("Blue Wolf Pup", ["FrontLeg_L", "HindLeg_R"]))
    result = classify_vrm_model_type(path)
    assert result["model_type"] == "quadruped"


def test_build_import_metadata(tmp_path: Path) -> None:
    path = tmp_path / "dragon.vrm"
    path.write_bytes(_make_minimal_glb("Red Dragon", ["Wing_L", "Wing_R", "Tail_01"]))
    meta = build_import_metadata(path)
    assert meta["model_type"] in ("winged", "serpent", "humanoid")
    assert "custom_properties" in meta
