"""
VRM 2.0 Loader

This module provides functionality to load and parse VRM 2.0 files,
extracting model data, materials, and animations.
"""
import json
import struct
import zlib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, BinaryIO, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VRMFileType(Enum):
    """Supported VRM file types."""
    GLB = "glb"
    VRM = "vrm"
    
class VRMVersion(Enum):
    """VRM specification versions."""
    VRM_2_0 = "2.0"
    VRM_1_0 = "1.0"
    VRM_0_X = "0.x"

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
    shader: str
    properties: Dict[str, Any]
    texture_indices: Dict[str, int] = field(default_factory=dict)

@dataclass
class VRMBlendShape:
    """Represents a blend shape (morph target) in a VRM model."""
    name: str
    preset: str  # e.g., "neutral", "a", "i", "u", "e", "o"
    is_binary: bool
    weight: float = 0.0
    bind_poses: Optional[Dict[str, List[float]]] = None
    delta_normals: Optional[Dict[str, List[float]]] = None
    delta_vertices: Optional[Dict[str, List[float]]] = None

@dataclass
class VRMBone:
    """Represents a bone in the VRM humanoid rig."""
    name: str
    parent: Optional[str]
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float, float]  # quaternion (x, y, z, w)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)

@dataclass
class VRMHumanoid:
    """Represents the humanoid configuration of a VRM model."""
    arm_stretch: float = 0.05
    leg_stretch: float = 0.05
    upper_arm_twist: float = 0.5
    lower_arm_twist: float = 0.5
    upper_leg_twist: float = 0.5
    lower_leg_twist: float = 0.5
    feet_spacing: float = 0.0
    has_translation_dof: bool = False

@dataclass
class VRMFirstPerson:
    """First-person view configuration for VRM models."""
    first_person_bone: str = ""
    first_person_bone_offset: Tuple[float, float, float] = (0, 0, 0)
    mesh_annotations: List[Dict] = field(default_factory=list)
    look_at_type_name: str = "Bone"  # "Bone" or "BlendShape"
    look_at_horizontal_inner: Dict = field(default_factory=dict)
    look_at_horizontal_outer: Dict = field(default_factory=dict)
    look_at_vertical_down: Dict = field(default_factory=dict)
    look_at_vertical_up: Dict = field(default_factory=dict)

class VRMLoader:
    """Loads and parses VRM 2.0 files."""
    
    def __init__(self):
        self.textures: List[VRMTexture] = []
        self.materials: List[VRMMaterial] = []
        self.blend_shapes: List[VRMBlendShape] = []
        self.bones: Dict[str, VRMBone] = {}
        self.humanoid: Optional[VRMHumanoid] = None
        self.first_person: Optional[VRMFirstPerson] = None
        self.metadata: Dict[str, Any] = {}
        
    @classmethod
    def from_file(cls, file_path: str) -> 'VRMLoader':
        """Load a VRM model from a file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"VRM file not found: {file_path}")
            
        loader = cls()
        
        # Check file extension
        ext = path.suffix.lower()
        if ext == '.vrm':
            loader._load_vrm(path)
        elif ext == '.glb':
            loader._load_glb(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        return loader
    
    def _load_vrm(self, file_path: Path):
        """Load a .vrm file (GLB with VRM extension)."""
        with open(file_path, 'rb') as f:
            # Read GLB header
            magic = f.read(4)
            if magic != b'glTF':
                raise ValueError("Invalid GLB file")
                
            version = struct.unpack('<I', f.read(4))[0]
            length = struct.unpack('<I', f.read(4))[0]
            
            # Read chunks
            while f.tell() < length:
                chunk_length = struct.unpack('<I', f.read(4))[0]
                chunk_type = f.read(4).decode('ascii')
                chunk_data = f.read(chunk_length)
                
                if chunk_type == 'JSON':
                    self._parse_gltf_json(chunk_data.decode('utf-8'))
                elif chunk_type == 'BIN\x00':
                    self._parse_binary_data(chunk_data)
                    
        # Process VRM extensions
        if 'extensions' in self.metadata and 'VRM' in self.metadata['extensions']:
            self._parse_vrm_extension(self.metadata['extensions']['VRM'])
    
    def _load_glb(self, file_path: Path):
        """Load a standard GLB file with VRM extensions."""
        # Similar to _load_vrm but with different expectations
        self._load_vrm(file_path)
    
    def _parse_gltf_json(self, json_str: str):
        """Parse the GLTF JSON data."""
        self.metadata = json.loads(json_str)
        
        # Process materials
        for mat_data in self.metadata.get('materials', []):
            self._parse_material(mat_data)
            
        # Process textures and images
        for tex_data in self.metadata.get('textures', []):
            self._parse_texture(tex_data)
    
    def _parse_material(self, mat_data: Dict):
        """Parse a material definition."""
        material = VRMMaterial(
            name=mat_data.get('name', f"material_{len(self.materials)}"),
            shader=mat_data.get('extensions', {}).get('KHR_materials_pbrSpecularGlossiness', {}).get('shader', 'pbr'),
            properties=mat_data
        )
        
        # Extract texture references
        if 'pbrMetallicRoughness' in mat_data:
            pbr = mat_data['pbrMetallicRoughness']
            if 'baseColorTexture' in pbr:
                material.texture_indices['baseColor'] = pbr['baseColorTexture']['index']
            if 'metallicRoughnessTexture' in pbr:
                material.texture_indices['metallicRoughness'] = pbr['metallicRoughnessTexture']['index']
                
        self.materials.append(material)
    
    def _parse_texture(self, tex_data: Dict):
        """Parse a texture definition."""
        # In a real implementation, this would load the actual texture data
        # For now, we'll just create a placeholder
        texture = VRMTexture(
            name=f"texture_{len(self.textures)}",
            data=bytes(),
            mime_type="image/png"  # Default, would be determined from actual data
        )
        self.textures.append(texture)
    
    def _parse_binary_data(self, data: bytes):
        """Parse binary data chunk."""
        # In a full implementation, this would process the binary data
        # and associate it with the appropriate textures, meshes, etc.
        pass
    
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
