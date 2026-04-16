"""
Clean MCP Server - AvatarMCP

Minimal MCP server implementation focused on protocol handling and tool delegation.
All tools are implemented in modular classes within the tools/ directory.
"""

import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

# Import FastMCP
try:
    from fastmcp import FastMCP

    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

# Import OSC client for Unity desktop avatar communication
try:
    from pythonosc.udp_client import SimpleUDPClient

    OSC_AVAILABLE = True
except ImportError:
    OSC_AVAILABLE = False
    logger.warning("python-osc not available - Unity desktop avatar integration disabled")


class MCPServer:
    """Clean MCP server that delegates all functionality to modular tool classes."""

    def __init__(self):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP is required but not available")

        # Initialize FastMCP with minimal configuration like other MCP servers
        self.mcp = FastMCP("avatarmcp")

        # Initialize OSC client for Unity desktop avatar communication
        self.osc_client: SimpleUDPClient | None = None
        self.unity_app_process: subprocess.Popen | None = None
        self._init_osc_client()

        # Register prompts
        self._register_prompts()

        # Initialize tool modules (tools are registered within modules)
        self._init_tool_modules()

    def _init_osc_client(self):
        """Initialize OSC client for Unity desktop avatar communication."""
        if OSC_AVAILABLE:
            try:
                # Unity desktop avatar listens on port 9000
                self.osc_client = SimpleUDPClient("127.0.0.1", 9000)
                logger.info("OSC client initialized for Unity desktop avatar (port 9000)")
            except Exception as e:
                logger.error(f"Failed to initialize OSC client: {e}")
                self.osc_client = None
        else:
            logger.warning("OSC client not available - Unity integration disabled")

    def _ensure_unity_app_running(self) -> bool:
        """Ensure the desktop avatar viewer application is running."""
        if not OSC_AVAILABLE:
            logger.warning("OSC not available - cannot communicate with avatar viewer")
            return False

        # Check if process is still running
        if self.unity_app_process and self.unity_app_process.poll() is None:
            return True

        # Try to launch the Python desktop avatar viewer
        viewer_paths = [
            os.path.join(os.getcwd(), "desktop_avatar_viewer.py"),
            os.path.join(os.getcwd(), "src", "desktop_avatar_viewer.py"),
        ]

        for viewer_path in viewer_paths:
            if os.path.exists(viewer_path):
                try:
                    logger.info(f"Launching desktop avatar viewer: {viewer_path}")
                    # Launch in background
                    self.unity_app_process = subprocess.Popen(
                        [sys.executable, viewer_path],
                        cwd=os.getcwd(),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    # Give it time to start
                    import time

                    time.sleep(3)
                    return True
                except Exception as e:
                    logger.error(f"Failed to launch avatar viewer at {viewer_path}: {e}")
                    continue

        logger.warning("Desktop avatar viewer not found. Please ensure desktop_avatar_viewer.py exists")
        return False

    def _send_osc_message(self, address: str, *args) -> bool:
        """Send an OSC message to the Unity desktop avatar."""
        if not self.osc_client:
            logger.error("OSC client not initialized")
            return False

        if not self._ensure_unity_app_running():
            logger.error("Unity desktop avatar not running")
            return False

        try:
            self.osc_client.send_message(address, args if len(args) > 1 else args[0] if args else [])
            logger.debug(f"Sent OSC: {address} {args}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OSC message {address}: {e}")
            return False

    def _register_prompts(self):
        """Register useful MCP prompts for avatar management."""

        @self.mcp.prompt()
        def avatar_setup_guide():
            """Complete guide for setting up and managing VRM avatars."""
            return """# AvatarMCP Setup Guide

Use `avatar_list` → `avatar_load` → `animation_play` for basic avatar control.
Use `unity_*` tools for Unity desktop integration.
See individual tool docs for detailed usage."""

        @self.mcp.prompt()
        def unity_desktop_setup():
            """Guide for Unity desktop avatar integration."""
            return """# Unity Setup

1. Install Unity + VRM/OSC packages
2. Configure OSC: unity_osc_bridge({'enable_bridge': True})
3. Load avatar: unity_avatar_load({'path': 'model.vrm'})
4. Position: unity_window_position({'x': 100, 'y': 100})"""

    def _init_tool_modules(self):
        """Initialize modular tool classes with absolute imports for compatibility."""
        # Use absolute imports to work whether run as module or script
        import avatarmcp.tools.animation.animation_tools as animation_module
        import avatarmcp.tools.audio.audio_tools as audio_module
        import avatarmcp.tools.core.core_tools as core_module
        import avatarmcp.tools.emotion.emotion_tools as emotion_module
        import avatarmcp.tools.resonite.resonite_tools as resonite_module

        self.core_tools = core_module.CoreTools(self)
        self.audio_tools = audio_module.AudioTools(self)
        self.animation_tools = animation_module.AnimationTools(self)
        self.emotion_tools = emotion_module.EmotionTools(self)
        self.resonite_tools = resonite_module.ResoniteTools(self)

    def run(self):
        """Run the MCP server using standard FastMCP stdio transport."""
        logger.info("Starting AvatarMCP server with FastMCP stdio transport")

        # Use the standard FastMCP approach that works with all other MCP servers
        import asyncio

        try:
            asyncio.run(self.mcp.run_stdio_async())
        except Exception as e:
            logger.error(f"Error running FastMCP server: {e}")
            import sys

            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()
