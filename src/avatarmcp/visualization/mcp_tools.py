"""
MCP Tools for 3D Visualization (FastMCP 2.11.3+).

This module provides FastMCP 2.11.3+ compatible tools for 3D visualization.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union

from ..core.mcp_tools import MCPTools as BaseTools
from .manager import VisualizationManager
from ..ai.voice_controller import VoiceController, VoiceConfig
from ..ai.chatbot import VoiceChatbot

logger = logging.getLogger(__name__)

@dataclass
class VoiceConfig:
    """Configuration for voice and speech settings."""
    voice_id: str = "english"
    rate: int = 150
    volume: float = 1.0
    listen_timeout: int = 5
    phrase_time_limit: int = 5

class VisualizationTools(BaseTools):
    """MCP Tools for 3D visualization, animation, and interaction."""
    
    def __init__(self, mcp_server, vrc_osc, visualization_manager: VisualizationManager):
        """Initialize visualization tools.
        
        Args:
            mcp_server: The MCP server instance
            vrc_osc: The VRChat OSC connector
            visualization_manager: The visualization manager instance
        """
        super().__init__(mcp_server, vrc_osc)
        self.visualization = visualization_manager
        self.active_animations = {}
        self.voice_enabled = False
        self.chatbot_enabled = False
        self.voice_controller = None
        self.chatbot = None
        self._register_commands()
        
        # Dance animation state
        self.dance_tasks = {}  # model_id -> dance_task
    
    def _register_commands(self):
        """Register MCP commands."""
        self.commands = {
            # Visualization commands
            "visualization.show": self.show_viewer,
            "visualization.hide": self.hide_viewer,
            "visualization.animate": self.animate,
            "visualization.stop_animation": self.stop_animation,
            "visualization.set_transform": self.set_transform,
            "visualization.dance": self.make_avatar_dance,
            
            # Animation box commands
            "animation_box.set": self.set_animation_box,
            "animation_box.show": self.show_animation_box,
            "animation_box.hide": self.hide_animation_box,
            "animation_box.get_properties": self.get_animation_box_properties,
            
            # Voice and chatbot commands
            "voice.enable": self.enable_voice,
            "voice.speak": self.speak,
            "voice.listen": self.listen,
            "chatbot.enable": self.enable_chatbot,
            "chatbot.process": self.process_chat
        }
    
    async def show_visualization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show the 3D visualization window.
        
        Args:
            params: Request parameters
                - model_id: ID of the model to show
                - window_size: Optional [width, height] for the window
                
        Returns:
            Response with status and window information
        """
        try:
            model_id = params.get('model_id')
            window_size = params.get('window_size', [1024, 768])
            
            if not model_id:
                return self._error_response("model_id is required")
                
            success = await self.visualization.show_model(model_id, window_size)
            if not success:
                return self._error_response(f"Failed to show model {model_id}")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'window_size': window_size
            }
        except Exception as e:
            logger.exception("Error showing visualization")
            return self._error_response(str(e))
    
    async def hide_visualization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hide the 3D visualization window.
        
        Args:
            params: Request parameters
                - model_id: Optional ID of the model to hide (hides all if not specified)
                
        Returns:
            Response with status
        """
        try:
            model_id = params.get('model_id')
            
            if model_id:
                await self.visualization.hide_model(model_id)
            else:
                await self.visualization.hide_all()
                
            return {'status': 'success'}
        except Exception as e:
            logger.exception("Error hiding visualization")
            return self._error_response(str(e))
    
    async def animate_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Animate a 3D model.
        
        Args:
            params: Request parameters
                - model_id: ID of the model to animate
                - animation_name: Name of the animation to play
                - loop: Whether to loop the animation (default: true)
                - speed: Playback speed multiplier (default: 1.0)
                - fade_in: Fade in duration in seconds (default: 0.0)
                
        Returns:
            Response with status and animation details
        """
        try:
            model_id = params['model_id']
            animation_name = params['animation_name']
            loop = params.get('loop', True)
            speed = float(params.get('speed', 1.0))
            fade_in = float(params.get('fade_in', 0.0))
            
            success = await self.visualization.play_animation(
                model_id=model_id,
                animation_name=animation_name,
                loop=loop,
                speed=speed,
                fade_in=fade_in
            )
            
            if not success:
                return self._error_response(f"Failed to play animation '{animation_name}'")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'animation': animation_name,
                'loop': loop,
                'speed': speed
            }
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error animating model")
            return self._error_response(str(e))
    
    async def stop_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop animation on a model.
        
        Args:
            params: Request parameters
                - model_id: ID of the model
                - animation_name: Optional name of the animation to stop (stops all if not specified)
                - fade_out: Fade out duration in seconds (default: 0.0)
                
        Returns:
            Response with status
        """
        try:
            model_id = params['model_id']
            animation_name = params.get('animation_name')
            fade_out = float(params.get('fade_out', 0.0))
            
            success = await self.visualization.stop_animation(
                model_id=model_id,
                animation_name=animation_name,
                fade_out=fade_out
            )
            
            if not success:
                return self._error_response("Failed to stop animation")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'stopped_animation': animation_name or 'all',
                'fade_out': fade_out
            }
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error stopping animation")
            return self._error_response(str(e))
    
    async def set_model_transform(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set model transform in the 3D view.
        
        Args:
            params: Request parameters
                - model_id: ID of the model
                - position: Optional [x, y, z] position
                - rotation: Optional [x, y, z, w] quaternion rotation
                - scale: Optional [x, y, z] scale
                
        Returns:
            Response with status and transform information
        """
        try:
            model_id = params['model_id']
            position = params.get('position')
            rotation = params.get('rotation')
            scale = params.get('scale')
            
            if not any([position, rotation, scale]):
                return self._error_response("At least one of position, rotation, or scale must be provided")
            
            success = await self.visualization.set_model_transform(
                model_id=model_id,
                position=position,
                rotation=rotation,
                scale=scale
            )
            
            if not success:
                return self._error_response("Failed to set model transform")
                
            return {
                'status': 'success',
                'model_id': model_id,
                'transform': {
                    'position': position,
                    'rotation': rotation,
                    'scale': scale
                }
            }
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error setting model transform")
            return self._error_response(str(e))
    
    async def set_animation_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set the animation box properties.
        
        Args:
            position: [x, y, z] position of the box center
            size: [width, height, depth] of the box
            visible: Whether to show the box outline (optional)
        """
        try:
            position = params.get("position", [0, 0, 0])
            size = params.get("size", [1.0, 1.0, 1.0])
            visible = params.get("visible", True)
            
            # Update the viewer's animation box
            if self.visualization_manager.viewer:
                self.visualization_manager.viewer.set_animation_box(
                    position=position,
                    size=size,
                    visible=visible
                )
                
            return {
                "status": "success",
                "message": "Animation box updated",
                "position": position,
                "size": size,
                "visible": visible
            }
            
        except Exception as e:
            logger.error(f"Error setting animation box: {e}")
            return {"status": "error", "message": str(e)}
    
    async def show_animation_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Show the animation box with current properties."""
        try:
            if not self.visualization_manager.viewer:
                return {"status": "error", "message": "No viewer available"}
                
            self.visualization_manager.viewer.set_animation_box(
                position=self.visualization_manager.viewer.animation_box_position,
                size=self.visualization_manager.viewer.animation_box_size,
                visible=True
            )
            
            return {"status": "success", "message": "Animation box shown"}
            
        except Exception as e:
            logger.error(f"Error showing animation box: {e}")
            return {"status": "error", "message": str(e)}
    
    async def hide_animation_box(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hide the animation box."""
        try:
            if not self.visualization_manager.viewer:
                return {"status": "error", "message": "No viewer available"}
                
            self.visualization_manager.viewer.set_animation_box(
                position=self.visualization_manager.viewer.animation_box_position,
                size=self.visualization_manager.viewer.animation_box_size,
                visible=False
            )
            
            return {"status": "success", "message": "Animation box hidden"}
            
        except Exception as e:
            logger.error(f"Error hiding animation box: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_animation_box_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current animation box properties."""
        try:
            if not self.visualization_manager.viewer:
                return {"status": "error", "message": "No viewer available"}
                
            return {
                "status": "success",
                "position": self.visualization_manager.viewer.animation_box_position,
                "size": self.visualization_manager.viewer.animation_box_size,
                "visible": self.visualization_manager.viewer.animation_box_visible
            }
            
        except Exception as e:
            logger.error(f"Error getting animation box properties: {e}")
            return {"status": "error", "message": str(e)}
    
    async def make_avatar_dance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an avatar dance by playing random dance animations.
        
        Args:
            params: Request parameters
                - model_id: ID of the model to animate
                - intensity: Optional dance intensity (0.5 to 2.0, default: 1.0)
                - duration: Optional dance duration in seconds (0 for infinite, default: 0)
                
        Returns:
            Response with status and dance information
        """
        try:
            model_id = params['model_id']
            intensity = float(params.get('intensity', 1.0))
            duration = float(params.get('duration', 0))
            
            # Get available animations
            animations_result = await self.mcp.handle_message({
                "jsonrpc": "2.0",
                "method": "list_animations",
                "params": {"model_id": model_id},
                "id": "dance_query"
            })
            
            if 'error' in animations_result:
                return self._error_response(f"Failed to get animations: {animations_result['error']}")
                
            # Find dance animations (assuming they contain 'dance' in the name)
            dance_anims = []
            for anim_type, anims in animations_result.get('result', {}).get('animations', {}).items():
                dance_anims.extend([
                    anim['name'] for anim in anims 
                    if 'dance' in anim['name'].lower()
                ])
            
            if not dance_anims:
                # Fallback to any looping animations if no dance animations found
                for anim_type, anims in animations_result.get('result', {}).get('animations', {}).items():
                    dance_anims.extend([
                        anim['name'] for anim in anims 
                        if anim.get('loop', False)
                    ])
            
            if not dance_anims:
                return self._error_response("No suitable dance animations found")
            
            # Cancel any existing dance for this model
            await self._stop_dancing(model_id)
            
            # Create dance task
            self.dance_tasks[model_id] = asyncio.create_task(
                self._dance_sequence(model_id, dance_anims, intensity, duration)
            )
            
            return {
                'status': 'success',
                'model_id': model_id,
                'dance_animations': dance_anims,
                'intensity': intensity,
                'duration': duration
            }
            
        except KeyError as e:
            return self._error_response(f"Missing required parameter: {e}")
        except Exception as e:
            logger.exception("Error making avatar dance")
            return self._error_response(str(e))
    
    async def _dance_sequence(self, model_id: str, animations: List[str], 
                            intensity: float, duration: float):
        """Run the dance sequence."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            while True:
                # Check if we should stop
                if model_id not in self.dance_tasks:
                    break
                    
                # Check duration
                if duration > 0 and (asyncio.get_event_loop().time() - start_time) > duration:
                    break
                
                # Pick a random dance animation
                anim = random.choice(animations)
                speed = 0.8 + (random.random() * 0.4) * intensity  # 0.8-1.2 * intensity
                
                # Play the animation
                await self.mcp.handle_message({
                    "jsonrpc": "2.0",
                    "method": "visualization.animate",
                    "params": {
                        "model_id": model_id,
                        "animation_name": anim,
                        "loop": False,
                        "speed": speed,
                        "fade_in": 0.3
                    },
                    "id": f"dance_{int(asyncio.get_event_loop().time())}"
                })
                
                # Random dance move duration (2-5 seconds)
                move_duration = 2.0 + (random.random() * 3.0) / intensity
                await asyncio.sleep(move_duration)
                
        except asyncio.CancelledError:
            # Clean up
            await self.mcp.handle_message({
                "jsonrpc": "2.0",
                "method": "visualization.stop_animation",
                "params": {"model_id": model_id},
                "id": "dance_cleanup"
            })
        except Exception as e:
            logger.error(f"Error in dance sequence: {e}")
        finally:
            self.dance_tasks.pop(model_id, None)
    
    async def _stop_dancing(self, model_id: str):
        """Stop any active dance sequence for a model."""
        if model_id in self.dance_tasks:
            task = self.dance_tasks[model_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
    def _error_response(self, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """Create an error response."""
        response = {
            'status': 'error',
            'error': message
        }
        if details:
            response['details'] = details
        return response
