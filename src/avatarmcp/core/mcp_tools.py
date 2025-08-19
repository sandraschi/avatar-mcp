"""
MCP Tools for AvatarMCP.

This module provides FastMCP 2.10.1 compatible tools for controlling avatars.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union

from ..models.vrm_model import VRMModel
from ..models.animation_controller import AnimationController
from ..network.osc.vrc_connector import VRChatOSC

logger = logging.getLogger(__name__)

class MCPTools:
    """MCP Tools for avatar control."""
    
    def __init__(self, mcp_server, vrc_osc: VRChatOSC):
        """Initialize the MCP tools.
        
        Args:
            mcp_server: The MCP server instance
            vrc_osc: The VRChat OSC connector
        """
        self.mcp = mcp_server
        self.osc = vrc_osc
        self.avatars: Dict[str, VRMModel] = {}
        self.animation_controllers: Dict[str, AnimationController] = {}
        
        # Register MCP commands
        self._register_commands()
    
    def _register_commands(self):
        """Register MCP commands."""
        # Avatar management
        self.mcp.register_handler("avatar.load", self.load_avatar)
        self.mcp.register_handler("avatar.unload", self.unload_avatar)
        self.mcp.register_handler("avatar.list", self.list_avatars)
        
        # Animation control
        self.mcp.register_handler("animation.play", self.play_animation)
        self.mcp.register_handler("animation.stop", self.stop_animation)
        self.mcp.register_handler("animation.list", self.list_animations)
        
        # Parameter control
        self.mcp.register_handler("parameter.set", self.set_parameter)
        self.mcp.register_handler("parameter.get", self.get_parameter)
        
        # OSC control
        self.mcp.register_handler("osc.send", self.send_osc_message)
        self.mcp.register_handler("osc.chat", self.send_chat_message)
        
        # Movement controls
        self.mcp.register_handler("movement.walk", self.walk)
        self.mcp.register_handler("movement.run", self.run)
        self.mcp.register_handler("movement.turn", self.turn)
        self.mcp.register_handler("movement.jump", self.jump)
        self.mcp.register_handler("movement.curtsy", self.curtsy)
        self.mcp.register_handler("movement.stop", self.stop_movement)
    
    # Avatar Management Commands
    
    async def load_avatar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load a VRM avatar.
        
        Args:
            params: {
                'id': str,           # Unique ID for the avatar
                'path': str,         # Path to the VRM file
                'scale': float = 1.0 # Optional scale factor
            }
            
        Returns:
            Information about the loaded avatar
        """
        avatar_id = params.get('id')
        path = params.get('path')
        scale = float(params.get('scale', 1.0))
        
        if not avatar_id or not path:
            raise ValueError("Both 'id' and 'path' are required")
        
        if avatar_id in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' already loaded")
        
        try:
            # Load the VRM model
            avatar = VRMModel.load(path)
            if scale != 1.0:
                avatar.scale(scale)
            
            # Create animation controller
            controller = AnimationController(avatar)
            
            # Store references
            self.avatars[avatar_id] = avatar
            self.animation_controllers[avatar_id] = controller
            
            return {
                'id': avatar_id,
                'name': avatar.metadata.get('name', 'Unnamed Avatar'),
                'bones': len(avatar.bone_names),
                'blend_shapes': len(avatar.blend_shape_names),
                'scale': scale
            }
            
        except Exception as e:
            logger.error(f"Failed to load avatar: {e}", exc_info=True)
            raise ValueError(f"Failed to load avatar: {str(e)}")
    
    async def unload_avatar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unload a VRM avatar.
        
        Args:
            params: {
                'id': str  # ID of the avatar to unload
            }
            
        Returns:
            Confirmation of the unload operation
        """
        avatar_id = params.get('id')
        if not avatar_id:
            raise ValueError("Avatar ID is required")
        
        if avatar_id not in self.avatars:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        # Stop any running animations
        if avatar_id in self.animation_controllers:
            controller = self.animation_controllers[avatar_id]
            controller.stop_all_animations()
            del self.animation_controllers[avatar_id]
        
        # Remove the avatar
        del self.avatars[avatar_id]
        
        return {'status': 'success', 'id': avatar_id}
    
    async def list_avatars(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all loaded avatars.
        
        Args:
            params: {}
            
        Returns:
            Information about all loaded avatars
        """
        return {
            'avatars': [
                {
                    'id': avatar_id,
                    'name': avatar.metadata.get('name', 'Unnamed Avatar'),
                    'bones': len(avatar.bone_names),
                    'blend_shapes': len(avatar.blend_shape_names)
                }
                for avatar_id, avatar in self.avatars.items()
            ]
        }
    
    # Animation Control Commands
    
    async def play_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Play an animation on an avatar.
        
        Args:
            params: {
                'avatar_id': str,     # ID of the avatar
                'animation': str,     # Name of the animation to play
                'loop': bool = False, # Whether to loop the animation
                'weight': float = 1.0 # Blend weight (0.0 to 1.0)
                'speed': float = 1.0  # Playback speed
            }
            
        Returns:
            Status of the animation play operation
        """
        avatar_id = params.get('avatar_id')
        animation_name = params.get('animation')
        
        if not avatar_id or not animation_name:
            raise ValueError("Both 'avatar_id' and 'animation' are required")
        
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        controller = self.animation_controllers[avatar_id]
        loop = bool(params.get('loop', False))
        weight = float(params.get('weight', 1.0))
        speed = float(params.get('speed', 1.0))
        
        controller.play_animation(
            animation_name=animation_name,
            loop=loop,
            weight=weight,
            speed=speed
        )
        
        return {
            'status': 'playing',
            'avatar_id': avatar_id,
            'animation': animation_name,
            'loop': loop,
            'weight': weight,
            'speed': speed
        }
    
    async def stop_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop an animation on an avatar.
        
        Args:
            params: {
                'avatar_id': str,     # ID of the avatar
                'animation': str,     # Name of the animation to stop
                'fade_out': float = 0 # Fade out duration in seconds
            }
            
        Returns:
            Status of the animation stop operation
        """
        avatar_id = params.get('avatar_id')
        animation_name = params.get('animation')
        
        if not avatar_id or not animation_name:
            raise ValueError("Both 'avatar_id' and 'animation' are required")
        
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        controller = self.animation_controllers[avatar_id]
        fade_out = float(params.get('fade_out', 0))
        
        controller.stop_animation(animation_name, fade_out=fade_out)
        
        return {
            'status': 'stopped',
            'avatar_id': avatar_id,
            'animation': animation_name,
            'fade_out': fade_out
        }
    
    async def list_animations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available animations for an avatar.
        
        Args:
            params: {
                'avatar_id': str  # ID of the avatar
            }
            
        Returns:
            List of available animations
        """
        avatar_id = params.get('avatar_id')
        if not avatar_id:
            raise ValueError("Avatar ID is required")
        
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        controller = self.animation_controllers[avatar_id]
        animations = controller.get_animation_list()
        
        return {
            'avatar_id': avatar_id,
            'animations': animations
        }
    
    # Parameter Control Commands
    
    async def set_parameter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set a parameter on an avatar.
        
        Args:
            params: {
                'avatar_id': str,  # ID of the avatar
                'name': str,       # Parameter name
                'value': Any       # Parameter value
            }
            
        Returns:
            Confirmation of the parameter set operation
        """
        avatar_id = params.get('avatar_id')
        name = params.get('name')
        value = params.get('value')
        
        if not all([avatar_id, name, value is not None]):
            raise ValueError("'avatar_id', 'name', and 'value' are required")
        
        if avatar_id not in self.avatars:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        # This is a simplified example - in a real implementation, you would
        # validate the parameter name and value against the avatar's schema
        
        # For now, we'll just forward the parameter to VRChat via OSC
        self.osc.send_parameter(name, value)
        
        return {
            'status': 'set',
            'avatar_id': avatar_id,
            'parameter': name,
            'value': value
        }
    
    async def get_parameter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a parameter value from an avatar.
        
        Args:
            params: {
                'avatar_id': str,  # ID of the avatar
                'name': str        # Parameter name
            }
            
        Returns:
            The current value of the parameter
        """
        # Note: This is a placeholder implementation
        # In a real implementation, you would need to track parameter values
        # or query them from the avatar/OSC system
        return {
            'status': 'not_implemented',
            'message': 'Parameter tracking is not yet implemented'
        }
    
    # OSC Control Commands
    
    async def send_osc_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a raw OSC message.
        
        Args:
            params: {
                'address': str,  # OSC address
                'args': list     # List of arguments
            }
            
        Returns:
            Confirmation of the message send
        """
        address = params.get('address')
        args = params.get('args', [])
        
        if not address:
            raise ValueError("'address' is required")
        
        self.osc.client.send_message(address, args)
        
        return {
            'status': 'sent',
            'address': address,
            'args': args
        }
    
    async def send_chat_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a chat message to VRChat.
        
        Args:
            params: {
                'message': str,      # Message to send
                'direct': bool = False # If true, send without prefix
            }
            
        Returns:
            Confirmation of the message send
        """
        message = params.get('message', '')
        direct = params.get('direct', False)
        
        if not message:
            raise ValueError("Message cannot be empty")
            
        await self.osc.send_chat(message, direct=direct)
        return {'status': 'sent', 'message': message}
        
    # Movement Controls
    
    async def walk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start walking animation.
        
        Args:
            params: {
                'avatar_id': str,  # ID of the avatar
                'direction': str = 'forward'  # 'forward', 'backward', 'left', 'right'
                'speed': float = 1.0  # Walking speed multiplier
            }
            
        Returns:
            Status of the movement
        """
        avatar_id = params.get('avatar_id')
        direction = params.get('direction', 'forward').lower()
        speed = float(params.get('speed', 1.0))
        
        if avatar_id not in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' not found")
            
        # Trigger walk animation and movement
        await self.osc.send_parameter(f"Avatar/Parameters/Walk", 1.0)
        await self.osc.send_parameter(f"Avatar/Parameters/MoveX", 
                                    1.0 if direction in ['forward', 'right'] else 
                                    -1.0 if direction in ['backward', 'left'] else 0.0)
        
        return {
            'status': 'walking',
            'direction': direction,
            'speed': speed
        }
    
    async def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start running animation.
        
        Args:
            params: {
                'avatar_id': str,  # ID of the avatar
                'direction': str = 'forward'  # 'forward', 'backward', 'left', 'right'
                'speed': float = 1.5  # Running speed multiplier
            }
            
        Returns:
            Status of the movement
        """
        avatar_id = params.get('avatar_id')
        direction = params.get('direction', 'forward').lower()
        speed = float(params.get('speed', 1.5))
        
        if avatar_id not in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' not found")
            
        # Trigger run animation and movement
        await self.osc.send_parameter(f"Avatar/Parameters/Run", 1.0)
        await self.osc.send_parameter(f"Avatar/Parameters/MoveX", 
                                    1.0 if direction in ['forward', 'right'] else 
                                    -1.0 if direction in ['backward', 'left'] else 0.0)
        
        return {
            'status': 'running',
            'direction': direction,
            'speed': speed
        }
    
    async def turn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Turn the avatar.
        
        Args:
            params: {
                'avatar_id': str,  # ID of the avatar
                'direction': str = 'right',  # 'left' or 'right'
                'angle': float = 90.0  # Angle in degrees
                'speed': float = 1.0  # Turning speed multiplier
            }
            
        Returns:
            Status of the turn
        """
        avatar_id = params.get('avatar_id')
        direction = params.get('direction', 'right').lower()
        angle = float(params.get('angle', 90.0))
        speed = float(params.get('speed', 1.0))
        
        if avatar_id not in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' not found")
            
        # Calculate turn direction (-1 for left, 1 for right)
        turn_direction = 1.0 if direction == 'right' else -1.0
        
        # Send turn command
        await self.osc.send_parameter("Avatar/Parameters/Turn", turn_direction * speed)
        
        return {
            'status': 'turning',
            'direction': direction,
            'angle': angle,
            'speed': speed
        }
    
    async def jump(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make the avatar jump.
        
        Args:
            params: {
                'avatar_id': str,  # ID of the avatar
                'height': float = 1.0  # Jump height multiplier
            }
            
        Returns:
            Status of the jump
        """
        avatar_id = params.get('avatar_id')
        height = float(params.get('height', 1.0))
        
        if avatar_id not in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' not found")
            
        # Trigger jump animation and physics
        await self.osc.send_parameter("Avatar/Parameters/Jump", 1.0)
        
        return {
            'status': 'jumping',
            'height': height
        }
    
    async def curtsy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make the avatar perform a curtsy.
        
        Args:
            params: {
                'avatar_id': str,  # ID of the avatar
                'style': str = 'default'  # Style of curtsy
            }
            
        Returns:
            Status of the gesture
        """
        avatar_id = params.get('avatar_id')
        style = params.get('style', 'default')
        
        if avatar_id not in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' not found")
            
        # Trigger curtsy animation
        await self.osc.send_parameter("Avatar/Parameters/Gesture/Curtsey", 1.0)
        
        return {
            'status': 'curtsying',
            'style': style
        }
    
    async def stop_movement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop all avatar movement.
        
        Args:
            params: {
                'avatar_id': str  # ID of the avatar
            }
            
        Returns:
            Confirmation of movement stop
        """
        avatar_id = params.get('avatar_id')
        
        if avatar_id not in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' not found")
            
        # Reset all movement parameters
        await self.osc.send_parameter("Avatar/Parameters/Walk", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/Run", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/MoveX", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/Turn", 0.0)
        
        return {
            'status': 'stopped',
            'avatar_id': avatar_id
        }
