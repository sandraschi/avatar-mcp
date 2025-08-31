"""
3D visualization for VRM models using PyVista.
"""
import numpy as np
import pyvista as pv
from typing import Optional, Dict, Any, List, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VRMViewer:
    """3D viewer for VRM models using PyVista."""
    
    def __init__(self, window_size=(1024, 768)):
        """Initialize the VRM viewer.
        
        Args:
            window_size: Tuple of (width, height) for the window
        """
        self.plotter = pv.Plotter(window_size=window_size)
        self.models = {}
        self.current_model = None
        self.is_playing = False
        self.animation_speed = 1.0
        self.current_frame = 0
        self.animation_fps = 60
        self.animation_actors = {}
        self.active_animations = {}
        self.animation_callbacks = {}
        self.animation_time = 0.0
        self.plotter.enable_terrain_style()
        self.plotter.add_axes()
        self.plotter.add_floor(color='lightgray')
        
        # Animation box properties
        self.animation_box = None
        self.animation_box_visible = False
        self.animation_box_position = [0, 0, 0]
        self.animation_box_size = [1.0, 1.0, 1.0]
        
        # Set up the animation timer
        self.plotter.add_callback(self.update, interval=16)  # ~60 FPS
        
    def load_vrm(self, model_id: str, file_path: str) -> bool:
        """Load a VRM model into the viewer.
        
        Args:
            model_id: Unique identifier for the model
            file_path: Path to the VRM file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # For now, we'll use a simple sphere as a placeholder
            # In a real implementation, you would load the VRM file here
            mesh = pv.Sphere()
            self.models[model_id] = self.plotter.add_mesh(
                mesh,
                color='lightblue',
                name=model_id,
                show_edges=True
            )
            self.plotter.reset_camera()
            return True
            
        except Exception as e:
            logger.error(f"Failed to load VRM {file_path}: {e}")
            return False
            
    def unload_vrm(self, model_id: str) -> bool:
        """Unload a VRM model from the viewer.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            bool: True if successful, False otherwise
        """
        if model_id in self.models:
            self.plotter.remove_actor(self.models[model_id])
            del self.models[model_id]
            return True
        return False
    
    def play_animation(self, model_id: str, animation_name: str) -> bool:
        """Play an animation on a model.
        
        Args:
            model_id: ID of the model
            animation_name: Name of the animation to play
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Animation playback would be implemented here
        logger.info(f"Playing animation '{animation_name}' on model '{model_id}'")
        self.is_playing = True
        return True
    
    def stop_animation(self, model_id: str, animation_name: str) -> bool:
        """Stop a playing animation.
        
        Args:
            model_id: ID of the model
            animation_name: Name of the animation to stop
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Stopping animation '{animation_name}' on model '{model_id}'")
        self.is_playing = False
        return True
    
    def update(self):
        """Update the viewer state."""
        if not self.is_playing:
            return
            
        # Update animation time based on speed
        self.animation_time += 0.016 * self.animation_speed  # ~60 FPS
        
        # Update all active animations
        for model_id, anim_data in list(self.active_animations.items()):
            if model_id not in self.animation_actors:
                continue
                
            actor = self.animation_actors[model_id]
            animation = anim_data['animation']
            start_time = anim_data['start_time']
            
            # Calculate animation time with loop handling
            anim_time = (self.animation_time - start_time) % animation.duration
            
            # Update bone transforms
            for bone_name, bone_animation in animation.bones.items():
                # Get interpolated transform at current time
                transform = bone_animation.evaluate(anim_time)
                
                # Apply transform to the actor (simplified - actual implementation depends on your model structure)
                if hasattr(actor, 'set_pose'):
                    actor.set_pose(bone_name, transform)
                
            # Update blend shapes if any
            if hasattr(animation, 'blend_shapes'):
                for shape_name, weight_curve in animation.blend_shapes.items():
                    weight = weight_curve.evaluate(anim_time)
                    if hasattr(actor, 'set_blend_shape_weight'):
                        actor.set_blend_shape_weight(shape_name, weight)
        
        # Request a redraw
        self.plotter.render()
    
    def play_animation(self, model_id: str, animation_name: str, loop: bool = True, speed: float = 1.0) -> bool:
        """Play an animation on a model.
        
        Args:
            model_id: ID of the model to animate
            animation_name: Name of the animation to play
            loop: Whether to loop the animation
            speed: Playback speed multiplier
            
        Returns:
            bool: True if animation was started successfully
        """
        if model_id not in self.models:
            logger.warning(f"Model {model_id} not found")
            return False
            
        model = self.models[model_id]
        
        # Get the animation (simplified - you'd load this from your model)
        animation = getattr(model, 'animations', {}).get(animation_name)
        if not animation:
            logger.warning(f"Animation '{animation_name}' not found for model {model_id}")
            return False
            
        # Store animation data
        self.active_animations[model_id] = {
            'animation': animation,
            'start_time': self.animation_time,
            'loop': loop,
            'speed': speed
        }
        
        # Update playback speed
        self.animation_speed = speed
        self.is_playing = True
        
        logger.info(f"Playing animation '{animation_name}' on model {model_id}")
        return True
        
    def stop_animation(self, model_id: str, animation_name: str = None, fade_out: float = 0.0) -> bool:
        """Stop an animation.
        
        Args:
            model_id: ID of the model
            animation_name: Optional name of the animation to stop (stops all if None)
            fade_out: Fade out duration in seconds
            
        Returns:
            bool: True if animation was stopped
        """
        if model_id not in self.active_animations:
            return False
            
        if animation_name:
            # Stop specific animation if it matches
            anim_data = self.active_animations[model_id]
            if anim_data['animation'].name == animation_name:
                del self.active_animations[model_id]
                logger.info(f"Stopped animation '{animation_name}' on model {model_id}")
                return True
            return False
        else:
            # Stop all animations for this model
            del self.active_animations[model_id]
            logger.info(f"Stopped all animations on model {model_id}")
            return True
    
    def show(self):
        """Show the viewer window."""
        # Set up animation callback if not already done
        if not hasattr(self, '_animation_callback_id'):
            self._animation_callback_id = self.plotter.add_callback(
                self.update, interval=16  # ~60 FPS
            )
        self.plotter.show()
        
    def close(self):
        """Close the viewer and clean up resources."""
        self.plotter.close()


# Example usage
if __name__ == "__main__":
    viewer = VRMViewer()
    
    # Example: Load a model
    viewer.load_vrm("test_model", "path/to/your/model.vrm")
    
    # Show the viewer
    viewer.show()
