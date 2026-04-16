"""
VRM 2.0 Loader

This module provides functionality to load and parse VRM 2.0 files,
extracting model data, materials, and animations using pygltflib and trimesh.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from pygltflib import GLTF2

logger = logging.getLogger(__name__)


class VRMFileType(Enum):
    """Supported VRM file types."""

    GLB = "glb"
    VRM = "vrm"


@dataclass
class VRMModel:
    """Represents a loaded VRM model with all its components."""

    meshes: list["VRMMesh"] = field(default_factory=list)
    materials: list["VRMMaterial"] = field(default_factory=list)
    textures: list["VRMTexture"] = field(default_factory=list)
    blend_shapes: list["VRMBlendShape"] = field(default_factory=list)
    bones: dict[str, "VRMBone"] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VRMMesh:
    """Represents a mesh in a VRM model."""

    name: str
    vertices: np.ndarray  # Nx3 array of vertex positions
    faces: np.ndarray  # Mx3 array of triangle indices
    normals: np.ndarray | None = None
    texcoords: np.ndarray | None = None
    material_index: int | None = None

    def get_pyvista_faces(self) -> np.ndarray:
        """
        Convert faces to PyVista format.

        PyVista expects faces as [n_points_in_cell, point1, point2, point3] for each triangle.

        Returns:
            Faces in PyVista format as a flat array
        """
        if self.faces is None or len(self.faces) == 0:
            return np.array([], dtype=np.uint32)

        # Convert triangular faces to PyVista format
        pv_faces = []
        for face in self.faces:
            if len(face) == 3:  # Triangular face
                pv_faces.extend([3, face[0], face[1], face[2]])

        return np.array(pv_faces, dtype=np.uint32)


@dataclass
class VRMTexture:
    """Represents a texture in a VRM model."""

    name: str
    data: bytes
    mime_type: str  # e.g., "image/png" or "image/jpeg"
    width: int = 0
    height: int = 0


@dataclass
class VRMMaterial:
    """Represents a material in a VRM model."""

    name: str
    base_color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    metallic_factor: float = 1.0
    roughness_factor: float = 1.0
    emissive_factor: tuple[float, float, float] = (0.0, 0.0, 0.0)
    alpha_mode: str = "OPAQUE"
    alpha_cutoff: float = 0.5
    double_sided: bool = False
    texture_indices: dict[str, int] = field(default_factory=dict)


@dataclass
class VRMBlendShape:
    """Represents a blend shape (morph target) in a VRM model."""

    name: str
    category: str  # e.g., "preset", "custom"
    is_binary: bool = False
    weight: float = 0.0
    # Maps from mesh index to vertex deltas
    morph_targets: dict[int, np.ndarray] = field(default_factory=dict)


@dataclass
class VRMBone:
    """Represents a bone in the VRM humanoid rig."""

    name: str
    parent: str | None
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # quaternion (x, y, z, w)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)


@dataclass
class VRMHumanoid:
    """VRM humanoid bone mapping."""

    human_bones: dict[str, Any] = field(default_factory=dict)


@dataclass
class VRMFirstPerson:
    """VRM first-person view settings."""

    first_person_bone: str | None = None
    first_person_bone_offset: tuple[float, float, float] = (0, 0, 0)
    look_at_type_name: str = "Bone"
    look_at_blend_shape_name: str | None = None


class VRMLoader:
    """Loads and parses VRM 2.0 files using pygltflib and trimesh."""

    @classmethod
    def from_file(cls, file_path: str | Path) -> VRMModel:
        """
        Load a VRM model from a file.

        Args:
            file_path: Path to the VRM or GLB file

        Returns:
            VRMModel: The loaded VRM model

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"VRM file not found: {path}")

        file_type = path.suffix.lower()[1:]  # Remove the dot
        if file_type not in [t.value for t in VRMFileType]:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Load the GLTF/GLB file
        try:
            # Try loading as binary GLB first
            if file_type == "glb" or file_type == "vrm":
                gltf = GLTF2().load_binary(str(path.absolute()))
            else:
                # For other formats, try loading as text with explicit UTF-8 encoding
                with open(path, encoding="utf-8") as f:
                    data = f.read()
                gltf = GLTF2().from_json(data)
        except Exception as e:
            raise ValueError(f"Failed to load VRM file: {e!s}") from e

        # Create a new VRM model
        model = VRMModel()
        model.metadata = cls._extract_metadata(gltf)

        # Load textures
        model.textures = cls._load_textures(gltf)

        # Load materials
        model.materials = cls._load_materials(gltf, model.textures)

        # Load meshes
        model.meshes = cls._load_meshes(gltf)

        # Load bones and armature
        model.bones = cls._load_armature(gltf)

        # Load blend shapes
        model.blend_shapes = cls._load_blend_shapes(gltf, model.meshes)

        return model

    @staticmethod
    def _extract_metadata(gltf: GLTF2) -> dict[str, Any]:
        """Extract metadata from the GLTF file."""
        metadata = {
            "version": "2.0",
            "generator": gltf.asset.generator if hasattr(gltf.asset, "generator") else "Unknown",
            "copyright": getattr(gltf.asset, "copyright", ""),
            "extensions": {},
        }

        # Extract VRM extension if present
        if hasattr(gltf, "extensions") and "VRM" in gltf.extensions:
            metadata["extensions"]["VRM"] = gltf.extensions["VRM"]

        return metadata

    @staticmethod
    def _load_textures(gltf: GLTF2) -> list[VRMTexture]:
        """Load textures from the GLTF file.

        Args:
            gltf: The loaded GLTF2 object

        Returns:
            List of VRMTexture objects
        """
        textures = []

        if not hasattr(gltf, "textures") or not gltf.textures:
            logger.debug("No textures found in GLTF file")
            return textures

        for tex_idx, tex in enumerate(gltf.textures):
            try:
                # Skip if no source image
                if not hasattr(tex, "source") or tex.source is None:
                    logger.debug(f"Texture {tex_idx} has no source, skipping")
                    continue

                # Get the source image
                if tex.source >= len(gltf.images):
                    logger.warning(f"Texture {tex_idx} references invalid image index {tex.source}")
                    continue

                img = gltf.images[tex.source]

                # Initialize texture data
                texture_data = b""
                width = getattr(img, "width", 0)
                height = getattr(img, "height", 0)
                mime_type = getattr(img, "mimeType", "image/png")

                # Handle different texture data sources
                if hasattr(img, "bufferView") and img.bufferView is not None:
                    # Get data from buffer view
                    if img.bufferView >= len(gltf.bufferViews):
                        logger.warning(f"Image {tex.source} references invalid buffer view {img.bufferView}")
                        continue

                    buffer_view = gltf.bufferViews[img.bufferView]

                    # Get the buffer containing the data
                    if buffer_view.buffer >= len(gltf.buffers):
                        logger.warning(f"BufferView {img.bufferView} references invalid buffer {buffer_view.buffer}")
                        continue

                    buffer = gltf.buffers[buffer_view.buffer]

                    # Handle different buffer data types
                    if hasattr(buffer, "data") and buffer.data is not None:
                        # Binary data is already loaded in memory
                        start = buffer_view.byteOffset
                        end = start + buffer_view.byteLength
                        texture_data = bytes(buffer.data[start:end])
                    elif hasattr(buffer, "uri") and buffer.uri:
                        # Handle external file reference
                        try:
                            uri = buffer.uri
                            if uri.startswith("data:"):
                                # Handle data URI
                                import base64

                                header, data = uri.split(",", 1)
                                if "base64" in header:
                                    texture_data = base64.b64decode(data)
                                else:
                                    texture_data = data.encode("utf-8")
                            else:
                                # Handle file path
                                with open(uri, "rb") as f:
                                    f.seek(buffer_view.byteOffset)
                                    texture_data = f.read(buffer_view.byteLength)
                        except Exception as e:
                            logger.warning(f"Failed to load texture from {getattr(buffer, 'uri', 'unknown')}: {e!s}")
                            continue

                # Handle embedded image data
                elif hasattr(img, "uri") and img.uri:
                    try:
                        if img.uri.startswith("data:"):
                            # Handle data URI
                            import base64

                            header, data = img.uri.split(",", 1)
                            if "base64" in header:
                                texture_data = base64.b64decode(data)
                                # Try to extract mime type from header
                                if ";" in header:
                                    mime_type = header.split(";")[0].split(":")[1]
                            else:
                                texture_data = data.encode("utf-8")
                        else:
                            # Handle file path
                            with open(img.uri, "rb") as f:
                                texture_data = f.read()
                    except Exception as e:
                        logger.warning(f"Failed to load texture from URI {img.uri}: {e!s}")
                        continue
                else:
                    logger.warning(f"No texture data available for texture {tex_idx}")
                    continue

                # Create texture data
                texture = VRMTexture(
                    name=f"texture_{len(textures)}",
                    data=texture_data,
                    mime_type=mime_type,
                    width=width,
                    height=height,
                )

                # Set name if available
                if hasattr(tex, "name") and tex.name:
                    texture.name = tex.name
                elif hasattr(img, "name") and img.name:
                    texture.name = img.name

                textures.append(texture)

            except Exception as e:
                logger.error(f"Error loading texture {tex_idx}: {e!s}", exc_info=True)
                continue

        return textures

    @staticmethod
    def _load_materials(gltf: GLTF2, textures: list[VRMTexture]) -> list[VRMMaterial]:
        """Load materials from the GLTF file.

        Args:
            gltf: The loaded GLTF2 object
            textures: List of loaded VRMTexture objects

        Returns:
            List of VRMMaterial objects
        """
        materials = []
        for i, mat in enumerate(gltf.materials or []):
            try:
                # Safely get alpha_cutoff with None check
                alpha_cutoff = getattr(mat, "alphaCutoff", 0.5)
                if alpha_cutoff is None:
                    alpha_cutoff = 0.5

                # Safely get pbr properties
                pbr = getattr(mat, "pbrMetallicRoughness", None)
                metallic = 1.0
                roughness = 1.0
                base_color = [1.0, 1.0, 1.0, 1.0]

                if pbr is not None:
                    metallic = float(getattr(pbr, "metallicFactor", 1.0))
                    roughness = float(getattr(pbr, "roughnessFactor", 1.0))
                    base_color = list(getattr(pbr, "baseColorFactor", [1.0, 1.0, 1.0, 1.0]))

                    # Handle base color factor if available
                    if hasattr(pbr, "baseColorFactor") and pbr.baseColorFactor is not None:
                        try:
                            base_color = [float(x) for x in pbr.baseColorFactor[:4]]
                        except (TypeError, ValueError, IndexError) as e:
                            logger.warning(f"Invalid baseColorFactor in material {i}: {e}")

                material = VRMMaterial(
                    name=f"material_{i}",
                    alpha_mode=getattr(mat, "alphaMode", "OPAQUE"),
                    alpha_cutoff=float(alpha_cutoff),
                    double_sided=bool(getattr(mat, "doubleSided", False)),
                    metallic_factor=metallic,
                    roughness_factor=roughness,
                    base_color=tuple(base_color),
                    emissive_factor=tuple(getattr(mat, "emissiveFactor", [0.0, 0.0, 0.0])),
                )

                # Handle texture indices if they exist
                if hasattr(pbr, "baseColorTexture") and hasattr(pbr.baseColorTexture, "index"):
                    tex_index = pbr.baseColorTexture.index
                    if 0 <= tex_index < len(textures):
                        material.texture_indices["baseColor"] = tex_index
                    else:
                        logger.warning(f"Invalid baseColorTexture index {tex_index} in material {i}")

                # Handle metallic and roughness factors
                if hasattr(pbr, "metallicFactor") and pbr.metallicFactor is not None:
                    try:
                        material.metallic_factor = float(pbr.metallicFactor)
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Invalid metallicFactor in material {i}: {e}")

                if hasattr(pbr, "roughnessFactor") and pbr.roughnessFactor is not None:
                    try:
                        material.roughness_factor = float(pbr.roughnessFactor)
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Invalid roughnessFactor in material {i}: {e}")

                # Handle base color texture
                if hasattr(pbr, "baseColorTexture") and hasattr(pbr.baseColorTexture, "index"):
                    tex_index = pbr.baseColorTexture.index
                    if 0 <= tex_index < len(textures):
                        material.texture_indices["baseColor"] = tex_index
                    else:
                        logger.warning(f"Invalid baseColorTexture index {tex_index} in material {i}")

                # Handle metallic-roughness texture
                if hasattr(pbr, "metallicRoughnessTexture") and hasattr(pbr.metallicRoughnessTexture, "index"):
                    tex_index = pbr.metallicRoughnessTexture.index
                    if 0 <= tex_index < len(textures):
                        material.texture_indices["metallicRoughness"] = tex_index
                    else:
                        logger.warning(f"Invalid metallicRoughnessTexture index {tex_index} in material {i}")

                # Handle normal map
                if hasattr(mat, "normalTexture") and hasattr(mat.normalTexture, "index"):
                    tex_index = mat.normalTexture.index
                    if 0 <= tex_index < len(textures):
                        material.texture_indices["normal"] = tex_index
                        # Store normal scale if available
                        if hasattr(mat.normalTexture, "scale"):
                            material.texture_indices["normalScale"] = float(mat.normalTexture.scale)
                    else:
                        logger.warning(f"Invalid normalTexture index {tex_index} in material {i}")

                # Handle occlusion texture
                if hasattr(mat, "occlusionTexture") and hasattr(mat.occlusionTexture, "index"):
                    tex_index = mat.occlusionTexture.index
                    if 0 <= tex_index < len(textures):
                        material.texture_indices["occlusion"] = tex_index
                        # Store occlusion strength if available
                        if hasattr(mat.occlusionTexture, "strength"):
                            material.texture_indices["occlusionStrength"] = float(mat.occlusionTexture.strength)
                    else:
                        logger.warning(f"Invalid occlusionTexture index {tex_index} in material {i}")

                # Handle emissive factor
                if hasattr(mat, "emissiveFactor") and mat.emissiveFactor is not None:
                    try:
                        material.emissive_factor = tuple(float(x) for x in mat.emissiveFactor[:3])
                    except (TypeError, ValueError, IndexError) as e:
                        logger.warning(f"Invalid emissiveFactor in material {i}: {e}")

                # Handle emissive texture
                if hasattr(mat, "emissiveTexture") and mat.emissiveTexture is not None:
                    tex_index = mat.emissiveTexture.index
                    if 0 <= tex_index < len(textures):
                        material.texture_indices["emissive"] = tex_index
                    else:
                        logger.warning(f"Invalid emissiveTexture index {tex_index} in material {i}")

                # Handle alpha mode and cutoff
                if hasattr(mat, "alphaMode") and mat.alphaMode is not None:
                    material.alpha_mode = str(mat.alphaMode).upper()

                if hasattr(mat, "alphaCutoff") and mat.alphaCutoff is not None:
                    try:
                        material.alpha_cutoff = float(mat.alphaCutoff)
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Invalid alphaCutoff in material {i}: {e}")

                # Handle double-sided flag
                if hasattr(mat, "doubleSided") and mat.doubleSided is not None:
                    material.double_sided = bool(mat.doubleSided)

                # Handle VRM material properties if available
                if hasattr(mat, "extensions") and mat.extensions and "KHR_materials_unlit" in mat.extensions:
                    material.texture_indices["unlit"] = True

                materials.append(material)
            except Exception as e:
                logger.error(f"Error loading material {i}: {e!s}", exc_info=True)
                # Create a default material if loading fails
                default_mat = VRMMaterial(
                    name=f"error_material_{i}",
                    base_color=(1.0, 0.0, 1.0, 1.0),  # Magenta to indicate error
                    metallic_factor=0.0,
                    roughness_factor=1.0,
                )
                materials.append(default_mat)
        return materials

    @classmethod
    def _get_accessor_data(cls, gltf, accessor_idx):
        """Get data from an accessor using pygltflib's built-in methods."""
        if accessor_idx is None or not hasattr(gltf, "accessors") or accessor_idx >= len(gltf.accessors):
            return None

        try:
            accessor = gltf.accessors[accessor_idx]

            # Use pygltflib's built-in method to get data
            try:
                # First try to get data directly from the accessor
                if hasattr(gltf, "get_data_from_accessor"):
                    data = gltf.get_data_from_accessor(accessor_idx)
                    if data is not None:
                        return data.tolist() if hasattr(data, "tolist") else data

                # If direct method fails, try to get data from buffer view
                if hasattr(accessor, "bufferView") and accessor.bufferView is not None:
                    buffer_view = gltf.bufferViews[accessor.bufferView]
                    buffer = gltf.buffers[buffer_view.buffer]

                    # Get the raw buffer data
                    if hasattr(gltf, "get_data_from_buffer_uri"):
                        buffer_data = gltf.get_data_from_buffer_uri(buffer.uri)
                    elif hasattr(gltf, "get_data_from_buffer_uri_index"):
                        buffer_data = gltf.get_data_from_buffer_uri_index(buffer_view.buffer)
                    else:
                        # Last resort: try to access buffer data directly
                        buffer_data = getattr(buffer, "data", None)

                    if buffer_data is None:
                        logger.warning(f"No data available for buffer view {accessor.bufferView}")
                        return None

                    # Get the data type and component count
                    dtype_map = {
                        5120: np.int8,  # BYTE
                        5121: np.uint8,  # UNSIGNED_BYTE
                        5122: np.int16,  # SHORT
                        5123: np.uint16,  # UNSIGNED_SHORT
                        5125: np.uint32,  # UNSIGNED_INT
                        5126: np.float32,  # FLOAT
                    }

                    dtype = dtype_map.get(accessor.componentType, np.float32)

                    # Calculate the number of components per element
                    num_components_map = {
                        "SCALAR": 1,
                        "VEC2": 2,
                        "VEC3": 3,
                        "VEC4": 4,
                        "MAT2": 4,
                        "MAT3": 9,
                        "MAT4": 16,
                    }
                    num_components = num_components_map.get(accessor.type, 1)

                    # Convert to numpy array
                    data = np.frombuffer(
                        buffer_data,
                        dtype=dtype,
                        count=accessor.count * num_components,
                        offset=buffer_view.byteOffset + (getattr(accessor, "byteOffset", 0) or 0),
                    )

                    # Reshape the data if needed
                    if num_components > 1:
                        data = data.reshape(-1, num_components)

                    return data.tolist()

                return None

            except Exception as e:
                logger.warning(f"Error getting data from accessor: {e!s}")
                return None

        except Exception as e:
            logger.error(f"Error in _get_accessor_data: {e!s}")
            return None

    @classmethod
    def _validate_faces(cls, faces: np.ndarray, vertex_count: int, mesh_idx: int) -> np.ndarray:
        """
        Validate and fix face indices to prevent PyVista errors.

        Args:
            faces: Face indices array
            vertex_count: Number of vertices in the mesh
            mesh_idx: Mesh index for logging

        Returns:
            Validated face array safe for PyVista
        """
        if faces is None or faces.size == 0:
            return np.array([], dtype=np.uint32).reshape(0, 3)

        faces = np.array(faces, dtype=np.uint32)

        # Ensure faces is 2D
        if faces.ndim == 1:
            if len(faces) % 3 == 0:
                faces = faces.reshape(-1, 3)
            else:
                logger.warning(f"Face array length {len(faces)} not divisible by 3 for mesh {mesh_idx}, truncating")
                faces = faces[: len(faces) // 3 * 3].reshape(-1, 3)

        # Validate face indices are within vertex bounds
        if faces.size > 0:
            max_index = faces.max()
            if max_index >= vertex_count:
                logger.warning(
                    f"Invalid face indices detected in mesh {mesh_idx}: "
                    f"max index {max_index} >= vertex count {vertex_count}"
                )
                # Remove faces with invalid indices
                valid_mask = np.all(faces < vertex_count, axis=1)
                invalid_count = np.sum(~valid_mask)
                faces = faces[valid_mask]
                logger.warning(f"Removed {invalid_count} invalid faces from mesh {mesh_idx}, {len(faces)} remain")

        return faces

    @classmethod
    def _load_meshes(cls, gltf: GLTF2) -> list[VRMMesh]:
        """Load meshes from the GLTF file.

        Args:
            gltf: The loaded GLTF2 object

        Returns:
            List of VRMMesh objects
        """
        meshes = []

        if not hasattr(gltf, "meshes") or not gltf.meshes:
            logger.debug("No meshes found in GLTF file")
            return meshes

        for mesh_idx, gltf_mesh in enumerate(gltf.meshes):
            try:
                if not hasattr(gltf_mesh, "primitives") or not gltf_mesh.primitives:
                    logger.debug(f"Mesh {mesh_idx} has no primitives, skipping")
                    continue

                # For now, just handle the first primitive of each mesh
                primitive = gltf_mesh.primitives[0]

                # Get the position data (required)
                positions = None
                if hasattr(primitive, "attributes") and hasattr(primitive.attributes, "POSITION"):
                    positions = cls._get_accessor_data(gltf, primitive.attributes.POSITION)
                    if positions is not None:
                        try:
                            positions = np.array(positions, dtype=np.float32)
                            if len(positions.shape) != 2 or positions.shape[1] != 3:
                                logger.warning(f"Invalid position data shape {positions.shape} in mesh {mesh_idx}")
                                positions = None
                        except Exception as e:
                            logger.warning(f"Error processing positions for mesh {mesh_idx}: {e!s}")
                            positions = None

                if positions is None:
                    logger.warning(f"Mesh {mesh_idx} has no valid position data, skipping")
                    continue

                # Get other attributes
                normals = None
                tex_coords = None
                joint_indices = None
                joint_weights = None

                if hasattr(primitive, "attributes"):
                    attrs = primitive.attributes

                    # Get normals if available
                    if hasattr(attrs, "NORMAL") and attrs.NORMAL is not None:
                        normals_data = cls._get_accessor_data(gltf, attrs.NORMAL)
                        if normals_data is not None:
                            try:
                                normals = np.array(normals_data, dtype=np.float32)
                                if len(normals) != len(positions):
                                    logger.warning(
                                        f"Normal count {len(normals)} does not match vertex count "
                                        f"{len(positions)} in mesh {mesh_idx}"
                                    )
                                    normals = None
                            except Exception as e:
                                logger.warning(f"Error processing normals for mesh {mesh_idx}: {e!s}")

                    # Get texture coordinates if available
                    if hasattr(attrs, "TEXCOORD_0") and attrs.TEXCOORD_0 is not None:
                        texcoords_data = cls._get_accessor_data(gltf, attrs.TEXCOORD_0)
                        if texcoords_data is not None:
                            try:
                                tex_coords = np.array(texcoords_data, dtype=np.float32)
                                if len(tex_coords) != len(positions):
                                    logger.warning(
                                        f"Texcoord count {len(tex_coords)} does not match "
                                        f"vertex count {len(positions)} in mesh {mesh_idx}"
                                    )
                                    tex_coords = None
                            except Exception as e:
                                logger.warning(f"Error processing texture coordinates for mesh {mesh_idx}: {e!s}")

                    # Get joint indices if available (for skinning)
                    if hasattr(attrs, "JOINTS_0") and attrs.JOINTS_0 is not None:
                        joint_indices_data = cls._get_accessor_data(gltf, attrs.JOINTS_0)
                        if joint_indices_data is not None:
                            try:
                                joint_indices = np.array(joint_indices_data, dtype=np.uint8)
                                if len(joint_indices) != len(positions):
                                    logger.warning(
                                        f"Joint index count {len(joint_indices)} does not match "
                                        f"vertex count {len(positions)} in mesh {mesh_idx}"
                                    )
                                    joint_indices = None
                            except Exception as e:
                                logger.warning(f"Error processing joint indices for mesh {mesh_idx}: {e!s}")

                    # Get joint weights if available (for skinning)
                    if hasattr(attrs, "WEIGHTS_0") and attrs.WEIGHTS_0 is not None:
                        joint_weights_data = cls._get_accessor_data(gltf, attrs.WEIGHTS_0)
                        if joint_weights_data is not None:
                            try:
                                joint_weights = np.array(joint_weights_data, dtype=np.float32)
                                if len(joint_weights) != len(positions):
                                    logger.warning(
                                        f"Joint weight count {len(joint_weights)} does not match "
                                        f"vertex count {len(positions)} in mesh {mesh_idx}"
                                    )
                                    joint_weights = None
                            except Exception as e:
                                logger.warning(f"Error processing joint weights for mesh {mesh_idx}: {e!s}")

                # Get faces (indices)
                faces = None
                if hasattr(primitive, "indices") and primitive.indices is not None:
                    indices_data = cls._get_accessor_data(gltf, primitive.indices)
                    if indices_data is not None:
                        try:
                            # Convert to numpy array and reshape to triangles
                            indices = np.array(indices_data, dtype=np.uint32)

                            # Determine primitive type (triangles, triangle_strip, etc.)
                            mode = getattr(primitive, "mode", 4)  # Default to TRIANGLES (4)

                            if mode == 4:  # TRIANGLES
                                if len(indices) % 3 != 0:
                                    logger.warning(
                                        f"Triangle indices count {len(indices)} is not "
                                        f"divisible by 3 in mesh {mesh_idx}"
                                    )
                                    faces = indices[: len(indices) // 3 * 3].reshape(-1, 3)
                                else:
                                    faces = indices.reshape(-1, 3)
                            elif mode == 5:  # TRIANGLE_STRIP
                                # Convert triangle strip to triangles
                                strip = indices
                                faces = []
                                for i in range(len(strip) - 2):
                                    if i % 2 == 0:
                                        faces.append([strip[i], strip[i + 1], strip[i + 2]])
                                    else:
                                        faces.append([strip[i + 1], strip[i], strip[i + 2]])
                                faces = np.array(faces, dtype=np.uint32)
                            else:
                                logger.warning(
                                    f"Unsupported primitive mode {mode} in mesh {mesh_idx}, "
                                    f"using vertex positions as point cloud"
                                )
                                # Fall back to point cloud
                                faces = np.arange(len(positions), dtype=np.uint32).reshape(-1, 1)

                        except Exception as e:
                            logger.warning(f"Error processing indices for mesh {mesh_idx}: {e!s}")
                            # Fall back to non-indexed geometry
                            faces = np.arange(len(positions), dtype=np.uint32).reshape(-1, 1)
                else:
                    # No indices provided, create non-indexed geometry
                    logger.debug(f"Mesh {mesh_idx} has no indices, creating non-indexed geometry")
                    faces = np.arange(len(positions), dtype=np.uint32).reshape(-1, 1)

                # Validate and fix face indices to prevent PyVista errors
                if faces is not None and len(faces) > 0:
                    faces = cls._validate_faces(faces, len(positions), mesh_idx)

                # Create the mesh
                vrm_mesh = VRMMesh(
                    name=f"mesh_{len(meshes)}",
                    vertices=positions,
                    faces=faces if faces is not None else np.array([], dtype=np.uint32).reshape(0, 3),
                    normals=normals,
                    texcoords=tex_coords,
                    material_index=getattr(primitive, "material", None),
                )

                # Set name if available
                if hasattr(gltf_mesh, "name") and gltf_mesh.name:
                    vrm_mesh.name = gltf_mesh.name.strip() or f"mesh_{len(meshes)}"

                # Store additional data as attributes
                vrm_mesh.attributes = {}
                if joint_indices is not None:
                    vrm_mesh.attributes["joint_indices"] = joint_indices
                if joint_weights is not None:
                    vrm_mesh.attributes["joint_weights"] = joint_weights

                meshes.append(vrm_mesh)

            except Exception as e:
                logger.error(f"Error loading mesh {mesh_idx}: {e!s}", exc_info=True)
                continue

        return meshes

    @classmethod
    def _load_armature(cls, gltf: GLTF2) -> dict[str, VRMBone]:
        """Load the armature (skeleton) from the GLTF file.

        Args:
            gltf: The loaded GLTF2 object

        Returns:
            Dictionary mapping bone names to VRMBone objects
        """
        bones = {}

        # Check if we have any skins (armatures)
        if not hasattr(gltf, "skins") or not gltf.skins:
            logger.debug("No skins found in GLTF file")
            return bones

        try:
            # For now, just handle the first skin
            skin = gltf.skins[0]

            # Get the joint indices and inverse bind matrices
            joint_indices = getattr(skin, "joints", [])

            # Get the inverse bind matrices if available
            inverse_bind_matrices = None
            if hasattr(skin, "inverseBindMatrices") and skin.inverseBindMatrices is not None:
                inverse_bind_data = cls._get_accessor_data(gltf, skin.inverseBindMatrices)
                if inverse_bind_data is not None:
                    try:
                        inverse_bind_matrices = np.array(inverse_bind_data, dtype=np.float32).reshape(-1, 4, 4)
                    except Exception as e:
                        logger.warning(f"Error processing inverse bind matrices: {e!s}")

            # Create a mapping from node index to bone name
            node_to_bone = {}

            # First pass: create all bones
            for i, joint_idx in enumerate(joint_indices):
                if joint_idx >= len(gltf.nodes):
                    logger.warning(f"Joint index {joint_idx} out of range, skipping")
                    continue

                node = gltf.nodes[joint_idx]

                # Get bone name
                if hasattr(node, "name") and node.name:
                    bone_name = node.name.strip()
                else:
                    bone_name = f"bone_{i}"

                # Get transform
                translation = (
                    tuple(node.translation)
                    if hasattr(node, "translation") and node.translation is not None
                    else (0.0, 0.0, 0.0)
                )
                rotation = (
                    tuple(node.rotation)
                    if hasattr(node, "rotation") and node.rotation is not None
                    else (0.0, 0.0, 0.0, 1.0)
                )
                scale = tuple(node.scale) if hasattr(node, "scale") and node.scale is not None else (1.0, 1.0, 1.0)

                # Get inverse bind matrix if available
                inv_bind_matrix = None
                if inverse_bind_matrices is not None and i < len(inverse_bind_matrices):
                    inv_bind_matrix = inverse_bind_matrices[i].tolist()

                # Create the bone
                bone = VRMBone(
                    name=bone_name,
                    parent=None,  # Will be set in the second pass
                    position=translation,
                    rotation=rotation,
                    scale=scale,
                )

                # Store additional data
                bone.node_index = joint_idx
                if inv_bind_matrix is not None:
                    bone.inverse_bind_matrix = inv_bind_matrix

                # Add to dictionaries
                bones[bone_name] = bone
                node_to_bone[joint_idx] = bone_name

            # Second pass: set up parent-child relationships
            for joint_idx, bone_name in node_to_bone.items():
                node = gltf.nodes[joint_idx]

                # Find parent node
                if hasattr(node, "children") and node.children:
                    # In GLTF, nodes have children, but we need to find the parent
                    for child_idx in node.children:
                        if child_idx in node_to_bone:
                            child_bone = bones[node_to_bone[child_idx]]
                            child_bone.parent = bone_name

                # Handle skin root bone
                if hasattr(skin, "skeleton") and skin.skeleton is not None and joint_idx == skin.skeleton:
                    bones[bone_name].is_root = True

            # If we have a skeleton root, mark it
            if hasattr(skin, "skeleton") and skin.skeleton is not None and skin.skeleton in node_to_bone:
                root_bone_name = node_to_bone[skin.skeleton]
                bones[root_bone_name].is_root = True

            logger.info(f"Loaded {len(bones)} bones for armature")

        except Exception as e:
            logger.error(f"Error loading armature: {e!s}", exc_info=True)

        return bones

    @classmethod
    def _load_blend_shapes(cls, gltf: GLTF2, meshes: list[VRMMesh]) -> list[VRMBlendShape]:
        """Load blend shapes (morph targets) from the GLTF file.

        Args:
            gltf: The loaded GLTF2 object
            meshes: List of loaded VRMMesh objects

        Returns:
            List of VRMBlendShape objects
        """
        blend_shapes = []

        # Check if we have any meshes with morph targets
        if not hasattr(gltf, "meshes") or not gltf.meshes:
            logger.debug("No meshes found for blend shapes")
            return blend_shapes

        # First, check for VRM blend shape groups if available
        vrm_blend_shape_groups = {}
        if hasattr(gltf, "extensions") and gltf.extensions and "VRM" in gltf.extensions:
            vrm_ext = gltf.extensions["VRM"]
            if "blendShapeMaster" in vrm_ext and "blendShapeGroups" in vrm_ext["blendShapeMaster"]:
                for group in vrm_ext["blendShapeMaster"]["blendShapeGroups"]:
                    if "name" in group and "binds" in group and group["binds"]:
                        vrm_blend_shape_groups[group["name"]] = group

        # Process each mesh
        for mesh_idx, gltf_mesh in enumerate(gltf.meshes):
            try:
                if not hasattr(gltf_mesh, "primitives") or not gltf_mesh.primitives:
                    continue

                # For now, just handle the first primitive of each mesh
                primitive = gltf_mesh.primitives[0]

                # Check for morph targets
                if not hasattr(primitive, "targets") or not primitive.targets:
                    continue

                # Get the mesh name for better blend shape naming
                mesh_name = getattr(gltf_mesh, "name", f"mesh_{mesh_idx}")

                # Process each target (blend shape)
                for target_idx, target in enumerate(primitive.targets):
                    try:
                        # Default blend shape name
                        blend_shape_name = f"blendshape_{len(blend_shapes)}"

                        # Try to get a better name from VRM extensions
                        if mesh_name in vrm_blend_shape_groups:
                            group = vrm_blend_shape_groups[mesh_name]
                            if target_idx < len(group.get("binds", [])):
                                bind = group["binds"][target_idx]
                                if "mesh" in bind and bind["mesh"] == mesh_idx and "index" in bind:
                                    if "name" in group:
                                        blend_shape_name = group["name"]

                        # Check if we already have a blend shape with this name
                        existing_idx = next(
                            (i for i, bs in enumerate(blend_shapes) if bs.name == blend_shape_name),
                            -1,
                        )

                        if existing_idx >= 0:
                            # Use existing blend shape
                            blend_shape = blend_shapes[existing_idx]
                        else:
                            # Create a new blend shape
                            is_binary = False
                            category = "custom"

                            # Check VRM preset categories
                            if blend_shape_name.lower() in [
                                "a",
                                "i",
                                "u",
                                "e",
                                "o",
                            ]:  # Common viseme presets
                                category = "viseme"
                            elif blend_shape_name.lower() in [
                                "neutral",
                                "joy",
                                "angry",
                                "sorrow",
                                "fun",
                            ]:
                                category = "preset"

                            blend_shape = VRMBlendShape(name=blend_shape_name, category=category, is_binary=is_binary)
                            blend_shapes.append(blend_shape)

                        # Process position deltas (morph target)
                        if "POSITION" in target and target["POSITION"] is not None:
                            positions = cls._get_accessor_data(gltf, target["POSITION"])
                            if positions is not None:
                                try:
                                    deltas = np.array(positions, dtype=np.float32)
                                    if len(deltas.shape) == 2 and deltas.shape[1] == 3:
                                        blend_shape.morph_targets[mesh_idx] = deltas
                                    else:
                                        logger.warning(
                                            f"Invalid position deltas shape {deltas.shape} "
                                            f"for blend shape {blend_shape_name}"
                                        )
                                except Exception as e:
                                    logger.warning(
                                        f"Error processing position deltas for blend shape {blend_shape_name}: {e!s}"
                                    )

                        # Process normal deltas if available
                        if "NORMAL" in target and target["NORMAL"] is not None:
                            normals = cls._get_accessor_data(gltf, target["NORMAL"])
                            if normals is not None:
                                try:
                                    normal_deltas = np.array(normals, dtype=np.float32)
                                    if len(normal_deltas.shape) == 2 and normal_deltas.shape[1] == 3:
                                        if not hasattr(blend_shape, "normal_deltas"):
                                            blend_shape.normal_deltas = {}
                                        blend_shape.normal_deltas[mesh_idx] = normal_deltas
                                except Exception as e:
                                    logger.warning(
                                        f"Error processing normal deltas for blend shape {blend_shape_name}: {e!s}"
                                    )

                        # Process tangent deltas if available
                        if "TANGENT" in target and target["TANGENT"] is not None:
                            tangents = cls._get_accessor_data(gltf, target["TANGENT"])
                            if tangents is not None:
                                try:
                                    tangent_deltas = np.array(tangents, dtype=np.float32)
                                    if len(tangent_deltas.shape) == 2 and tangent_deltas.shape[1] == 3:
                                        if not hasattr(blend_shape, "tangent_deltas"):
                                            blend_shape.tangent_deltas = {}
                                        blend_shape.tangent_deltas[mesh_idx] = tangent_deltas
                                except Exception as e:
                                    logger.warning(
                                        f"Error processing tangent deltas for blend shape {blend_shape_name}: {e!s}"
                                    )

                    except Exception as e:
                        logger.error(
                            f"Error processing blend shape target {target_idx} for mesh {mesh_idx}: {e!s}",
                            exc_info=True,
                        )
                        continue

            except Exception as e:
                logger.error(f"Error processing mesh {mesh_idx} for blend shapes: {e!s}", exc_info=True)
                continue

        logger.info(f"Loaded {len(blend_shapes)} blend shapes")
        return blend_shapes

    def _parse_vrm_extension(self, vrm_data: dict):
        """Parse VRM-specific extension data."""
        # Parse humanoid data
        if "humanoid" in vrm_data:
            self.humanoid = VRMHumanoid(**vrm_data["humanoid"])

        # Parse first-person data
        if "firstPerson" in vrm_data:
            self.first_person = VRMFirstPerson()
            fp_data = vrm_data["firstPerson"]

            if "firstPersonBone" in fp_data:
                self.first_person.first_person_bone = fp_data["firstPersonBone"]
                self.first_person.first_person_bone_offset = fp_data.get("firstPersonBoneOffset", [0, 0, 0])

            # Parse look-at settings
            if "lookAtTypeName" in fp_data:
                self.first_person.look_at_type_name = fp_data["lookAtTypeName"]

            # Parse blend shape settings if using blend shapes for look-at
            if "lookAtBlendShapeName" in fp_data:
                self.first_person.look_at_type_name = "BlendShape"
                # Additional processing for blend shape look-at

    def get_blend_shape_names(self) -> list[str]:
        """Get a list of all blend shape names."""
        return [bs.name for bs in self.blend_shapes]

    def get_bone_names(self) -> list[str]:
        """Get a list of all bone names."""
        return list(self.bones.keys())

    def get_material_names(self) -> list[str]:
        """Get a list of all material names."""
        return [mat.name for mat in self.materials]

    def get_texture_data(self, index: int) -> bytes | None:
        """Get the raw texture data for a texture index."""
        if 0 <= index < len(self.textures):
            return self.textures[index].data
        return None
