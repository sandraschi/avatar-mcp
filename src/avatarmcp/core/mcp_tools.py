"""
MCP Tools for AvatarMCP.

This module provides FastMCP 2.12+ compatible tools for controlling avatars.
"""

import asyncio
import datetime
import inspect
import logging
import os
from typing import Any, Union

# Check FastMCP version
import fastmcp
from packaging import version

from ..models.animation_controller import AnimationController

# NO duplicate FastMCP instance - will use the one from server.py
from ..models.vrm_model import VRMModel
from ..network.osc.vrc_connector import VRChatOSC
from .mcp_base import MCPToolsBase

MIN_FASTMCP_VERSION = "2.12.0"
if version.parse(fastmcp.__version__) < version.parse(MIN_FASTMCP_VERSION):
    raise RuntimeError(f"FastMCP {MIN_FASTMCP_VERSION}+ required (found {fastmcp.__version__})")

logger = logging.getLogger(__name__)

# Type aliases
AvatarID = str
AnimationName = str
ParameterName = str
ParameterValue = str | int | float | bool | None


class MCPTools(MCPToolsBase):
    """MCP Tools for avatar control with FastMCP 2.12+ compatibility.

    This class provides a collection of MCP tools for controlling avatars, animations,
    and other functionality in the AvatarMCP system. It's designed to work with
    FastMCP 2.12.0 and above.
    """

    def __init__(self, mcp_server: Any, vrc_osc: VRChatOSC) -> None:
        """Initialize the MCP tools with required dependencies.

        Args:
            mcp_server: The MCP server instance that manages these tools
            vrc_osc: The VRChat OSC connector for sending/receiving OSC messages

        Raises:
            RuntimeError: If the FastMCP version is not compatible
        """
        super().__init__(mcp_server)
        self.osc = vrc_osc
        self.avatars: dict[AvatarID, VRMModel] = {}
        self.animation_controllers: dict[AvatarID, AnimationController] = {}

        # Use the FastMCP instance from mcp_server
        self.mcp = mcp_server

        # Ensure we're using a compatible FastMCP version
        self._check_fastmcp_version()

        # Register tools on the server instance
        self._register_tools()

    def _check_fastmcp_version(self) -> None:
        """Check that FastMCP version is 2.12.0 or higher."""
        import fastmcp
        from packaging import version

        if version.parse(fastmcp.__version__) < version.parse("2.12.0"):
            raise RuntimeError(f"FastMCP version 2.12.0 or higher is required, but found {fastmcp.__version__}")

    def _register_tools(self) -> None:
        """Register all MCP tools using the FastMCP server instance."""

        @self.mcp.tool(name="tools.discover", description="List all available MCP tools with their metadata")
        async def discover_tools() -> dict[str, Any]:
            return await self.discover_tools()

        @self.mcp.tool(name="avatar.load", description="Load a VRM avatar model into the system")
        async def load_avatar(
            id: str, path: str, scale: float = 1.0, auto_play_animations: bool = True
        ) -> dict[str, Any]:
            return await self.load_avatar(id, path, scale, auto_play_animations)

        @self.mcp.tool(name="avatar.unload", description="Unload a VRM avatar from the system")
        async def unload_avatar(id: str) -> dict[str, Any]:
            return await self.unload_avatar(id)

        @self.mcp.tool(name="avatar.list", description="List all currently loaded avatars and their details")
        async def list_avatars() -> dict[str, Any]:
            return await self.list_avatars()

        @self.mcp.tool(name="animation.play", description="Play an animation on a loaded avatar")
        async def play_animation(
            avatar_id: str,
            animation: str,
            loop: bool = False,
            weight: float = 1.0,
            speed: float = 1.0,
        ) -> dict[str, Any]:
            return await self.play_animation(avatar_id, animation, loop, weight, speed)

        @self.mcp.tool(name="animation.stop", description="Stop a currently playing animation on an avatar")
        async def stop_animation(avatar_id: str, animation: str) -> dict[str, Any]:
            return await self.stop_animation(avatar_id, animation)

        @self.mcp.tool(name="animation.list", description="List available animations for an avatar")
        async def list_animations(avatar_id: str) -> dict[str, Any]:
            return await self.list_animations(avatar_id)

        @self.mcp.tool(name="parameter.set", description="Set a parameter value on an avatar")
        async def set_parameter(avatar_id: str, name: str, value: ParameterValue) -> dict[str, Any]:
            return await self.set_parameter(avatar_id, name, value)

        @self.mcp.tool(name="parameter.get", description="Get the current value of a parameter from an avatar")
        async def get_parameter(avatar_id: str, name: str) -> dict[str, Any]:
            return await self.get_parameter(avatar_id, name)

        @self.mcp.tool(name="osc.send", description="Send a raw OSC message to VRChat")
        async def send_osc_message(address: str, args: list | None = None) -> dict[str, Any]:
            return await self.send_osc_message(address, args)

        @self.mcp.tool(name="osc.chat", description="Send a chat message to VRChat")
        async def send_chat_message(message: str, direct: bool = False) -> dict[str, Any]:
            return await self.send_chat_message(message, direct)

        # Movement tools
        @self.mcp.tool(name="movement.walk", description="Start a walking animation for an avatar")
        async def walk(avatar_id: str, direction: str = "forward", speed: float = 1.0) -> dict[str, Any]:
            return await self.walk(avatar_id, direction, speed)

        @self.mcp.tool(name="movement.run", description="Start a running animation for an avatar")
        async def run(avatar_id: str, direction: str = "forward", speed: float = 2.0) -> dict[str, Any]:
            return await self.run(avatar_id, direction, speed)

        @self.mcp.tool(name="movement.turn", description="Turn an avatar left or right")
        async def turn(
            avatar_id: str, direction: str = "left", angle: float = 45.0, speed: float = 1.0
        ) -> dict[str, Any]:
            return await self.turn(avatar_id, direction, angle, speed)

        @self.mcp.tool(name="movement.jump", description="Make an avatar jump")
        async def jump(avatar_id: str, height: float = 1.0) -> dict[str, Any]:
            return await self.jump(avatar_id, height)

        @self.mcp.tool(name="movement.curtsy", description="Make an avatar perform a curtsy")
        async def curtsy(avatar_id: str, style: str = "default", intensity: float = 1.0) -> dict[str, Any]:
            return await self.curtsy(avatar_id, style, intensity)

        @self.mcp.tool(name="movement.stop", description="Stop all movement for an avatar")
        async def stop_movement(avatar_id: str) -> dict[str, Any]:
            return await self.stop_movement(avatar_id)

    async def discover_tools(self) -> dict[str, Any]:
        """Discover all available MCP tools with their metadata.

        This method returns information about all registered tools in a format
        that's compatible with the MCP protocol.

        Returns:
            Dictionary containing:
            - tools: List of tool metadata including name, description, and parameters
            - version: The FastMCP version in use
        """
        tools = []

        # Get all registered tools from FastMCP
        for tool_name, tool_info in self.mcp.tools.items():
            # Skip internal tools
            if tool_name.startswith("_") or not callable(tool_info.get("function")):
                continue

            # Get function signature for parameter information
            func = tool_info["function"]
            sig = inspect.signature(func)

            # Build parameter schema
            parameters = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                param_info = {
                    "type": self._get_type_name(param.annotation),
                    "description": param.default if param.default is not inspect.Parameter.empty else "",
                    "required": param.default is inspect.Parameter.empty,
                }

                if param.default is not inspect.Parameter.empty:
                    param_info["default"] = param.default

                parameters[param_name] = param_info

            tools.append(
                {
                    "name": tool_name,
                    "description": tool_info.get("description", "").strip(),
                    "async": asyncio.iscoroutinefunction(func),
                    "parameters": parameters,
                }
            )

        return {"tools": tools, "version": fastmcp.__version__}

    def _get_type_name(self, type_hint) -> str:
        """Convert Python type hints to string representations."""
        if type_hint is inspect.Parameter.empty:
            return "any"
        if hasattr(type_hint, "__origin__"):
            if type_hint.__origin__ is Union:
                return " | ".join(self._get_type_name(arg) for arg in type_hint.__args__)
            return type_hint.__origin__.__name__
        return type_hint.__name__

    async def load_avatar(
        self, id: str, path: str, scale: float = 1.0, auto_play_animations: bool = True
    ) -> dict[str, Any]:
        """Load a VRM avatar model.

        Loads a VRM model from the specified path and makes it available for animation
        and control. The model is scaled according to the provided scale factor.

        Args:
            id: Unique identifier for the avatar
            path: Filesystem path to the VRM file
            scale: Scale factor for the avatar model (default: 1.0)
            auto_play_animations: Whether to automatically play default animations (default: True)

        Returns:
            Dictionary containing avatar metadata including ID, name, and model statistics

        Raises:
            ValueError: If avatar with ID already exists or loading fails
            FileNotFoundError: If the VRM file is not found
        """
        avatar_id = id

        if not avatar_id or not path:
            raise ValueError("Both id and path must be provided")

        # Normalize path and check if file exists
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.isfile(path):
            raise ValueError(f"VRM file not found: {path}")

        # Check if avatar with this ID already exists
        if hasattr(self, "avatars") and avatar_id in self.avatars:
            raise ValueError(f"Avatar with ID '{avatar_id}' already exists")

        try:
            # Load the VRM model
            # Note: Replace this with actual VRM loading logic
            avatar_data = {
                "id": avatar_id,
                "path": path,
                "scale": scale,
                "status": "loaded",
                "bones": [],  # This would be populated with actual bone data
                "materials": [],  # This would be populated with material data
                "blend_shapes": [],  # This would be populated with blend shape data
                "auto_play_animations": auto_play_animations,
                "loaded_at": datetime.datetime.utcnow().isoformat(),
            }

            # Store the avatar data
            if not hasattr(self, "avatars"):
                self.avatars = {}
            self.avatars[avatar_id] = avatar_data

            # Log the successful load
            logger.info(f"Loaded avatar '{avatar_id}' from {path}")

            return {
                "success": True,
                "avatar": avatar_data,
                "message": f"Successfully loaded avatar '{avatar_id}'",
            }

        except Exception as e:
            error_msg = f"Failed to load avatar '{avatar_id}': {e!s}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    async def unload_avatar(self, id: str) -> dict[str, Any]:
        """Unload a previously loaded VRM avatar.

        Removes the specified avatar from the system and cleans up associated resources.

        Args:
            id: Unique ID of the avatar to unload

        Returns:
            Dictionary with status and the ID of the unloaded avatar

        Raises:
            ValueError: If avatar with given ID is not found
        """
        if not hasattr(self, "avatars") or id not in self.avatars:
            raise ValueError(f"No avatar found with ID: {id}")

        try:
            # Get avatar data before removing it
            avatar_data = self.avatars[id]

            # Stop any running animations
            if hasattr(self, "animation_controllers") and id in self.animation_controllers:
                controller = self.animation_controllers[id]
                if hasattr(controller, "stop_all_animations"):
                    controller.stop_all_animations()
                del self.animation_controllers[id]

            # Remove the avatar from the dictionary
            del self.avatars[id]

            logger.info(f"Unloaded avatar '{id}': {avatar_data.get('path', '')}")

            return {
                "success": True,
                "message": f"Successfully unloaded avatar '{id}'",
                "avatar_id": id,
            }

        except Exception as e:
            error_msg = f"Failed to unload avatar '{id}': {e!s}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

    async def list_avatars(self) -> dict[str, Any]:
        """List all currently loaded avatars.

        Returns a list of all avatars that are currently loaded in the system,
        along with their basic metadata.

        Returns:
            Dictionary with a 'avatars' key containing a list of avatar metadata
        """
        return {
            "avatars": [
                {
                    "id": avatar_id,
                    "name": avatar.get("name", "Unnamed Avatar"),
                    "bones": len(avatar.get("bones", [])),
                    "blend_shapes": len(avatar.get("blend_shapes", [])),
                }
                for avatar_id, avatar in self.avatars.items()
            ]
        }

    async def play_animation(
        self,
        avatar_id: str,
        animation: str,
        loop: bool = False,
        weight: float = 1.0,
        speed: float = 1.0,
    ) -> dict[str, Any]:
        """Play an animation on the specified avatar.

        Starts playing the specified animation on the avatar with the given ID.
        The animation can be configured to loop and have custom blend weight and speed.

        Args:
            avatar_id: ID of the target avatar
            animation: Name of the animation to play
            loop: Whether to loop the animation (default: False)
            weight: Blend weight (0.0 to 1.0, default: 1.0)
            speed: Playback speed multiplier (default: 1.0)

        Returns:
            Dictionary with animation status and parameters

        Raises:
            ValueError: If avatar is not found or parameters are invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")

        controller = self.animation_controllers[avatar_id]
        weight = max(0.0, min(1.0, weight))  # Clamp to 0.0-1.0
        speed = max(0.1, min(10.0, speed))  # Clamp to reasonable range

        controller.play_animation(animation_name=animation, loop=loop, weight=weight, speed=speed)

        return {
            "status": "playing",
            "avatar_id": avatar_id,
            "animation": animation,
            "loop": loop,
            "weight": weight,
            "speed": speed,
        }

    async def stop_animation(self, avatar_id: str, animation: str) -> dict[str, Any]:
        """Stop a specific animation on the specified avatar.

        Args:
            avatar_id: ID of the target avatar
            animation: Name of the animation to stop

        Returns:
            Dictionary with stop status and animation details

        Raises:
            ValueError: If avatar is not found or animation is not playing
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")

        controller = self.animation_controllers[avatar_id]
        controller.stop_animation(animation)

        return {"status": "stopped", "avatar_id": avatar_id, "animation": animation}

    async def list_animations(self, avatar_id: str) -> dict[str, Any]:
        """List all available animations for the specified avatar.

        Args:
            avatar_id: ID of the target avatar

        Returns:
            Dictionary containing the avatar ID and list of available animations

        Raises:
            ValueError: If avatar is not found
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")

        controller = self.animation_controllers[avatar_id]
        animations = controller.list_animations()

        return {"avatar_id": avatar_id, "animations": animations}

    async def set_parameter(self, avatar_id: str, name: str, value: ParameterValue) -> dict[str, Any]:
        """Set a parameter value on the specified avatar.

        Updates the value of a named parameter for the given avatar. The parameter
        will be created if it doesn't exist.

        Args:
            avatar_id: ID of the target avatar
            name: Name of the parameter to set
            value: New value for the parameter (string, number, boolean, or null)

        Returns:
            Dictionary with status and the set parameter details

        Raises:
            ValueError: If avatar is not found or parameter name is invalid
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")

        controller = self.animation_controllers[avatar_id]
        controller.set_parameter(name, value)

        return {"status": "set", "avatar_id": avatar_id, "parameter": name, "value": value}

    async def get_parameter(self, avatar_id: str, name: str) -> dict[str, Any]:
        """Retrieve the current value of a parameter from the specified avatar.

        Args:
            avatar_id: ID of the target avatar
            name: Name of the parameter to retrieve

        Returns:
            Dictionary containing the parameter name and its current value

        Raises:
            ValueError: If avatar is not found or parameter doesn't exist
            NotImplementedError: If parameter tracking is not implemented for this avatar
        """
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")

        # This is a simplified example - in a real implementation, you would
        # get the current parameter value from the avatar/controller
        # For now, we'll return a not implemented response
        raise NotImplementedError("Parameter tracking is not yet implemented")

    async def send_osc_message(self, address: str, args: list | None = None) -> dict[str, Any]:
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

        return {"status": "sent", "address": address, "args": serializable_args}

    async def send_chat_message(self, message: str, direct: bool = False) -> dict[str, Any]:
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

        return {"status": "sent", "message": message, "direct": direct}

    # Movement methods remain the same...
    async def walk(self, avatar_id: str, direction: str = "forward", speed: float = 1.0) -> dict[str, Any]:
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        if direction not in ["forward", "backward", "left", "right"]:
            raise ValueError("Direction must be one of: 'forward', 'backward', 'left', 'right'")
        speed = max(0.1, min(5.0, float(speed)))
        return {
            "status": "walking",
            "avatar_id": avatar_id,
            "movement": "walk",
            "direction": direction,
            "speed": speed,
        }

    async def run(self, avatar_id: str, direction: str = "forward", speed: float = 2.0) -> dict[str, Any]:
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        if direction not in ["forward", "backward", "left", "right"]:
            raise ValueError("Direction must be one of: 'forward', 'backward', 'left', 'right'")
        speed = max(0.5, min(10.0, float(speed)))
        return {
            "status": "running",
            "avatar_id": avatar_id,
            "movement": "run",
            "direction": direction,
            "speed": speed,
        }

    async def turn(
        self, avatar_id: str, direction: str = "left", angle: float = 45.0, speed: float = 1.0
    ) -> dict[str, Any]:
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        if direction not in ["left", "right"]:
            raise ValueError("Direction must be 'left' or 'right'")
        angle = max(1.0, min(360.0, float(angle)))
        speed = max(0.1, min(5.0, float(speed)))
        return {
            "status": "turning",
            "avatar_id": avatar_id,
            "movement": "turn",
            "direction": direction,
            "angle": angle,
            "speed": speed,
        }

    async def jump(self, avatar_id: str, height: float = 1.0) -> dict[str, Any]:
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        height = max(0.1, min(5.0, float(height)))
        return {"status": "jumping", "avatar_id": avatar_id, "movement": "jump", "height": height}

    async def curtsy(self, avatar_id: str, style: str = "default", intensity: float = 1.0) -> dict[str, Any]:
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        if style not in ["default", "formal", "playful", "respectful"]:
            raise ValueError("Style must be one of: 'default', 'formal', 'playful', 'respectful'")
        intensity = max(0.1, min(2.0, float(intensity)))
        return {
            "status": "curtsying",
            "avatar_id": avatar_id,
            "movement": "curtsy",
            "style": style,
            "intensity": intensity,
        }

    async def stop_movement(self, avatar_id: str) -> dict[str, Any]:
        if avatar_id not in self.animation_controllers:
            raise ValueError(f"No avatar with ID '{avatar_id}' is loaded")
        # In a real implementation, you would stop all movement here
        await self.osc.send_parameter("Avatar/Parameters/Walk", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/Run", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/MoveX", 0.0)
        await self.osc.send_parameter("Avatar/Parameters/Turn", 0.0)
        return {"status": "stopped", "avatar_id": avatar_id, "movement": "stop"}
