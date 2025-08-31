"""
AvatarMCP - FastMCP 2.11.3 Server Implementation

This module implements the MCP (Model Context Protocol) server for AvatarMCP,
following the FastMCP 2.11.3 standard for communication via stdio.
"""
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable, Set

from fastmcp import FastMCP
from osc4py3.as_eventloop import OSCServer, OSCClient, OSCUDPServer, OSCUDPClient
from osc4py3 import oscmethod, oscbuildparse

# Local imports
from .models.vrm_manager import VRMManager, VRMMetadata
from .models.vrm_model import VRMModel
from .tools.chat_tools import ChatTool
from .handlers.chatbot_handler import ChatbotHandler

logger = logging.getLogger(__name__)

class OSCConfig:
    def __init__(self, client_address: str = "127.0.0.1", client_port: int = 9000, server_address: str = "127.0.0.1", server_port: int = 9001):
        self.client_address = client_address
        self.client_port = client_port
        self.server_address = server_address
        self.server_port = server_port

class OSCManager:
    def __init__(self, osc_config: Optional[OSCConfig] = None):
        if osc_config is None:
            osc_config = OSCConfig()
        self.osc_config = osc_config
        self.osc_server = OSCUDPServer((osc_config.server_address, osc_config.server_port), self)
        self.osc_client = OSCUDPClient()
        self.osc_client.connect((osc_config.client_address, osc_config.client_port))

    @oscmethod("/avatar/osc/*")
    def handle_osc_message(self, path, tags, args, source):
        logger.info(f"Received OSC message: {path} {args}")

class AvatarMCPServer:
    """MCP server implementation for AvatarMCP.
    
    This server handles communication with MCP clients and manages VRM models,
    animations, and other avatar-related functionality.
    """
    
    def __init__(self, osc_config: Optional[OSCConfig] = None, models_dir: Optional[str] = None):
        """Initialize the MCP server.
        
        Args:
            osc_config: Optional configuration for OSC client/server.
                       If None, default values will be used.
            models_dir: Directory where VRM models are stored. If None, uses default location.
        """
        self.mcp = FastMCP("avatarmcp")
        self.running = False
        self.osc_manager = OSCManager(osc_config)
        self._message_id = 0
        
        # Initialize VRM manager
        self.vrm_manager = VRMManager(models_dir)
        self.loaded_models: Dict[str, VRMModel] = {}
        self.active_model_id: Optional[str] = None
        
        # Initialize chat components
        self.chatbot_handler = ChatbotHandler()
        self.chat_tool = ChatTool()
        self.chat_tool.chatbot_handler = self.chatbot_handler
        
        # Track server state
        self.start_time = time.time()
        self.initialized = False
        
        # Register MCP methods
        self._register_methods()
    
    def _register_methods(self) -> None:
        """Register all MCP methods and tools."""
        # Core MCP methods
        self.mcp.method("initialize")(self.handle_initialize)
        self.mcp.method("shutdown")(self.handle_shutdown)
        
        # Chat tools
        self.mcp.method("chat.start")(self.handle_chat_start)
        self.mcp.method("chat.send_message")(self.handle_chat_send_message)
        self.mcp.method("chat.stop")(self.handle_chat_stop)
        self.mcp.method("chat.get_state")(self.handle_chat_get_state)
        
        # Avatar management
        self.mcp.method("avatar.load")(self.handle_avatar_load)
        self.mcp.method("avatar.unload")(self.handle_avatar_unload)
        self.mcp.method("avatar.list")(self.handle_avatar_list)
        self.mcp.method("avatar.get_metadata")(self.handle_avatar_get_metadata)
        self.mcp.method("avatar.set_active")(self.handle_avatar_set_active)
        self.mcp.method("avatar.get_active")(self.handle_avatar_get_active)
        self.mcp.method("avatar.load")(self.handle_avatar_load)
        self.mcp.method("avatar.unload")(self.handle_avatar_unload)
        self.mcp.method("avatar.list")(self.handle_avatar_list)
        
        # Animation control
        self.mcp.method("animation.play")(self.handle_animation_play)
        self.mcp.method("animation.stop")(self.handle_animation_stop)
        self.mcp.method("animation.list")(self.handle_animation_list)
        
        # Parameter control
        self.mcp.method("parameter.set")(self.handle_parameter_set)
        self.mcp.method("parameter.get")(self.handle_parameter_get)
        
        # OSC control
        self.mcp.method("osc.send")(self.handle_osc_send)
        self.mcp.method("osc.receive")(self.handle_osc_receive)
        
        # Visualization control
        self.mcp.method("visualization.enable")(self.handle_visualization_enable)
        self.mcp.method("visualization.disable")(self.handle_visualization_disable)
        self.mcp.method("visualization.set_camera")(self.handle_set_camera)
        self.mcp.method("visualization.set_lighting")(self.handle_set_lighting)
        
        # Voice and chat
        self.mcp.method("voice.enable")(self.handle_voice_enable)
        self.mcp.method("voice.disable")(self.handle_voice_disable)
        self.mcp.method("voice.speak")(self.handle_voice_speak)
        self.mcp.method("voice.listen")(self.handle_voice_listen)
        self.mcp.method("chatbot.process")(self.handle_chatbot_process)
        
        # Animation box control
        self.mcp.method("animation_box.set")(self.handle_animation_box_set)
        self.mcp.method("animation_box.show")(self.handle_animation_box_show)
        self.mcp.method("animation_box.hide")(self.handle_animation_box_hide)
        self.mcp.method("animation_box.get_properties")(self.handle_animation_box_get_properties)
        
        # Dance and martial arts animations
        self.mcp.method("animation.dance.start")(self.handle_dance_start)
        self.mcp.method("animation.dance.stop")(self.handle_dance_stop)
        self.mcp.method("animation.martial_arts.pose")(self.handle_martial_arts_pose)
        self.mcp.method("animation.martial_arts.sequence")(self.handle_martial_arts_sequence)
        
        # System and debugging
        self.mcp.method("system.status")(self.handle_system_status)
        self.mcp.method("debug.log")(self.handle_debug_log)
        self.mcp.method("debug.echo")(self.handle_debug_echo)
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request.
        
        Args:
            params: Dictionary containing initialization parameters
                   - models_dir: Optional directory to scan for VRM models
                   
        Returns:
            Dictionary with initialization status and server information
        """
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
        return {}
    
    async def handle_avatar_load(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle avatar loading request.
        
        Args:
            params: Dictionary containing:
                   - path: Path to the VRM file or model ID
                   - make_active: Whether to make this the active model (default: True)
                   - metadata: Optional metadata for the model
                   
        Returns:
            Dictionary with load status and model information
        """
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
            
            # Prepare response
            response = {
                "status": "success",
                "model_id": model_id,
                "active": make_active,
                "metadata": model_info.get('metadata', {})
            }
            
            logger.info(f"Successfully loaded avatar: {model_id}")
            return response
            
        except Exception as e:
            error_msg = f"Failed to load avatar: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    async def handle_animation_play(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation play request."""
        try:
            animation_name = params.get("name")
            if not animation_name:
                raise ValueError("No animation name provided")
                
            logger.info(f"Playing animation: {animation_name}")
            # TODO: Implement actual animation playing
            
            return {"status": "success", "message": f"Playing animation: {animation_name}"}
            
        except Exception as e:
            logger.error(f"Failed to play animation: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def handle_animation_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation stop request."""
        try:
            animation_name = params.get("name")
            logger.info(f"Stopping animation: {animation_name or 'all'}")
            # TODO: Implement actual animation stopping
            
            return {"status": "success", "message": f"Stopped animation: {animation_name or 'all'}"}
            
        except Exception as e:
            logger.error(f"Failed to stop animation: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    # Avatar Management Handlers
    async def handle_avatar_unload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle avatar unload request.
        
        Args:
            params: Dictionary containing:
                   - id: ID of the avatar to unload
                   - force: Whether to force unload even if it's the active model (default: False)
                   
        Returns:
            Dictionary with unload status
        """
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
                
            logger.info(f"Successfully unloaded avatar: {avatar_id}")
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
        """Handle avatar list request.
        
        Args:
            params: Dictionary containing optional filters:
                   - loaded_only: If True, only return currently loaded avatars (default: False)
                   - include_metadata: If True, include full metadata for each avatar (default: False)
                   
        Returns:
            Dictionary with list of available avatars and their status
        """
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")
                
            loaded_only = params.get("loaded_only", False)
            include_metadata = params.get("include_metadata", False)
            
            avatars = []
            
            # Get all available models from VRM manager
            if not loaded_only:
                for model_id, model_info in self.vrm_manager.models.items():
                    is_loaded = model_id in self.loaded_models
                    avatar_info = {
                        "id": model_id,
                        "name": model_info.get("metadata", {}).get("name", model_id),
                        "status": "loaded" if is_loaded else "available",
                        "path": model_info.get("path", "")
                    }
                    
                    if include_metadata:
                        if is_loaded:
                            avatar_info["metadata"] = self.loaded_models[model_id].to_dict()
                        else:
                            # Load basic metadata without loading the full model
                            metadata_path = os.path.join(
                                os.path.dirname(model_info.get("path", "")),
                                f"{model_id}.meta.json"
                            )
                            if os.path.exists(metadata_path):
                                try:
                                    async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as f:
                                        avatar_info["metadata"] = json.loads(await f.read())
                                except Exception as e:
                                    logger.warning(f"Failed to load metadata for {model_id}: {e}")
                    
                    avatars.append(avatar_info)
            
            # Add loaded models that might not be in the VRM manager (e.g., temporary models)
            loaded_ids = {model_id for model_id in self.loaded_models.keys()}
            if not loaded_only:
                loaded_ids = loaded_ids - set(self.vrm_manager.models.keys())
                
            for model_id in loaded_ids:
                avatar_info = {
                    "id": model_id,
                    "name": model_id,  # Use ID as name if no metadata available
                    "status": "loaded",
                    "is_temporary": True
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
            
    async def handle_animation_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation list request."""
        try:
            # TODO: Implement actual animation listing
            return {
                "status": "success",
                "animations": [
                    {"name": "idle", "type": "loop", "duration": 0},
                    {"name": "walk", "type": "loop", "duration": 0},
                    {"name": "run", "type": "loop", "duration": 0},
                    # Add more animations as needed
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to list animations: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    # Parameter Control Handlers
    async def handle_parameter_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parameter set request."""
        try:
            name = params.get("name")
            value = params.get("value")
            
            if name is None or value is None:
                raise ValueError("Both name and value must be provided")
                
            logger.info(f"Setting parameter {name} = {value}")
            # TODO: Implement actual parameter setting
            
            return {"status": "success", "message": f"Set parameter {name} = {value}"}
            
        except Exception as e:
            logger.error(f"Failed to set parameter: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_parameter_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parameter get request."""
        try:
            name = params.get("name")
            
            if not name:
                raise ValueError("Parameter name must be provided")
                
            # TODO: Implement actual parameter getting
            value = 0  # Default value
            
            return {
                "status": "success",
                "name": name,
                "value": value
            }
            
        except Exception as e:
            logger.error(f"Failed to get parameter: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    # OSC Handlers
    async def handle_osc_send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSC send request.
        
        Args:
            params: Dictionary containing:
                   - address: OSC address pattern (e.g., "/avatar/parameters/Blink")
                   - value: Value to send (will be converted based on type)
                   - type: Optional OSC type ('f' for float, 'i' for int, 's' for string, etc.)
        """
        try:
            address = params.get("address")
            value = params.get("value")
            osc_type = params.get("type")
            
            if not address or value is None:
                raise ValueError("Both address and value must be provided")
                
            # Convert type string to OSCMessageType if provided
            msg_type = None
            if osc_type:
                try:
                    msg_type = OSCMessageType(osc_type.lower())
                except ValueError:
                    logger.warning(f"Unknown OSC type: {osc_type}. Using default.")
            
            # Send the OSC message
            self.osc_manager.send_message(address, value, msg_type)
            
            return {
                "status": "success", 
                "message": f"Sent OSC: {address} = {value}",
                "type": msg_type.value if msg_type else self.osc_manager.config.default_message_type.value
            }
            
        except Exception as e:
            error_msg = f"Failed to send OSC: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
            
    async def handle_osc_receive(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSC receive request.
        
        Args:
            params: Dictionary containing:
                   - address: Optional OSC address pattern to filter messages
                   - timeout: Maximum time to wait for messages in seconds (default: 1.0)
                   - max_messages: Maximum number of messages to return (default: 10)
                   
        Returns:
            Dictionary with status and list of received messages in the format:
            {
                "status": "success",
                "messages": [
                    {"address": "/path", "args": [value1, value2, ...]},
                    ...
                ]
            }
        """
        try:
            address_pattern = params.get("address")
            timeout = float(params.get("timeout", 1.0))
            max_messages = int(params.get("max_messages", 10))
            
            messages = []
            start_time = asyncio.get_event_loop().time()
            
            # Check for messages until timeout or max_messages reached
            while len(messages) < max_messages:
                time_remaining = timeout - (asyncio.get_event_loop().time() - start_time)
                if time_remaining <= 0:
                    break
                    
                # Wait for next message with remaining timeout
                msg = await self.osc_manager.get_next_message(timeout=time_remaining)
                if not msg:
                    break
                    
                msg_address, msg_args = msg
                
                # Filter by address pattern if specified
                if address_pattern and not self._match_osc_pattern(msg_address, address_pattern):
                    continue
                    
                messages.append({
                    "address": msg_address,
                    "args": msg_args
                })
            
            return {
                "status": "success",
                "messages": messages,
                "count": len(messages)
            }
            
        except Exception as e:
            error_msg = f"Failed to receive OSC messages: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
            
    def _match_osc_pattern(self, address: str, pattern: str) -> bool:
        """Check if an OSC address matches a pattern with wildcards.
        
        Args:
            address: OSC address (e.g., "/avatar/parameters/Blink")
            pattern: Pattern with wildcards (e.g., "/avatar/parameters/*")
            
        Returns:
            True if address matches the pattern, False otherwise
        """
        import fnmatch
        return fnmatch.fnmatch(address, pattern)
            
    # Visualization Handlers
    async def handle_visualization_enable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visualization enable request."""
        try:
            logger.info("Enabling visualization")
            # TODO: Implement actual visualization enabling
            
            return {"status": "success", "message": "Visualization enabled"}
            
        except Exception as e:
            logger.error(f"Failed to enable visualization: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_visualization_disable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visualization disable request."""
        try:
            logger.info("Disabling visualization")
            # TODO: Implement actual visualization disabling
            
            return {"status": "success", "message": "Visualization disabled"}
            
        except Exception as e:
            logger.error(f"Failed to disable visualization: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_set_camera(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle set camera request."""
        try:
            position = params.get("position", [0, 0, 0])
            target = params.get("target", [0, 0, 0])
            
            logger.info(f"Setting camera: position={position}, target={target}")
            # TODO: Implement actual camera setting
            
            return {"status": "success", "message": "Camera position set"}
            
        except Exception as e:
            logger.error(f"Failed to set camera: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_set_lighting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle set lighting request."""
        try:
            intensity = params.get("intensity", 1.0)
            color = params.get("color", [1.0, 1.0, 1.0])
            
            logger.info(f"Setting lighting: intensity={intensity}, color={color}")
            # TODO: Implement actual lighting setting
            
            return {"status": "success", "message": "Lighting set"}
            
        except Exception as e:
            logger.error(f"Failed to set lighting: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    # Voice and Chat Handlers
    async def handle_voice_enable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice enable request."""
        try:
            logger.info("Enabling voice")
            # TODO: Implement actual voice enabling
            
            return {"status": "success", "message": "Voice enabled"}
            
        except Exception as e:
            logger.error(f"Failed to enable voice: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_voice_disable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice disable request."""
        try:
            logger.info("Disabling voice")
            # TODO: Implement actual voice disabling
            
            return {"status": "success", "message": "Voice disabled"}
            
        except Exception as e:
            logger.error(f"Failed to disable voice: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_voice_speak(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle speak request."""
        try:
            text = params.get("text")
            if not text:
                raise ValueError("Text must be provided")
                
            logger.info(f"Speaking: {text}")
            # TODO: Implement actual text-to-speech
            
            return {"status": "success", "message": f"Spoke: {text}"}
            
        except Exception as e:
            logger.error(f"Failed to speak: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_voice_listen(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle listen request."""
        try:
            timeout = params.get("timeout", 5)
            logger.info(f"Listening for speech (timeout: {timeout}s)")
            # TODO: Implement actual speech recognition
            
            return {
                "status": "success",
                "text": "Recognized speech would appear here",
                "confidence": 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to listen: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Chat Handlers
    async def handle_chat_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat start request.
        
        Args:
            params: Dictionary containing:
                   - wake_word: Optional wake word to use
                   - auto_listen: Whether to automatically listen after response
                   - voice_feedback: Whether to enable voice feedback
        """
        try:
            return await self.chat_tool._start_chat(
                wake_word=params.get("wake_word"),
                auto_listen=params.get("auto_listen"),
                voice_feedback=params.get("voice_feedback")
            )
        except Exception as e:
            logger.error(f"Failed to start chat: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
            
    async def handle_chat_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sending a message to the chat.
        
        Args:
            params: Dictionary containing:
                   - message: The message text to send
        """
        try:
            message = params.get("message")
            if not message:
                return {"status": "error", "message": "Message is required"}
                
            return await self.chat_tool._send_message(message)
        except Exception as e:
            logger.error(f"Failed to send chat message: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
            
    async def handle_chat_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stopping the chat."""
        try:
            return await self.chat_tool._stop_chat()
        except Exception as e:
            logger.error(f"Failed to stop chat: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
            
    async def handle_chat_get_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current chat state."""
        try:
            return await self.chat_tool._get_chat_state()
        except Exception as e:
            logger.error(f"Failed to get chat state: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
            
    async def handle_chatbot_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chatbot process request."""
        try:
            text = params.get("text")
            if not text:
                raise ValueError("Text must be provided")
                
            logger.info(f"Processing chat: {text}")
            # TODO: Implement actual chatbot processing
            
            return {
                "status": "success",
                "response": f"Echo: {text}"  # Simple echo for now
            }
            
        except Exception as e:
            logger.error(f"Failed to process chat: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    # Animation Box Handlers
    async def handle_animation_box_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation box set request."""
        try:
            position = params.get("position", [0, 0, 0])
            size = params.get("size", [1, 1, 1])
            
            logger.info(f"Setting animation box: position={position}, size={size}")
            # TODO: Implement actual animation box setting
            
            return {"status": "success", "message": "Animation box set"}
            
        except Exception as e:
            logger.error(f"Failed to set animation box: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_animation_box_show(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation box show request."""
        try:
            logger.info("Showing animation box")
            # TODO: Implement actual animation box showing
            
            return {"status": "success", "message": "Animation box shown"}
            
        except Exception as e:
            logger.error(f"Failed to show animation box: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_animation_box_hide(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation box hide request."""
        try:
            logger.info("Hiding animation box")
            # TODO: Implement actual animation box hiding
            
            return {"status": "success", "message": "Animation box hidden"}
            
        except Exception as e:
            logger.error(f"Failed to hide animation box: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_animation_box_get_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle animation box get properties request."""
        try:
            # TODO: Implement actual animation box properties getting
            return {
                "status": "success",
                "visible": True,
                "position": [0, 0, 0],
                "size": [1, 1, 1]
            }
            
        except Exception as e:
            logger.error(f"Failed to get animation box properties: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_avatar_get_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed metadata for a specific avatar.
        
        Args:
            params: Dictionary containing:
                   - id: ID of the avatar (defaults to active model if not specified)
                   - refresh: If True, reload metadata from disk (default: False)
                   
        Returns:
            Dictionary containing the avatar's metadata
        """
        try:
            if not self.initialized:
                raise RuntimeError("Server not initialized. Call 'initialize' first.")
                
            avatar_id = params.get("id", self.active_model_id)
            refresh = params.get("refresh", False)
            
            if not avatar_id:
                raise ValueError("No avatar ID provided and no active model")
                
            # Check if the model is loaded
            if avatar_id in self.loaded_models:
                if refresh:
                    # Reload the model to refresh metadata
                    model_info = await self.vrm_manager.load_model(avatar_id)
                    if model_info and 'status' in model_info and model_info['status'] == 'success':
                        self.loaded_models[avatar_id] = VRMModel(model_info['path'])
                
                return {
                    "status": "success",
                    "id": avatar_id,
                    "loaded": True,
                    "active": avatar_id == self.active_model_id,
                    "metadata": self.loaded_models[avatar_id].to_dict()
                }
            
            # If not loaded, try to get metadata from VRM manager
            if avatar_id in self.vrm_manager.models:
                model_info = self.vrm_manager.models[avatar_id]
                metadata = {}
                
                # Try to load metadata file if it exists
                metadata_path = os.path.join(
                    os.path.dirname(model_info.get("path", "")),
                    f"{avatar_id}.meta.json"
                )
                
                if os.path.exists(metadata_path):
                    try:
                        async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.loads(await f.read())
                    except Exception as e:
                        logger.warning(f"Failed to load metadata for {avatar_id}: {e}")
                
                # Fall back to basic info if no metadata file
                if not metadata:
                    metadata = {
                        "name": avatar_id,
                        "version": "1.0",
                        "author": "Unknown",
                        "path": model_info.get("path", "")
                    }
                
                return {
                    "status": "success",
                    "id": avatar_id,
                    "loaded": False,
                    "active": False,
                    "metadata": metadata
                }
            
            raise ValueError(f"Avatar not found: {avatar_id}")
            
        except Exception as e:
            error_msg = f"Failed to get avatar metadata: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
            
    # Dance and Martial Arts Handlers
    async def handle_dance_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dance start request."""
        try:
            dance_name = params.get("name", "default")
            logger.info(f"Starting dance: {dance_name}")
            # TODO: Implement actual dance starting
            
            return {"status": "success", "message": f"Started dance: {dance_name}"}
            
        except Exception as e:
            logger.error(f"Failed to start dance: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_dance_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dance stop request."""
        try:
            logger.info("Stopping dance")
            # TODO: Implement actual dance stopping
            
            return {"status": "success", "message": "Stopped dance"}
                
            response = {
                "status": "success",
                "active": True,
                "id": self.active_model_id,
                "loaded": True
            }
            
            # Add metadata if requested
            if include_metadata and self.active_model_id in self.loaded_models:
                response["metadata"] = self.loaded_models[self.active_model_id].to_dict()
            
            # Add basic info if metadata not available or not requested
            if "metadata" not in response:
                model_info = self.vrm_manager.models.get(self.active_model_id, {})
                response.update({
                    "name": model_info.get("metadata", {}).get("name", self.active_model_id),
                    "path": model_info.get("path", "")
                })
            
            return response
            
        except Exception as e:
            error_msg = f"Failed to get active avatar: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
            
    async def handle_martial_arts_sequence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle martial arts sequence request."""
        try:
            sequence = params.get("sequence")
            if not sequence or not isinstance(sequence, list):
                raise ValueError("Sequence must be provided as a list of poses")
                
            logger.info(f"Playing martial arts sequence: {sequence}")
            # TODO: Implement actual martial arts sequence playing
            
            return {"status": "success", "message": f"Played martial arts sequence with {len(sequence)} moves"}
            
        except Exception as e:
            logger.error(f"Failed to play martial arts sequence: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    # System and Debug Handlers
    async def handle_system_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system status request."""
        try:
            return {
                "status": "success",
                "system": {
                    "name": "AvatarMCP",
                    "version": "0.1.0",
                    "status": "running",
                    "uptime": 0,  # TODO: Implement actual uptime calculation
                    "memory_usage": 0,  # TODO: Implement actual memory usage
                    "cpu_usage": 0  # TODO: Implement actual CPU usage
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_debug_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug log request."""
        try:
            message = params.get("message")
            level = params.get("level", "info").lower()
            
            if not message:
                raise ValueError("Message must be provided")
                
            log_method = getattr(logger, level, logger.info)
            log_method(f"[DEBUG] {message}")
            
            return {"status": "success", "message": "Logged debug message"}
            
        except Exception as e:
            logger.error(f"Failed to log debug message: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_debug_echo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug echo request."""
        try:
            return {
                "status": "success",
                "echo": params
            }
            
        except Exception as e:
            logger.error(f"Failed to echo: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def start(self) -> None:
        """Start the MCP server."""
        if self.running:
            return
            
        logger.info("Starting AvatarMCP server (FastMCP 2.11.3)")
        self.running = True
        
        # Set up stdio communication
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin,
            asyncio.streams._DUMMY_PIPE
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())
        
        # Process incoming messages
        while self.running:
            try:
                # Read a line from stdin
                line = await reader.readline()
                if not line:
                    break
                    
                # Parse the JSON-RPC message
                try:
                    message = json.loads(line.decode('utf-8').strip())
                    logger.debug(f"Received message: {message}")
                    
                    # Process the message using FastMCP
                    response = await self.mcp.process_message(message)
                    
                    # Send the response if there is one
                    if response:
                        response_json = json.dumps(response) + "\n"
                        writer.write(response_json.encode('utf-8'))
                        await writer.drain()
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        if not self.running:
            return
            
        logger.info("Stopping AvatarMCP server")
        self.running = False
        
        # Stop OSC server
        await self.osc_manager.stop()


async def main():
    """Main entry point for the MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
    
    # Start the server
    server = AvatarMCPServer()
    try:
        await server.start()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        await server.stop()
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
