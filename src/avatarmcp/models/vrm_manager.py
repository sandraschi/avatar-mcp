"""
VRM Manager

This module provides tools for managing VRM models, including loading, processing,
and converting between different formats. It supports both humanoid and non-humanoid
(animal/creature) VRM models.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
import aiofiles

logger = logging.getLogger(__name__)

@dataclass
class VRMMetadata:
    """Metadata for a VRM model."""
    name: str
    version: str
    author: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    is_humanoid: bool = True
    model_type: str = "humanoid"  # humanoid, quadruped, winged, etc.
    required_parameters: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)

class VRMManager:
    """Manages VRM models for use in VRChat and other platforms."""
    
    def __init__(self, models_dir: Optional[str] = None):
        """Initialize the VRM manager.
        
        Args:
            models_dir: Directory where VRM models are stored
        """
        self.models_dir = models_dir or os.path.join(Path.home(), ".avatarmcp", "models")
        self.models: Dict[str, Dict] = {}
        self.metadata_cache: Dict[str, VRMMetadata] = {}
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
    
    async def scan_models(self) -> List[str]:
        """Scan the models directory for VRM files.
        
        Returns:
            List of model IDs found
        """
        self.models = {}
        model_ids = []
        
        for root, _, files in os.walk(self.models_dir):
            for filename in files:
                if filename.lower().endswith('.vrm'):
                    model_id = os.path.splitext(filename)[0]
                    model_path = os.path.join(root, filename)
                    self.models[model_id] = {
                        'path': model_path,
                        'id': model_id,
                        'filename': filename,
                        'directory': root
                    }
                    model_ids.append(model_id)
                    
                    # Load metadata if available
                    metadata_path = os.path.join(root, f"{model_id}.meta.json")
                    if os.path.exists(metadata_path):
                        try:
                            async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as f:
                                metadata = json.loads(await f.read())
                                self.metadata_cache[model_id] = VRMMetadata(**metadata)
                        except Exception as e:
                            logger.error(f"Error loading metadata for {model_id}: {e}")
        
        return model_ids
    
    async def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get information about a specific model.
        
        Args:
            model_id: ID of the model to get info for
            
        Returns:
            Dictionary with model information, or None if not found
        """
        if not self.models:
            await self.scan_models()
            
        model_info = self.models.get(model_id)
        if not model_info:
            return None
            
        # Add metadata if available
        metadata = self.metadata_cache.get(model_id)
        if metadata:
            model_info['metadata'] = metadata.__dict__
            
        return model_info
    
    async def load_model(self, model_id: str) -> Dict:
        """Load a VRM model.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            Dictionary with model data and metadata
        """
        model_info = await self.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model not found: {model_id}")
            
        # In a real implementation, this would load the actual VRM data
        # For now, we'll just return the model info
        return {
            'status': 'success',
            'model_id': model_id,
            'path': model_info['path'],
            'metadata': model_info.get('metadata', {})
        }
    
    async def import_model(self, vrm_path: str, metadata: Optional[Dict] = None) -> str:
        """Import a VRM model into the models directory.
        
        Args:
            vrm_path: Path to the VRM file to import
            metadata: Optional metadata for the model
            
        Returns:
            ID of the imported model
        """
        if not os.path.exists(vrm_path):
            raise FileNotFoundError(f"VRM file not found: {vrm_path}")
            
        # Generate model ID from filename
        model_id = os.path.splitext(os.path.basename(vrm_path))[0]
        
        # Create a clean ID (alphanumeric + underscores)
        import re
        model_id = re.sub(r'[^a-zA-Z0-9_]', '_', model_id)
        
        # Ensure the model ID is unique
        counter = 1
        original_id = model_id
        while os.path.exists(os.path.join(self.models_dir, f"{model_id}.vrm")):
            model_id = f"{original_id}_{counter}"
            counter += 1
        
        # Copy the VRM file
        import shutil
        dest_path = os.path.join(self.models_dir, f"{model_id}.vrm")
        shutil.copy2(vrm_path, dest_path)
        
        # Save metadata if provided
        if metadata:
            metadata_path = os.path.join(self.models_dir, f"{model_id}.meta.json")
            async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
        
        # Rescan models to update the cache
        await self.scan_models()
        
        return model_id
    
    async def get_model_thumbnail(self, model_id: str) -> Optional[bytes]:
        """Get a thumbnail image for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Thumbnail image data as bytes, or None if not available
        """
        model_info = await self.get_model_info(model_id)
        if not model_info:
            return None
            
        # Check for thumbnail file
        thumbnail_path = os.path.join(model_info['directory'], f"{model_id}.thumb.png")
        if os.path.exists(thumbnail_path):
            with open(thumbnail_path, 'rb') as f:
                return f.read()
                
        # If no thumbnail exists, we could generate one here
        # For now, return None
        return None

# Sources for animal/creature VRMs
VRM_SOURCES = {
    'booth.pm': 'https://booth.pm/ja/items?tags%5B%5D=VRM&sort=new&animal=1',
    'sketchfab': 'https://sketchfab.com/3d-models?features=downloadable&tags=anime,animal,creature&sort_by=-publishedAt',
    'vrchat.com': 'https://vrchat.com/home/avatars?tags=animal,creature',
    'vroid_hub': 'https://hub.vroid.com/en/characters?tag_ids=3',  # Animal tag
    'pixiv': 'https://www.pixiv.net/tags/VRM/artworks?mode=safe&s_mode=s_tag&tag=動物',
    'github': 'https://github.com/search?q=VRM+animal+creature',
    'deviantart': 'https://www.deviantart.com/search?q=VRM+animal',
    'artstation': 'https://www.artstation.com/marketplace?sort_by=published_at&tags=VRM,animal',
    'unity_asset_store': 'https://assetstore.unity.com/search?k=VRM%20animal',
    'cults3d': 'https://cults3d.com/en/3d-model/character?tags=VRM,animal',
    'thingiverse': 'https://www.thingiverse.com/search?q=VRM+animal&type=things&sort=relevant',
    'gumroad': 'https://gumroad.com/discover?query=VRM%20animal',
    'cgtrader': 'https://www.cgtrader.com/3d-models/character/anime/vrm?query=animal',
    'turboquid': 'https://www.turbosquid.com/Search/3D-Models/vrm/animal',
    'free3d': 'https://free3d.com/3d-models/vrm/animal',
    'open3dmodel': 'https://www.open3dmodel.com/3d-models/vrm/animal',
    'clara': 'https://clara.io/library?query=VRM%20animal',
    'myminifactory': 'https://www.myminifactory.com/search/vrm?query=animal',
    'skfb': 'https://sketchfab.com/3d-models?features=downloadable&tags=VRM,animal,creature',
    'vrchat_avatars': 'https://vrchat-avatars.com/category/animal/',
    'vroid_showcase': 'https://vroid.com/en/studio/showcase?tag=animal',
}

# Example usage
if __name__ == "__main__":
    import asyncio
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
    logger = logging.getLogger(__name__)
    
    async def main():
        # Create a VRM manager
        vrm_manager = VRMManager()
        
        # Scan for models
        model_ids = await vrm_manager.scan_models()
        logger.info(f"Found {len(model_ids)} models:")
        for model_id in model_ids:
            logger.info(f"- {model_id}")
        
        # Log VRM sources
        logger.info("\nVRM Sources:")
        for name, url in VRM_SOURCES.items():
            logger.info(f"- {name}: {url}")
    
    asyncio.run(main())
