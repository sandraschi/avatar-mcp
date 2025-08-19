"""
AvatarMCP Service

Main service class for managing VRM avatars and animations using the VRMModelManager.
"""
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple, Union
import json
import logging
import time
import numpy as np
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Local imports
from ..models.vrm_loader import VRMModel as VRMLoaderModel, VRMBone, VRMBlendShape, VRMMaterial, VRMTexture
from ..models.model_manager import VRMModelManager, ModelCacheEntry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AnimationState:
    """Tracks the state of an animation."""
    name: str
    start_time: float
    is_playing: bool = True
    loop: bool = False
    speed: float = 1.0
    weight: float = 1.0
    current_time: float = 0.0

@dataclass
class AvatarInstance:
    """Represents an instance of a loaded VRM model with runtime state."""
    model: VRMLoaderModel
    current_pose: Dict[str, Tuple[float, float, float, float]] = field(default_factory=dict)  # bone_name -> quat
    current_blend_shapes: Dict[str, float] = field(default_factory=dict)  # blend_shape_name -> weight
    active_animations: Dict[str, AnimationState] = field(default_factory=dict)
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # quaternion
    scale: float = 1.0

class AvatarService:
    """
    Main service for managing VRM avatars and animations.
    
    This service provides high-level functionality for loading VRM models,
    playing animations, and managing the state of multiple avatars.
    """
    
    def __init__(self, model_manager: Optional[VRMModelManager] = None):
        """
        Initialize the AvatarService.
        
        Args:
            model_manager: Optional VRMModelManager instance. If not provided,
                         a new one will be created.
        """
        self.avatars: Dict[str, AvatarInstance] = {}
        self.model_manager = model_manager if model_manager is not None else VRMModelManager()
        self._last_update_time = time.time()
        logger.info("AvatarService initialized with model caching enabled")
    
    def load_vrm(
        self, 
        file_path: Union[str, Path], 
        avatar_id: Optional[str] = None,
        force_reload: bool = False,
        validate: bool = True
    ) -> Dict:
        """
        Load a VRM model from the specified file path with caching support.
        
        Args:
            file_path: Path to the .vrm or .glb file
            avatar_id: Optional ID for the avatar. If None, will use the file stem.
            force_reload: If True, force reload the model even if it's in the cache
            validate: If True, validate the VRM file before loading
            
        Returns:
            Dict: Metadata about the loaded avatar
            
        Raises:
            FileNotFoundError: If the VRM file doesn't exist
            ValueError: If the file is not a valid VRM/GLB file
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"VRM file not found: {file_path}")
        
        # Use file stem as ID if not provided
        if avatar_id is None:
            avatar_id = path.stem
        
        # Check if we already have this avatar loaded with the same ID
        if avatar_id in self.avatars and not force_reload:
            logger.info(f"Using existing avatar instance: {avatar_id}")
            return self._get_avatar_metadata(avatar_id)
        
        # Load the VRM model using the model manager
        try:
            vrm_model = self.model_manager.load_model(
                file_path=path,
                force_reload=force_reload,
                validate=validate
            )
            
            if vrm_model is None:
                raise ValueError(f"Failed to load VRM model: {path}")
            
            # Create an avatar instance
            avatar = AvatarInstance(model=vrm_model)
            
            # Initialize default pose
            self._initialize_default_pose(avatar)
            
            # Store the avatar
            self.avatars[avatar_id] = avatar
            
            logger.info(f"Loaded VRM model: {path.name} as '{avatar_id}'")
            
            # Return metadata
            return {
                'id': avatar_id,
                'name': getattr(vrm_model.metadata, 'name', path.stem),
                'bones': list(avatar.current_pose.keys()),
                'blend_shapes': [bs.name for bs in vrm_model.blend_shapes],
                'textures': len(vrm_model.textures),
                'materials': len(vrm_model.materials),
                'meshes': len(vrm_model.meshes)
            }
            
        except Exception as e:
            logger.error(f"Failed to load VRM model {path}: {str(e)}", exc_info=True)
            raise ValueError(f"Invalid VRM file: {str(e)}")
    
    def _initialize_default_pose(self, avatar: AvatarInstance) -> None:
        """Initialize the default pose for an avatar."""
        # Reset to bind pose (identity rotations for all bones)
        for bone_name, bone in avatar.model.bones.items():
            avatar.current_pose[bone_name] = bone.rotation  # Use the bone's default rotation
    
    def get_avatar_metadata(self, avatar_id: str) -> Dict:
        """
        Get metadata about a loaded avatar.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            Dict: Metadata including model info, bones, materials, etc.
            
        Raises:
            KeyError: If the avatar is not found
        """
        if avatar_id not in self.avatars:
            raise KeyError(f"Avatar not found: {avatar_id}")
            
        return self._get_avatar_metadata(avatar_id)
    
    def _get_avatar_metadata(self, avatar_id: str) -> Dict:
        """Internal method to get avatar metadata."""
        avatar = self.avatars[avatar_id]
        model = avatar.model
        
        # Get cache info if available
        cache_info = {}
        file_path = getattr(avatar, '_source_path', None)
        if file_path and hasattr(self.model_manager, 'get_cache_info'):
            cache_info = self.model_manager.get_cache_info()
        
        return {
            "id": avatar_id,
            "bones": list(model.bones.keys()),
            "materials": [mat.name for mat in model.materials],
            "blend_shapes": [bs.name for bs in model.blend_shapes],
            "mesh_count": len(model.meshes),
            "texture_count": len(model.textures),
            "cached": file_path is not None,
            "source_file": str(file_path) if file_path else None,
            "cache_info": cache_info
        }
    
    def get_avatar(self, avatar_id: str) -> Optional[Dict]:
        """
        Get information about a loaded avatar.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            Optional[Dict]: Avatar information, or None if not found
        """
        if avatar_id not in self.avatars:
            return None
            
        avatar = self.avatars[avatar_id]
        return {
            'id': avatar_id,
            'bone_count': len(avatar.current_pose),
            'blend_shape_count': len(avatar.current_blend_shapes),
            'active_animations': [name for name, state in avatar.active_animations.items() 
                                if state.is_playing]
        }
    
    def play_animation(self, avatar_id: str, animation_name: str, 
                      loop: bool = False, speed: float = 1.0, 
                      weight: float = 1.0) -> bool:
        """
        Play an animation on the specified avatar.
        
        Args:
            avatar_id: ID of the avatar
            animation_name: Name of the animation to play
            loop: Whether to loop the animation
            speed: Playback speed (1.0 = normal speed)
            weight: Blend weight (0.0 to 1.0)
            
        Returns:
            bool: True if the animation was started, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar not found: {avatar_id}")
            return False
            
        avatar = self.avatars[avatar_id]
        
        # For now, we'll just log the animation play
        # In a real implementation, this would set up animation state
        logger.info(f"Playing animation '{animation_name}' on avatar '{avatar_id}' "
                   f"(loop={loop}, speed={speed}, weight={weight})")
        
        # Create or update animation state
        if animation_name in avatar.active_animations:
            state = avatar.active_animations[animation_name]
            state.is_playing = True
            state.loop = loop
            state.speed = speed
            state.weight = weight
        else:
            state = AnimationState(
                name=animation_name,
                start_time=time.time(),
                loop=loop,
                speed=speed,
                weight=weight
            )
            avatar.active_animations[animation_name] = state
        
        return True
    
    def stop_animation(self, avatar_id: str, animation_name: str) -> bool:
        """
        Stop a specific animation on the avatar.
        
        Args:
            avatar_id: ID of the avatar
            animation_name: Name of the animation to stop
            
        Returns:
            bool: True if the animation was stopped, False if not found
        """
        if avatar_id not in self.avatars:
            return False
            
        avatar = self.avatars[avatar_id]
        
        if animation_name in avatar.active_animations:
            del avatar.active_animations[animation_name]
            return True
            
        return False
    
    def unload_avatar(self, avatar_id: str, remove_from_cache: bool = False) -> bool:
        """
        Unload an avatar and optionally remove it from the model cache.
        
        Args:
            avatar_id: ID of the avatar to unload
            remove_from_cache: If True, also remove the model from the model cache
            
        Returns:
            bool: True if the avatar was unloaded, False if not found
        """
        if avatar_id in self.avatars:
            # Get the file path if available
            avatar = self.avatars[avatar_id]
            file_path = getattr(avatar, '_source_path', None)
            
            # Clean up any resources
            # TODO: Add resource cleanup for animations, etc.
            
            # Remove from cache if requested
            if remove_from_cache and file_path and hasattr(self.model_manager, 'unload_model'):
                self.model_manager.unload_model(file_path)
            
            # Remove the avatar
            del self.avatars[avatar_id]
            logger.info(f"Unloaded avatar: {avatar_id}" + 
                      (f" and removed from cache" if remove_from_cache else ""))
            return True
            
        return False
    
    def list_loaded_avatars(self, include_cache_info: bool = False) -> List[Dict]:
        """
        Get a list of all loaded avatars with basic info.
        
        Args:
            include_cache_info: If True, include detailed cache information
            
        Returns:
            List[Dict]: List of avatar metadata dictionaries
        """
        avatars = []
        for avatar_id in self.avatars:
            try:
                meta = self._get_avatar_metadata(avatar_id)
                if not include_cache_info:
                    meta.pop('cache_info', None)
                avatars.append(meta)
            except Exception as e:
                logger.warning(f"Error getting metadata for avatar {avatar_id}: {e}")
        return avatars
    
    def get_cache_info(self) -> Dict:
        """
        Get information about the model cache.
        
        Returns:
            Dict: Cache statistics and state
        """
        if hasattr(self.model_manager, 'get_cache_info'):
            return self.model_manager.get_cache_info()
        return {"error": "Model caching is not enabled"}
    
    def clear_cache(self) -> Dict:
        """
        Clear the model cache.
        
        Returns:
            Dict: Status of the operation
        """
        if hasattr(self.model_manager, 'clear_cache'):
            self.model_manager.clear_cache()
            return {"status": "success", "message": "Model cache cleared"}
        return {"status": "error", "message": "Model caching is not enabled"}
    
    def get_avatar_pose(self, avatar_id: str) -> Dict:
        """
        Get the current pose of an avatar.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            Dict: The current pose information
        """
        if avatar_id not in self.avatars:
            return {}
            
        avatar = self.avatars[avatar_id]
        
        # Convert the pose to a serializable format
        pose = {}
        for bone_name, rotation in avatar.current_pose.items():
            pose[bone_name] = {
                'rotation': rotation,
                'position': list(avatar.model.bones[bone_name].position) if bone_name in avatar.model.bones else [0, 0, 0]
            }
        
        return {
            'bones': pose,
            'blend_shapes': avatar.current_blend_shapes,
            'active_animations': [{
                'name': state.name,
                'time': state.current_time,
                'weight': state.weight
            } for state in avatar.active_animations.values()]
        }
