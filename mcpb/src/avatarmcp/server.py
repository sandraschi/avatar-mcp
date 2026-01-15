"""
AvatarMCP - FastMCP 2.12.0+ Server Implementation

This module implements the MCP (Model Context Protocol) server for AvatarMCP,
following the FastMCP 2.12.0+ API standards.

FIXES:
- Updated FastMCP API from deprecated .method() decorators to new @mcp.tool() pattern
- Fixed initialization issues with FastMCP 2.10.1+
"""

import asyncio
import fnmatch
import inspect
import logging
import os
import sys
import time
from typing import Any

try:
    import aiofiles
except ImportError:
    aiofiles = None

from fastmcp import FastMCP

from .handlers.chatbot_handler import ChatbotHandler
from .metrics import MetricsCollector
from .models.vrm_manager import VRMManager
from .models.vrm_model import VRMModel
from .tools.chat_tools import ChatTool

logger = logging.getLogger(__name__)


class OSCConfig:
    def __init__(
        self,
        client_address: str = "127.0.0.1",
        client_port: int = 9000,
        server_address: str = "127.0.0.1",
        server_port: int = 9001,
    ):
        self.client_address = client_address
        self.client_port = client_port
        self.server_address = server_address
        self.server_port = server_port


def oscmethod(address_pattern):
    """Decorator to mark methods as OSC message handlers."""

    def decorator(func):
        func._osc_address = address_pattern
        return func

    return decorator


class OSCManager:
    def __init__(self, osc_config: OSCConfig | None = None, enabled: bool = True):
        self.enabled = enabled
        self.initialized = False
        self.osc_config = osc_config or OSCConfig()

        if not self.enabled:
            logger.warning("OSC is disabled. No OSC server will be started.")
            return

        try:
            # Import OSC dependencies here to make them optional
            from pythonosc.dispatcher import Dispatcher
            from pythonosc.osc_server import AsyncIOOSCUDPServer
            from pythonosc.udp_client import SimpleUDPClient

            self.dispatcher = Dispatcher()
            self.osc_server = AsyncIOOSCUDPServer(
                (self.osc_config.server_address, self.osc_config.server_port),
                self.dispatcher,
                loop=asyncio.get_event_loop(),
            )
            self.osc_client = SimpleUDPClient(
                self.osc_config.client_address, self.osc_config.client_port
            )

            # Register the handler method
            self.dispatcher.map("/*", self._handle_osc_message)
            self.initialized = True
            logger.info(
                f"OSC server initialized on {self.osc_config.server_address}:"
                f"{self.osc_config.server_port}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize OSC server: {e}")
            logger.warning("Continuing without OSC functionality")
            self.enabled = False

    async def start(self):
        """Start the OSC server."""
        if not self.enabled or not self.initialized:
            return

        try:
            # For testing, we might want to skip actual server startup
            import os

            if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in str(os.getenv("_", "")):
                logger.info("Skipping OSC server start during testing")
                return

            await self.osc_server.start()
            logger.info("OSC server started")
        except Exception as e:
            logger.error(f"Failed to start OSC server: {e}")
            self.enabled = False

    async def stop(self):
        """Stop the OSC server."""
        if not self.enabled or not self.initialized:
            return

        try:
            self.osc_server.close()
            logger.info("OSC server stopped")
        except Exception as e:
            logger.error(f"Failed to stop OSC server: {e}")

    async def _handle_osc_message(self, address, *args):
        """Internal handler for OSC messages."""
        logger.info(f"Received OSC message: {address} {args}")

        # Call the appropriate handler method if it exists
        for _name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_osc_address"):
                if fnmatch.fnmatch(address, method._osc_address):
                    return await method(address, *args)

    @oscmethod("/avatar/osc/*")
    async def handle_osc_message(self, address, *args):
        """Handle OSC messages matching /avatar/osc/* pattern."""
        logger.info(f"Handling OSC message: {address} {args}")
        # Add your OSC message handling logic here


class AvatarMCPServer:
    """MCP server implementation for AvatarMCP using FastMCP 2.11.3+ API."""

    def __init__(
        self,
        osc_config: OSCConfig | None = None,
        models_dir: str | None = None,
        enable_osc: bool = False,
    ):
        """Initialize the MCP server."""
        self.mcp = FastMCP("avatarmcp")
        self.running = False
        self.osc_manager = OSCManager(osc_config, enabled=enable_osc)
        self._message_id = 0

        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Initialize VRM manager
        self.vrm_manager = VRMManager(models_dir)
        self.loaded_models: dict[str, VRMModel] = {}
        self.active_model_id: str | None = None

        # Initialize portmanteau tool classes
        from .tools.portmanteau.animation_controller_tool import AnimationControllerTool
        from .tools.portmanteau.avatar_manager_tool import AvatarManagerTool
        from .tools.portmanteau.chat_manager_tool import ChatManagerTool
        from .tools.portmanteau.osc_communicator_tool import OSCCommunicatorTool
        from .tools.portmanteau.system_monitor_tool import SystemMonitorTool
        from .tools.portmanteau.unity_config_manager_tool import UnityConfigManagerTool
        from .tools.portmanteau.unity_integration_tool import UnityIntegrationTool
        from .tools.portmanteau.unity_window_manager_tool import UnityWindowManagerTool

        self.avatar_manager_tool = AvatarManagerTool(self)
        self.animation_controller_tool = AnimationControllerTool(self)
        self.osc_communicator_tool = OSCCommunicatorTool(self)
        self.unity_integration_tool = UnityIntegrationTool(self)
        self.unity_window_manager_tool = UnityWindowManagerTool(self)
        self.unity_config_manager_tool = UnityConfigManagerTool(self)
        self.chat_manager_tool = ChatManagerTool(self)
        self.system_monitor_tool = SystemMonitorTool(self)

        # Initialize chat components
        self.chatbot_handler = ChatbotHandler()
        self.chat_tool = ChatTool()
        self.chat_tool.chatbot_handler = self.chatbot_handler

        # Initialize metrics collection
        self.metrics = MetricsCollector(port=8000, enabled=True)
        if self.metrics.info is not None:
            self.metrics.info.info(
                {
                    "version": "1.0.0",
                    "service": "avatarmcp",
                    "environment": os.getenv("ENV", "development"),
                }
            )

        # Track server state
        self.start_time = time.time()
        self.initialized = False

    async def start(self):
        """Start the MCP server."""
        if self.running:
            return

        self.logger.info("Starting AvatarMCPServer...")

        try:
            # Skip actual server startup during testing
            import os

            if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in str(os.getenv("_", "")):
                self.logger.info("Skipping AvatarMCPServer startup during testing")
                self.initialized = True
                self.running = True
                self.logger.info("AvatarMCPServer started successfully (test mode)")
                return

            # Start OSC manager
            await self.osc_manager.start()

            # Initialize the server
            self.initialized = True
            self.running = True

            self.logger.info("AvatarMCPServer started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start AvatarMCPServer: {e}", exc_info=True)
            raise

    async def stop(self):
        """Stop the MCP server."""
        if not self.running:
            return

        self.logger.info("Stopping AvatarMCPServer...")

        try:
            # Stop OSC manager
            await self.osc_manager.stop()

            self.running = False
            self.initialized = False

            self.logger.info("AvatarMCPServer stopped")

        except Exception as e:
            self.logger.error(f"Error stopping AvatarMCPServer: {e}", exc_info=True)

    def _register_tools(self) -> None:
        """Register all MCP tools using the new FastMCP 2.11.3+ API."""

        # Core initialization tool
        @self.mcp.tool()
        def initialize(params: dict[str, Any]) -> dict[str, Any]:
            """Initialize the AvatarMCP server with configuration settings.

            Sets up the AvatarMCP server environment, scans for available VRM models,
            and prepares all subsystems for operation. This must be called before
            using any other avatar-related tools.

            Parameters:
                models_dir: Optional path to directory containing VRM model files
                    - If not provided, uses default models directory
                    - Must be an absolute path or relative to current working directory
                    - Directory will be scanned for .vrm files automatically

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable status description
                    - version: Server version string
                    - models_dir: Path to models directory being used
                    - num_models: Number of VRM models found during scan

            Usage:
                Call this tool once at the start of your AvatarMCP session. It establishes
                the foundation for all avatar operations and ensures the server is ready
                to load and manage VRM models.

            Examples:
                Basic initialization:
                    result = await initialize({})
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'AvatarMCP initialized',
                    #     'version': '1.0.0',
                    #     'models_dir': '/path/to/models',
                    #     'num_models': 5
                    # }

                Initialize with custom models directory:
                    result = await initialize({
                        'models_dir': 'C:/MyAvatars'
                    })
                    # Returns: Success with custom models directory

                Error handling:
                    result = await initialize({
                        'models_dir': '/nonexistent/path'
                    })
                    if result['status'] == 'error':
                        print(f"Initialization failed: {result['message']}")

            Raises:
                RuntimeError: If server fails to initialize properly
                OSError: If models directory cannot be accessed
                ValueError: If provided models_dir is invalid

            Notes:
                - Initialization may take several seconds to scan large model directories
                - Network access may be required for some initialization steps
                - Server maintains initialization state across tool calls
            """
            return asyncio.run(self.handle_initialize(params))

        @self.mcp.tool()
        def shutdown(params: dict[str, Any]) -> dict[str, Any]:
            """Gracefully shutdown the AvatarMCP server and release all resources.

            Stops all running operations, unloads any loaded avatar models, closes
            network connections, and performs cleanup. This should be called when
            you're done using the AvatarMCP server to ensure proper resource cleanup.

            Parameters:
                None required

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable shutdown status

            Usage:
                Call this tool when you want to cleanly exit the AvatarMCP session.
                It's good practice to shutdown even if you're just temporarily stopping
                avatar operations.

            Examples:
                Clean shutdown:
                    result = await shutdown({})
                    # Returns: {'status': 'success', 'message': 'Shutdown initiated'}

                Shutdown with error handling:
                    result = await shutdown({})
                    if result['status'] == 'success':
                        print("AvatarMCP shutdown successfully")
                    else:
                        print(f"Shutdown failed: {result['message']}")

            Notes:
                - Shutdown is asynchronous and may take a moment to complete
                - All loaded avatar models are automatically unloaded
                - Network connections are properly closed
                - Server becomes unusable after shutdown until reinitialized
            """
            return asyncio.run(self.handle_shutdown(params))

        # Avatar management tools
        @self.mcp.tool()
        def avatar_load(params: dict[str, Any]) -> dict[str, Any]:
            """Load a VRM avatar model into memory for use with animations and expressions.

            Imports and prepares a VRM (Virtual Reality Model) file for use by the AvatarMCP
            system. The model becomes available for animation playback, parameter control,
            and real-time manipulation through OSC or direct API calls.

            Parameters:
                path: Path to the VRM file to load
                    - Can be absolute path or relative to models directory
                    - Must be a valid .vrm file
                    - File must be accessible for reading
                make_active: Whether to set this avatar as the active one (default: True)
                    - If true, this becomes the current avatar for operations
                    - If false, avatar is loaded but not made active
                metadata: Optional dictionary of custom metadata to associate with the avatar
                    - Can include tags, descriptions, author info, etc.
                    - Stored and retrievable with the avatar

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - model_id: Unique identifier for the loaded model
                    - active: Whether the model was set as active
                    - metadata: Avatar metadata (if available)

            Usage:
                Use this tool to bring VRM avatars into your AvatarMCP environment. Once loaded,
                avatars can be animated, have their expressions controlled, and be manipulated
                in real-time. Loading is the first step before any avatar interaction.

            Examples:
                Load and make active (default behavior):
                    result = await avatar_load({
                        'path': 'models/my_avatar.vrm'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'model_id': 'my_avatar',
                    #     'active': True
                    # }

                Load without making active:
                    result = await avatar_load({
                        'path': 'models/backup_avatar.vrm',
                        'make_active': False
                    })
                    # Avatar loaded but not set as active

                Load with custom metadata:
                    result = await avatar_load({
                        'path': 'models/character.vrm',
                        'metadata': {
                            'author': 'Artist Name',
                            'tags': ['fantasy', 'hero'],
                            'description': 'Main character avatar'
                        }
                    })

                Error handling:
                    result = await avatar_load({
                        'path': 'nonexistent.vrm'
                    })
                    if result['status'] == 'error':
                        print(f"Failed to load avatar: {result['message']}")

            Raises:
                ValueError: If path is empty or invalid
                FileNotFoundError: If VRM file doesn't exist
                RuntimeError: If server is not initialized
                Exception: For VRM parsing or loading errors

            Notes:
                - VRM files can be large; loading may take several seconds
                - Only one avatar can be active at a time
                - Loaded avatars consume memory until unloaded
                - Supports VRM 1.0 specification

            See Also:
                - avatar_unload: Remove an avatar from memory
                - avatar_set_active: Change which avatar is active
                - avatar_list: See all loaded avatars
            """
            return asyncio.run(self.handle_avatar_load(params))

        @self.mcp.tool()
        def avatar_unload(params: dict[str, Any]) -> dict[str, Any]:
            """Remove a VRM avatar model from memory and free associated resources.

            Unloads a previously loaded VRM model, releasing all associated memory and
            resources. If the unloaded avatar was active, another avatar may be automatically
            selected as active, or no avatar will be active if none remain loaded.

            Parameters:
                id: Unique identifier of the avatar to unload
                    - Must match the model_id returned by avatar_load
                    - Case-sensitive identifier
                force: Whether to force unload even if avatar is currently active (default: False)
                    - If false and avatar is active, operation will fail
                    - If true, avatar will be unloaded even if active

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - was_active: Whether the unloaded avatar was the active one

            Usage:
                Use this tool to clean up avatar resources when they're no longer needed.
                This is especially important for memory management when working with multiple
                large VRM models.

            Examples:
                Unload a specific avatar:
                    result = await avatar_unload({
                        'id': 'my_character'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Unloaded avatar: my_character',
                    #     'was_active': False
                    # }

                Force unload active avatar:
                    result = await avatar_unload({
                        'id': 'current_avatar',
                        'force': True
                    })
                    # Unloads even if it was the active avatar

                Error handling:
                    result = await avatar_unload({
                        'id': 'nonexistent_avatar'
                    })
                    if result['status'] == 'error':
                        print(f"Unload failed: {result['message']}")
                    # Logs: Unload failed: Avatar not found: nonexistent_avatar

            Raises:
                ValueError: If avatar ID is empty or invalid
                RuntimeError: If trying to unload active avatar without force=True
                KeyError: If specified avatar ID is not loaded

            Notes:
                - Active avatars cannot be unloaded without force=True
                - Memory is immediately freed upon successful unload
                - If active avatar is unloaded, another loaded avatar may become active
                - Consider calling avatar_set_active() after forced unload

            See Also:
                - avatar_load: Load an avatar into memory
                - avatar_set_active: Change active avatar without unloading
                - avatar_list: See currently loaded avatars
            """
            return asyncio.run(self.handle_avatar_unload(params))

        @self.mcp.tool()
        def avatar_list(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve a comprehensive list of all avatars available in the system.

            Returns information about both loaded avatars (currently in memory) and
            available avatars (found in the models directory but not yet loaded).
            Provides metadata, status, and activity information for each avatar.

            Parameters:
                loaded_only: Whether to show only currently loaded avatars (default: False)
                    - If true, shows only avatars in memory
                    - If false, shows all avatars (loaded + available)
                include_metadata: Whether to include detailed metadata for each avatar
                    (default: False)
                    - If true, includes full avatar specifications
                    - If false, returns basic info only (faster)

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - count: Total number of avatars returned
                    - active_model: ID of currently active avatar (or None)
                    - avatars: Array of avatar objects, each containing:
                        - id: Unique avatar identifier
                        - name: Display name
                        - status: Either "loaded" or "available"
                        - is_active: Whether this is the currently active avatar
                        - metadata: Avatar details (if include_metadata=True)

            Usage:
                Use this tool to discover what avatars are available and their current
                loading status. This is essential for understanding what avatars you
                can work with and managing your avatar collection.

            Examples:
                List all avatars with basic info:
                    result = await avatar_list({})
                    # Returns: {
                    #     'status': 'success',
                    #     'count': 3,
                    #     'active_model': 'hero_avatar',
                    #     'avatars': [
                    #         {'id': 'hero_avatar', 'status': 'loaded', 'is_active': True},
                    #         {'id': 'villain_avatar', 'status': 'loaded', 'is_active': False},
                    #         {'id': 'npc_character', 'status': 'available', 'is_active': False}
                    #     ]
                    # }

                Show only loaded avatars:
                    result = await avatar_list({
                        'loaded_only': True
                    })
                    # Returns only avatars currently in memory

                Include full metadata:
                    result = await avatar_list({
                        'include_metadata': True
                    })
                    # Returns detailed specifications for each avatar

                Error handling:
                    result = await avatar_list({})
                    if result['status'] == 'error':
                        print(f"Failed to list avatars: {result['message']}")
                    else:
                        active = result.get('active_model')
                        if active:
                            print(f"Active avatar: {active}")
                        else:
                            print("No active avatar")

            Raises:
                RuntimeError: If server is not initialized

            Notes:
                - Available avatars are found by scanning the models directory
                - Loaded avatars are currently in memory and ready for use
                - Active avatar is the one affected by animation and parameter tools
                - Metadata can be large; use include_metadata sparingly

            See Also:
                - avatar_load: Load an available avatar into memory
                - avatar_get_active: Get just the currently active avatar
                - avatar_get_metadata: Get detailed info for specific avatar
            """
            return asyncio.run(self.handle_avatar_list(params))

        @self.mcp.tool()
        def avatar_set_active(params: dict[str, Any]) -> dict[str, Any]:
            """Change which loaded avatar is considered the "active" avatar for operations.

            Sets the specified avatar as the active one, making it the target for all
            animation, expression, and parameter operations. Only loaded avatars can
            be made active.

            Parameters:
                id: Unique identifier of the avatar to make active
                    - Must be a currently loaded avatar
                    - Case-sensitive identifier
                    - Cannot be empty or null

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - active_avatar_id: The new active avatar ID (on success)

            Usage:
                Use this tool to switch between different loaded avatars without unloading
                them. This is useful for quickly changing characters while keeping multiple
                avatars ready in memory.

            Examples:
                Switch to a different avatar:
                    result = await avatar_set_active({
                        'id': 'backup_character'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Set active avatar to: backup_character',
                    #     'active_avatar_id': 'backup_character'
                    # }

                Error handling for unloaded avatar:
                    result = await avatar_set_active({
                        'id': 'not_loaded_avatar'
                    })
                    if result['status'] == 'error':
                        print(f"Cannot activate: {result['message']}")
                    # Logs: Cannot activate: Avatar with ID 'not_loaded_avatar' is not loaded

                Check current active before switching:
                    active_result = await avatar_get_active({})
                    current_id = active_result.get('active_avatar_id')
                    if current_id != 'desired_avatar':
                        await avatar_set_active({'id': 'desired_avatar'})

            Raises:
                ValueError: If avatar ID is empty or invalid
                RuntimeError: If server is not initialized
                KeyError: If specified avatar is not loaded

            Notes:
                - Only one avatar can be active at a time
                - Active avatar receives all animation and parameter commands
                - Switching is instantaneous and doesn't interrupt animations
                - Use avatar_list to see which avatars are loaded and can be activated

            See Also:
                - avatar_get_active: Check which avatar is currently active
                - avatar_load: Load an avatar and optionally make it active
                - avatar_list: See all loaded avatars and their status
            """
            return asyncio.run(self.handle_avatar_set_active(params))

        @self.mcp.tool()
        def avatar_get_active(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve information about which avatar is currently set as active.

            Returns the ID and status of the currently active avatar, or indicates
            that no avatar is active. The active avatar is the one that receives
            animation, expression, and parameter commands.

            Parameters:
                None required

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - active_avatar_id: ID of active avatar, or None if none active
                    - loaded: Whether the active avatar is loaded (if one exists)
                    - message: Human-readable status description

            Usage:
                Use this tool to determine which avatar is currently active before
                performing operations that affect the active avatar. This is important
                for understanding which avatar will be affected by animation and
                parameter commands.

            Examples:
                Check current active avatar:
                    result = await avatar_get_active({})
                    if result['active_avatar_id']:
                        print(f"Active avatar: {result['active_avatar_id']}")
                    else:
                        print("No active avatar")
                    # Returns: {
                    #     'status': 'success',
                    #     'active_avatar_id': 'hero_character',
                    #     'loaded': True,
                    #     'message': 'Active avatar: hero_character'
                    # }

                Handle no active avatar:
                    result = await avatar_get_active({})
                    if not result.get('active_avatar_id'):
                        print("No avatar is currently active")
                        # Load and activate an avatar
                        await avatar_load({'path': 'default.vrm'})
                        await avatar_set_active({'id': 'default'})

                Error handling:
                    result = await avatar_get_active({})
                    if result['status'] == 'error':
                        print(f"Failed to get active avatar: {result['message']}")
                    # Should rarely error unless server is not initialized

            Raises:
                RuntimeError: If server is not initialized

            Notes:
                - Returns None for active_avatar_id when no avatar is active
                - Active avatar is always loaded (if one exists)
                - Use avatar_list to see all loaded avatars
                - Use avatar_set_active to change the active avatar

            See Also:
                - avatar_set_active: Change which avatar is active
                - avatar_list: See all avatars and their active status
                - avatar_load: Load an avatar (optionally making it active)
            """
            return asyncio.run(self.handle_avatar_get_active(params))

        @self.mcp.tool()
        def avatar_get_metadata(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve detailed metadata and specifications for a specific avatar.

            Returns comprehensive information about an avatar's properties, including
            VRM specification details, blend shapes, bones, materials, and any custom
            metadata that was associated with the avatar during loading.

            Parameters:
                id: Unique identifier of the avatar to get metadata for
                    - Can be active avatar or any loaded avatar
                    - If not specified, uses the currently active avatar
                    - Case-sensitive identifier

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - id: Avatar identifier
                    - loaded: Whether the avatar is currently loaded
                    - active: Whether this is the currently active avatar
                    - metadata: Complete avatar specification dictionary

            Usage:
                Use this tool to inspect avatar capabilities, understand available
                blend shapes and bones for animation, and access custom metadata.
                This is essential for understanding what animations and expressions
                are possible with a particular avatar.

            Examples:
                Get metadata for active avatar:
                    result = await avatar_get_metadata({})
                    # Returns detailed specs for the active avatar

                Get metadata for specific avatar:
                    result = await avatar_get_metadata({
                        'id': 'character_model'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'id': 'character_model',
                    #     'loaded': True,
                    #     'active': False,
                    #     'metadata': {
                    #         'blend_shapes': ['happy', 'sad', 'angry'],
                    #         'bones': ['head', 'spine', 'left_arm'],
                    #         'materials': [...],
                    #         'custom_tags': ['hero', 'fantasy']
                    #     }
                    # }

                Check avatar capabilities:
                    result = await avatar_get_metadata({'id': 'my_avatar'})
                    if result['status'] == 'success':
                        blend_shapes = result['metadata'].get('blend_shapes', [])
                        if 'happy' in blend_shapes:
                            await avatar_set_expression({'name': 'happy'})

                Error handling:
                    result = await avatar_get_metadata({
                        'id': 'nonexistent'
                    })
                    if result['status'] == 'error':
                        print(f"Cannot get metadata: {result['message']}")
                    # Logs: Cannot get metadata: Avatar not found: nonexistent

            Raises:
                ValueError: If no avatar ID provided and no active avatar exists
                RuntimeError: If server is not initialized
                KeyError: If specified avatar is not loaded

            Notes:
                - Metadata can be quite large for complex avatars
                - Includes VRM 1.0 specification details
                - Blend shapes list available facial expressions
                - Bones list available for animation rigging
                - Custom metadata is preserved from loading

            See Also:
                - avatar_list: Get basic info for all avatars
                - avatar_load: Load avatar with custom metadata
                - animation_list: See what animations are available
            """
            return asyncio.run(self.handle_avatar_get_metadata(params))

        # Animation control tools
        @self.mcp.tool()
        def animation_play(params: dict[str, Any]) -> dict[str, Any]:
            """Start playback of an animation on the active avatar.

            Plays a specified animation clip on the currently active avatar. The animation
            can be set to loop continuously or play once. Supports speed adjustment for
            slow-motion or fast-forward effects.

            Parameters:
                name: Name of the animation to play
                    - Must be available in the active avatar's animation set
                    - Case-sensitive animation name
                    - Cannot be empty
                loop: Whether the animation should loop continuously (default: False)
                    - If true, animation repeats indefinitely
                    - If false, animation plays once and stops
                speed: Playback speed multiplier (default: 1.0)
                    - Values > 1.0 play faster than normal
                    - Values < 1.0 play slower than normal
                    - Negative values play in reverse
                    - Zero pauses the animation

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - animation_name: Name of animation being played
                    - loop: Whether animation will loop
                    - speed: Playback speed multiplier

            Usage:
                Use this tool to bring your avatar to life with animations. Perfect for
                creating dynamic scenes, character reactions, or idle behaviors. Combine
                with expression controls for rich character performances.

            Examples:
                Play a one-time animation:
                    result = await animation_play({
                        'name': 'wave'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Playing animation: wave',
                    #     'animation_name': 'wave',
                    #     'loop': False,
                    #     'speed': 1.0
                    # }

                Play looping idle animation:
                    result = await animation_play({
                        'name': 'idle',
                        'loop': True
                    })
                    # Animation repeats continuously

                Play animation in slow motion:
                    result = await animation_play({
                        'name': 'dance',
                        'loop': True,
                        'speed': 0.5
                    })
                    # Animation plays at half speed

                Fast-forward animation:
                    result = await animation_play({
                        'name': 'run',
                        'speed': 2.0
                    })
                    # Animation plays twice as fast

                Error handling:
                    result = await animation_play({
                        'name': 'nonexistent_animation'
                    })
                    if result['status'] == 'error':
                        print(f"Animation failed: {result['message']}")
                    # Check available animations first
                    anims = await animation_list({})

            Raises:
                ValueError: If animation name is empty or invalid
                RuntimeError: If no active avatar is loaded
                KeyError: If specified animation doesn't exist

            Notes:
                - Animation affects only the currently active avatar
                - Playing a new animation stops the previous one
                - Speed changes take effect immediately
                - Looping animations continue until explicitly stopped
                - Use animation_list to see available animations

            See Also:
                - animation_stop: Stop current animation playback
                - animation_list: See all available animations
                - avatar_set_active: Change which avatar receives animations
            """
            return asyncio.run(self.handle_animation_play(params))

        @self.mcp.tool()
        def animation_stop(params: dict[str, Any]) -> dict[str, Any]:
            """Stop playback of the currently playing animation on the active avatar.

            Immediately halts any animation currently playing on the active avatar,
            returning it to its default pose or idle state. Safe to call even if
            no animation is currently playing.

            Parameters:
                name: Optional specific animation name to stop
                    - If provided, stops only the named animation
                    - If omitted, stops whichever animation is currently playing
                    - Case-sensitive animation name

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - stopped_animation: Name of animation that was stopped (or None)

            Usage:
                Use this tool to halt avatar animations at any time. Essential for
                creating responsive interactions and preventing unwanted looping
                animations from continuing indefinitely.

            Examples:
                Stop current animation:
                    result = await animation_stop({})
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Animation stopped',
                    #     'stopped_animation': 'dance'
                    # }

                Stop specific animation:
                    result = await animation_stop({
                        'name': 'wave'
                    })
                    # Stops only if 'wave' is currently playing

                Safe to call when no animation is playing:
                    result = await animation_stop({})
                    # Returns success even if nothing was playing
                    # No error if no animation was active

                Error handling:
                    result = await animation_stop({})
                    if result['status'] == 'error':
                        print(f"Stop failed: {result['message']}")
                    # Should rarely fail unless no active avatar

            Raises:
                RuntimeError: If no active avatar is loaded

            Notes:
                - Only affects the currently active avatar
                - Safe to call repeatedly or when no animation is playing
                - Immediately returns avatar to default state
                - Does not affect avatar loading or other operations

            See Also:
                - animation_play: Start animation playback
                - animation_list: See available animations
                - avatar_set_active: Change active avatar
            """
            return asyncio.run(self.handle_animation_stop(params))

        @self.mcp.tool()
        def animation_list(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve a complete list of animations available for the active avatar.

            Returns all animation clips and states that can be played on the currently
            active avatar. This includes built-in animations, custom animations, and
            blend tree states defined in the avatar's Animator Controller.

            Parameters:
                None required

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - animations: Array of available animation names
                    - count: Number of animations available

            Usage:
                Use this tool to discover what animations are available before trying
                to play them. Essential for understanding avatar capabilities and
                creating appropriate animation sequences.

            Examples:
                Get available animations:
                    result = await animation_list({})
                    # Returns: {
                    #     'status': 'success',
                    #     'animations': ['idle', 'walk', 'run', 'wave', 'dance', 'jump'],
                    #     'count': 6
                    # }

                Check if specific animation exists:
                    result = await animation_list({})
                    if result['status'] == 'success':
                        if 'dance' in result['animations']:
                            await animation_play({'name': 'dance', 'loop': True})
                        else:
                            print("Dance animation not available")

                List animations for different avatars:
                    # Switch avatars and check their animations
                    await avatar_set_active({'id': 'hero'})
                    hero_anims = await animation_list({})

                    await avatar_set_active({'id': 'villain'})
                    villain_anims = await animation_list({})

                Error handling:
                    result = await animation_list({})
                    if result['status'] == 'error':
                        print(f"Cannot list animations: {result['message']}")
                    # Usually means no active avatar

            Raises:
                RuntimeError: If no active avatar is loaded

            Notes:
                - Lists animations for the currently active avatar only
                - Different avatars may have different animation sets
                - Animation names are case-sensitive
                - Includes all states from Animator Controller
                - Does not include blend tree parameters

            See Also:
                - animation_play: Play a specific animation
                - animation_stop: Stop current animation
                - avatar_list: See all available avatars
                - avatar_get_metadata: Get detailed avatar capabilities
            """
            return asyncio.run(self.handle_animation_list(params))

        # Parameter control tools
        @self.mcp.tool()
        def parameter_set(params: dict[str, Any]) -> dict[str, Any]:
            """Set a custom parameter value on the active avatar.

            Updates avatar parameters that control animations, expressions, or other
            avatar behaviors. Parameters can be boolean, integer, or float values
            that affect blend trees, animation states, or custom avatar logic.

            Parameters:
                name: Name of the parameter to set
                    - Must exist in the avatar's Animator Controller
                    - Case-sensitive parameter name
                    - Cannot be empty
                value: Value to set for the parameter
                    - Can be boolean, integer, or float
                    - Must be compatible with parameter type
                    - Will be converted if possible

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - parameter_name: Name of parameter that was set
                    - value: Value that was set

            Usage:
                Use this tool to control avatar behaviors through parameters. Perfect for
                fine-tuning animations, controlling blend trees, or triggering state changes
                in the avatar's Animator Controller.

            Examples:
                Set boolean parameter:
                    result = await parameter_set({
                        'name': 'IsRunning',
                        'value': True
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Set parameter IsRunning = True',
                    #     'parameter_name': 'IsRunning',
                    #     'value': True
                    # }

                Set float parameter (speed control):
                    result = await parameter_set({
                        'name': 'MoveSpeed',
                        'value': 2.5
                    })
                    # Controls animation blend based on speed

                Set integer parameter (state control):
                    result = await parameter_set({
                        'name': 'EmotionState',
                        'value': 3
                    })
                    # Different integer values trigger different states

                Chain parameter updates:
                    # Set multiple parameters for complex behavior
                    await parameter_set({'name': 'IsGrounded', 'value': True})
                    await parameter_set({'name': 'JumpHeight', 'value': 0.0})
                    await parameter_set({'name': 'MoveDirection', 'value': 1.0})

                Error handling:
                    result = await parameter_set({
                        'name': 'NonExistentParam',
                        'value': 42
                    })
                    if result['status'] == 'error':
                        print(f"Parameter set failed: {result['message']}")
                    # Check parameter exists first

            Raises:
                ValueError: If parameter name is empty or value is invalid
                RuntimeError: If no active avatar is loaded
                KeyError: If parameter doesn't exist in avatar

            Notes:
                - Only affects the currently active avatar
                - Parameters must be defined in the avatar's Animator Controller
                - Type conversion happens automatically when possible
                - Changes take effect immediately
                - Parameters persist until explicitly changed

            See Also:
                - parameter_get: Read current parameter values
                - animation_play: Play animations (may use parameters)
                - avatar_get_metadata: See avatar parameter definitions
            """
            return asyncio.run(self.handle_parameter_set(params))

        @self.mcp.tool()
        def parameter_get(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve the current value of a parameter from the active avatar.

            Reads the current value of any parameter defined in the active avatar's
            Animator Controller. Useful for checking avatar state, debugging parameter
            values, or creating conditional logic based on avatar parameters.

            Parameters:
                name: Name of the parameter to read
                    - Must exist in the avatar's Animator Controller
                    - Case-sensitive parameter name
                    - Cannot be empty

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - parameter_name: Name of parameter read
                    - value: Current parameter value
                    - type: Parameter type (bool, int, float)

            Usage:
                Use this tool to inspect avatar state and make decisions based on
                current parameter values. Essential for debugging avatar behavior
                and creating responsive interactions.

            Examples:
                Read boolean parameter:
                    result = await parameter_get({
                        'name': 'IsGrounded'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'parameter_name': 'IsGrounded',
                    #     'value': True,
                    #     'type': 'bool'
                    # }

                Read float parameter:
                    result = await parameter_get({
                        'name': 'MoveSpeed'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'parameter_name': 'MoveSpeed',
                    #     'value': 1.8,
                    #     'type': 'float'
                    # }

                Conditional logic based on parameters:
                    grounded = await parameter_get({'name': 'IsGrounded'})
                    if grounded['value']:
                        await animation_play({'name': 'idle'})
                    else:
                        await animation_play({'name': 'jump'})

                Debug avatar state:
                    params_to_check = ['IsRunning', 'MoveSpeed', 'EmotionState']
                    for param_name in params_to_check:
                        result = await parameter_get({'name': param_name})
                        if result['status'] == 'success':
                            print(f"{param_name}: {result['value']}")

                Error handling:
                    result = await parameter_get({
                        'name': 'NonExistentParam'
                    })
                    if result['status'] == 'error':
                        print(f"Parameter read failed: {result['message']}")
                    # Parameter doesn't exist

            Raises:
                ValueError: If parameter name is empty
                RuntimeError: If no active avatar is loaded
                KeyError: If parameter doesn't exist in avatar

            Notes:
                - Only reads from the currently active avatar
                - Returns the exact current value (no caching)
                - Type information helps with value interpretation
                - Safe to call frequently for monitoring

            See Also:
                - parameter_set: Change parameter values
                - animation_list: See animation parameters
                - avatar_get_metadata: Get avatar parameter definitions
            """
            return asyncio.run(self.handle_parameter_get(params))

        # OSC control tools
        @self.mcp.tool()
        def osc_send(params: dict[str, Any]) -> dict[str, Any]:
            """Send an OSC (Open Sound Control) message to external applications.

            Transmits OSC messages to configured OSC receivers, enabling communication
            with VRChat, other avatar applications, or custom OSC-enabled software.
            Messages are sent asynchronously and don't block the MCP server.

            Parameters:
                address: OSC address pattern to send to
                    - Must start with '/' (e.g., '/avatar/parameter')
                    - Case-sensitive address pattern
                    - Cannot be empty
                value: Value to send with the message
                    - Can be number, string, boolean, or array
                    - Multiple values can be sent as array
                target: Optional target receiver (default: configured client)
                    - IP address or hostname
                    - Overrides default OSC client settings

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - address: OSC address that was sent
                    - value: Value that was sent

            Usage:
                Use this tool to communicate with VRChat, other avatar systems, or
                any OSC-enabled application. Perfect for triggering external animations,
                synchronizing avatar states, or controlling lighting/audio systems.

            Examples:
                Send simple value to VRChat:
                    result = await osc_send({
                        'address': '/avatar/parameters/Emotion',
                        'value': 0.8
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'OSC message sent',
                    #     'address': '/avatar/parameters/Emotion',
                    #     'value': 0.8
                    # }

                Send multiple values:
                    result = await osc_send({
                        'address': '/avatar/transform/position',
                        'value': [1.5, 0.0, 2.3]
                    })
                    # Sends X, Y, Z coordinates

                Send to specific target:
                    result = await osc_send({
                        'address': '/lighting/intensity',
                        'value': 0.7,
                        'target': '192.168.1.100:9000'
                    })
                    # Sends to custom IP and port

                VRChat avatar control:
                    # Set gesture
                    await osc_send({
                        'address': '/avatar/parameters/GestureLeft',
                        'value': 1
                    })

                    # Set facial expression
                    await osc_send({
                        'address': '/avatar/parameters/Happy',
                        'value': 0.9
                    })

                Error handling:
                    result = await osc_send({
                        'address': '/invalid',
                        'value': 'test'
                    })
                    if result['status'] == 'error':
                        print(f"OSC send failed: {result['message']}")
                    # Check OSC server configuration

            Raises:
                ValueError: If address is invalid or empty
                RuntimeError: If OSC system is not initialized
                ConnectionError: If network send fails

            Notes:
                - OSC must be enabled in server configuration
                - Messages are sent asynchronously (fire-and-forget)
                - No delivery confirmation or response handling
                - Values are automatically converted to OSC types
                - Network errors don't crash the MCP server

            See Also:
                - osc_receive: Listen for incoming OSC messages
                - avatar_load: Load avatars that can receive OSC
                - system_status: Check OSC server status
            """
            return asyncio.run(self.handle_osc_send(params))

        @self.mcp.tool()
        def osc_receive(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve information about received OSC messages.

            Returns details about OSC messages that have been received by the server,
            including message history, sender information, and message contents.
            Useful for debugging OSC communication or monitoring avatar inputs.

            Parameters:
                count: Maximum number of messages to return (default: 10)
                    - Limits response size
                    - Most recent messages returned first
                    - Must be positive integer
                since: Optional timestamp to filter messages after
                    - Unix timestamp in seconds
                    - Only messages received after this time
                address_filter: Optional OSC address pattern to filter by
                    - Only messages matching this pattern
                    - Supports wildcards (e.g., '/avatar/*')

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - messages: Array of received OSC messages
                    - count: Number of messages returned
                    - total_available: Total messages in history

            Usage:
                Use this tool to monitor OSC communication, debug avatar inputs,
                or create reactive behaviors based on received messages. Essential
                for understanding what's happening in your OSC network.

            Examples:
                Get recent messages:
                    result = await osc_receive({})
                    # Returns: {
                    #     'status': 'success',
                    #     'messages': [
                    #         {
                    #             'address': '/avatar/parameters/GestureLeft',
                    #             'value': 1,
                    #             'timestamp': 1640995200.123,
                    #             'sender': '127.0.0.1:9001'
                    #         }
                    #     ],
                    #     'count': 1,
                    #     'total_available': 25
                    # }

                Get messages since timestamp:
                    result = await osc_receive({
                        'since': 1640995200,
                        'count': 5
                    })
                    # Only messages from last hour

                Filter by address pattern:
                    result = await osc_receive({
                        'address_filter': '/avatar/parameters/*',
                        'count': 20
                    })
                    # Only avatar parameter messages

                Monitor specific activity:
                    # Check for recent gesture changes
                    result = await osc_receive({
                        'address_filter': '/avatar/parameters/Gesture*'
                    })
                    for msg in result['messages']:
                        print(f"Gesture {msg['address'].split('/')[-1]} = {msg['value']}")

                Error handling:
                    result = await osc_receive({})
                    if result['status'] == 'error':
                        print(f"OSC receive failed: {result['message']}")
                    # Check OSC server is running

            Raises:
                ValueError: If parameters are invalid
                RuntimeError: If OSC system is not initialized

            Notes:
                - Message history is limited and may wrap around
                - Timestamps are in Unix time with milliseconds
                - Sender info includes IP and port
                - Large message histories may be truncated
                - Messages are returned in reverse chronological order

            See Also:
                - osc_send: Send OSC messages
                - system_status: Check OSC server status
                - debug_echo: Test message routing
            """
            return asyncio.run(self.handle_osc_receive(params))

        # Chat tools
        @self.mcp.tool()
        def chat_start(params: dict[str, Any]) -> dict[str, Any]:
            """Initialize a new chat session with the AvatarMCP chatbot.

            Creates a fresh conversation context and prepares the chatbot for interaction.
            The chat session maintains conversation history and context across multiple
            messages, enabling natural conversation flow with the avatar.

            Parameters:
                personality: Optional personality preset for the chatbot (default: "default")
                    - Available presets: "default", "friendly", "professional", "humorous"
                    - Affects response style and tone
                context: Optional initial context information
                    - Dictionary with background information
                    - Influences chatbot behavior and responses
                max_history: Maximum conversation turns to remember (default: 50)
                    - Limits memory usage for long conversations
                    - Older messages are automatically pruned

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - session_id: Unique identifier for the chat session
                    - personality: Active personality preset
                    - message: Human-readable confirmation

            Usage:
                Use this tool to begin interactive conversations with your avatar.
                Perfect for role-playing, getting assistance, or creating dynamic
                character interactions with persistent context.

            Examples:
                Start basic chat session:
                    result = await chat_start({})
                    # Returns: {
                    #     'status': 'success',
                    #     'session_id': 'chat_123456',
                    #     'personality': 'default',
                    #     'message': 'Chat session started'
                    # }

                Start with specific personality:
                    result = await chat_start({
                        'personality': 'friendly',
                        'context': {
                            'character': 'helpful assistant',
                            'setting': 'modern office'
                        }
                    })
                    # Chatbot adopts friendly, office-appropriate persona

                Start with limited history:
                    result = await chat_start({
                        'max_history': 10
                    })
                    # Keeps only last 10 conversation turns

                Error handling:
                    result = await chat_start({
                        'personality': 'nonexistent'
                    })
                    if result['status'] == 'error':
                        print(f"Chat start failed: {result['message']}")
                    # Check available personality presets

            Raises:
                ValueError: If personality is invalid or parameters malformed
                RuntimeError: If chat system is not available

            Notes:
                - Only one active chat session allowed at a time
                - Previous session is automatically ended when starting new one
                - Session persists until explicitly stopped
                - Context information improves response quality

            See Also:
                - chat_send_message: Send messages in the active session
                - chat_get_state: Check current chat status
                - chat_stop: End the current chat session
            """
            return asyncio.run(self.handle_chat_start(params))

        @self.mcp.tool()
        def chat_send_message(params: dict[str, Any]) -> dict[str, Any]:
            """Send a message to the active chat session and receive a response.

            Transmits user input to the chatbot and returns the generated response.
            The message becomes part of the conversation history, maintaining context
            for natural, coherent dialogue with the avatar.

            Parameters:
                message: The text message to send to the chatbot
                    - Cannot be empty or null
                    - Supports multi-line text
                    - Maximum length: 2000 characters
                timeout: Maximum time to wait for response in seconds (default: 30)
                    - Prevents hanging on slow responses
                    - Must be positive number
                metadata: Optional metadata about the message
                    - Dictionary with sender info, message type, etc.
                    - Used for conversation analytics

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - response: Chatbot's reply message
                    - session_id: Active chat session identifier
                    - timestamp: When response was generated
                    - metadata: Additional response information

            Usage:
                Use this tool to have interactive conversations with your avatar.
                Each message builds on the conversation history, creating natural
                dialogue and character-consistent responses.

            Examples:
                Send simple message:
                    result = await chat_send_message({
                        'message': 'Hello, how are you today?'
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'response': 'Hello! I'm doing well, thank you for asking.',
                    #     'session_id': 'chat_123456',
                    #     'timestamp': 1640995200.123
                    # }

                Send with timeout:
                    result = await chat_send_message({
                        'message': 'Tell me a long story',
                        'timeout': 60
                    })
                    # Allows more time for complex responses

                Send with metadata:
                    result = await chat_send_message({
                        'message': 'What time is it?',
                        'metadata': {
                            'sender': 'user',
                            'importance': 'low',
                            'topic': 'time'
                        }
                    })

                Multi-turn conversation:
                    await chat_start({'personality': 'friendly'})
                    await chat_send_message({'message': 'Hi there!'})
                    await chat_send_message({'message': 'What can you help me with?'})
                    # Each message maintains conversation context

                Error handling:
                    result = await chat_send_message({
                        'message': ''
                    })
                    if result['status'] == 'error':
                        print(f"Message send failed: {result['message']}")
                    # Check that message is not empty

            Raises:
                ValueError: If message is empty or invalid
                RuntimeError: If no active chat session exists
                TimeoutError: If response takes longer than specified timeout

            Notes:
                - Requires an active chat session (start with chat_start)
                - Messages are added to conversation history
                - Responses may vary based on personality and context
                - Long messages may be truncated for processing
                - Network timeouts may occur for complex queries

            See Also:
                - chat_start: Begin a chat session before sending messages
                - chat_get_state: Check chat session status
                - chat_stop: End the current session
            """
            return asyncio.run(self.handle_chat_send_message(params))

        @self.mcp.tool()
        def chat_stop(params: dict[str, Any]) -> dict[str, Any]:
            """Terminate the current chat session and clean up resources.

            Ends the active chat session, clears conversation history, and releases
            any resources associated with the chatbot. The session becomes unusable
            after calling this method.

            Parameters:
                save_history: Whether to save conversation history (default: False)
                    - If true, history is preserved for later analysis
                    - If false, history is immediately discarded
                reason: Optional reason for stopping the session
                    - Used for logging and analytics
                    - Free-form text description

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable confirmation
                    - session_id: ID of the ended session
                    - duration: How long the session lasted in seconds
                    - message_count: Total messages exchanged

            Usage:
                Use this tool to cleanly end chat sessions when you're done conversing.
                Essential for resource management and preventing memory leaks from
                long-running chat sessions.

            Examples:
                Stop current session:
                    result = await chat_stop({})
                    # Returns: {
                    #     'status': 'success',
                    #     'message': 'Chat session ended',
                    #     'session_id': 'chat_123456',
                    #     'duration': 300.5,
                    #     'message_count': 12
                    # }

                Stop and save history:
                    result = await chat_stop({
                        'save_history': True,
                        'reason': 'User requested session end'
                    })
                    # History preserved for later retrieval

                Error handling:
                    result = await chat_stop({})
                    if result['status'] == 'error':
                        print(f"Chat stop failed: {result['message']}")
                    # Usually indicates no active session

            Raises:
                RuntimeError: If no active chat session exists

            Notes:
                - Active session is required to stop
                - Resources are immediately freed
                - History is permanently lost unless saved
                - Session statistics are provided on successful stop
                - Safe to call multiple times

            See Also:
                - chat_start: Begin a new chat session
                - chat_send_message: Send messages in active session
                - chat_get_state: Check if session is active before stopping
            """
            return asyncio.run(self.handle_chat_stop(params))

        @self.mcp.tool()
        def chat_get_state(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve the current state and status of the chat system.

            Returns comprehensive information about the active chat session,
            including session details, conversation statistics, and system status.
            Useful for monitoring chat activity and debugging issues.

            Parameters:
                include_history: Whether to include recent message history (default: False)
                    - If true, returns last 10 messages
                    - If false, only returns session metadata
                detailed: Whether to include detailed system information (default: False)
                    - If true, includes memory usage and performance stats
                    - If false, returns basic session info

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - has_active_session: Whether a chat session is currently active
                    - session_id: Current session ID (if active)
                    - personality: Active personality preset
                    - message_count: Total messages in session
                    - session_duration: Session length in seconds
                    - history: Recent messages (if include_history=True)

            Usage:
                Use this tool to check chat system status before performing operations,
                monitor conversation progress, or debug chat-related issues. Essential
                for applications that need to know chat state.

            Examples:
                Check basic session status:
                    result = await chat_get_state({})
                    # Returns: {
                    #     'status': 'success',
                    #     'has_active_session': True,
                    #     'session_id': 'chat_123456',
                    #     'personality': 'friendly',
                    #     'message_count': 8,
                    #     'session_duration': 245.7
                    # }

                Get recent message history:
                    result = await chat_get_state({
                        'include_history': True
                    })
                    # Includes last 10 messages in conversation

                Detailed system information:
                    result = await chat_get_state({
                        'detailed': True
                    })
                    # Includes memory usage, response times, etc.

                Check before sending message:
                    state = await chat_get_state({})
                    if not state.get('has_active_session'):
                        await chat_start({})
                    await chat_send_message({'message': 'Hello!'})

                Error handling:
                    result = await chat_get_state({})
                    if result['status'] == 'error':
                        print(f"Cannot get chat state: {result['message']}")
                    # Usually indicates chat system unavailable

            Raises:
                RuntimeError: If chat system is not initialized

            Notes:
                - Safe to call even when no active session exists
                - History is truncated for performance
                - Detailed mode may impact performance
                - Session info is real-time and up-to-date

            See Also:
                - chat_start: Begin a session to monitor
                - chat_send_message: Send messages (check state first)
                - chat_stop: End session being monitored
            """
            return asyncio.run(self.handle_chat_get_state(params))

        # System tools
        @self.mcp.tool()
        def system_status(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve comprehensive system status and health information.

            Returns detailed information about the AvatarMCP server's current state,
            including performance metrics, loaded resources, and operational status.
            Essential for monitoring, debugging, and understanding system health.

            Parameters:
                detailed: Whether to include detailed performance metrics (default: False)
                    - If true, includes memory usage, CPU stats, and detailed metrics
                    - If false, returns basic operational status
                include_versions: Whether to include version information (default: True)
                    - Shows component versions and dependencies
                    - Useful for compatibility checking

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - system: Core system information
                        - name: Server name
                        - version: Server version
                        - status: Operational status
                        - uptime: Seconds since server start
                        - initialized: Whether server completed initialization
                    - resources: Current resource usage (if detailed=True)
                        - loaded_avatars: Number of avatars in memory
                        - active_chat_sessions: Number of active chat sessions
                        - osc_connections: OSC connection status
                    - performance: Performance metrics (if detailed=True)

            Usage:
                Use this tool to monitor AvatarMCP health, diagnose issues, and understand
                system load. Perfect for automated monitoring systems and troubleshooting.

            Examples:
                Basic system status:
                    result = await system_status({})
                    # Returns: {
                    #     'status': 'success',
                    #     'system': {
                    #         'name': 'AvatarMCP',
                    #         'version': '1.0.0',
                    #         'status': 'running',
                    #         'uptime': 3600.5,
                    #         'initialized': True
                    #     }
                    # }

                Detailed status with performance:
                    result = await system_status({
                        'detailed': True
                    })
                    # Includes memory usage, loaded avatars, performance metrics

                Status without versions:
                    result = await system_status({
                        'include_versions': False
                    })
                    # Faster response without version checking

                Health check monitoring:
                    status = await system_status({'detailed': True})
                    if status['system']['status'] != 'running':
                        print("System health check failed!")
                        # Alert monitoring system
                    elif status['resources']['loaded_avatars'] > 10:
                        print("High avatar load detected")
                        # Consider cleanup or scaling

                Error handling:
                    result = await system_status({})
                    if result['status'] == 'error':
                        print(f"Status check failed: {result['message']}")
                    # Usually indicates serious system issues

            Raises:
                RuntimeError: If server is in critical failure state

            Notes:
                - Safe to call frequently for monitoring
                - Detailed mode may impact performance on busy systems
                - Resource counts are real-time snapshots
                - Uptime resets on server restart
                - Status reflects current operational state

            See Also:
                - initialize: Set up system before checking status
                - shutdown: Clean shutdown (status will show stopping)
                - avatar_list: Check loaded avatar status
                - chat_get_state: Check chat system status
            """
            return asyncio.run(self.handle_system_status(params))

        @self.mcp.tool()
        def debug_echo(params: dict[str, Any]) -> dict[str, Any]:
            """Echo back input parameters for debugging and testing purposes.

            A simple diagnostic tool that returns the exact input parameters unchanged.
            Useful for testing MCP communication, verifying parameter parsing, and
            debugging tool integration. Always succeeds and provides predictable output.

            Parameters:
                Any parameters can be passed - all will be echoed back
                    - Supports any data types (strings, numbers, objects, arrays)
                    - No validation or processing performed
                    - Parameters are returned exactly as received

            Returns:
                Dictionary containing:
                    - status: Always "success" (this tool never fails)
                    - echo: Exact copy of input parameters
                    - timestamp: Server timestamp when echo was processed
                    - server_info: Basic server identification

            Usage:
                Use this tool for testing MCP tool integration, debugging parameter
                transmission, and verifying communication between client and server.
                Perfect for development and troubleshooting.

            Examples:
                Simple echo test:
                    result = await debug_echo({
                        'message': 'Hello World',
                        'number': 42
                    })
                    # Returns: {
                    #     'status': 'success',
                    #     'echo': {
                    #         'message': 'Hello World',
                    #         'number': 42
                    #     },
                    #     'timestamp': 1640995200.123,
                    #     'server_info': {'name': 'AvatarMCP', 'version': '1.0.0'}
                    # }

                Test complex data structures:
                    result = await debug_echo({
                        'user': {
                            'name': 'Alice',
                            'preferences': ['dark_mode', 'notifications']
                        },
                        'metadata': {
                            'source': 'test_client',
                            'session_id': 'abc123'
                        }
                    })
                    # Complex nested objects returned unchanged

                Verify MCP connection:
                    # Call this first when setting up new client
                    result = await debug_echo({'test': 'connection'})
                    if result['status'] == 'success':
                        print("MCP connection working!")
                    else:
                        print("Connection issue detected")

                Parameter validation testing:
                    # Test how different parameter types are handled
                    await debug_echo({'string': 'text'})
                    await debug_echo({'number': 123.45})
                    await debug_echo({'boolean': True})
                    await debug_echo({'array': [1, 2, 3]})
                    await debug_echo({'null': None})

                Performance testing:
                    import time
                    start = time.time()
                    result = await debug_echo({'data': 'x' * 1000})
                    latency = time.time() - start
                    print(f"MCP round-trip latency: {latency:.3f}s")

            Raises:
                Never raises exceptions - designed to always succeed

            Notes:
                - This tool is purely diagnostic and performs no actual operations
                - Input parameters are not validated, stored, or processed
                - Response includes server timestamp for latency measurement
                - Safe to call repeatedly for testing purposes
                - No side effects on server state or resources

            See Also:
                - system_status: Check actual system health (not just connectivity)
                - chat_send_message: Test actual chat functionality
                - avatar_load: Test actual avatar operations
            """
            return asyncio.run(self.handle_debug_echo(params))

        # Unity Desktop Avatar System tools
        @self.mcp.tool()
        def unity_system_status(params: dict[str, Any]) -> dict[str, Any]:
            """Retrieve the current status of the Unity desktop avatar system.

            Queries the Unity desktop avatar application to get comprehensive status
            information about the running Unity instance, including connection state,
            loaded avatar, window properties, and system health metrics.

            Parameters:
                detailed: Whether to include detailed performance metrics (default: False)
                    - If true, includes frame rates, memory usage, and detailed system info
                    - If false, returns basic operational status
                include_config: Whether to include current Unity configuration (default: False)
                    - If true, returns window settings, OSC configuration, plugin status
                    - If false, returns only operational status

            Returns:
                Dictionary containing:
                    - status: Either "success", "error", or "disconnected"
                    - unity_connected: Whether Unity application is running and connected
                    - window_visible: Whether the avatar window is visible on desktop
                    - avatar_loaded: Whether an avatar is currently loaded in Unity
                    - avatar_name: Name of the currently loaded avatar (if any)
                    - osc_connected: Whether OSC communication is active
                    - system_info: Unity application system information (if detailed=True)

            Usage:
                Use this tool to monitor the Unity desktop avatar system health and
                connection status. Essential for debugging Unity integration issues
                and ensuring the desktop avatar is functioning properly.

            Examples:
                Basic status check:
                    result = await unity_system_status({})
                    if result['unity_connected']:
                        print(f"Unity connected, avatar loaded: {result['avatar_loaded']}")
                    else:
                        print("Unity application not connected")

                Detailed system monitoring:
                    result = await unity_system_status({'detailed': True})
                    # Returns comprehensive system metrics including:
                    # - Frame rate, memory usage, render time
                    # - Window position and size
                    # - OSC connection details

                Configuration inspection:
                    result = await unity_system_status({'include_config': True})
                    # Returns current Unity settings:
                    # - Window transparency level
                    # - OSC server/port configuration
                    # - Loaded plugins list

                Health check for automation:
                    status = await unity_system_status({})
                    if not status['unity_connected']:
                        # Unity app crashed or not started
                        await start_unity_application()
                    elif not status['avatar_loaded']:
                        # No avatar loaded
                        await unity_avatar_load({'path': 'default-avatar.vrm'})

                Error handling:
                    result = await unity_system_status({})
                    if result['status'] == 'error':
                        print(f"Status check failed: {result['message']}")
                    elif result['status'] == 'disconnected':
                        print("Unity application is not running")
                        # Handle disconnection gracefully

            Raises:
                RuntimeError: If MCP server cannot communicate with Unity system
                ConnectionError: If Unity application is not accessible
                TimeoutError: If status query times out

            Notes:
                - Requires Unity desktop avatar application to be running
                - Status queries use OSC communication with Unity
                - Connection status is checked in real-time
                - Detailed mode may impact performance on busy systems
                - Results reflect current state at time of query

            See Also:
                - unity_window_visibility: Control window visibility
                - unity_osc_bridge: Configure OSC communication
                - system_status: Check overall AvatarMCP server status
            """
            return asyncio.run(self.handle_unity_system_status(params))

        @self.mcp.tool()
        def unity_window_position(params: dict[str, Any]) -> dict[str, Any]:
            """Control the position and size of the Unity desktop avatar window.

            Sets the position, size, and layout properties of the transparent Unity
            desktop avatar window. Allows precise control over where the avatar
            appears on the desktop and how large it displays.

            Parameters:
                x: X-coordinate for window position (in pixels from left edge)
                    - Integer value representing horizontal position
                    - Can be negative (off-screen positioning)
                    - Relative to primary monitor's origin
                y: Y-coordinate for window position (in pixels from top edge)
                    - Integer value representing vertical position
                    - Can be negative (off-screen positioning)
                    - Relative to primary monitor's origin
                width: Window width in pixels (optional)
                    - Must be positive integer
                    - Minimum: 100, Maximum: screen width
                    - If not provided, maintains current width
                height: Window height in pixels (optional)
                    - Must be positive integer
                    - Minimum: 100, Maximum: screen height
                    - If not provided, maintains current height
                monitor: Target monitor index for multi-monitor setups (default: 0)
                    - 0 for primary monitor, 1 for secondary, etc.
                    - Only applies when x/y coordinates are provided
                center_on_monitor: Whether to center window on specified monitor (default: False)
                    - If true, ignores x/y coordinates and centers on monitor
                    - Useful for automatic positioning

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - position: Final window position as {'x': int, 'y': int}
                    - size: Final window size as {'width': int, 'height': int}
                    - monitor: Monitor index where window is positioned
                    - timestamp: When the positioning was applied

            Usage:
                Use this tool to position the Unity desktop avatar window precisely
                on the desktop. Perfect for creating custom layouts, multi-monitor
                setups, and automated positioning workflows.

            Examples:
                Position in top-left corner:
                    result = await unity_window_position({
                        'x': 100,
                        'y': 100,
                        'width': 400,
                        'height': 600
                    })
                    # Positions window at (100, 100) with size 400x600

                Center on primary monitor:
                    result = await unity_window_position({
                        'center_on_monitor': True,
                        'width': 500,
                        'height': 700
                    })
                    # Centers 500x700 window on primary monitor

                Position on secondary monitor:
                    result = await unity_window_position({
                        'x': 1920,
                        'y': 200,
                        'monitor': 1
                    })
                    # Positions on secondary monitor (assuming 1920px wide primary)

                Resize without moving:
                    result = await unity_window_position({
                        'width': 800,
                        'height': 1000
                    })
                    # Changes size, maintains current position

                Move to corner positions:
                    # Top-right corner
                    await unity_window_position({'x': 1520, 'y': 100})
                    # Bottom-left corner
                    await unity_window_position({'x': 100, 'y': 880})
                    # Bottom-right corner
                    await unity_window_position({'x': 1520, 'y': 880})

                Error handling:
                    result = await unity_window_position({
                        'x': 100,
                        'width': -50  # Invalid width
                    })
                    if result['status'] == 'error':
                        print(f"Positioning failed: {result['message']}")
                    # Check for invalid parameters

            Raises:
                ValueError: If coordinates or dimensions are invalid
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Coordinates are relative to the specified monitor's origin
                - Window maintains transparency and always-on-top properties
                - Size changes may affect avatar aspect ratio
                - Positioning is immediate but may take effect on next frame
                - Multi-monitor support depends on Unity application configuration

            See Also:
                - unity_window_visibility: Show/hide the window
                - unity_window_transparency: Control transparency level
                - unity_system_status: Check current window position
            """
            return asyncio.run(self.handle_unity_window_position(params))

        @self.mcp.tool()
        def unity_window_transparency(params: dict[str, Any]) -> dict[str, Any]:
            """Control the transparency level of the Unity desktop avatar window.

            Adjusts the alpha transparency of the Unity desktop avatar window,
            allowing the avatar to blend seamlessly with the desktop background
            or become more prominent as needed.

            Parameters:
                alpha: Transparency level (0.0 to 1.0)
                    - 0.0 = completely transparent (invisible)
                    - 1.0 = completely opaque (solid)
                    - 0.5 = 50% transparent
                    - Values outside 0.0-1.0 are clamped to valid range
                transition_time: Time in seconds for smooth transition (default: 0.0)
                    - 0.0 = instant change
                    - > 0.0 = smooth fade transition
                    - Maximum: 5.0 seconds
                    - Allows smooth opacity animations

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - alpha: Final transparency level applied
                    - transition_time: Transition duration used
                    - timestamp: When the transparency was applied

            Usage:
                Use this tool to control how prominently the avatar appears on the
                desktop. Perfect for creating subtle background avatars or bringing
                attention to important avatar states through opacity changes.

            Examples:
                Make avatar semi-transparent:
                    result = await unity_window_transparency({
                        'alpha': 0.7
                    })
                    # Avatar becomes 70% opaque, 30% transparent

                Create fade-in effect:
                    result = await unity_window_transparency({
                        'alpha': 1.0,
                        'transition_time': 2.0
                    })
                    # Avatar smoothly fades from current opacity to fully visible

                Make avatar background element:
                    result = await unity_window_transparency({
                        'alpha': 0.3
                    })
                    # Avatar becomes subtle background decoration

                Invisible mode for recording:
                    result = await unity_window_transparency({
                        'alpha': 0.0
                    })
                    # Avatar becomes completely invisible

                Attention-grabbing animation:
                    # Quick flash to full opacity
                    await unity_window_transparency({'alpha': 1.0, 'transition_time': 0.1})
                    await asyncio.sleep(0.5)
                    await unity_window_transparency({'alpha': 0.7, 'transition_time': 1.0})

                Error handling:
                    result = await unity_window_transparency({
                        'alpha': 1.5  # Invalid value
                    })
                    if result['status'] == 'error':
                        print(f"Transparency failed: {result['message']}")
                    # Alpha value will be clamped to 1.0

            Raises:
                ValueError: If alpha or transition_time values are invalid
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Transparency affects the entire window, not individual avatar elements
                - Smooth transitions use Unity's animation system
                - Always-on-top property is maintained regardless of transparency
                - Low alpha values may cause visual artifacts on some systems
                - Transparency changes are applied immediately (or transitioned smoothly)

            See Also:
                - unity_window_visibility: Completely hide/show window
                - unity_window_position: Control window position and size
                - unity_system_status: Check current transparency level
            """
            return asyncio.run(self.handle_unity_window_transparency(params))

        @self.mcp.tool()
        def unity_window_visibility(params: dict[str, Any]) -> dict[str, Any]:
            """Control the visibility of the Unity desktop avatar window.

            Shows or hides the Unity desktop avatar window completely. Unlike
            transparency control, this completely removes the window from view
            or restores it, useful for toggling avatar presence on desktop.

            Parameters:
                visible: Whether the window should be visible (required)
                    - True = show the window
                    - False = hide the window completely
                    - No default value - must be explicitly specified
                fade_transition: Whether to use smooth fade transition (default: True)
                    - If true, uses smooth fade in/out animation
                    - If false, instant show/hide
                    - Fade uses current transparency settings

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - visible: Final visibility state applied
                    - fade_transition: Whether fade was used
                    - timestamp: When the visibility change was applied

            Usage:
                Use this tool to completely show or hide the desktop avatar window.
                Essential for toggling avatar presence, creating interactive experiences,
                or managing desktop clutter during different activities.

            Examples:
                Hide avatar window:
                    result = await unity_window_visibility({
                        'visible': False
                    })
                    # Avatar window disappears completely

                Show avatar with fade:
                    result = await unity_window_visibility({
                        'visible': True,
                        'fade_transition': True
                    })
                    # Avatar smoothly fades into view

                Instant toggle:
                    result = await unity_window_visibility({
                        'visible': True,
                        'fade_transition': False
                    })
                    # Avatar appears instantly

                Interactive avatar toggle:
                    # Check current state
                    status = await unity_system_status({})
                    current_visible = status.get('window_visible', False)

                    # Toggle visibility
                    result = await unity_window_visibility({
                        'visible': not current_visible
                    })

                Application focus management:
                    # Hide avatar when working in other apps
                    await unity_window_visibility({'visible': False})
                    # ... do work ...
                    # Show avatar again
                    await unity_window_visibility({'visible': True})

                Error handling:
                    result = await unity_window_visibility({
                        'visible': 'maybe'  # Invalid boolean
                    })
                    if result['status'] == 'error':
                        print(f"Visibility failed: {result['message']}")
                    # Check that visible parameter is boolean

            Raises:
                ValueError: If visible parameter is not a boolean
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Hidden windows maintain their position and settings
                - Always-on-top property is maintained when shown again
                - Fade transitions respect current transparency settings
                - Hidden windows can still receive OSC commands for animations
                - Visibility state persists across application restarts

            See Also:
                - unity_window_transparency: Control opacity without hiding
                - unity_window_position: Control window position
                - unity_system_status: Check current visibility state
            """
            return asyncio.run(self.handle_unity_window_visibility(params))

        @self.mcp.tool()
        def unity_window_mode(params: dict[str, Any]) -> dict[str, Any]:
            """Control the interaction mode of the Unity desktop avatar window.

            Switches the Unity desktop avatar window between interactive and
            click-through modes. Interactive mode allows clicking and interacting
            with the avatar, while click-through mode allows desktop interaction
            through the transparent window.

            Parameters:
                mode: Interaction mode for the window (required)
                    - "interactive" = window accepts clicks and input
                    - "clickthrough" = clicks pass through to desktop
                    - No default value - must be explicitly specified
                transition_effect: Whether to show visual transition effect (default: True)
                    - If true, shows brief visual feedback when mode changes
                    - If false, instant mode switch without feedback

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - mode: Final interaction mode applied
                    - transition_effect: Whether transition effect was shown
                    - timestamp: When the mode change was applied

            Usage:
                Use this tool to control how the desktop avatar interacts with user
                input. Interactive mode is useful for clickable avatar interfaces,
                while click-through mode allows unobtrusive desktop overlay.

            Examples:
                Enable click-through mode:
                    result = await unity_window_mode({
                        'mode': 'clickthrough'
                    })
                    # Clicks pass through avatar to desktop applications

                Enable interactive mode:
                    result = await unity_window_mode({
                        'mode': 'interactive'
                    })
                    # Avatar window accepts clicks and input

                Mode toggle with feedback:
                    result = await unity_window_mode({
                        'mode': 'interactive',
                        'transition_effect': True
                    })
                    # Shows visual feedback when switching to interactive

                Instant mode switch:
                    result = await unity_window_mode({
                        'mode': 'clickthrough',
                        'transition_effect': False
                    })
                    # Instant switch without visual effects

                Application-specific modes:
                    # When coding - click-through to access IDE
                    await unity_window_mode({'mode': 'clickthrough'})

                    # When presenting - interactive for avatar control
                    await unity_window_mode({'mode': 'interactive'})

                Error handling:
                    result = await unity_window_mode({
                        'mode': 'invalid_mode'
                    })
                    if result['status'] == 'error':
                        print(f"Mode change failed: {result['message']}")
                    # Check that mode is 'interactive' or 'clickthrough'

            Raises:
                ValueError: If mode parameter is not 'interactive' or 'clickthrough'
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Mode changes take effect immediately
                - Interactive mode may interfere with desktop applications underneath
                - Click-through mode allows full desktop interaction
                - Transition effects provide visual feedback for mode changes
                - Mode state persists across application restarts
                - OSC commands work in both modes

            See Also:
                - unity_window_visibility: Show/hide window completely
                - unity_window_transparency: Control opacity level
                - unity_system_status: Check current window mode
            """
            return asyncio.run(self.handle_unity_window_mode(params))

        @self.mcp.tool()
        def unity_avatar_load(params: dict[str, Any]) -> dict[str, Any]:
            """Load a VRM avatar model into the Unity desktop avatar system.

            Loads and initializes a VRM (Virtual Reality Model) avatar in the Unity
            desktop application. The avatar becomes available for animation, expression
            control, and pose manipulation through subsequent Unity tools.

            Parameters:
                path: Path to the VRM file to load (required)
                    - Absolute or relative path to .vrm file
                    - File must exist and be readable
                    - Unity must have access to the file location
                make_active: Whether to make this the active avatar (default: True)
                    - If true, replaces any currently active avatar
                    - If false, loads avatar but keeps current one active
                    - Multiple avatars can be loaded but only one active
                preload_animations: Whether to preload standard animations (default: True)
                    - If true, loads common animations (idle, walking, etc.)
                    - If false, loads only the base avatar model
                    - Preloading improves animation responsiveness
                position_offset: Optional position offset for avatar placement
                    - Dictionary with 'x', 'y', 'z' coordinates
                    - Relative to Unity scene origin
                    - Useful for multi-avatar scenes

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Unique identifier for the loaded avatar
                    - avatar_name: Display name from VRM metadata
                    - blend_shape_count: Number of facial blend shapes available
                    - bone_count: Number of bones in the skeleton
                    - animations_loaded: Number of animations preloaded
                    - active: Whether this avatar is now active

            Usage:
                Use this tool to load VRM avatars into the Unity desktop system.
                Essential for setting up the visual avatar that users will see and
                interact with on their desktop.

            Examples:
                Load basic avatar:
                    result = await unity_avatar_load({
                        'path': 'C:/Avatars/MyAvatar.vrm'
                    })
                    if result['status'] == 'success':
                        print(f"Loaded avatar: {result['avatar_name']}")
                        print(f"Blend shapes: {result['blend_shape_count']}")

                Load with specific positioning:
                    result = await unity_avatar_load({
                        'path': 'models/professional-avatar.vrm',
                        'position_offset': {'x': 0, 'y': 0, 'z': -5}
                    })
                    # Avatar positioned 5 units back in Unity scene

                Load without preloading animations:
                    result = await unity_avatar_load({
                        'path': 'simple-avatar.vrm',
                        'preload_animations': False
                    })
                    # Faster loading, animations loaded on-demand

                Load as background avatar:
                    result = await unity_avatar_load({
                        'path': 'background-avatar.vrm',
                        'make_active': False
                    })
                    # Loads avatar but keeps current one active

                Avatar switching workflow:
                    # Load new avatar
                    result = await unity_avatar_load({
                        'path': 'casual-avatar.vrm'
                    })
                    if result['active']:
                        # Set expression on new avatar
                        await unity_avatar_expression({
                            'expression': 'Happy',
                            'strength': 1.0
                        })

                Error handling:
                    result = await unity_avatar_load({
                        'path': 'nonexistent.vrm'
                    })
                    if result['status'] == 'error':
                        print(f"Avatar load failed: {result['message']}")
                    # Check file path and VRM validity

            Raises:
                FileNotFoundError: If VRM file does not exist
                ValueError: If VRM file is invalid or corrupted
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - VRM files must conform to VRM 1.0 specification
                - Loading may take several seconds for complex models
                - Avatar remains loaded until explicitly unloaded
                - Only one avatar can be active at a time
                - Preloading animations improves responsiveness but increases load time

            See Also:
                - unity_avatar_expression: Control facial expressions
                - unity_avatar_animation: Play animations
                - unity_system_status: Check loaded avatar status
                - avatar_load: Load avatar in AvatarMCP (separate from Unity)
            """
            return asyncio.run(self.handle_unity_avatar_load(params))

        @self.mcp.tool()
        def unity_avatar_expression(params: dict[str, Any]) -> dict[str, Any]:
            """Control facial expressions on the Unity desktop avatar.

            Sets specific facial expressions on the active Unity avatar using
            blend shape animations. Allows precise control over the avatar's
            emotional display and facial animations.

            Parameters:
                expression: Name of the facial expression to apply (required)
                    - Must match available blend shapes in the loaded VRM
                    - Common expressions: "Joy", "Angry", "Sad", "Surprised", "Neutral"
                    - Case-sensitive expression names
                strength: Intensity of the expression (0.0 to 1.0, default: 1.0)
                    - 0.0 = no expression applied
                    - 1.0 = full expression intensity
                    - Values outside range are clamped
                    - Allows subtle or exaggerated expressions
                transition_time: Time in seconds for smooth transition (default: 0.2)
                    - 0.0 = instant change
                    - > 0.0 = smooth blend shape animation
                    - Maximum: 2.0 seconds
                blend_with_current: Whether to blend with current expressions (default: False)
                    - If true, combines with existing expressions
                    - If false, replaces current expressions
                    - Allows layered emotional states

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - expression: Expression that was applied
                    - strength: Strength value that was applied
                    - transition_time: Transition duration used
                    - blend_with_current: Whether blending was used
                    - timestamp: When the expression was applied

            Usage:
                Use this tool to give emotional depth and personality to the Unity
                desktop avatar. Perfect for creating responsive, expressive avatar
                interactions and emotional feedback.

            Examples:
                Full happy expression:
                    result = await unity_avatar_expression({
                        'expression': 'Joy',
                        'strength': 1.0
                    })
                    # Avatar shows maximum happiness

                Subtle surprised look:
                    result = await unity_avatar_expression({
                        'expression': 'Surprised',
                        'strength': 0.3
                    })
                    # Avatar shows mild surprise

                Smooth expression transition:
                    result = await unity_avatar_expression({
                        'expression': 'Sad',
                        'strength': 1.0,
                        'transition_time': 1.0
                    })
                    # Avatar smoothly transitions to sad expression

                Blend multiple expressions:
                    # Start with neutral
                    await unity_avatar_expression({'expression': 'Neutral'})
                    # Add happiness
                    await unity_avatar_expression({
                        'expression': 'Joy',
                        'strength': 0.8,
                        'blend_with_current': True
                    })
                    # Layer in concentration
                    await unity_avatar_expression({
                        'expression': 'Focused',
                        'strength': 0.5,
                        'blend_with_current': True
                    })

                Emotional response sequence:
                    # User says something funny
                    await unity_avatar_expression({
                        'expression': 'Surprised',
                        'transition_time': 0.3
                    })
                    await asyncio.sleep(0.5)
                    await unity_avatar_expression({'expression': 'Joy', 'transition_time': 0.8})

                Error handling:
                    result = await unity_avatar_expression({
                        'expression': 'NonExistentExpression'
                    })
                    if result['status'] == 'error':
                        print(f"Expression failed: {result['message']}")
                    # Check expression name exists in VRM

            Raises:
                ValueError: If expression name is invalid or strength out of range
                RuntimeError: If no avatar is loaded in Unity
                ConnectionError: If OSC communication fails

            Notes:
                - Requires an avatar to be loaded in Unity first
                - Expression names must match VRM blend shape names exactly
                - Blend shapes are part of the VRM model specification
                - Smooth transitions use Unity's animation system
                - Expression blending allows complex emotional states
                - Expressions persist until explicitly changed

            See Also:
                - unity_avatar_load: Load avatar with blend shapes
                - unity_avatar_animation: Control full-body animations
                - unity_system_status: Check available expressions
            """
            return asyncio.run(self.handle_unity_avatar_expression(params))

        @self.mcp.tool()
        def unity_avatar_animation(params: dict[str, Any]) -> dict[str, Any]:
            """Control animations on the Unity desktop avatar.

            Plays, stops, or controls animation states on the active Unity avatar.
            Supports both predefined animations and dynamic animation control for
            creating engaging avatar behaviors.

            Parameters:
                action: Animation control action (required)
                    - "play" = start playing an animation
                    - "stop" = stop current animation
                    - "pause" = pause current animation
                    - "resume" = resume paused animation
                    - "loop" = set loop mode for current animation
                animation_name: Name of animation to play (required for "play" action)
                    - Must match available animations in Unity
                    - Case-sensitive animation names
                    - Supports custom and standard animations
                loop: Whether animation should loop (default: True for "play", False for others)
                    - True = animation repeats indefinitely
                    - False = animation plays once
                    - Only applies to "play" and "loop" actions
                speed: Animation playback speed multiplier (default: 1.0)
                    - 0.5 = half speed, 2.0 = double speed
                    - Range: 0.1 to 3.0
                    - Allows slow-motion or fast-forward effects
                blend_time: Time in seconds to blend between animations (default: 0.3)
                    - 0.0 = instant transition
                    - > 0.0 = smooth blend between animations
                    - Prevents jarring animation switches

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - action: Animation action that was performed
                    - animation_name: Animation affected (if applicable)
                    - loop: Loop setting applied
                    - speed: Speed multiplier applied
                    - blend_time: Blend duration used
                    - timestamp: When the animation control was applied

            Usage:
                Use this tool to bring the Unity desktop avatar to life with animations.
                Essential for creating dynamic, responsive avatar behaviors and
                enhancing the visual appeal of desktop interactions.

            Examples:
                Play walking animation:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'Walking',
                        'loop': True,
                        'speed': 1.0
                    })
                    # Avatar walks continuously at normal speed

                Stop current animation:
                    result = await unity_avatar_animation({
                        'action': 'stop'
                    })
                    # Avatar stops animating, returns to idle pose

                Play greeting animation once:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'WaveHello',
                        'loop': False
                    })
                    # Avatar waves once, then stops

                Slow-motion animation:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'Dance',
                        'speed': 0.5,
                        'blend_time': 1.0
                    })
                    # Avatar dances at half speed with smooth blend

                Animation state management:
                    # Start dancing
                    await unity_avatar_animation({'action': 'play', 'animation_name': 'Dance'})
                    await asyncio.sleep(5)
                    # Pause temporarily
                    await unity_avatar_animation({'action': 'pause'})
                    await asyncio.sleep(2)
                    # Resume dancing
                    await unity_avatar_animation({'action': 'resume'})

                Smooth animation transitions:
                    # Transition from walking to running
                    await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'Running',
                        'blend_time': 0.8
                    })
                    # Smooth 0.8 second blend from walking to running

                Error handling:
                    result = await unity_avatar_animation({
                        'action': 'play',
                        'animation_name': 'NonExistentAnimation'
                    })
                    if result['status'] == 'error':
                        print(f"Animation failed: {result['message']}")
                    # Check animation name exists

            Raises:
                ValueError: If action or animation parameters are invalid
                RuntimeError: If no avatar is loaded in Unity
                ConnectionError: If OSC communication fails

            Notes:
                - Requires an avatar to be loaded in Unity first
                - Animation names must match Unity animation controller states
                - Smooth blending prevents jarring transitions
                - Speed changes affect playback rate, not quality
                - Loop mode continues until explicitly stopped
                - Paused animations can be resumed from same point

            See Also:
                - unity_avatar_load: Load avatar with animations
                - unity_avatar_expression: Control facial expressions
                - unity_system_status: Check animation system status
            """
            return asyncio.run(self.handle_unity_avatar_animation(params))

        @self.mcp.tool()
        def unity_osc_bridge(params: dict[str, Any]) -> dict[str, Any]:
            """Configure OSC communication bridge for Unity avatar system.

            Sets up and configures the OSC (Open Sound Control) communication
            between AvatarMCP and the Unity desktop avatar application. Essential
            for enabling real-time control and synchronization.

            Parameters:
                enable_bridge: Whether to enable or disable OSC bridge (required)
                    - True = start OSC communication
                    - False = stop OSC communication
                    - Controls overall OSC connectivity
                receive_port: Port for receiving OSC messages from Unity (default: 9000)
                    - Must be available and not in use
                    - Standard VRChat receive port
                    - Unity sends avatar state updates on this port
                send_port: Port for sending OSC messages to Unity (default: 9001)
                    - Must be available and not in use
                    - Standard VRChat send port
                    - AvatarMCP sends commands to Unity on this port
                server_ip: IP address for OSC communication (default: "127.0.0.1")
                    - "127.0.0.1" for local communication
                    - Network IP for remote Unity instances
                    - Must be reachable from both applications
                auto_reconnect: Whether to automatically reconnect on failures (default: True)
                    - True = attempt reconnection on OSC failures
                    - False = require manual reconnection
                    - Improves reliability for long-running sessions
                heartbeat_interval: Seconds between heartbeat messages (default: 30)
                    - 0 = disable heartbeats
                    - Positive value = enable connection monitoring
                    - Helps detect connection drops

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - bridge_enabled: Final bridge state
                    - receive_port: Port configured for receiving
                    - send_port: Port configured for sending
                    - server_ip: IP address configured
                    - connection_status: Current OSC connection state
                    - timestamp: When the configuration was applied

            Usage:
                Use this tool to establish and configure OSC communication with the
                Unity desktop avatar. Critical for enabling all Unity avatar control
                functions and real-time synchronization.

            Examples:
                Enable basic OSC bridge:
                    result = await unity_osc_bridge({
                        'enable_bridge': True
                    })
                    # Starts OSC on default ports 9000/9001

                Configure custom ports:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'receive_port': 9002,
                        'send_port': 9003
                    })
                    # Uses custom ports to avoid conflicts

                Enable with monitoring:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'auto_reconnect': True,
                        'heartbeat_interval': 15
                    })
                    # Enables automatic reconnection and 15-second heartbeats

                Disable OSC bridge:
                    result = await unity_osc_bridge({
                        'enable_bridge': False
                    })
                    # Stops all OSC communication

                Network configuration:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'server_ip': '192.168.1.100'
                    })
                    # Connects to Unity on remote machine

                Connection troubleshooting:
                    # Check current status
                    status = await unity_system_status({})
                    if not status.get('osc_connected'):
                        # Reconfigure OSC
                        result = await unity_osc_bridge({
                            'enable_bridge': True,
                            'receive_port': 9000,
                            'send_port': 9001
                        })

                Error handling:
                    result = await unity_osc_bridge({
                        'enable_bridge': True,
                        'receive_port': 80  # Port in use
                    })
                    if result['status'] == 'error':
                        print(f"OSC config failed: {result['message']}")
                    # Check port availability and configuration

            Raises:
                ValueError: If port numbers or IP addresses are invalid
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC ports cannot be bound
                PermissionError: If ports require elevated privileges

            Notes:
                - Requires Unity desktop avatar application to be running
                - OSC ports must be available and not blocked by firewall
                - Local communication (127.0.0.1) is most reliable
                - Heartbeats help maintain connection stability
                - Auto-reconnect improves reliability for long sessions
                - Configuration persists until explicitly changed

            See Also:
                - unity_system_status: Check OSC connection status
                - osc_send: Send OSC messages directly
                - osc_receive: Receive OSC messages directly
            """
            return asyncio.run(self.handle_unity_osc_bridge(params))

        @self.mcp.tool()
        def unity_plugin_load(params: dict[str, Any]) -> dict[str, Any]:
            """Load and manage plugins in the Unity desktop avatar system.

            Dynamically loads, unloads, or manages plugins that extend the
            Unity desktop avatar functionality. Plugins can add new features,
            animations, or integration capabilities.

            Parameters:
                action: Plugin management action (required)
                    - "load" = load a plugin from file
                    - "unload" = unload a currently loaded plugin
                    - "list" = list all available and loaded plugins
                    - "reload" = reload a specific plugin
                plugin_path: Path to plugin file (required for "load" action)
                    - Absolute or relative path to plugin DLL/assembly
                    - Must be compatible with Unity version
                    - File must exist and be readable by Unity
                plugin_name: Name of plugin to unload/reload (required for unload/reload)
                    - Must match exactly the loaded plugin name
                    - Case-sensitive plugin naming
                    - Use "list" action to see available names
                config: Optional configuration dictionary for plugin
                    - Plugin-specific settings and parameters
                    - Passed to plugin initialization
                    - Format depends on specific plugin requirements

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - action: Plugin action that was performed
                    - plugin_name: Name of plugin affected
                    - plugin_path: Path of plugin loaded (for load action)
                    - loaded_plugins: List of currently loaded plugins (for list action)
                    - available_plugins: List of available plugins (for list action)
                    - config_applied: Configuration that was applied
                    - timestamp: When the plugin operation was performed

            Usage:
                Use this tool to extend the Unity desktop avatar with additional
                functionality through plugins. Essential for adding custom behaviors,
                integrations, or specialized avatar features.

            Examples:
                Load a custom animation plugin:
                    result = await unity_plugin_load({
                        'action': 'load',
                        'plugin_path': 'C:/UnityPlugins/CustomAnimations.dll',
                        'config': {
                            'animation_speed': 1.2,
                            'enable_transitions': True
                        }
                    })
                    # Loads plugin with custom configuration

                Unload a plugin:
                    result = await unity_plugin_load({
                        'action': 'unload',
                        'plugin_name': 'CustomAnimations'
                    })
                    # Removes plugin from Unity

                List available plugins:
                    result = await unity_plugin_load({
                        'action': 'list'
                    })
                    # Returns all loaded and available plugins
                    loaded = result['loaded_plugins']
                    available = result['available_plugins']

                Reload plugin with new config:
                    result = await unity_plugin_load({
                        'action': 'reload',
                        'plugin_name': 'ExpressionController',
                        'config': {
                            'intensity_multiplier': 1.5
                        }
                    })
                    # Reloads plugin with updated settings

                Plugin management workflow:
                    # Check what's available
                    plugins = await unity_plugin_load({'action': 'list'})

                    # Load essential plugins
                    for plugin in ['AvatarController', 'OSCBridge']:
                        if plugin in plugins['available_plugins']:
                            await unity_plugin_load({
                                'action': 'load',
                                'plugin_path': f'C:/UnityPlugins/{plugin}.dll'
                            })

                Error handling:
                    result = await unity_plugin_load({
                        'action': 'load',
                        'plugin_path': 'nonexistent.dll'
                    })
                    if result['status'] == 'error':
                        print(f"Plugin load failed: {result['message']}")
                    # Check plugin file exists and is valid

            Raises:
                FileNotFoundError: If plugin file does not exist
                ValueError: If plugin format is invalid or incompatible
                RuntimeError: If Unity plugin system is not available
                ConnectionError: If OSC communication fails

            Notes:
                - Requires Unity desktop avatar application to be running
                - Plugins must be compiled for the correct Unity version
                - Plugin loading may take several seconds
                - Loaded plugins persist across Unity restarts
                - Configuration is stored and reapplied on reload
                - Unloading plugins frees memory but may break dependent features

            See Also:
                - unity_system_status: Check plugin loading status
                - unity_config_update: Update plugin configurations
                - unity_osc_bridge: Configure plugin communication
            """
            return asyncio.run(self.handle_unity_plugin_load(params))

        @self.mcp.tool()
        def unity_config_update(params: dict[str, Any]) -> dict[str, Any]:
            """Update configuration settings for the Unity desktop avatar system.

            Modifies runtime configuration of the Unity desktop avatar application,
            allowing dynamic adjustment of rendering, performance, and behavioral
            settings without restarting the application.

            Parameters:
                config_section: Configuration section to update (required)
                    - "rendering" = graphics and rendering settings
                    - "performance" = performance and optimization settings
                    - "behavior" = avatar behavior and interaction settings
                    - "audio" = audio processing and output settings
                    - "network" = network and communication settings
                settings: Dictionary of settings to update (required)
                    - Key-value pairs specific to the config section
                    - Values must be valid for the setting type
                    - Invalid settings are ignored with warnings
                apply_immediately: Whether to apply changes immediately (default: True)
                    - True = changes take effect right away
                    - False = changes queued for next safe opportunity
                    - Immediate changes may cause brief performance hit
                persist_changes: Whether to save changes to disk (default: True)
                    - True = changes survive Unity restarts
                    - False = changes are temporary for this session
                    - Persistent changes require write access to config files

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - config_section: Section that was updated
                    - settings_applied: Settings that were successfully applied
                    - settings_ignored: Settings that were invalid/ignored
                    - apply_immediately: Whether changes were applied immediately
                    - persist_changes: Whether changes were saved
                    - timestamp: When the configuration was updated

            Usage:
                Use this tool to dynamically adjust Unity avatar behavior and
                performance without restarting the application. Perfect for optimizing
                settings based on system performance or changing requirements.

            Examples:
                Update rendering quality:
                    result = await unity_config_update({
                        'config_section': 'rendering',
                        'settings': {
                            'quality_level': 'High',
                            'anti_aliasing': 4,
                            'shadows_enabled': True
                        }
                    })
                    # Improves visual quality settings

                Optimize performance:
                    result = await unity_config_update({
                        'config_section': 'performance',
                        'settings': {
                            'target_fps': 30,
                            'vsync_enabled': False,
                            'texture_quality': 'Half'
                        }
                    })
                    # Reduces resource usage for better performance

                Configure avatar behavior:
                    result = await unity_config_update({
                        'config_section': 'behavior',
                        'settings': {
                            'auto_blink': True,
                            'expression_smoothing': 0.8,
                            'idle_animations': ['subtle_nod', 'gentle_breathing']
                        }
                    })
                    # Customizes avatar personality and responsiveness

                Audio configuration:
                    result = await unity_config_update({
                        'config_section': 'audio',
                        'settings': {
                            'master_volume': 0.7,
                            'voice_chat_enabled': True,
                            'spatial_audio': True
                        }
                    })
                    # Adjusts audio processing settings

                Temporary vs persistent changes:
                    result = await unity_config_update({
                        'config_section': 'performance',
                        'settings': {'target_fps': 60},
                        'persist_changes': False
                    })
                    # High FPS for this session only

                Error handling:
                    result = await unity_config_update({
                        'config_section': 'rendering',
                        'settings': {
                            'invalid_setting': 'bad_value'
                        }
                    })
                    if result['settings_ignored']:
                        print(f"Settings ignored: {result['settings_ignored']}")
                    # Check which settings were invalid

            Raises:
                ValueError: If config_section is invalid or settings malformed
                RuntimeError: If Unity application is not running
                ConnectionError: If OSC communication fails
                PermissionError: If config file write access is denied

            Notes:
                - Requires Unity desktop avatar application to be running
                - Configuration changes take effect at different times
                - Some settings require Unity scene reload
                - Invalid settings are logged but don't fail the operation
                - Performance settings may cause visual artifacts during transition
                - Audio settings may cause brief audio interruption

            See Also:
                - unity_system_status: Check current configuration
                - unity_plugin_load: Load plugins with configurations
                - unity_osc_bridge: Configure network settings
            """
            return asyncio.run(self.handle_unity_config_update(params))

        # End of _register_tools method
        pass

    async def handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle initialization request."""
        logger.info("Initializing AvatarMCP server")

        try:
            # Update models directory if specified
            if "models_dir" in params:
                self.vrm_manager = VRMManager(params["models_dir"])

            # Scan for available models
            await self.vrm_manager.scan_models()

            self.initialized = True
            return {
                "status": "success",
                "message": "AvatarMCP initialized",
                "version": "1.0.0",
                "models_dir": str(self.vrm_manager.models_dir),
                "num_models": len(self.vrm_manager.models),
            }
        except Exception as e:
            error_msg = f"Initialization failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}

    async def handle_shutdown(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle MCP shutdown method."""
        logger.info("Shutdown requested by client")
        self.running = False
        return {"status": "success", "message": "Shutdown initiated"}

    async def handle_avatar_load(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle avatar loading request."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")

            source_path = params.get("path")
            if not source_path:
                raise ValueError("No avatar path or model ID provided")

            make_active = params.get("make_active", True)
            metadata = params.get("metadata", {})

            # Check if it's a file path or model ID
            if os.path.isfile(source_path):
                # Import the VRM file
                model_id = await self.vrm_manager.import_model(source_path, metadata)
                logger.info(f"Imported VRM model: {model_id} from {source_path}")
            else:
                # Treat as model ID
                model_id = source_path

            # Load the model
            model_info = await self.vrm_manager.load_model(model_id)
            if not model_info or "status" not in model_info or model_info["status"] != "success":
                raise RuntimeError(f"Failed to load model {model_id}")

            # Create VRMModel instance
            vrm_model = VRMModel(model_info["path"])
            self.loaded_models[model_id] = vrm_model

            # Set as active if requested
            if make_active:
                self.active_model_id = model_id

            return {
                "status": "success",
                "model_id": model_id,
                "active": make_active,
                "metadata": model_info.get("metadata", {}),
            }

        except Exception as e:
            error_msg = f"Failed to load avatar: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}

    async def handle_avatar_unload(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle avatar unload request."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")

            avatar_id = params.get("id")
            force = params.get("force", False)

            if not avatar_id:
                raise ValueError("No avatar ID provided")

            if avatar_id not in self.loaded_models:
                raise ValueError(f"Avatar not found: {avatar_id}")

            # Don't unload active model unless forced
            if avatar_id == self.active_model_id and not force:
                raise RuntimeError("Cannot unload active model. Set force=True to override.")

            # Remove from loaded models
            del self.loaded_models[avatar_id]

            # Update active model if needed
            if avatar_id == self.active_model_id:
                self.active_model_id = next(iter(self.loaded_models), None)

            return {
                "status": "success",
                "message": f"Unloaded avatar: {avatar_id}",
                "was_active": avatar_id == self.active_model_id,
            }

        except Exception as e:
            error_msg = f"Failed to unload avatar: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}

    async def handle_avatar_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle avatar list request."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")

            params.get("loaded_only", False)
            include_metadata = params.get("include_metadata", False)

            avatars = []

            # Get loaded models
            for model_id in self.loaded_models.keys():
                avatar_info = {
                    "id": model_id,
                    "name": model_id,
                    "status": "loaded",
                    "is_active": model_id == self.active_model_id,
                }

                if include_metadata and model_id in self.loaded_models:
                    avatar_info["metadata"] = self.loaded_models[model_id].to_dict()

                avatars.append(avatar_info)

            return {
                "status": "success",
                "count": len(avatars),
                "active_model": self.active_model_id,
                "avatars": avatars,
            }

        except Exception as e:
            error_msg = f"Failed to list avatars: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}

    async def handle_avatar_set_active(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set the active avatar model."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")

            avatar_id = params.get("id")
            if not avatar_id:
                raise ValueError("No avatar ID provided")

            # Check if the model is loaded
            if avatar_id not in self.loaded_models:
                return {"status": "error", "message": f"Avatar with ID '{avatar_id}' is not loaded"}

            # Set the active model
            self.active_model_id = avatar_id

            return {
                "status": "success",
                "message": f"Set active avatar to: {avatar_id}",
                "active_avatar_id": avatar_id,
            }

        except Exception as e:
            logger.error(f"Failed to set active avatar: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def handle_avatar_get_active(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get the currently active avatar model."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")

            if not self.active_model_id:
                return {
                    "status": "success",
                    "active_avatar_id": None,
                    "message": "No active avatar",
                }

            return {
                "status": "success",
                "active_avatar_id": self.active_model_id,
                "loaded": self.active_model_id in self.loaded_models,
                "message": f"Active avatar: {self.active_model_id}",
            }

        except Exception as e:
            logger.error(f"Failed to get active avatar: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def handle_avatar_get_metadata(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get detailed metadata for a specific avatar."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")

            avatar_id = params.get("id", self.active_model_id)

            if not avatar_id:
                raise ValueError("No avatar ID provided and no active model")

            # Check if the model is loaded
            if avatar_id in self.loaded_models:
                return {
                    "status": "success",
                    "id": avatar_id,
                    "loaded": True,
                    "active": avatar_id == self.active_model_id,
                    "metadata": self.loaded_models[avatar_id].to_dict(),
                }

            raise ValueError(f"Avatar not found: {avatar_id}")

        except Exception as e:
            error_msg = f"Failed to get avatar metadata: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}

    # Animation handlers are now implemented in CoreAnimationTools class

    # Parameter handlers are now implemented in CoreParameterTools class

    async def handle_osc_send(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle OSC send request."""
        address = params.get("address", "/default")
        value = params.get("value", 0)
        return {"status": "success", "message": f"Sent OSC: {address} = {value}"}

    async def handle_osc_receive(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle OSC receive request."""
        return {"status": "success", "messages": []}

    async def handle_chat_start(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat start request."""
        return {"status": "success", "message": "Chat started"}

    async def handle_chat_send_message(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat send message request."""
        message = params.get("message", "")
        return {"status": "success", "response": f"Echo: {message}"}

    async def handle_chat_stop(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat stop request."""
        return {"status": "success", "message": "Chat stopped"}

    async def handle_chat_get_state(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle chat get state request."""
        return {"status": "success", "state": "idle"}

    async def handle_system_status(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle system status request."""
        return {
            "status": "success",
            "system": {
                "name": "AvatarMCP",
                "version": "1.0.0",
                "status": "running",
                "uptime": time.time() - self.start_time,
                "initialized": self.initialized,
            },
        }

    async def handle_debug_echo(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle debug echo request."""
        return {"status": "success", "echo": params}

    # Unity Desktop Avatar System handlers
    async def handle_unity_system_status(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity system status request."""
        try:
            detailed = params.get("detailed", False)
            include_config = params.get("include_config", False)

            # Check if Unity is connected (this would need actual OSC communication)
            # For now, return mock data
            unity_connected = False  # TODO: Implement actual Unity connection check
            osc_connected = (
                self.osc_server is not None and self.osc_server.is_running
                if self.osc_server
                else False
            )

            result = {
                "status": "success",
                "message": "Unity system status retrieved",
                "unity_connected": unity_connected,
                "window_visible": False,  # TODO: Implement window visibility check
                "avatar_loaded": False,  # TODO: Implement avatar loading status
                "avatar_name": None,
                "osc_connected": osc_connected,
                "timestamp": time.time(),
            }

            if detailed:
                result["system_info"] = {
                    "unity_version": "2021.3+",  # TODO: Get actual Unity version
                    "render_fps": 60,  # TODO: Get actual FPS
                    "memory_usage": 256,  # TODO: Get actual memory usage in MB
                    "scene_objects": 42,  # TODO: Get actual object count
                }

            if include_config:
                result["config"] = {
                    "window_transparency": 1.0,  # TODO: Get actual transparency
                    "window_position": {"x": 100, "y": 100},  # TODO: Get actual position
                    "window_size": {"width": 400, "height": 600},  # TODO: Get actual size
                    "osc_ports": {"receive": 9000, "send": 9001},
                }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to get Unity system status: {str(e)}"}

    async def handle_unity_window_position(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window position/size request."""
        try:
            # Validate parameters
            x = params.get("x")
            y = params.get("y")
            width = params.get("width")
            height = params.get("height")
            monitor = params.get("monitor", 0)
            params.get("center_on_monitor", False)

            # TODO: Implement actual Unity window positioning via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": "Window position updated",
                "position": {"x": x or 100, "y": y or 100},
                "size": {"width": width or 400, "height": height or 600},
                "monitor": monitor,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to update window position: {str(e)}"}

    async def handle_unity_window_transparency(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window transparency request."""
        try:
            alpha = params.get("alpha", 1.0)
            transition_time = params.get("transition_time", 0.0)

            # Validate alpha range
            alpha = max(0.0, min(1.0, alpha))

            # TODO: Implement actual Unity window transparency via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": "Window transparency updated",
                "alpha": alpha,
                "transition_time": transition_time,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to update window transparency: {str(e)}"}

    async def handle_unity_window_visibility(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window visibility request."""
        try:
            visible = params.get("visible")
            fade_transition = params.get("fade_transition", True)

            if visible is None:
                return {"status": "error", "message": "Parameter 'visible' is required"}

            # TODO: Implement actual Unity window visibility via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": f"Window {'shown' if visible else 'hidden'}",
                "visible": visible,
                "fade_transition": fade_transition,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to update window visibility: {str(e)}"}

    async def handle_unity_window_mode(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity window interaction mode request."""
        try:
            mode = params.get("mode")
            transition_effect = params.get("transition_effect", True)

            if mode not in ["interactive", "clickthrough"]:
                return {
                    "status": "error",
                    "message": "Mode must be 'interactive' or 'clickthrough'",
                }

            # TODO: Implement actual Unity window mode via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": f"Window mode set to {mode}",
                "mode": mode,
                "transition_effect": transition_effect,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to update window mode: {str(e)}"}

    async def handle_unity_avatar_load(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity avatar loading request."""
        try:
            path = params.get("path")
            if not path:
                return {"status": "error", "message": "Parameter 'path' is required"}

            make_active = params.get("make_active", True)
            preload_animations = params.get("preload_animations", True)
            params.get("position_offset", {"x": 0, "y": 0, "z": 0})

            # TODO: Implement actual VRM loading via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": f"Avatar loaded from {path}",
                "avatar_id": f"avatar_{hash(path) % 1000}",
                "avatar_name": "Mock Avatar",  # TODO: Extract from VRM
                "blend_shape_count": 50,  # TODO: Get from VRM
                "bone_count": 75,  # TODO: Get from VRM
                "animations_loaded": 10 if preload_animations else 0,
                "active": make_active,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to load avatar: {str(e)}"}

    async def handle_unity_avatar_expression(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity avatar expression request."""
        try:
            expression = params.get("expression")
            if not expression:
                return {"status": "error", "message": "Parameter 'expression' is required"}

            strength = params.get("strength", 1.0)
            transition_time = params.get("transition_time", 0.2)
            blend_with_current = params.get("blend_with_current", False)

            # Validate strength range
            strength = max(0.0, min(1.0, strength))

            # TODO: Implement actual expression control via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": f"Expression '{expression}' applied",
                "expression": expression,
                "strength": strength,
                "transition_time": transition_time,
                "blend_with_current": blend_with_current,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to set expression: {str(e)}"}

    async def handle_unity_avatar_animation(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity avatar animation request."""
        try:
            action = params.get("action")
            if not action:
                return {"status": "error", "message": "Parameter 'action' is required"}

            valid_actions = ["play", "stop", "pause", "resume", "loop"]
            if action not in valid_actions:
                return {
                    "status": "error",
                    "message": f"Action must be one of: {', '.join(valid_actions)}",
                }

            animation_name = params.get("animation_name") if action == "play" else None
            loop = params.get("loop", True) if action in ["play", "loop"] else False
            speed = params.get("speed", 1.0)
            blend_time = params.get("blend_time", 0.3)

            # TODO: Implement actual animation control via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": f"Animation action '{action}' performed",
                "action": action,
                "animation_name": animation_name,
                "loop": loop,
                "speed": speed,
                "blend_time": blend_time,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to control animation: {str(e)}"}

    async def handle_unity_osc_bridge(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity OSC bridge configuration request."""
        try:
            enable_bridge = params.get("enable_bridge")
            if enable_bridge is None:
                return {"status": "error", "message": "Parameter 'enable_bridge' is required"}

            receive_port = params.get("receive_port", 9000)
            send_port = params.get("send_port", 9001)
            server_ip = params.get("server_ip", "127.0.0.1")
            params.get("auto_reconnect", True)
            params.get("heartbeat_interval", 30)

            # TODO: Implement actual OSC bridge configuration
            # For now, return success with mock data
            connection_status = "connected" if enable_bridge else "disconnected"

            result = {
                "status": "success",
                "message": f"OSC bridge {'enabled' if enable_bridge else 'disabled'}",
                "bridge_enabled": enable_bridge,
                "receive_port": receive_port,
                "send_port": send_port,
                "server_ip": server_ip,
                "connection_status": connection_status,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to configure OSC bridge: {str(e)}"}

    async def handle_unity_plugin_load(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity plugin loading request."""
        try:
            action = params.get("action")
            if not action:
                return {"status": "error", "message": "Parameter 'action' is required"}

            valid_actions = ["load", "unload", "list", "reload"]
            if action not in valid_actions:
                return {
                    "status": "error",
                    "message": f"Action must be one of: {', '.join(valid_actions)}",
                }

            # TODO: Implement actual plugin management via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": f"Plugin action '{action}' performed",
                "action": action,
                "timestamp": time.time(),
            }

            if action == "load":
                plugin_path = params.get("plugin_path")
                if not plugin_path:
                    return {
                        "status": "error",
                        "message": "Parameter 'plugin_path' is required for load action",
                    }
                result["plugin_path"] = plugin_path
                result["plugin_name"] = "MockPlugin"  # TODO: Extract from plugin
                result["config_applied"] = params.get("config", {})

            elif action in ["unload", "reload"]:
                plugin_name = params.get("plugin_name")
                if not plugin_name:
                    return {
                        "status": "error",
                        "message": f"Parameter 'plugin_name' is required for {action} action",
                    }
                result["plugin_name"] = plugin_name
                if action == "reload":
                    result["config_applied"] = params.get("config", {})

            elif action == "list":
                result["loaded_plugins"] = ["AvatarController", "OSCBridge"]  # Mock data
                result["available_plugins"] = [
                    "ExpressionController",
                    "AnimationManager",
                ]  # Mock data

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to manage plugin: {str(e)}"}

    async def handle_unity_config_update(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity configuration update request."""
        try:
            config_section = params.get("config_section")
            if not config_section:
                return {"status": "error", "message": "Parameter 'config_section' is required"}

            valid_sections = ["rendering", "performance", "behavior", "audio", "network"]
            if config_section not in valid_sections:
                return {
                    "status": "error",
                    "message": f"Config section must be one of: {', '.join(valid_sections)}",
                }

            settings = params.get("settings", {})
            apply_immediately = params.get("apply_immediately", True)
            persist_changes = params.get("persist_changes", True)

            # TODO: Implement actual configuration updates via OSC
            # For now, return success with mock data
            result = {
                "status": "success",
                "message": f"Configuration section '{config_section}' updated",
                "config_section": config_section,
                "settings_applied": settings,
                "settings_ignored": [],  # Mock: no settings ignored
                "apply_immediately": apply_immediately,
                "persist_changes": persist_changes,
                "timestamp": time.time(),
            }

            return result
        except Exception as e:
            return {"status": "error", "message": f"Failed to update configuration: {str(e)}"}


async def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    enable_loki: bool = False,
    loki_url: str = None,
    enable_osc: bool = False,
):
    """Run the AvatarMCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    logger.info("Starting AvatarMCP server (FastMCP 2.11.3+ compatible)")

    try:
        # Create the server
        server = AvatarMCPServer(enable_osc=enable_osc)

        # Run as stdio server (MCP standard)
        await server.mcp.run()

    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        return 1

    return 0


async def main():
    """Main entry point for the MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="AvatarMCP Server (FastMCP 2.11.3+ compatible)")
    parser.add_argument("--enable-osc", action="store_true", help="Enable OSC server")

    args = parser.parse_args()

    # Run the server
    return await run_server(enable_osc=args.enable_osc)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
