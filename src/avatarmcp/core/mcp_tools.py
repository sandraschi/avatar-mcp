"""
MCP Tools for AvatarMCP.

This module provides FastMCP 2.12+ compatible tools for controlling avatars.
"""
import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union, Type, TypeVar, Generic, Callable, Awaitable
from pathlib import Path

from .decorators import mcp_tool
from .mcp_base import MCPTool, MCPToolsBase

from ..models.vrm_model import VRMModel
from ..models.animation_controller import AnimationController
from ..network.osc.vrc_connector import VRChatOSC

# Check FastMCP version
import fastmcp
from packaging import version

MIN_FASTMCP_VERSION = "2.12.0"
if version.parse(fastmcp.__version__) < version.parse(MIN_FASTMCP_VERSION):
    raise RuntimeError(f"FastMCP {MIN_FASTMCP_VERSION}+ required (found {fastmcp.__version__})")

logger = logging.getLogger(__name__)

# Type aliases
AvatarID = str
AnimationName = str
ParameterName = str
ParameterValue = Union[str, int, float, bool, None]

class MCPTools(MCPToolsBase):
    """MCP Tools for avatar control with FastMCP 2.12+ compatibility."""
    
    def __init__(self, mcp_server, vrc_osc: VRChatOSC):
        """Initialize the MCP tools.
        
        Args:
            mcp_server: The MCP server instance
            vrc_osc: The VRChat OSC connector
        """
        super().__init__(mcp_server)
        self.osc = vrc_osc
        self.avatars: Dict[AvatarID, VRMModel] = {}
        self.animation_controllers: Dict[AvatarID, AnimationController] = {}
        
        # Check FastMCP version
        self._check_fastmcp_version()
        
        # Register all tools with @mcp_tool decorator
        self.register_tools()
    
    def _check_fastmcp_version(self) -> None:
        """Check that FastMCP version is 2.12.0 or higher."""
        import fastmcp
        from packaging import version
        
        if version.parse(fastmcp.__version__) < version.parse('2.12.0'):
            raise RuntimeError(
                f"FastMCP version 2.12.0 or higher is required, but found {fastmcp.__version__}"
            )
            
    def register_tools(self):
        """Register all tools with the MCP server."""
        # Tools will be registered automatically by MCPToolsBase
        # using @mcp_tool decorators
        pass
        
    @mcp_tool(
        name="tools.discover",
        description="List all available MCP tools with their metadata",
        parameters={},
        returns={
            "type": "object",
            "properties": {
                "tools": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "parameters": {"type": "object"}
                        }
                    }
                }
            }
        }
    )
    async def discover_tools(self) -> Dict[str, Any]:
        """Discover all available MCP tools with their metadata.
        
        Returns:
            Dictionary containing information about all available tools
            
        Note:
            This is a placeholder method. The actual tool discovery is handled by FastMCP's 
            introspection of the @mcp_tool decorators.
        """
        return {
            "status": "success",
            "message": "Tool discovery is handled by FastMCP introspection. Use the MCP server's built-in discovery mechanism.",
            "tools": []  # Actual tools will be discovered by FastMCP
        }
    
    # Avatar Management Commands
    
    @mcp_tool(
        name="avatar.load",
        description="Load a VRM avatar model",
        parameters={
            "id": {"type": "string", "description": "Unique ID for the avatar"},
            "path": {"type": "string", "description": "Path to the VRM file"},
            "scale": {"type": "number", "description": "Scale factor for the model", "default": 1.0}
        },
        returns={
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "bones": {"type": "integer"},
                "blend_shapes": {"type": "integer"},
                "scale": {"type": "number"}
            }
        }
    )
    async def load_avatar(self, id: str, path: str, scale: float = 1.0) -> Dict[str, Any]:
        """Load a VRM avatar.
        
        Args:
            id: Unique ID for the avatar
            path: Path to the VRM file
            scale: Optional scale factor (default: 1.0)
            
        Returns:
            Dictionary containing avatar metadata including ID, name, bone count, etc.
            
        Raises:
            ValueError: If avatar with ID already exists or loading fails
        """
        avatar_id = id
        
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
    
    @mcp_tool(
        name="avatar.unload",
        description="Unload a VRM avatar",
        parameters={
            "id": {"type": "string", "description": "ID of the avatar to unload"}
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "id": {"type": "string"}
            }
        }
    )
    async def unload_avatar(self, id: str) -> Dict[str, Any]:
        """Unload a VRM avatar.
        
        Args:
            id: ID of the avatar to unload
            
        Returns:
            Dictionary with status and avatar ID
            
        Raises:
            ValueError: If avatar with ID is not found
        """
        avatar_id = id
        
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
    
    @mcp_tool(
        name="avatar.list",
        description="List all loaded avatars",
        parameters={},
        returns={
            "type": "object",
            "properties": {
                "avatars": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "bones": {"type": "integer"},
                            "blend_shapes": {"type": "integer"}
                        }
                    }
                }
            }
        }
    )
    async def list_avatars(self) -> Dict[str, Any]:
        """List all loaded avatars.
        
        Returns:
            Dictionary with a list of loaded avatars and their metadata
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
    
    @mcp_tool(
        name="animation.play",
        description="Play an animation on an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "animation": {"type": "string", "description": "Name of the animation to play"},
            "loop": {"type": "boolean", "description": "Whether to loop the animation", "default": False},
            "weight": {"type": "number", "description": "Blend weight (0.0 to 1.0)", "default": 1.0, "minimum": 0.0, "maximum": 1.0},
            "speed": {"type": "number", "description": "Playback speed multiplier", "default": 1.0, "minimum": 0.1, "maximum": 10.0}
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "animation": {"type": "string"},
                "avatar_id": {"type": "string"}
            }
        }
    )
    async def play_animation(
        self,
        avatar_id: str,
        animation: str,
        loop: bool = False,
        weight: float = 1.0,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """Play an animation on an avatar.
        
        Args:
            avatar_id: ID of the avatar
            animation: Name of the animation to play
            loop: Whether to loop the animation (default: False)
            weight: Blend weight (0.0 to 1.0, default: 1.0)
            speed: Playback speed multiplier (default: 1.0)
            
        Returns:
            Dictionary with animation status
            
        Raises:
            ValueError: If avatar is not found or parameters are invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        controller = self.animation_controllers[avatar_id]
        weight = max(0.0, min(1.0, weight))  # Clamp to 0.0-1.0
        speed = max(0.1, min(10.0, speed))   # Clamp to reasonable range
        
        controller.play_animation(
            animation_name=animation,
            loop=loop,
            weight=weight,
            speed=speed
        )
        
        return {
            'status': 'playing',
            'avatar_id': avatar_id,
            'animation': animation,
            'loop': loop,
            'weight': weight,
            'speed': speed
        }
    
    @mcp_tool(
        name="animation.stop",
        description="Stop an animation on an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "animation": {"type": "string", "description": "Name of the animation to stop"}
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "animation": {"type": "string"}
            }
        }
    )
    async def stop_animation(self, avatar_id: str, animation: str) -> Dict[str, Any]:
        """Stop an animation on an avatar.
        
        Args:
            avatar_id: ID of the avatar
            animation: Name of the animation to stop
            
        Returns:
            Dictionary with animation stop status
            
        Raises:
            ValueError: If avatar is not found or parameters are invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        controller = self.animation_controllers[avatar_id]
        controller.stop_animation(animation)
        
        return {
            'status': 'stopped',
            'avatar_id': avatar_id,
            'animation': animation
        }
    
    @mcp_tool(
        name="animation.list",
        description="List available animations for an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"}
        },
        returns={
            "type": "object",
            "properties": {
                "avatar_id": {"type": "string"},
                "animations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "duration": {"type": "number"},
                            "loop": {"type": "boolean"}
                        }
                    }
                }
            }
        }
    )
    async def list_animations(self, avatar_id: str) -> Dict[str, Any]:
        """List available animations for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            
        Returns:
            Dictionary containing avatar ID and list of available animations
            
        Raises:
            ValueError: If avatar is not found
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        controller = self.animation_controllers[avatar_id]
        animations = controller.list_animations()
        
        return {
            'avatar_id': avatar_id,
            'animations': animations
        }
    
    # Parameter Control Commands
    
    @mcp_tool(
        name="parameter.set",
        description="Set a parameter value on an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "name": {"type": "string", "description": "Name of the parameter to set"},
            "value": {"type": ["string", "number", "boolean", "null"], "description": "Value to set"}
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "parameter": {"type": "string"},
                "value": {"type": ["string", "number", "boolean", "null"]}
            }
        }
    )
    async def set_parameter(self, avatar_id: str, name: str, value: ParameterValue) -> Dict[str, Any]:
        """Set a parameter on an avatar.
        
        Args:
            avatar_id: ID of the avatar
            name: Name of the parameter to set
            value: Value to set (string, number, boolean, or null)
            
        Returns:
            Dictionary with parameter set status
            
        Raises:
            ValueError: If avatar is not found or parameters are invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        controller = self.animation_controllers[avatar_id]
        controller.set_parameter(name, value)
        
        return {
            'status': 'set',
            'avatar_id': avatar_id,
            'parameter': name,
            'value': value
        }
    
    @mcp_tool(
        name="parameter.get",
        description="Get the current value of a parameter from an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "name": {"type": "string", "description": "Name of the parameter to get"}
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "parameter": {"type": "string"},
                "value": {"type": ["string", "number", "boolean", "null"]}
            }
        }
    )
    async def get_parameter(self, avatar_id: str, name: str) -> Dict[str, Any]:
        """Get the current value of a parameter from an avatar.
        
        Args:
            avatar_id: ID of the avatar
            name: Name of the parameter to get
            
        Returns:
            Dictionary containing the parameter value and status
            
        Raises:
            ValueError: If avatar is not found or parameter is invalid
            NotImplementedError: If parameter tracking is not implemented
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        
        # This is a simplified example - in a real implementation, you would
        # get the current parameter value from the avatar/controller
        # For now, we'll return a not implemented response
        raise NotImplementedError("Parameter tracking is not yet implemented")
        
        # Example implementation (commented out):
        # controller = self.animation_controllers[avatar_id]
        # value = controller.get_parameter(name)
        # return {
        #     'status': 'success',
        #     'avatar_id': avatar_id,
        #     'parameter': name,
        #     'value': value
        # }
    
    # OSC Control Commands
    
    @mcp_tool(
        name="osc.send",
        description="Send a raw OSC message to VRChat",
        parameters={
            "address": {"type": "string", "description": "OSC address pattern (e.g. /avatar/parameters/ParameterName)"},
            "args": {
                "type": "array",
                "description": "List of OSC arguments",
                "items": {"type": ["string", "number", "boolean", "null"]},
                "default": []
            }
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "address": {"type": "string"},
                "args": {"type": "array"}
            }
        }
    )
    async def send_osc_message(self, address: str, args: list = None) -> Dict[str, Any]:
        """Send a raw OSC message to VRChat.
        
        Args:
            address: OSC address pattern (e.g. /avatar/parameters/ParameterName)
            args: List of OSC arguments (strings, numbers, booleans, or null)
            
        Returns:
            Dictionary with send status and message details
            
        Raises:
            ValueError: If address is not provided or invalid
        """
        if not address or not isinstance(address, str):
            raise ValueError("Valid 'address' string is required")
            
        if args is None:
            args = []
            
        # Ensure args is a list of serializable values
        serializable_args = []
        for arg in args:
            if isinstance(arg, (str, int, float, bool)) or arg is None:
                serializable_args.append(arg)
            else:
                # Convert other types to string
                serializable_args.append(str(arg))
        
        # Send the OSC message
        self.osc.client.send_message(address, serializable_args)
        
        return {
            'status': 'sent',
            'address': address,
            'args': serializable_args
        }
    
    @mcp_tool(
        name="osc.chat",
        description="Send a chat message to VRChat",
        parameters={
            "message": {"type": "string", "description": "Message to send"},
            "direct": {
                "type": "boolean",
                "description": "If true, send without MCP prefix",
                "default": False
            }
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "direct": {"type": "boolean"}
            }
        }
    )
    async def send_chat_message(self, message: str, direct: bool = False) -> Dict[str, Any]:
        """Send a chat message to VRChat.
        
        Args:
            message: The message text to send
            direct: If true, send without MCP prefix (default: False)
            
        Returns:
            Dictionary with send status and message details
            
        Raises:
            ValueError: If message is empty or invalid
        """
        if not message or not isinstance(message, str):
            raise ValueError("Valid 'message' string is required")
        
        # Add prefix if not direct
        if not direct:
            message = f"[MCP] {message}"
        
        # Send via OSC
        self.osc.send_chat(message)
        
        return {
            'status': 'sent',
            'message': message,
            'direct': direct
        }
    
    @mcp_tool(
        name="movement.walk",
        description="Start a walking animation for an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "direction": {
                "type": "string",
                "description": "Walking direction",
                "enum": ["forward", "backward", "left", "right"],
                "default": "forward"
            },
            "speed": {
                "type": "number",
                "description": "Walking speed multiplier",
                "default": 1.0,
                "minimum": 0.1,
                "maximum": 5.0
            }
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "direction": {"type": "string"},
                "speed": {"type": "number"}
            }
        }
    )
    async def walk(
        self,
        avatar_id: str,
        direction: str = "forward",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """Start a walking animation for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            direction: Walking direction (forward, backward, left, right)
            speed: Walking speed multiplier (0.1 to 5.0)
            
        Returns:
            Dictionary with walk status and parameters
            
        Raises:
            ValueError: If avatar is not found or direction is invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
            
        if direction not in ["forward", "backward", "left", "right"]:
            raise ValueError(
                "Direction must be one of: 'forward', 'backward', 'left', 'right'"
            )
            
        # Clamp speed to reasonable range
        speed = max(0.1, min(5.0, float(speed)))
        
        # In a real implementation, you would control the avatar's movement here
        # This is a simplified example that just returns the status
        return {
            'status': 'walking',
            'avatar_id': avatar_id,
            'direction': direction,
            'speed': speed
        }
    
    @mcp_tool(
        name="movement.run",
        description="Start a running animation for an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "direction": {
                "type": "string",
                "description": "Running direction",
                "enum": ["forward", "backward", "left", "right"],
                "default": "forward"
            },
            "speed": {
                "type": "number",
                "description": "Running speed multiplier",
                "default": 2.0,
                "minimum": 0.5,
                "maximum": 10.0
            }
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "direction": {"type": "string"},
                "speed": {"type": "number"}
            }
        }
    )
    async def run(
        self,
        avatar_id: str,
        direction: str = "forward",
        speed: float = 2.0
    ) -> Dict[str, Any]:
        """Start a running animation for an avatar.
        
        Args:
            avatar_id: ID of the avatar
            direction: Running direction (forward, backward, left, right)
            speed: Running speed multiplier (0.5 to 10.0)
            
        Returns:
            Dictionary with run status and parameters
            
        Raises:
            ValueError: If avatar is not found or direction is invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
            
        if direction not in ["forward", "backward", "left", "right"]:
            raise ValueError(
                "Direction must be one of: 'forward', 'backward', 'left', 'right'"
            )
            
        # Clamp speed to reasonable range
        speed = max(0.5, min(10.0, float(speed)))
        
        # In a real implementation, you would control the avatar's movement here
        # This is a simplified example that just returns the status
        return {
            'status': 'running',
            'avatar_id': avatar_id,
            'direction': direction,
            'speed': speed
        }
    
    @mcp_tool(
        name="movement.turn",
        description="Turn an avatar left or right",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "direction": {
                "type": "string",
                "description": "Turning direction",
                "enum": ["left", "right"],
                "default": "left"
            },
            "angle": {
                "type": "number",
                "description": "Angle in degrees to turn",
                "default": 45.0,
                "minimum": 1.0,
                "maximum": 360.0
            },
            "speed": {
                "type": "number",
                "description": "Turning speed multiplier",
                "default": 1.0,
                "minimum": 0.1,
                "maximum": 5.0
            }
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "direction": {"type": "string"},
                "angle": {"type": "number"},
                "speed": {"type": "number"}
            }
        }
    )
    async def turn(
        self,
        avatar_id: str,
        direction: str = "left",
        angle: float = 45.0,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """Turn an avatar left or right.
        
        Args:
            avatar_id: ID of the avatar
            direction: Turning direction ('left' or 'right')
            angle: Angle in degrees to turn (1.0 to 360.0)
            speed: Turning speed multiplier (0.1 to 5.0)
            
        Returns:
            Dictionary with turn status and parameters
            
        Raises:
            ValueError: If avatar is not found or parameters are invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
            
        if direction not in ["left", "right"]:
            raise ValueError("Direction must be 'left' or 'right'")
            
        # Clamp values to reasonable ranges
        angle = max(1.0, min(360.0, float(angle)))
        speed = max(0.1, min(5.0, float(speed)))
        
        # In a real implementation, you would control the avatar's rotation here
        # This is a simplified example that just returns the status
        return {
            'status': 'turning',
            'avatar_id': avatar_id,
            'direction': direction,
            'angle': angle,
            'speed': speed
        }
    
    @mcp_tool(
        name="movement.jump",
        description="Make an avatar jump",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "height": {
                "type": "number",
                "description": "Jump height multiplier",
                "default": 1.0,
                "minimum": 0.1,
                "maximum": 5.0
            }
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "height": {"type": "number"}
            }
        }
    )
    async def jump(
        self,
        avatar_id: str,
        height: float = 1.0
    ) -> Dict[str, Any]:
        """Make an avatar jump.
        
        Args:
            avatar_id: ID of the avatar
            height: Jump height multiplier (0.1 to 5.0)
            
        Returns:
            Dictionary with jump status and parameters
            
        Raises:
            ValueError: If avatar is not found
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
            
        # Clamp height to reasonable range
        height = max(0.1, min(5.0, float(height)))
        
        # In a real implementation, you would trigger a jump animation here
        # This is a simplified example that just returns the status
        return {
            'status': 'jumping',
            'avatar_id': avatar_id,
            'height': height
        }
    
    @mcp_tool(
        name="movement.curtsy",
        description="Make an avatar perform a curtsy",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"},
            "style": {
                "type": "string",
                "description": "Style of curtsy",
                "enum": ["default", "formal", "playful", "respectful"],
                "default": "default"
            },
            "intensity": {
                "type": "number",
                "description": "Intensity of the curtsy (0.1 to 2.0)",
                "default": 1.0,
                "minimum": 0.1,
                "maximum": 2.0
            }
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"},
                "style": {"type": "string"},
                "intensity": {"type": "number"}
            }
        }
    )
    async def curtsy(
        self,
        avatar_id: str,
        style: str = "default",
        intensity: float = 1.0
    ) -> Dict[str, Any]:
        """Make an avatar perform a curtsy.
        
        Args:
            avatar_id: ID of the avatar
            style: Style of curtsy (default, formal, playful, respectful)
            intensity: Intensity of the curtsy (0.1 to 2.0)
            
        Returns:
            Dictionary with curtsy status and parameters
            
        Raises:
            ValueError: If avatar is not found or parameters are invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
            
        if style not in ["default", "formal", "playful", "respectful"]:
            raise ValueError(
                "Style must be one of: 'default', 'formal', 'playful', 'respectful'"
            )
            
        # Clamp intensity to reasonable range
        intensity = max(0.1, min(2.0, float(intensity)))
        
        # In a real implementation, you would trigger a curtsy animation here
        # This is a simplified example that just returns the status
        return {
            'status': 'curtsying',
            'avatar_id': avatar_id,
            'style': style,
            'intensity': intensity
        }
    
    @mcp_tool(
        name="movement.stop",
        description="Stop all movement for an avatar",
        parameters={
            "avatar_id": {"type": "string", "description": "ID of the avatar"}
        },
        returns={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "avatar_id": {"type": "string"}
            }
        }
    )
    async def stop_movement(self, avatar_id: str) -> Dict[str, Any]:
        """Stop all movement for an avatar.
        
        Args:
            avatar_id: ID of the avatar to stop
            
        Returns:
            Dictionary with stop status
            
        Raises:
            ValueError: If avatar is not found
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
            
        # In a real implementation, you would stop all movement here
        # This is a simplified example that just returns the status
        await self.osc.send_parameter("Avatar/Parameters/Walk", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/Run", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/MoveX", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/Turn", 0.0)
        
        return {
            'status': 'stopped',
            'avatar_id': avatar_id
        }
