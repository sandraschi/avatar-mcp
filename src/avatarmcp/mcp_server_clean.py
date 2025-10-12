"""
Clean MCP Server - AvatarMCP

Minimal MCP server implementation focused on protocol handling and tool delegation.
All tools are implemented in modular classes within the tools/ directory.
"""
import json
import sys
import os
import logging
import asyncio
from typing import Any, Dict, Optional

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

        # Initialize FastMCP
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
        """Initialize modular tool classes."""
        try:
            # Import and initialize core tools
            import avatarmcp.tools.core.core_tools as core_module
            self.core_tools = core_module.CoreTools(self)
            logger.info("Core tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import core tools: {e}")
            self.core_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize core tools: {e}")
            self.core_tools = None

        try:
            # Import and initialize audio tools
            import avatarmcp.tools.audio.audio_tools as audio_module
            self.audio_tools = audio_module.AudioTools(self)
            logger.info("Audio tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import audio tools: {e}")
            self.audio_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize audio tools: {e}")
            self.audio_tools = None

        try:
            # Import and initialize animation tools
            import avatarmcp.tools.animation.animation_tools as animation_module
            self.animation_tools = animation_module.AnimationTools(self)
            logger.info("Animation tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import animation tools: {e}")
            self.animation_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize animation tools: {e}")
            self.animation_tools = None

        try:
            # Import and initialize emotion tools
            import avatarmcp.tools.emotion.emotion_tools as emotion_module
            self.emotion_tools = emotion_module.EmotionTools(self)
            logger.info("Emotion tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import emotion tools: {e}")
            self.emotion_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize emotion tools: {e}")
            self.emotion_tools = None

        try:
            # Import and initialize interactive tools
            import avatarmcp.tools.interactive.interactive_tools as interactive_module
            self.interactive_tools = interactive_module.InteractiveTools(self)
            logger.info("Interactive tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import interactive tools: {e}")
            self.interactive_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize interactive tools: {e}")
            self.interactive_tools = None

        try:
            # Import and initialize performance tools
            import avatarmcp.tools.performance.performance_tools as performance_module
            self.performance_tools = performance_module.PerformanceTools(self)
            logger.info("Performance tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import performance tools: {e}")
            self.performance_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize performance tools: {e}")
            self.performance_tools = None

        try:
            # Import and initialize content creation tools
            import avatarmcp.tools.content.content_tools as content_module
            self.content_tools = content_module.ContentTools(self)
            logger.info("Content creation tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import content creation tools: {e}")
            self.content_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize content creation tools: {e}")
            self.content_tools = None

        try:
            # Import and initialize collaboration tools
            import avatarmcp.tools.collaboration.collaboration_tools as collaboration_module
            self.collaboration_tools = collaboration_module.CollaborationTools(self)
            logger.info("Collaboration tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import collaboration tools: {e}")
            self.collaboration_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize collaboration tools: {e}")
            self.collaboration_tools = None

        try:
            # Import and initialize AI behavior tools
            import avatarmcp.tools.ai_behavior.ai_behavior_tools as ai_behavior_module
            self.ai_behavior_tools = ai_behavior_module.AIBehaviorTools(self)
            logger.info("AI behavior tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import AI behavior tools: {e}")
            self.ai_behavior_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize AI behavior tools: {e}")
            self.ai_behavior_tools = None

        try:
            # Import and initialize Unity tools
            import avatarmcp.tools.unity.unity_tools as unity_module
            self.unity_tools = unity_module.UnityTools(self)
            logger.info("Unity tools initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import Unity tools: {e}")
            self.unity_tools = None
        except Exception as e:
            logger.error(f"Failed to initialize Unity tools: {e}")
            self.unity_tools = None

    def run(self):
        """Run the FastMCP server using manual stdio handling for MCP protocol."""
        logger.info("Starting MCP server with manual stdio handling")

        # Manual MCP protocol handling since FastMCP stdio doesn't work properly
        import asyncio
        import json
        import sys

        async def handle_stdio():
            """Handle MCP protocol over stdio."""
            loop = asyncio.get_event_loop()

            while True:
                try:
                    # Read line from stdin
                    line = await loop.run_in_executor(None, sys.stdin.readline)
                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # logger.debug(f"Received: {line}")  # Commented out to reduce spam

                    # Parse JSON
                    try:
                        request = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                        continue

                    # Handle request
                    response = await self._handle_mcp_request(request)

                    # Send response
                    if response:
                        response_json = json.dumps(response)
                        # logger.debug(f"Sending: {response_json}")  # Commented out to reduce spam
                        print(response_json, flush=True)

                except Exception as e:
                    logger.error(f"Error in stdio loop: {e}")
                    break

        # Run the stdio handler
        asyncio.run(handle_stdio())

    async def _handle_mcp_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle an MCP protocol request."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id")

            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "avatarmcp",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "tools/list":
                # Get tools from FastMCP
                tools_data = await self.mcp.get_tools()
                tools = []
                for tool_name in tools_data:
                    tool = await self.mcp.get_tool(tool_name)
                    tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": {
                            "type": "object",
                            "additionalProperties": True
                        }
                    })

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": tools}
                }

            elif method == "prompts/list":
                # Get prompts from FastMCP
                prompts_data = await self.mcp.get_prompts()
                prompts = []
                for prompt_name in prompts_data:
                    prompt = await self.mcp.get_prompt(prompt_name)
                    prompts.append({
                        "name": prompt_name,
                        "description": prompt.description if hasattr(prompt, 'description') else "",
                        "arguments": prompt.arguments if hasattr(prompt, 'arguments') else []
                    })

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"prompts": prompts}
                }

            elif method == "resources/list":
                # This server doesn't provide resources
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"resources": []}
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})

                if tool_name:
                    # Call the tool through FastMCP
                    result = await self.mcp.call_tool(tool_name, tool_args)
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": result
                    }

        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
