"""
Enhanced VRM Model class for handling VRM 2.0 avatar data and operations.
"""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO

from pygltflib import GLTF2
from pyvrm import VrmData


@dataclass
class VRMBlendShape:
    """Represents a VRM blend shape (morph target)."""

    name: str
    category: str  # e.g., 'preset', 'custom'
    preset_name: str | None = None
    bindings: list[dict[str, Any]] = field(default_factory=list)
    material_values: list[dict[str, Any]] = field(default_factory=list)
    is_binary: bool = False
    weight: float = 0.0


@dataclass
class VRMBlendShapeGroup:
    """Represents a group of blend shapes that work together."""

    name: str
    preset_name: str
    binds: list[VRMBlendShape] = field(default_factory=list)
    material_values: list[dict[str, Any]] = field(default_factory=list)
    is_binary: bool = False


class VRMModelEnhanced:
    """Enhanced VRM model class with VRM 2.0 support."""

    def __init__(self, file_path: str | Path | BinaryIO):
        """Initialize a VRM model from a file or file-like object.

        Args:
            file_path: Path to the VRM file or a file-like object
        """
        self.file_path = str(file_path) if isinstance(file_path, (str, Path)) else "<file-like>"
        self.model_id = self._generate_model_id()
        self.metadata: dict[str, Any] = {}
        self.gltf: GLTF2 | None = None
        self.vrm_data: VrmData | None = None
        self.blend_shapes: dict[str, VRMBlendShape] = {}
        self.blend_shape_groups: dict[str, VRMBlendShapeGroup] = {}
        self.human_bones: dict[str, dict] = {}
        self._load_model()

    def _generate_model_id(self) -> str:
        """Generate a unique ID for the model."""
        if hasattr(self, "file_path") and self.file_path != "<file-like>":
            base_name = os.path.basename(self.file_path)
            name, _ = os.path.splitext(base_name)
            timestamp = int(time.time() * 1000)
            return f"{name}_{timestamp}"
        return f"model_{id(self)}"

    def _load_model(self) -> None:
        """Load the VRM model from file or file-like object."""
        try:
            # Load the GLTF/GLB file
            if isinstance(self.file_path, (str, Path)):
                self.gltf = GLTF2().load(self.file_path)
            else:
                self.gltf = GLTF2().load_from_file_obj(self.file_path)

            # Parse VRM extension
            self._parse_vrm_extension()

            # Extract metadata and other VRM-specific data
            self._extract_metadata()

        except Exception as e:
            raise ValueError(f"Failed to load VRM model: {str(e)}") from e

    def _parse_vrm_extension(self) -> None:
        """Parse VRM extension data from the GLTF model."""
        if not self.gltf or not hasattr(self.gltf, "extensions") or not self.gltf.extensions:
            return

        # Look for VRM extension
        vrm_ext = self.gltf.extensions.get("VRM")
        if not vrm_ext:
            return

        # Parse VRM metadata
        self.metadata = {
            "name": vrm_ext.get("name", "Unnamed VRM"),
            "version": vrm_ext.get("version", "1.0"),
            "author": vrm_ext.get("author", "Unknown"),
            "contactInformation": vrm_ext.get("contactInformation", ""),
            "reference": vrm_ext.get("reference", ""),
            "title": vrm_ext.get("title", ""),
            "texture": vrm_ext.get("texture", []),
            "allowedUserName": vrm_ext.get("allowedUserName", ""),
            "violentUssageName": vrm_ext.get("violentUssageName", ""),
            "sexualUssageName": vrm_ext.get("sexualUssageName", ""),
            "commercialUssageName": vrm_ext.get("commercialUssageName", ""),
            "licenseName": vrm_ext.get("licenseName", ""),
            "otherLicenseUrl": vrm_ext.get("otherLicenseUrl", ""),
            "otherPermissionUrl": vrm_ext.get("otherPermissionUrl", ""),
        }

        # Parse humanoid bones
        if "humanoid" in vrm_ext and "humanBones" in vrm_ext["humanoid"]:
            for bone in vrm_ext["humanoid"]["humanBones"]:
                bone_name = bone.get("bone", "")
                if bone_name:
                    self.human_bones[bone_name] = bone

        # Parse blend shapes
        if "blendShapeMaster" in vrm_ext and "blendShapeGroups" in vrm_ext["blendShapeMaster"]:
            for group_data in vrm_ext["blendShapeMaster"]["blendShapeGroups"]:
                group_name = group_data.get("name", "unnamed_group")
                preset_name = group_data.get("presetName", "unknown")

                blend_shapes = []
                for bind in group_data.get("binds", []):
                    shape_name = bind.get("mesh", "") + f"_shape_{len(blend_shapes)}"
                    blend_shapes.append(
                        VRMBlendShape(
                            name=shape_name,
                            category="preset" if preset_name != "unknown" else "custom",
                            preset_name=preset_name if preset_name != "unknown" else None,
                            bindings=[bind],
                            is_binary=group_data.get("isBinary", False),
                        )
                    )

                self.blend_shape_groups[group_name] = VRMBlendShapeGroup(
                    name=group_name,
                    preset_name=preset_name,
                    binds=blend_shapes,
                    material_values=group_data.get("materialValues", []),
                    is_binary=group_data.get("isBinary", False),
                )

    def _extract_metadata(self) -> None:
        """Extract metadata from the VRM model."""
        if not self.gltf:
            return

        # Basic metadata
        self.metadata.update(
            {
                "bones": self._extract_bones(),
                "materials": self._extract_materials(),
                "textures": self._extract_textures(),
                "animations": self._extract_animations(),
                "meshes": self._extract_meshes(),
                "nodes": self._extract_nodes(),
                "scenes": self._extract_scenes(),
                "cameras": self._extract_cameras(),
                "skins": self._extract_skins(),
            }
        )

    def _extract_bones(self) -> list[dict[str, Any]]:
        """Extract bone information from the model."""
        if not self.gltf or not self.gltf.nodes:
            return []

        bones = []
        for i, node in enumerate(self.gltf.nodes):
            if not node:
                continue

            bone = {
                "index": i,
                "name": getattr(node, "name", f"bone_{i}"),
                "children": getattr(node, "children", []),
                "translation": list(getattr(node, "translation", [0, 0, 0])),
                "rotation": list(getattr(node, "rotation", [0, 0, 0, 1])),
                "scale": list(getattr(node, "scale", [1, 1, 1])),
                "is_humanoid": getattr(node, "name", "") in self.human_bones,
            }
            bones.append(bone)

        return bones

    def _extract_materials(self) -> list[dict[str, Any]]:
        """Extract material information from the model."""
        if not self.gltf or not self.gltf.materials:
            return []

        return [
            {
                "index": i,
                "name": getattr(mat, "name", f"material_{i}"),
                "alpha_mode": getattr(mat, "alphaMode", "OPAQUE"),
                "double_sided": getattr(mat, "doubleSided", False),
            }
            for i, mat in enumerate(self.gltf.materials)
        ]

    def _extract_textures(self) -> list[dict[str, Any]]:
        """Extract texture information from the model."""
        if not self.gltf or not self.gltf.textures:
            return []

        textures = []
        for i, tex in enumerate(self.gltf.textures):
            if not tex:
                continue

            texture_info = {
                "index": i,
                "name": getattr(tex, "name", f"texture_{i}"),
                "source": getattr(tex, "source", -1),
                "sampler": getattr(tex, "sampler", -1),
            }

            # Get image URI if available
            if hasattr(tex, "extras") and isinstance(tex.extras, dict):
                texture_info.update(tex.extras)

            textures.append(texture_info)

        return textures

    def _extract_animations(self) -> list[dict[str, Any]]:
        """Extract animation information from the model."""
        if not self.gltf or not self.gltf.animations:
            return []

        return [
            {
                "index": i,
                "name": getattr(anim, "name", f"animation_{i}"),
                "channels": [
                    {
                        "sampler": chan.sampler,
                        "target": {"node": chan.target.node, "path": chan.target.path},
                    }
                    for chan in getattr(anim, "channels", [])
                ],
                "samplers": [
                    {
                        "input": samp.input,
                        "output": samp.output,
                        "interpolation": getattr(samp, "interpolation", "LINEAR"),
                    }
                    for samp in getattr(anim, "samplers", [])
                ],
            }
            for i, anim in enumerate(self.gltf.animations)
        ]

    def _extract_meshes(self) -> list[dict[str, Any]]:
        """Extract mesh information from the model."""
        if not self.gltf or not self.gltf.meshes:
            return []

        return [
            {
                "index": i,
                "name": getattr(mesh, "name", f"mesh_{i}"),
                "primitives": [
                    {
                        "attributes": prim.attributes.__dict__,
                        "indices": getattr(prim, "indices", -1),
                        "material": getattr(prim, "material", -1),
                        "mode": getattr(prim, "mode", 4),  # TRIANGLES by default
                    }
                    for prim in getattr(mesh, "primitives", [])
                ],
            }
            for i, mesh in enumerate(self.gltf.meshes)
        ]

    def _extract_nodes(self) -> list[dict[str, Any]]:
        """Extract node information from the model."""
        if not self.gltf or not self.gltf.nodes:
            return []

        return [
            {
                "index": i,
                "name": getattr(node, "name", f"node_{i}"),
                "children": getattr(node, "children", []),
                "mesh": getattr(node, "mesh", -1),
                "skin": getattr(node, "skin", -1),
                "camera": getattr(node, "camera", -1),
                "translation": list(getattr(node, "translation", [0, 0, 0])),
                "rotation": list(getattr(node, "rotation", [0, 0, 0, 1])),
                "scale": list(getattr(node, "scale", [1, 1, 1])),
                "matrix": getattr(node, "matrix", None),
            }
            for i, node in enumerate(self.gltf.nodes)
        ]

    def _extract_scenes(self) -> list[dict[str, Any]]:
        """Extract scene information from the model."""
        if not self.gltf or not self.gltf.scenes:
            return []

        return [
            {
                "index": i,
                "name": getattr(scene, "name", f"scene_{i}"),
                "nodes": getattr(scene, "nodes", []),
            }
            for i, scene in enumerate(self.gltf.scenes)
        ]

    def _extract_cameras(self) -> list[dict[str, Any]]:
        """Extract camera information from the model."""
        if not self.gltf or not self.gltf.cameras:
            return []

        cameras = []
        for i, cam in enumerate(self.gltf.cameras):
            camera_info = {
                "index": i,
                "name": getattr(cam, "name", f"camera_{i}"),
                "type": getattr(cam, "type", "perspective"),
            }

            # Add perspective or orthographic properties
            if hasattr(cam, "perspective"):
                camera_info.update(
                    {
                        "aspect_ratio": getattr(cam.perspective, "aspectRatio", None),
                        "yfov": getattr(cam.perspective, "yfov", 0.0),
                        "zfar": getattr(cam.perspective, "zfar", None),
                        "znear": getattr(cam.perspective, "znear", 0.1),
                    }
                )
            elif hasattr(cam, "orthographic"):
                camera_info.update(
                    {
                        "xmag": getattr(cam.orthographic, "xmag", 1.0),
                        "ymag": getattr(cam.orthographic, "ymag", 1.0),
                        "zfar": getattr(cam.orthographic, "zfar", 100.0),
                        "znear": getattr(cam.orthographic, "znear", 0.1),
                    }
                )

            cameras.append(camera_info)

        return cameras

    def _extract_skins(self) -> list[dict[str, Any]]:
        """Extract skin information from the model."""
        if not self.gltf or not self.gltf.skins:
            return []

        return [
            {
                "index": i,
                "name": getattr(skin, "name", f"skin_{i}"),
                "inverse_bind_matrices": getattr(skin, "inverseBindMatrices", -1),
                "skeleton": getattr(skin, "skeleton", -1),
                "joints": getattr(skin, "joints", []),
            }
            for i, skin in enumerate(self.gltf.skins)
        ]

    def get_blend_shape_names(self) -> list[str]:
        """Get a list of all blend shape names in the model."""
        return list(self.blend_shapes.keys())

    def get_blend_shape_group_names(self) -> list[str]:
        """Get a list of all blend shape group names in the model."""
        return list(self.blend_shape_groups.keys())

    def get_human_bone_names(self) -> list[str]:
        """Get a list of all human bone names in the model."""
        return list(self.human_bones.keys())

    def get_animation_names(self) -> list[str]:
        """Get a list of all animation names in the model."""
        if not self.gltf or not self.gltf.animations:
            return []
        return [
            getattr(anim, "name", f"animation_{i}") for i, anim in enumerate(self.gltf.animations)
        ]

    def get_mesh_names(self) -> list[str]:
        """Get a list of all mesh names in the model."""
        if not self.gltf or not self.gltf.meshes:
            return []
        return [getattr(mesh, "name", f"mesh_{i}") for i, mesh in enumerate(self.gltf.meshes)]

    def get_texture_uris(self) -> list[str]:
        """Get a list of all texture URIs in the model."""
        if not self.gltf or not self.gltf.images:
            return []

        uris = []
        for img in self.gltf.images:
            if hasattr(img, "uri") and img.uri:
                uris.append(img.uri)
        return uris

    def get_metadata_summary(self) -> dict[str, Any]:
        """Get a summary of the model's metadata."""
        return {
            "model_id": self.model_id,
            "name": self.metadata.get("name", "Unnamed VRM"),
            "version": self.metadata.get("version", "1.0"),
            "author": self.metadata.get("author", "Unknown"),
            "num_bones": len(self.human_bones),
            "num_blend_shapes": len(self.blend_shapes),
            "num_blend_shape_groups": len(self.blend_shape_groups),
            "num_animations": len(self.gltf.animations)
            if self.gltf and hasattr(self.gltf, "animations")
            else 0,
            "num_meshes": len(self.gltf.meshes)
            if self.gltf and hasattr(self.gltf, "meshes")
            else 0,
            "num_textures": len(self.gltf.textures)
            if self.gltf and hasattr(self.gltf, "textures")
            else 0,
            "num_materials": len(self.gltf.materials)
            if self.gltf and hasattr(self.gltf, "materials")
            else 0,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary representation."""
        return {
            "model_id": self.model_id,
            "file_path": self.file_path,
            "metadata": self.metadata,
            "human_bones": self.human_bones,
            "blend_shapes": {
                name: {
                    "name": shape.name,
                    "category": shape.category,
                    "preset_name": shape.preset_name,
                    "is_binary": shape.is_binary,
                    "weight": shape.weight,
                }
                for name, shape in self.blend_shapes.items()
            },
            "blend_shape_groups": {
                name: {
                    "name": group.name,
                    "preset_name": group.preset_name,
                    "is_binary": group.is_binary,
                    "num_binds": len(group.binds),
                    "num_material_values": len(group.material_values),
                }
                for name, group in self.blend_shape_groups.items()
            },
            "summary": self.get_metadata_summary(),
        }

    def __str__(self) -> str:
        """Get a string representation of the model."""
        summary = self.get_metadata_summary()
        return (
            f"VRMModel(id='{self.model_id}', "
            f"name='{summary['name']}', "
            f"version='{summary['version']}', "
            f"bones={summary['num_bones']}, "
            f"blend_shapes={summary['num_blend_shapes']}, "
            f"animations={summary['num_animations']})"
        )

    def __repr__(self) -> str:
        """Get a detailed string representation of the model."""
        return f"<VRMModel {self.model_id} at {hex(id(self))}>"
