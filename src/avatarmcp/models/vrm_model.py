"""
VRM Model class for handling VRM avatar data and operations.
"""
from typing import Dict, Any, List, Optional, Tuple
import os
import json

import numpy as np
from pygltflib import GLTF2

class VRMModel:
    """Class representing a loaded VRM model."""
    
    def __init__(self, file_path: str):
        """Initialize a VRM model from a file.
        
        Args:
            file_path: Path to the VRM file
        """
        self.file_path = file_path
        self.model_id = self._generate_model_id(file_path)
        self.metadata: Dict[str, Any] = {}
        self.gltf: Optional[GLTF2] = None
        self._load_model()
    
    def _generate_model_id(self, file_path: str) -> str:
        """Generate a unique ID for the model based on the file path."""
        base_name = os.path.basename(file_path)
        name, _ = os.path.splitext(base_name)
        return f"{name}_{id(self)}"
    
    def _load_model(self):
        """Load the VRM model from file."""
        try:
            self.gltf = GLTF2().load(self.file_path)
            self._extract_metadata()
        except Exception as e:
            raise ValueError(f"Failed to load VRM model: {str(e)}")
    
    def _extract_metadata(self):
        """Extract metadata from the VRM model."""
        if not self.gltf:
            return
            
        self.metadata = {
            "name": "Unnamed VRM",
            "version": "1.0",
            "bones": [],
            "materials": [],
            "textures": []
        }
        
        # Extract VRM extension data if available
        if hasattr(self.gltf, 'extensions') and 'VRM' in self.gltf.extensions:
            vrm_data = self.gltf.extensions['VRM']
            if 'meta' in vrm_data:
                self.metadata.update({
                    "name": vrm_data['meta'].get('title', 'Unnamed VRM'),
                    "version": vrm_data['meta'].get('version', '1.0'),
                    "author": vrm_data['meta'].get('author', 'Unknown'),
                    "reference": vrm_data['meta'].get('reference', '')
                })
    
    def get_blend_shape_names(self) -> List[str]:
        """Get a list of all blend shape names in the model."""
        if not self.gltf or not hasattr(self.gltf, 'extensions') or 'VRM' not in self.gltf.extensions:
            return []
            
        vrm = self.gltf.extensions['VRM']
        if 'blendShapeMaster' not in vrm or 'blendShapeGroups' not in vrm['blendShapeMaster']:
            return []
            
        return [group.get('name', '') for group in vrm['blendShapeMaster']['blendShapeGroups']]
    
    def get_bone_names(self) -> List[str]:
        """Get a list of all bone names in the model."""
        if not self.gltf or not hasattr(self.gltf, 'nodes'):
            return []
            
        return [node.name for node in self.gltf.nodes if node.name]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary representation."""
        return {
            "model_id": self.model_id,
            "name": self.metadata.get('name', 'Unnamed VRM'),
            "version": self.metadata.get('version', '1.0'),
            "num_bones": len(self.metadata.get('bones', [])),
            "num_materials": len(self.metadata.get('materials', [])),
            "num_blend_shapes": len(self.get_blend_shape_names()),
            "file_path": self.file_path
        }
