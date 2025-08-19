"""
Model-related commands for AvatarMCP.

This module provides commands for loading, managing, and manipulating
VRM models in the AvatarMCP server.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import AvatarMCP
    from ..models.vrm_model import VRMModel

# Re-export for easy imports
__all__ = ['register_commands']

def register_commands(registry):
    """Register all model-related commands.
    
    Args:
        registry: Command registry instance to register commands with
    """
    app = registry.app
    
    @registry.register(
        name="load_model",
        description="Load a VRM model into the server.",
        examples=[
            "load_model('path/to/model.vrm')",
            "load_model(path='path/to/model.vrm', model_id='my_model', scale=1.0)"
        ]
    )
    def load_model(
        app: 'AvatarMCP',
        path: str,
        model_id: Optional[str] = None,
        scale: float = 1.0
    ) -> Dict[str, Any]:
        """Load a VRM model into the server.
        
        Args:
            path: Filesystem path to the VRM file
            model_id: Optional ID to assign to the model (defaults to filename)
            scale: Scale factor to apply to the model
            
        Returns:
            Dict with status and model information
        """
        try:
            # Import here to avoid circular imports
            from ..models.vrm_model import VRMModel
            
            # Load the model
            model = VRMModel.load(path)
            
            # Generate ID if not provided
            if not model_id:
                import os
                model_id = os.path.splitext(os.path.basename(path))[0]
            
            # Apply scale
            if scale != 1.0:
                model.scale(scale)
            
            # Store the model
            if model_id in app.models:
                return {
                    'status': 'error',
                    'error': f'Model with ID {model_id} already exists',
                    'model_id': model_id
                }
                
            app.models[model_id] = model
            
            # Create animation controller for the model
            from ..models.animation_controller import AnimationController
            app.animation_controllers[model_id] = AnimationController(model)
            
            return {
                'status': 'success',
                'model_id': model_id,
                'path': path,
                'metadata': model.metadata,
                'bone_count': len(model.bone_names),
                'blend_shape_count': len(model.blend_shape_names)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'path': path,
                'model_id': model_id
            }
    
    @registry.register(
        name="unload_model",
        description="Unload a VRM model from the server.",
        examples=["unload_model('model_123')"]
    )
    def unload_model(
        app: 'AvatarMCP',
        model_id: str
    ) -> Dict[str, Any]:
        """Unload a VRM model from the server.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            Dict with status information
        """
        if model_id not in app.models:
            return {
                'status': 'error',
                'error': f'Model {model_id} not found',
                'model_id': model_id
            }
            
        try:
            # Clean up resources
            if model_id in app.animation_controllers:
                del app.animation_controllers[model_id]
            
            # Remove the model
            del app.models[model_id]
            
            return {
                'status': 'success',
                'model_id': model_id
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'model_id': model_id
            }
    
    @registry.register(
        name="list_models",
        description="List all loaded VRM models.",
        examples=["list_models()"]
    )
    def list_models(
        app: 'AvatarMCP'
    ) -> Dict[str, Any]:
        """List all loaded VRM models.
        
        Returns:
            Dict with status and list of models
        """
        try:
            models_info = []
            for model_id, model in app.models.items():
                models_info.append({
                    'model_id': model_id,
                    'bone_count': len(model.bone_names),
                    'blend_shape_count': len(model.blend_shape_names),
                    'metadata': model.metadata
                })
            
            return {
                'status': 'success',
                'models': models_info,
                'count': len(models_info)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @registry.register(
        name="get_model_info",
        description="Get detailed information about a loaded model.",
        examples=["get_model_info('model_123')"]
    )
    def get_model_info(
        app: 'AvatarMCP',
        model_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a loaded model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dict with detailed model information
        """
        if model_id not in app.models:
            return {
                'status': 'error',
                'error': f'Model {model_id} not found',
                'model_id': model_id
            }
            
        try:
            model = app.models[model_id]
            
            return {
                'status': 'success',
                'model_id': model_id,
                'bone_names': model.bone_names,
                'blend_shape_names': model.blend_shape_names,
                'metadata': model.metadata,
                'has_animations': model_id in app.animation_controllers
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'model_id': model_id
            }
    
    @registry.register(
        name="set_blend_shape",
        description="Set the weight of a blend shape on a model.",
        examples=[
            "set_blend_shape('model_123', 'blink', 0.5)",
            "set_blend_shape(model_id='model_123', name='smile', weight=1.0)"
        ]
    )
    def set_blend_shape(
        app: 'AvatarMCP',
        model_id: str,
        name: str,
        weight: float
    ) -> Dict[str, Any]:
        """Set the weight of a blend shape on a model.
        
        Args:
            model_id: ID of the model
            name: Name of the blend shape
            weight: Weight value (0.0 to 1.0)
            
        Returns:
            Dict with status information
        """
        if model_id not in app.models:
            return {
                'status': 'error',
                'error': f'Model {model_id} not found',
                'model_id': model_id
            }
            
        try:
            model = app.models[model_id]
            
            # Validate blend shape name
            if name not in model.blend_shape_names:
                return {
                    'status': 'error',
                    'error': f'Blend shape {name} not found',
                    'model_id': model_id,
                    'blend_shape': name
                }
            
            # Set the blend shape weight
            model.set_blend_shape_weight(name, weight)
            
            # Update any active animations
            if model_id in app.animation_controllers:
                controller = app.animation_controllers[model_id]
                controller.update_blend_shape(name, weight)
            
            return {
                'status': 'success',
                'model_id': model_id,
                'blend_shape': name,
                'weight': weight
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'model_id': model_id,
                'blend_shape': name
            }
