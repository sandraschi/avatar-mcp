"""
Clean MCP Server - AvatarMCP

Minimal MCP server implementation focused on protocol handling and tool delegation.
All tools are implemented in modular classes within the tools/ directory.
"""
import json
import sys
import os
import logging
from typing import Any, Dict

# Import FastMCP
try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

logger = logging.getLogger(__name__)

class MCPServer:
    """Clean MCP server that delegates all functionality to modular tool classes."""

    def __init__(self):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP is required but not available")

        # Initialize FastMCP with minimal configuration like other MCP servers
        self.mcp = FastMCP("avatarmcp")

        # Register prompts
        self._register_prompts()

        # Initialize tool modules (tools are registered within modules)
        self._init_tool_modules()

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
        import avatarmcp.tools.core.core_tools as core_module
        import avatarmcp.tools.audio.audio_tools as audio_module
        import avatarmcp.tools.animation.animation_tools as animation_module
        import avatarmcp.tools.emotion.emotion_tools as emotion_module
        import avatarmcp.tools.interactive.interactive_tools as interactive_module
        import avatarmcp.tools.performance.performance_tools as performance_module
        import avatarmcp.tools.content.content_tools as content_module
        import avatarmcp.tools.collaboration.collaboration_tools as collaboration_module
        import avatarmcp.tools.ai_behavior.ai_behavior_tools as ai_behavior_module
        import avatarmcp.tools.unity.unity_tools as unity_module

        self.core_tools = core_module.CoreTools(self)
        self.audio_tools = audio_module.AudioTools(self)
        self.animation_tools = animation_module.AnimationTools(self)
        self.emotion_tools = emotion_module.EmotionTools(self)
        self.interactive_tools = interactive_module.InteractiveTools(self)
        self.performance_tools = performance_module.PerformanceTools(self)
        self.content_tools = content_module.ContentTools(self)
        self.collaboration_tools = collaboration_module.CollaborationTools(self)
        self.ai_behavior_tools = ai_behavior_module.AIBehaviorTools(self)
        self.unity_tools = unity_module.UnityTools(self)


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

