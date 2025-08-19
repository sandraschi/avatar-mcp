"""
VRM 2.0 Loader

This module provides functionality to load and parse VRM 2.0 files,
extracting model data, materials, and animations using pygltflib and trimesh.
"""
import json
import logging
import struct
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, BinaryIO

import numpy as np
import trimesh
from pygltflib import GLTF2, BufferFormat, BUFFERVIEW_TARGETS, COMPONENT_TYPES

logger = logging.getLogger(__name__)

class VRMFileType(Enum):
    """Supported VRM file types."""
    GLB = "glb"
    VRM = "vrm"

@dataclass
class VRMModel:
    """Represents a loaded VRM model with all its components."""
    meshes: List['VRMMesh'] = field(default_factory=list)
    materials: List['VRMMaterial'] = field(default_factory=list)
    textures: List['VRMTexture'] = field(default_factory=list)
    blend_shapes: List['VRMBlendShape'] = field(default_factory=list)
    bones: Dict[str, 'VRMBone'] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VRMMesh:
    """Represents a mesh in a VRM model."""
    name: str
    vertices: np.ndarray  # Nx3 array of vertex positions
    faces: np.ndarray     # Mx3 array of triangle indices
    normals: Optional[np.ndarray] = None
    texcoords: Optional[np.ndarray] = None
    material_index: Optional[int] = None

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
    base_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    metallic_factor: float = 1.0
    roughness_factor: float = 1.0
    emissive_factor: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    alpha_mode: str = "OPAQUE"
    alpha_cutoff: float = 0.5
    double_sided: bool = False
    texture_indices: Dict[str, int] = field(default_factory=dict)

@dataclass
class VRMBlendShape:
    """Represents a blend shape (morph target) in a VRM model."""
    name: str
    category: str  # e.g., "preset", "custom"
    is_binary: bool = False
    weight: float = 0.0
    # Maps from mesh index to vertex deltas
    morph_targets: Dict[int, np.ndarray] = field(default_factory=dict)

@dataclass
class VRMBone:
    """Represents a bone in the VRM humanoid rig."""
    name: str
    parent: Optional[str]
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # quaternion (x, y, z, w)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)

class VRMLoader:
    """Loads and parses VRM 2.0 files using pygltflib and trimesh."""
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> VRMModel:
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
            raise FileNotFoundError(f"VRM file not found: {file_path}")
        
        # Load the GLTF/GLB file
        gltf = GLTF2().load(str(path.absolute()))
        
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
    def _extract_metadata(gltf: GLTF2) -> Dict[str, Any]:
        """Extract metadata from the GLTF file."""
        metadata = {
            'version': '2.0',
            'generator': gltf.asset.generator if hasattr(gltf.asset, 'generator') else 'Unknown',
            'copyright': getattr(gltf.asset, 'copyright', ''),
            'extensions': {}
        }
        
        # Extract VRM extension if present
        if hasattr(gltf, 'extensions') and 'VRM' in gltf.extensions:
            metadata['extensions']['VRM'] = gltf.extensions['VRM']
            
        return metadata
    
    @staticmethod
    def _load_textures(gltf: GLTF2) -> List[VRMTexture]:
        """Load textures from the GLTF file."""
        textures = []
        
        if not hasattr(gltf, 'textures') or not gltf.textures:
            return textures
            
        for tex_idx, tex in enumerate(gltf.textures):
            # Skip if no source image
            if not hasattr(tex, 'source') or tex.source is None:
                continue
                
            # Get the source image
            img = gltf.images[tex.source]
            
            # Create texture data
            texture = VRMTexture(
                name=f"texture_{len(textures)}",
                data=img.data,
                mime_type=img.mimeType,
                width=getattr(img, 'width', 0),
                height=getattr(img, 'height', 0)
            )
            
            if hasattr(tex, 'name') and tex.name:
                texture.name = tex.name
                
            textures.append(texture)
            
        return textures
    
    @staticmethod
    def _load_materials(gltf: GLTF2, textures: List[VRMMaterial]) -> List[VRMMaterial]:
        """Load materials from the GLTF file."""
        materials = []
        
        if not hasattr(gltf, 'materials') or not gltf.materials:
            return materials
            
        for mat_idx, mat in enumerate(gltf.materials):
            # Create base material
            material = VRMMaterial(
                name=f"material_{len(materials)}",
                alpha_mode=getattr(mat, 'alphaMode', 'OPAQUE'),
                alpha_cutoff=getattr(mat, 'alphaCutoff', 0.5),
                double_sided=getattr(mat, 'doubleSided', False)
            )
            
            # Set name if available
            if hasattr(mat, 'name') and mat.name:
                material.name = mat.name
                
            # Handle PBR material properties
            if hasattr(mat, 'pbrMetallicRoughness'):
                pbr = mat.pbrMetallicRoughness
                
                # Base color
                if hasattr(pbr, 'baseColorFactor') and pbr.baseColorFactor:
                    material.base_color = tuple(pbr.baseColorFactor)
                    
                # Metallic and roughness
                material.metallic_factor = getattr(pbr, 'metallicFactor', 1.0)
                material.roughness_factor = getattr(pbr, 'roughnessFactor', 1.0)
                
                # Textures
                if hasattr(pbr, 'baseColorTexture') and pbr.baseColorTexture:
                    material.texture_indices['baseColor'] = pbr.baseColorTexture.index
                    
                if hasattr(pbr, 'metallicRoughnessTexture') and pbr.metallicRoughnessTexture:
                    material.texture_indices['metallicRoughness'] = pbr.metallicRoughnessTexture.index
            
            # Handle emissive factor
            if hasattr(mat, 'emissiveFactor') and mat.emissiveFactor:
                material.emissive_factor = tuple(mat.emissiveFactor)
                
            # Handle normal map
            if hasattr(mat, 'normalTexture') and mat.normalTexture:
                material.texture_indices['normal'] = mat.normalTexture.index
                
            # Handle occlusion map
            if hasattr(mat, 'occlusionTexture') and mat.occlusionTexture:
                material.texture_indices['occlusion'] = mat.occlusionTexture.index
                
            # Handle emissive texture
            if hasattr(mat, 'emissiveTexture') and mat.emissiveTexture:
                material.texture_indices['emissive'] = mat.emissiveTexture.index
                
            materials.append(material)
            
        return materials
    
    @staticmethod
    def _load_meshes(gltf: GLTF2) -> List[VRMMesh]:
        """Load meshes from the GLTF file."""
        meshes = []
        
        if not hasattr(gltf, 'meshes') or not gltf.meshes:
            return meshes
            
        for mesh_idx, mesh in enumerate(gltf.meshes):
            # Skip if no primitives
            if not hasattr(mesh, 'primitives') or not mesh.primitives:
                continue
                
            # For now, just handle the first primitive
            primitive = mesh.primitives[0]
            
            # Get vertex positions
            positions = None
            if 'POSITION' in primitive.attributes:
                accessor = gltf.accessors[primitive.attributes['POSITION']]
                buffer_view = gltf.bufferViews[accessor.bufferView]
                buffer = gltf.buffers[buffer_view.buffer]
                
                # Extract position data
                positions = np.frombuffer(
                    buffer.data,
                    dtype=np.float32,
                    count=accessor.count * 3,
                    offset=buffer_view.byteOffset + (accessor.byteOffset or 0)
                ).reshape(-1, 3)
            
            # Get faces (indices)
            faces = None
            if hasattr(primitive, 'indices') and primitive.indices is not None:
                accessor = gltf.accessors[primitive.indices]
                buffer_view = gltf.bufferViews[accessor.bufferView]
                buffer = gltf.buffers[buffer_view.buffer]
                
                # Determine the data type
                if accessor.componentType == 5123:  # UNSIGNED_SHORT
                    dtype = np.uint16
                elif accessor.componentType == 5125:  # UNSIGNED_INT
                    dtype = np.uint32
                else:  # Default to unsigned short
                    dtype = np.uint16
                
                # Extract index data
                indices = np.frombuffer(
                    buffer.data,
                    dtype=dtype,
                    count=accessor.count,
                    offset=buffer_view.byteOffset + (accessor.byteOffset or 0)
                )
                
                # Reshape to triangles
                faces = indices.reshape(-1, 3)
            
            # Create the mesh
            if positions is not None and faces is not None:
                vrm_mesh = VRMMesh(
                    name=f"mesh_{len(meshes)}",
                    vertices=positions,
                    faces=faces,
                    material_index=getattr(primitive, 'material', None)
                )
                
                # Set name if available
                if hasattr(mesh, 'name') and mesh.name:
                    vrm_mesh.name = mesh.name
                    
                meshes.append(vrm_mesh)
        
        return meshes
    
    @staticmethod
    def _load_armature(gltf: GLTF2) -> Dict[str, VRMBone]:
        """Load the armature (skeleton) from the GLTF file."""
        bones = {}
        
        # Check if we have skins (armatures)
        if not hasattr(gltf, 'skins') or not gltf.skins:
            return bones
            
        # For simplicity, just handle the first skin
        skin = gltf.skins[0]
        
        # Get the joint names
        joint_names = []
        if hasattr(skin, 'joints') and skin.joints:
            joint_names = [gltf.nodes[joint].name for joint in skin.joints 
                          if hasattr(gltf.nodes[joint], 'name') and gltf.nodes[joint].name]
        
        # Create bone entries
        for i, joint_idx in enumerate(skin.joints):
            node = gltf.nodes[joint_idx]
            
            # Get parent bone index if it exists
            parent = None
            if hasattr(skin, 'skeleton') and skin.skeleton is not None:
                # This is a simplification - in a real implementation, you'd need to traverse the node hierarchy
                pass
                
            # Create the bone
            bone = VRMBone(
                name=node.name if hasattr(node, 'name') and node.name else f"bone_{i}",
                parent=parent,
                position=tuple(node.translation) if hasattr(node, 'translation') else (0.0, 0.0, 0.0),
                rotation=tuple(node.rotation) if hasattr(node, 'rotation') else (0.0, 0.0, 0.0, 1.0),
                scale=tuple(node.scale) if hasattr(node, 'scale') else (1.0, 1.0, 1.0)
            )
            
            bones[bone.name] = bone
        
        return bones
    
    @staticmethod
    def _load_blend_shapes(gltf: GLTF2, meshes: List[VRMMesh]) -> List[VRMBlendShape]:
        """Load blend shapes (morph targets) from the GLTF file."""
        blend_shapes = []
        
        # Check if we have any meshes with morph targets
        if not hasattr(gltf, 'meshes') or not gltf.meshes:
            return blend_shapes
            
        for mesh_idx, mesh in enumerate(gltf.meshes):
            if not hasattr(mesh, 'primitives') or not mesh.primitives:
                continue
                
            primitive = mesh.primitives[0]
            
            # Check for morph targets
            if not hasattr(primitive, 'targets') or not primitive.targets:
                continue
                
            for target_idx, target in enumerate(primitive.targets):
                # Create a blend shape for each target
                blend_shape = VRMBlendShape(
                    name=f"blendshape_{len(blend_shapes)}",
                    category="custom",
                    is_binary=False
                )
                
                # Get the position deltas
                if 'POSITION' in target:
                    accessor = gltf.accessors[target['POSITION']]
                    buffer_view = gltf.bufferViews[accessor.bufferView]
                    buffer = gltf.buffers[buffer_view.buffer]
                    
                    # Extract position deltas
                    deltas = np.frombuffer(
                        buffer.data,
                        dtype=np.float32,
                        count=accessor.count * 3,
                        offset=buffer_view.byteOffset + (accessor.byteOffset or 0)
                    ).reshape(-1, 3)
                    
                    # Store the deltas for this mesh
                    blend_shape.morph_targets[mesh_idx] = deltas
                
                blend_shapes.append(blend_shape)
        
        return blend_shapes
    
    def _parse_vrm_extension(self, vrm_data: Dict):
        """Parse VRM-specific extension data."""
        # Parse humanoid data
        if 'humanoid' in vrm_data:
            self.humanoid = VRMHumanoid(**vrm_data['humanoid'])
            
        # Parse first-person data
        if 'firstPerson' in vrm_data:
            self.first_person = VRMFirstPerson()
            fp_data = vrm_data['firstPerson']
            
            if 'firstPersonBone' in fp_data:
                self.first_person.first_person_bone = fp_data['firstPersonBone']
                self.first_person.first_person_bone_offset = fp_data.get(
                    'firstPersonBoneOffset', [0, 0, 0])
            
            # Parse look-at settings
            if 'lookAtTypeName' in fp_data:
                self.first_person.look_at_type_name = fp_data['lookAtTypeName']
                
            # Parse blend shape settings if using blend shapes for look-at
            if 'lookAtBlendShapeName' in fp_data:
                self.first_person.look_at_type_name = 'BlendShape'
                # Additional processing for blend shape look-at
    
    def get_blend_shape_names(self) -> List[str]:
        """Get a list of all blend shape names."""
        return [bs.name for bs in self.blend_shapes]
    
    def get_bone_names(self) -> List[str]:
        """Get a list of all bone names."""
        return list(self.bones.keys())
    
    def get_material_names(self) -> List[str]:
        """Get a list of all material names."""
        return [mat.name for mat in self.materials]
    
    def get_texture_data(self, index: int) -> Optional[bytes]:
        """Get the raw texture data for a texture index."""
        if 0 <= index < len(self.textures):
            return self.textures[index].data
        return None
