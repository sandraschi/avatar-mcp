"""Heuristic VRM model_type detection from glTF/VRM metadata and bone names."""

from __future__ import annotations

import json
import logging
import re
import struct
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MODEL_TYPES = ("humanoid", "quadruped", "winged", "serpent", "taur", "creature", "generic")

_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "quadruped": (
        "dog",
        "wolf",
        "fox",
        "puppy",
        "quadruped",
        "feral",
        "canine",
        "feline",
        "catgirl",
        "neko",
        "animal",
        "pup",
        "hound",
        "k9",
    ),
    "winged": ("dragon", "wing", "bat", "angel", "fairy", "phoenix", "wyvern", "harpy"),
    "serpent": ("snake", "naga", "serpent", "lamia", "coil", "python"),
    "taur": ("taur", "centaur", "anthro", "minotaur"),
}

_BONE_QUADRUPED_HINTS = (
    "frontleg",
    "hindleg",
    "foreleg",
    "backleg",
    "front_leg",
    "hind_leg",
    "front_l",
    "front_r",
    "hind_l",
    "hind_r",
    "leg_fl",
    "leg_fr",
    "leg_bl",
    "leg_br",
)

_BONE_WING_HINTS = ("wing", "wing_l", "wing_r", "wingl", "wingr")
_BONE_TAIL_HINTS = ("tail", "tail_", "tailbone")


def _read_glb_json(path: Path) -> dict[str, Any] | None:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        logger.warning("Cannot read VRM for type detect: %s", exc)
        return None

    if len(raw) < 20 or raw[:4] != b"glTF":
        return None

    offset = 12
    while offset + 8 <= len(raw):
        chunk_len = struct.unpack("<I", raw[offset : offset + 4])[0]
        chunk_type = raw[offset + 4 : offset + 8]
        chunk_data = raw[offset + 8 : offset + 8 + chunk_len]
        offset += 8 + chunk_len
        if chunk_type == b"JSON":
            try:
                return json.loads(chunk_data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                logger.warning("Invalid GLB JSON chunk: %s", exc)
                return None
    return None


def _collect_text_blobs(gltf: dict[str, Any]) -> str:
    parts: list[str] = []
    for node in gltf.get("nodes") or []:
        if isinstance(node, dict) and node.get("name"):
            parts.append(str(node["name"]))
    for ext_key in ("VRM", "VRMC_vrm"):
        ext = (gltf.get("extensions") or {}).get(ext_key)
        if not isinstance(ext, dict):
            continue
        for key in ("title", "name", "author", "reference", "version"):
            val = ext.get(key)
            if val:
                parts.append(str(val))
        meta = ext.get("meta")
        if isinstance(meta, dict):
            for key in ("title", "author", "version", "licenseUrl"):
                val = meta.get(key)
                if val:
                    parts.append(str(val))
    return " ".join(parts).lower()


def _score_keywords(text: str) -> dict[str, int]:
    scores = {key: 0 for key in _TYPE_KEYWORDS}
    for model_type, words in _TYPE_KEYWORDS.items():
        for word in words:
            if word in text:
                scores[model_type] += 1
    return scores


def _score_bone_names(gltf: dict[str, Any]) -> dict[str, int]:
    scores = {"quadruped": 0, "winged": 0, "serpent": 0}
    names: list[str] = []
    for node in gltf.get("nodes") or []:
        if isinstance(node, dict) and node.get("name"):
            names.append(str(node["name"]).lower())

    joined = " ".join(names)
    for hint in _BONE_QUADRUPED_HINTS:
        if hint in joined:
            scores["quadruped"] += 1
    for hint in _BONE_WING_HINTS:
        if hint in joined:
            scores["winged"] += 1
    for hint in _BONE_TAIL_HINTS:
        if hint in joined:
            scores["serpent"] += 1

    leg_upper = sum(1 for n in names if "upperleg" in n or "thigh" in n)
    if leg_upper >= 4:
        scores["quadruped"] += 2
    return scores


def _has_humanoid_mapping(gltf: dict[str, Any]) -> bool:
    for ext_key in ("VRM", "VRMC_vrm"):
        ext = (gltf.get("extensions") or {}).get(ext_key)
        if not isinstance(ext, dict):
            continue
        humanoid = ext.get("humanoid") or {}
        bones = humanoid.get("humanBones")
        if isinstance(bones, list) and len(bones) >= 8:
            return True
        if isinstance(bones, dict) and len(bones) >= 8:
            return True
    return False


def classify_vrm_model_type(vrm_path: str | Path) -> dict[str, Any]:
    """Return model_type, is_humanoid, confidence, and detection hints."""
    path = Path(vrm_path)
    if not path.is_file():
        return {
            "model_type": "humanoid",
            "is_humanoid": True,
            "confidence": 0.0,
            "hints": ["file_missing"],
        }

    gltf = _read_glb_json(path)
    if not gltf:
        return {
            "model_type": "humanoid",
            "is_humanoid": True,
            "confidence": 0.1,
            "hints": ["unparsed_glb"],
        }

    text = _collect_text_blobs(gltf)
    kw_scores = _score_keywords(text)
    bone_scores = _score_bone_names(gltf)
    humanoid_mapped = _has_humanoid_mapping(gltf)

    combined: dict[str, float] = {}
    for key in set(kw_scores) | set(bone_scores):
        combined[key] = float(kw_scores.get(key, 0)) + float(bone_scores.get(key, 0)) * 1.5

    best_type = "humanoid"
    best_score = 0.0
    for model_type, score in combined.items():
        if score > best_score:
            best_score = score
            best_type = model_type

    hints: list[str] = []
    if kw_scores.get(best_type, 0):
        hints.append("keyword_match")
    if bone_scores.get(best_type, 0):
        hints.append("bone_name_match")

    if best_score < 1.0:
        best_type = "humanoid" if humanoid_mapped else "generic"
        confidence = 0.5 if humanoid_mapped else 0.3
    else:
        confidence = min(0.95, 0.4 + best_score * 0.15)

    is_humanoid = best_type in ("humanoid", "taur") or (humanoid_mapped and best_type == "generic")
    if best_type == "taur":
        is_humanoid = True

    title = ""
    for ext_key in ("VRM", "VRMC_vrm"):
        ext = (gltf.get("extensions") or {}).get(ext_key)
        if isinstance(ext, dict):
            title = str(ext.get("title") or ext.get("name") or "")
            if title:
                break

    author = ""
    for ext_key in ("VRM", "VRMC_vrm"):
        ext = (gltf.get("extensions") or {}).get(ext_key)
        if isinstance(ext, dict):
            author = str(ext.get("author") or "")
            if author:
                break

    name = title or path.stem
    name = re.sub(r"[^a-zA-Z0-9_\- ]", "_", name).strip() or path.stem

    return {
        "model_type": best_type,
        "is_humanoid": is_humanoid,
        "confidence": round(confidence, 2),
        "hints": hints or ["default_humanoid"],
        "name": name,
        "author": author or "unknown",
        "title": title or path.stem,
    }


def build_import_metadata(vrm_path: str | Path, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build VRMMetadata-compatible dict with optional caller overrides."""
    detected = classify_vrm_model_type(vrm_path)
    meta: dict[str, Any] = {
        "name": detected.get("name", Path(vrm_path).stem),
        "version": "1.0",
        "author": detected.get("author", "unknown"),
        "description": f"Imported via avatar pipeline (type={detected.get('model_type')})",
        "tags": [detected.get("model_type", "humanoid")],
        "is_humanoid": bool(detected.get("is_humanoid", True)),
        "model_type": str(detected.get("model_type", "humanoid")),
        "custom_properties": {
            "type_detection": {
                "confidence": detected.get("confidence"),
                "hints": detected.get("hints"),
            }
        },
    }
    if overrides:
        meta.update({k: v for k, v in overrides.items() if v is not None})
    return meta
