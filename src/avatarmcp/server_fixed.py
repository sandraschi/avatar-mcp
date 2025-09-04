"""
AvatarMCP - FastMCP 2.11.3 Server Implementation - FIXED

This module implements the MCP (Model Context Protocol) server for AvatarMCP,
following the FastMCP 2.11.3+ API standards.

FIXES:
- Updated FastMCP API from deprecated .method() decorators to new @mcp.tool() pattern
- Fixed initialization issues with FastMCP 2.12.0+
"""
import asyncio
import fnmatch
import inspect
import json
import logging
import os
import signal
import sys
import time
from typing import Any, Dict, List, Optional, Union, cast

try:
    import aiofiles
except ImportError:
    aiofiles = None

from fastmcp import FastMCP

from .models.vrm_model import VRMModel
from .models.vrm_manager import VRMManager
from .handlers.logging_handler import LoggingHandler
from .handlers.settings_handler import SettingsHandler
from .handlers.rest_handler import RESTHandler
from .handlers.websocket_handler import WebSocketHandler
from .tools.chat_tools import ChatTool
from .handlers.chatbot_handler import ChatbotHandler
from .metrics import MetricsCollector

logger = logging.getLogger(__name__)

class OSCConfig:
    def __init__(self, client_address: str = "127.0.0.1", client_port: int = 9000, server_address: str = "127.0.0.1", server_port: int = 9001):
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
    def __init__(self, osc_config: Optional[OSCConfig] = None, enabled: bool = True):
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
                self.dispatcher
            )
            self.osc_client = SimpleUDPClient(
                self.osc_config.client_address, 
                self.osc_config.client_port
            )
            
            # Register the handler method
            self.dispatcher.map("/*", self._handle_osc_message)
            self.initialized = True
            logger.info(f"OSC server initialized on {self.osc_config.server_address}:{self.osc_config.server_port}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OSC server: {e}")
            logger.warning("Continuing without OSC functionality")
            self.enabled = False
    
    async def _handle_osc_message(self, address, *args):
        """Internal handler for OSC messages."""
        logger.info(f"Received OSC message: {address} {args}")
        
        # Call the appropriate handler method if it exists
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '_osc_address'):
                if fnmatch.fnmatch(address, method._osc_address):
                    return await method(address, *args)
    
    @oscmethod("/avatar/osc/*")
    async def handle_osc_message(self, address, *args):
        """Handle OSC messages matching /avatar/osc/* pattern."""
        logger.info(f"Handling OSC message: {address} {args}")
        # Add your OSC message handling logic here

class AvatarMCPServer:
    """MCP server implementation for AvatarMCP using FastMCP 2.11.3+ API."""
    
    def __init__(self, osc_config: Optional[OSCConfig] = None, models_dir: Optional[str] = None, enable_osc: bool = False):
        """Initialize the MCP server."""
        self.mcp = FastMCP("avatarmcp")
        self.running = False
        self.osc_manager = OSCManager(osc_config, enabled=enable_osc)
        self._message_id = 0
        
        # Initialize VRM manager
        self.vrm_manager = VRMManager(models_dir)
        self.loaded_models: Dict[str, VRMModel] = {}
        self.active_model_id: Optional[str] = None
        
        # Initialize chat components
        self.chatbot_handler = ChatbotHandler()
        self.chat_tool = ChatTool()
        self.chat_tool.chatbot_handler = self.chatbot_handler
        
        # Initialize metrics collection
        self.metrics = MetricsCollector(port=8000, enabled=True)
        self.metrics.info.info({
            'version': '1.0.0',
            'service': 'avatarmcp',
            'environment': os.getenv('ENV', 'development')
        })
        
        # Track server state
        self.start_time = time.time()
        self.initialized = False
        
        # Register MCP methods using NEW API
        self._register_tools()
        
        # Set up periodic metrics update
        self._metrics_task = None
    
    def _register_tools(self) -> None:
        """Register all MCP tools using the new FastMCP 2.11.3+ API."""
        
        # Core initialization tool
        @self.mcp.tool()
        def initialize(params: Dict[str, Any]) -> Dict[str, Any]:
            """Initialize the AvatarMCP server."""
            return asyncio.run(self.handle_initialize(params))
        
        @self.mcp.tool()
        def shutdown(params: Dict[str, Any]) -> Dict[str, Any]:
            """Shutdown the AvatarMCP server."""
            return asyncio.run(self.handle_shutdown(params))
        
        # Avatar management tools
        @self.mcp.tool()
        def avatar_load(params: Dict[str, Any]) -> Dict[str, Any]:
            """Load an avatar model."""
            return asyncio.run(self.handle_avatar_load(params))
        
        @self.mcp.tool()
        def avatar_unload(params: Dict[str, Any]) -> Dict[str, Any]:
            """Unload an avatar model."""
            return asyncio.run(self.handle_avatar_unload(params))
        
        @self.mcp.tool()
        def avatar_list(params: Dict[str, Any]) -> Dict[str, Any]:
            """List available avatars."""
            return asyncio.run(self.handle_avatar_list(params))
        
        @self.mcp.tool()
        def avatar_set_active(params: Dict[str, Any]) -> Dict[str, Any]:
            """Set the active avatar."""
            return asyncio.run(self.handle_avatar_set_active(params))
        
        @self.mcp.tool()
        def avatar_get_active(params: Dict[str, Any]) -> Dict[str, Any]:
            """Get the active avatar."""
            return asyncio.run(self.handle_avatar_get_active(params))
        
        @self.mcp.tool()
        def avatar_get_metadata(params: Dict[str, Any]) -> Dict[str, Any]:
            """Get avatar metadata."""
            return asyncio.run(self.handle_avatar_get_metadata(params))
        
        # Animation control tools
        @self.mcp.tool()
        def animation_play(params: Dict[str, Any]) -> Dict[str, Any]:
            """Play an animation."""
            return asyncio.run(self.handle_animation_play(params))
        
        @self.mcp.tool()
        def animation_stop(params: Dict[str, Any]) -> Dict[str, Any]:
            """Stop an animation."""
            return asyncio.run(self.handle_animation_stop(params))
        
        @self.mcp.tool()
        def animation_list(params: Dict[str, Any]) -> Dict[str, Any]:
            """List available animations."""
            return asyncio.run(self.handle_animation_list(params))
        
        # Parameter control tools
        @self.mcp.tool()
        def parameter_set(params: Dict[str, Any]) -> Dict[str, Any]:
            """Set a parameter value."""
            return asyncio.run(self.handle_parameter_set(params))
        
        @self.mcp.tool()
        def parameter_get(params: Dict[str, Any]) -> Dict[str, Any]:
            """Get a parameter value."""
            return asyncio.run(self.handle_parameter_get(params))
        
        # OSC control tools
        @self.mcp.tool()
        def osc_send(params: Dict[str, Any]) -> Dict[str, Any]:
            """Send an OSC message."""
            return asyncio.run(self.handle_osc_send(params))
        
        @self.mcp.tool()
        def osc_receive(params: Dict[str, Any]) -> Dict[str, Any]:
            """Receive OSC messages."""
            return asyncio.run(self.handle_osc_receive(params))
        
        # Chat tools
        @self.mcp.tool()
        def chat_start(params: Dict[str, Any]) -> Dict[str, Any]:
            """Start a chat session."""
            return asyncio.run(self.handle_chat_start(params))
        
        @self.mcp.tool()
        def chat_send_message(params: Dict[str, Any]) -> Dict[str, Any]:
            """Send a chat message."""
            return asyncio.run(self.handle_chat_send_message(params))
        
        @self.mcp.tool()
        def chat_stop(params: Dict[str, Any]) -> Dict[str, Any]:
            """Stop a chat session."""
            return asyncio.run(self.handle_chat_stop(params))
        
        @self.mcp.tool()
        def chat_get_state(params: Dict[str, Any]) -> Dict[str, Any]:
            """Get chat state."""
            return asyncio.run(self.handle_chat_get_state(params))
        
        # System tools
        @self.mcp.tool()
        def system_status(params: Dict[str, Any]) -> Dict[str, Any]:
            """Get system status."""
            return asyncio.run(self.handle_system_status(params))
        
        @self.mcp.tool()
        def debug_echo(params: Dict[str, Any]) -> Dict[str, Any]:
            """Echo debug message."""
            return asyncio.run(self.handle_debug_echo(params))
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        logger.info("Initializing AvatarMCP server")
        
        try:
            # Update models directory if specified
            if 'models_dir' in params:
                self.vrm_manager = VRMManager(params['models_dir'])
            
            # Scan for available models
            await self.vrm_manager.scan_models()
            
            self.initialized = True
            return {
                "status": "success",
                "message": "AvatarMCP initialized",
                "version": "1.0.0",
                "models_dir": str(self.vrm_manager.models_dir),
                "num_models": len(self.vrm_manager.models)
            }
        except Exception as e:
            error_msg = f"Initialization failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    async def handle_shutdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP shutdown method."""
        logger.info("Shutdown requested by client")
        self.running = False
        return {"status": "success", "message": "Shutdown initiated"}
    
    async def handle_avatar_load(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
            if not model_info or 'status' not in model_info or model_info['status'] != 'success':
                raise RuntimeError(f"Failed to load model {model_id}")
            
            # Create VRMModel instance
            vrm_model = VRMModel(model_info['path'])
            self.loaded_models[model_id] = vrm_model
            
            # Set as active if requested
            if make_active:
                self.active_model_id = model_id
            
            return {
                "status": "success",
                "model_id": model_id,
                "active": make_active,
                "metadata": model_info.get('metadata', {})
            }
            
        except Exception as e:
            error_msg = f"Failed to load avatar: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    async def handle_avatar_unload(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
                "was_active": avatar_id == self.active_model_id
            }
            
        except Exception as e:
            error_msg = f"Failed to unload avatar: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    async def handle_avatar_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle avatar list request."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")
                
            loaded_only = params.get("loaded_only", False)
            include_metadata = params.get("include_metadata", False)
            
            avatars = []
            
            # Get loaded models
            for model_id in self.loaded_models.keys():
                avatar_info = {
                    "id": model_id,
                    "name": model_id,
                    "status": "loaded",
                    "is_active": model_id == self.active_model_id
                }
                
                if include_metadata and model_id in self.loaded_models:
                    avatar_info["metadata"] = self.loaded_models[model_id].to_dict()
                    
                avatars.append(avatar_info)
            
            return {
                "status": "success",
                "count": len(avatars),
                "active_model": self.active_model_id,
                "avatars": avatars
            }
            
        except Exception as e:
            error_msg = f"Failed to list avatars: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    async def handle_avatar_set_active(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set the active avatar model."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")
                
            avatar_id = params.get("id")
            if not avatar_id:
                raise ValueError("No avatar ID provided")
                
            # Check if the model is loaded
            if avatar_id not in self.loaded_models:
                return {
                    "status": "error",
                    "message": f"Avatar with ID '{avatar_id}' is not loaded"
                }
                
            # Set the active model
            self.active_model_id = avatar_id
            
            return {
                "status": "success",
                "message": f"Set active avatar to: {avatar_id}",
                "active_avatar_id": avatar_id
            }
            
        except Exception as e:
            logger.error(f"Failed to set active avatar: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    async def handle_avatar_get_active(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the currently active avatar model."""
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")
                
            if not self.active_model_id:
                return {
                    "status": "success",
                    "active_avatar_id": None,
                    "message": "No active avatar"
                }
                
            return {
                "status": "success",
                "active_avatar_id": self.active_model_id,
                "loaded": self.active_model_id in self.loaded_models,
                "message": f"Active avatar: {self.active_model_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to get active avatar: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    async def handle_avatar_get_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
                    "metadata": self.loaded_models[avatar_id].to_dict()
                }
            
            raise ValueError(f"Avatar not found: {avatar_id}")
            
        except Exception as e:
            error_msg = f"Failed to get avatar metadata: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    # Placeholder implementations for other handlers
    async def handle_animation_play(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation play request."""
        animation_name = params.get("name", "default")
        return {"status": "success", "message": f"Playing animation: {animation_name}"}
    
    async def handle_animation_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation stop request."""
        return {"status": "success", "message": "Animation stopped"}
    
    async def handle_animation_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation list request."""
        return {
            "status": "success",
            "animations": ["idle", "walk", "run", "wave", "dance"]
        }
    
    async def handle_parameter_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parameter set request."""
        name = params.get("name", "unknown")
        value = params.get("value", 0)
        return {"status": "success", "message": f"Set parameter {name} = {value}"}
    
    async def handle_parameter_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parameter get request."""
        name = params.get("name", "unknown")
        return {"status": "success", "name": name, "value": 0}
    
    async def handle_osc_send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSC send request."""
        address = params.get("address", "/default")
        value = params.get("value", 0)
        return {"status": "success", "message": f"Sent OSC: {address} = {value}"}
    
    async def handle_osc_receive(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSC receive request."""
        return {"status": "success", "messages": []}
    
    async def handle_chat_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat start request."""
        return {"status": "success", "message": "Chat started"}
    
    async def handle_chat_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat send message request."""
        message = params.get("message", "")
        return {"status": "success", "response": f"Echo: {message}"}
    
    async def handle_chat_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat stop request."""
        return {"status": "success", "message": "Chat stopped"}
    
    async def handle_chat_get_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat get state request."""
        return {"status": "success", "state": "idle"}
    
    async def handle_system_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system status request."""
        return {
            "status": "success",
            "system": {
                "name": "AvatarMCP",
                "version": "1.0.0",
                "status": "running",
                "uptime": time.time() - self.start_time,
                "initialized": self.initialized
            }
        }
    
    async def handle_debug_echo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug echo request."""
        return {"status": "success", "echo": params}


async def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    enable_loki: bool = False,
    loki_url: str = None,
    enable_osc: bool = False
):
    """Run the AvatarMCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    
    logger.info(f"Starting AvatarMCP server (FastMCP 2.11.3+ compatible)")
    
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
    parser = argparse.ArgumentParser(description='AvatarMCP Server (FastMCP 2.11.3+ compatible)')
    parser.add_argument('--enable-osc', action='store_true',
                      help='Enable OSC server')
    
    args = parser.parse_args()
    
    # Run the server
    return await run_server(enable_osc=args.enable_osc)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
