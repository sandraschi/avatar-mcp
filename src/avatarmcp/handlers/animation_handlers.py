"""
Animation management handlers for MCP server.

This module provides handlers for managing avatar animations, including playing,
stopping, and querying animation states.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

class AnimationHandler(BaseHandler):
    """Handles animation-related MCP requests."""
    
    def __init__(self, server: Any = None):
        """Initialize the animation handler.
        
        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self.animation_controller = None
        self.active_animations = {}

    async def _initialize(self) -> None:
        """Initialize the animation controller."""
        if not hasattr(self.server, 'animation_controller'):
            from ..models.animation_controller import AnimationController
            self.animation_controller = AnimationController()
            self.server.animation_controller = self.animation_controller
        else:
            self.animation_controller = self.server.animation_controller
        
        logger.info("Animation handler initialized")

    async def handle_animation_play(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Play an animation on the active avatar.
        
        Args:
            params: Dictionary containing:
                   - name: Name of the animation to play
                   - loop: Whether to loop the animation (default: False)
                   - speed: Playback speed multiplier (default: 1.0)
                   - blend_time: Time to blend to this animation (default: 0.2)
                   
        Returns:
            Dictionary with status and animation information
        """
        try:
            self._check_initialized()
            
            if not hasattr(self.server, 'avatar_handler'):
                return self._create_error_response("Avatar handler not available")
                
            avatar_handler = self.server.avatar_handler
            
            if not avatar_handler.active_model_id:
                return self._create_error_response("No active avatar")
                
            model_id = avatar_handler.active_model_id
            model = avatar_handler.loaded_models.get(model_id)
            
            if not model:
                return self._create_error_response("Active model not found")
            
            animation_name = params.get("name")
            if not animation_name:
                return self._create_error_response("Animation name is required")
                
            loop = params.get("loop", False)
            speed = float(params.get("speed", 1.0))
            blend_time = float(params.get("blend_time", 0.2))
            
            success = await self.animation_controller.play_animation(
                model=model,
                animation_name=animation_name,
                loop=loop,
                speed=speed,
                blend_time=blend_time
            )
            
            if not success:
                return self._create_error_response(f"Failed to play animation: {animation_name}")
            
            # Track active animation
            self.active_animations[model_id] = {
                "name": animation_name,
                "loop": loop,
                "speed": speed
            }
            
            return self._create_success_response(
                message=f"Playing animation: {animation_name}",
                animation=animation_name,
                model_id=model_id,
                loop=loop,
                speed=speed
            )
            
        except Exception as e:
            logger.error(f"Failed to play animation: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def handle_animation_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop the current animation on the active avatar.
        
        Args:
            params: Dictionary containing:
                   - blend_time: Time to blend out the animation (default: 0.2)
                   
        Returns:
            Dictionary with status and stop information
        """
        try:
            self._check_initialized()
            
            if not hasattr(self.server, 'avatar_handler'):
                return self._create_error_response("Avatar handler not available")
                
            avatar_handler = self.server.avatar_handler
            
            if not avatar_handler.active_model_id:
                return self._create_success_response(
                    message="No active avatar",
                    was_playing=False
                )
                
            model_id = avatar_handler.active_model_id
            model = avatar_handler.loaded_models.get(model_id)
            
            if not model:
                return self._create_success_response(
                    message="Active model not found",
                    was_playing=False
                )
            
            blend_time = float(params.get("blend_time", 0.2))
            was_playing = await self.animation_controller.stop_animation(
                model=model,
                blend_time=blend_time
            )
            
            # Clear active animation
            if was_playing and model_id in self.active_animations:
                del self.active_animations[model_id]
            
            return self._create_success_response(
                message="Animation stopped" if was_playing else "No animation was playing",
                was_playing=was_playing,
                model_id=model_id
            )
            
        except Exception as e:
            logger.error(f"Failed to stop animation: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))

    async def handle_animation_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available animations for the active avatar.
        
        Args:
            params: Dictionary containing optional filter parameters
            
        Returns:
            Dictionary with list of available animations
        """
        try:
            self._check_initialized()
            
            if not hasattr(self.server, 'avatar_handler'):
                return self._create_error_response("Avatar handler not available")
                
            avatar_handler = self.server.avatar_handler
            
            if not avatar_handler.active_model_id:
                return self._create_error_response("No active avatar")
                
            model_id = avatar_handler.active_model_id
            model = avatar_handler.loaded_models.get(model_id)
            
            if not model:
                return self._create_error_response("Active model not found")
            
            # Get standard animations
            animations = await self.animation_controller.list_animations(model)
            
            # Get current animation state if any
            current_animation = None
            if model_id in self.active_animations:
                current_animation = self.active_animations[model_id]["name"]
            
            return self._create_success_response(
                animations=animations,
                current_animation=current_animation,
                model_id=model_id
            )
            
        except Exception as e:
            logger.error(f"Failed to list animations: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))
    
    async def handle_animation_get_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current animation state for the active avatar.
        
        Args:
            params: Dictionary containing optional parameters
            
        Returns:
            Dictionary with current animation state
        """
        try:
            self._check_initialized()
            
            if not hasattr(self.server, 'avatar_handler'):
                return self._create_error_response("Avatar handler not available")
                
            avatar_handler = self.server.avatar_handler
            
            if not avatar_handler.active_model_id:
                return self._create_success_response(
                    active=False,
                    message="No active avatar"
                )
                
            model_id = avatar_handler.active_model_id
            
            if model_id not in self.active_animations:
                return self._create_success_response(
                    active=False,
                    message="No active animation",
                    model_id=model_id
                )
            
            animation_info = self.active_animations[model_id]
            
            return self._create_success_response(
                active=True,
                animation=animation_info["name"],
                loop=animation_info["loop"],
                speed=animation_info["speed"],
                model_id=model_id
            )
            
        except Exception as e:
            logger.error(f"Failed to get animation state: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))
    
    async def shutdown(self) -> None:
        """Clean up resources used by the handler."""
        # Stop all active animations
        for model_id in list(self.active_animations.keys()):
            try:
                if hasattr(self.server, 'avatar_handler'):
                    avatar_handler = self.server.avatar_handler
                    if model_id in avatar_handler.loaded_models:
                        model = avatar_handler.loaded_models[model_id]
                        await self.animation_controller.stop_animation(model)
            except Exception as e:
                logger.error(f"Error stopping animation for model {model_id}: {str(e)}")
        
        self.active_animations.clear()
        self.initialized = False
        logger.info("Animation handler shutdown complete")
