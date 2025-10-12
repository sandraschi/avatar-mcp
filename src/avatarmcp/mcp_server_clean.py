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

        # Ensure the package path is set up correctly
        import os
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Initialize FastMCP
        self.mcp = FastMCP("avatarmcp")

        # Register prompts
        self._register_prompts()

        # Initialize tool modules (tools are registered within modules)
        self._init_tool_modules()

        # Cache tool information to avoid repeated lookups
        self._cached_tools = None

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

    def _get_cached_tools(self):
        """Get cached tools information."""
        if self._cached_tools is None:
            try:
                tools_data = self.mcp.get_tools()
                tools = []
                for tool_name in tools_data:
                    tool = self.mcp.get_tool(tool_name)
                    tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": {"type": "object", "additionalProperties": True}
                    })
                self._cached_tools = tools
            except Exception as e:
                logger.error(f"Error caching tools: {e}")
                self._cached_tools = []
        return self._cached_tools

    def run(self):
        """Run the MCP server with manual stdio handling."""
        logger.info("Starting MCP server with manual stdio handling")

        # Manual stdio handling to avoid Windows subprocess issues
        import sys
        import json
        import time

        # CRITICAL: Cache tools BEFORE entering the main loop
        # This ensures no output to stdout during request processing
        tools = self._get_cached_tools()
        logger.info(f"Cached {len(tools)} tools")

        try:
            while True:
                # Read line from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                    method = request.get("method")
                    req_id = request.get("id")

                    if method == "initialize":
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {"tools": {"listChanged": True}},
                                "serverInfo": {"name": "avatarmcp", "version": "1.0.0"}
                            }
                        }
                        print(json.dumps(response), flush=True)

                    elif method == "tools/list":
                        response = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}
                        print(json.dumps(response), flush=True)

                    elif method == "tools/call":
                        # Handle tool calls
                        tool_name = request.get("params", {}).get("name")
                        tool_args = request.get("params", {}).get("arguments", {})

                        try:
                            # Call tool synchronously
                            result = self.mcp.call_tool(tool_name, tool_args)
                            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
                        except Exception as e:
                            response = {
                                "jsonrpc": "2.0",
                                "id": req_id,
                                "error": {"code": -32603, "message": str(e)}
                            }
                        print(json.dumps(response), flush=True)

                    elif method == "prompts/list":
                        try:
                            prompts_data = self.mcp.get_prompts()
                            prompts = []
                            for prompt_name in prompts_data:
                                prompt = self.mcp.get_prompt(prompt_name)
                                prompts.append({
                                    "name": prompt_name,
                                    "description": getattr(prompt, 'description', ""),
                                    "arguments": getattr(prompt, 'arguments', [])
                                })
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": prompts}}
                        except Exception as e:
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}
                        print(json.dumps(response), flush=True)

                    elif method == "resources/list":
                        response = {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}
                        print(json.dumps(response), flush=True)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32603, "message": str(e)}
                    }
                    print(json.dumps(error_response), flush=True)

        except KeyboardInterrupt:
            logger.info("Server shutting down")
        except Exception as e:
            logger.error(f"Fatal error in server: {e}")
            sys.stderr.write(f"Fatal error: {e}\n")
            sys.stderr.flush()

