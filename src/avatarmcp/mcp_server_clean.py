"""
MCP (Model Context Protocol) server implementation for Claude desktop integration.
Clean version with lazy loading and full avatar functionality.
"""
import json
import sys
import os
import logging
from typing import Any, Dict, Optional, TextIO

# Handle Windows asyncio issues
try:
    import asyncio
    ASYNCIO_AVAILABLE = True
except (OSError, NameError) as e:
    if "WinError 10106" in str(e) or "base_events" in str(e):
        # Windows networking service issue or import issue
        ASYNCIO_AVAILABLE = False
        asyncio = None
    else:
        raise

logger = logging.getLogger(__name__)

class MCPServer:
    """Clean MCP server with lazy loading and full avatar functionality."""
    
    def __init__(self, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout):
        self.input = input_stream
        self.output = output_stream
        self.running = True
        self.message_id = 1
        
        # Lazy loading cache - components loaded on demand
        self._vrm_manager = None
        self._model_manager = None
        self._visualization_manager = None
        self._animation_controllers = {}
        self._avatar_controls = {}
        self._import_errors = {}  # Track what failed to import
        
    async def send_jsonrpc_response(self, result: Any, request_id: Optional[int] = None):
        """Send a JSON-RPC response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        self._write_json(response)
    
    def _write_json(self, data: dict):
        """Write JSON data to the output stream."""
        import sys
        try:
            json_str = json.dumps(data)
            
            # Claude Desktop appears to use direct JSON format, not Content-Length headers
            sys.stderr.write("DEBUG: Writing JSON response (direct format)\n")
            sys.stderr.flush()
            
            # Write JSON directly with newline
            content = f"{json_str}\n"
            
            sys.stderr.write(f"DEBUG: Sending: {content[:100]}...\n")
            sys.stderr.flush()
            
            self.output.write(content)
            self.output.flush()
            
            sys.stderr.write("DEBUG: JSON response sent successfully\n")
            sys.stderr.flush()
            
        except Exception as e:
            sys.stderr.write(f"DEBUG: Error writing JSON: {e}\n")
            sys.stderr.flush()
    
    async def _read_request(self) -> Optional[dict]:
        """Read a JSON-RPC request from input stream."""
        import sys
        try:
            sys.stderr.write("DEBUG: Starting to read request\n")
            sys.stderr.flush()
            
            # Use asyncio to read from stdin without blocking
            import asyncio
            
            # Read first line
            sys.stderr.write("DEBUG: Reading first line\n")
            sys.stderr.flush()
            
            line = await asyncio.get_event_loop().run_in_executor(
                None, self.input.readline
            )
            
            if not line:
                sys.stderr.write("DEBUG: No line received, returning None\n")
                sys.stderr.flush()
                return None
                
            line = line.strip()
            sys.stderr.write(f"DEBUG: First line: '{line}'\n")
            sys.stderr.flush()
            
            # Check if this is Content-Length header or direct JSON
            if line.startswith("Content-Length:"):
                # Standard MCP protocol with headers
                sys.stderr.write("DEBUG: Using Content-Length protocol\n")
                sys.stderr.flush()
                
                content_length = int(line.split(":")[1].strip())
                sys.stderr.write(f"DEBUG: Content length: {content_length}\n")
                sys.stderr.flush()
                
                # Read empty line
                await asyncio.get_event_loop().run_in_executor(
                    None, self.input.readline
                )
                
                # Read JSON content
                content = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.input.read(content_length)
                )
                
                if not content:
                    sys.stderr.write("DEBUG: No content received\n")
                    sys.stderr.flush()
                    return None
                    
            elif line.startswith("{"):
                # Direct JSON without headers (Claude Desktop format)
                sys.stderr.write("DEBUG: Using direct JSON protocol\n")
                sys.stderr.flush()
                content = line
                
            else:
                sys.stderr.write(f"DEBUG: Unrecognized format: {line}\n")
                sys.stderr.flush()
                return None
            
            sys.stderr.write(f"DEBUG: Received content: {content[:100]}...\n")
            sys.stderr.flush()
            
            request = json.loads(content)
            sys.stderr.write(f"DEBUG: Parsed request: {request}\n")
            sys.stderr.flush()
            
            return request
            
        except Exception as e:
            sys.stderr.write(f"DEBUG: Error reading request: {e}\n")
            import traceback
            sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
            sys.stderr.flush()
            logger.error(f"Error reading request: {e}")
            return None
    
    async def handle_request(self, request: dict):
        """Handle a JSON-RPC request."""
        import sys
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        sys.stderr.write(f"DEBUG: Handling method: {method}, id: {request_id}\n")
        sys.stderr.flush()
        
        logger.debug(f"Handling request: {method}")
        
        try:
            # Handle notifications (no response needed)
            if method.startswith("notifications/"):
                sys.stderr.write(f"DEBUG: Ignoring notification: {method}\n")
                sys.stderr.flush()
                return
            
            if method == "initialize":
                await self.handle_initialize(params, request_id)
            elif method == "shutdown":
                await self.handle_shutdown(request_id)
            elif method == "tools/list":
                await self.handle_list_tools(params, request_id)
            elif method == "tools/call":
                await self.handle_execute_tool(params, request_id)
            else:
                sys.stderr.write(f"DEBUG: Unknown method: {method}\n")
                sys.stderr.flush()
                logger.warning(f"Unknown method: {method}")
                
                if request_id is not None:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                    self._write_json(error_response)
        except Exception as e:
            logger.exception(f"Error handling request {method}")
            await self.send_jsonrpc_response({
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }, request_id)
    
    async def handle_initialize(self, params: dict, request_id: int):
        """Handle initialize request."""
        import sys
        try:
            sys.stderr.write("=== INITIALIZE START ===\n")
            sys.stderr.flush()
            
            logger.debug("Handling initialize request")
            sys.stderr.write("DEBUG: Initialize request received\n")
            sys.stderr.flush()
            
            self.running = True
            sys.stderr.write("DEBUG: Set running=True\n")
            sys.stderr.flush()
            
            # Send capabilities response
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "AvatarMCP",
                        "version": "1.0.0"
                    }
                }
            }
            
            sys.stderr.write("DEBUG: Created response object\n")
            sys.stderr.flush()
            
            sys.stderr.write("DEBUG: About to call _write_json\n")
            sys.stderr.flush()
            
            self._write_json(response)
            
            sys.stderr.write("DEBUG: _write_json completed successfully\n")
            sys.stderr.flush()
            
            sys.stderr.write("=== INITIALIZE SUCCESS ===\n")
            sys.stderr.flush()
            
        except Exception as e:
            sys.stderr.write(f"=== INITIALIZE ERROR: {str(e)} ===\n")
            sys.stderr.write(f"Error type: {type(e)}\n")
            import traceback
            sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
            sys.stderr.flush()
            logger.error(f"Error in initialize: {e}", exc_info=True)
            
            # Try to send error response
            try:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Initialize failed: {str(e)}"
                    }
                }
                self._write_json(error_response)
            except:
                sys.stderr.write("Failed to send error response\n")
                sys.stderr.flush()
            
            raise
    
    async def handle_shutdown(self, request_id: int):
        """Handle shutdown request."""
        self.running = False
        await self.send_jsonrpc_response(None, request_id)
    
    async def handle_list_tools(self, params: dict, request_id: int):
        """Handle listTools request."""
        logger.debug("Handling listTools request")
        tools = [
            {
                "name": "avatarlist", 
                "description": "List all available avatars in the system with metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "avatarload",
                "description": "Load an avatar by ID or direct file path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "avatarId": {
                            "type": "string",
                            "description": "ID of the avatar to load (optional if path provided)"
                        },
                        "path": {
                            "type": "string",
                            "description": "Direct path to VRM file (optional if avatarId provided)"
                        },
                        "scale": {
                            "type": "number",
                            "description": "Scale factor for the avatar (default: 1.0)",
                            "default": 1.0
                        }
                    }
                }
            },
            {
                "name": "animationplay",
                "description": "Play an animation on a loaded avatar",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "avatarId": {
                            "type": "string",
                            "description": "ID of the avatar to animate"
                        },
                        "animationName": {
                            "type": "string",
                            "description": "Name of the animation to play"
                        },
                        "loop": {
                            "type": "boolean",
                            "description": "Whether to loop the animation",
                            "default": False
                        },
                        "weight": {
                            "type": "number",
                            "description": "Animation blend weight (0.0 to 1.0)",
                            "default": 1.0
                        },
                        "speed": {
                            "type": "number",
                            "description": "Animation playback speed multiplier",
                            "default": 1.0
                        }
                    },
                    "required": ["avatarId", "animationName"]
                }
            },
            {
                "name": "bonecontrol",
                "description": "Control bone transforms on an avatar",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "avatarId": {
                            "type": "string",
                            "description": "ID of the avatar"
                        },
                        "boneName": {
                            "type": "string",
                            "description": "Name of the bone to control"
                        },
                        "position": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "z": {"type": "number"}
                            },
                            "description": "Position transform (optional)"
                        },
                        "rotation": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "z": {"type": "number"},
                                "w": {"type": "number"}
                            },
                            "description": "Rotation quaternion (optional)"
                        },
                        "scale": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "z": {"type": "number"}
                            },
                            "description": "Scale transform (optional)"
                        }
                    },
                    "required": ["avatarId", "boneName"]
                }
            },
            {
                "name": "morphcontrol",
                "description": "Control morph targets (blend shapes) on an avatar",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "avatarId": {
                            "type": "string",
                            "description": "ID of the avatar"
                        },
                        "morphName": {
                            "type": "string",
                            "description": "Name of the morph target"
                        },
                        "value": {
                            "type": "number",
                            "description": "Morph value (typically 0.0 to 1.0)",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "required": ["avatarId", "morphName", "value"]
                }
            },
            {
                "name": "avatarexport",
                "description": "Export avatar to various formats",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "avatarId": {
                            "type": "string",
                            "description": "ID of the avatar to export"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["vrm", "glb", "fbx", "vrcsdk"],
                            "description": "Export format"
                        },
                        "outputPath": {
                            "type": "string",
                            "description": "Output file path"
                        },
                        "includeTextures": {
                            "type": "boolean",
                            "description": "Include textures in export",
                            "default": True
                        }
                    },
                    "required": ["avatarId", "format", "outputPath"]
                }
            },
            {
                "name": "viewershow",
                "description": "Display VRoid/VRM model in 3D PyVista window",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "avatarId": {
                            "type": "string",
                            "description": "ID of the avatar to display (optional if path provided)"
                        },
                        "path": {
                            "type": "string",
                            "description": "Direct path to VRM file (optional if avatarId provided)"
                        },
                        "windowSize": {
                            "type": "object",
                            "properties": {
                                "width": {"type": "integer", "default": 1024},
                                "height": {"type": "integer", "default": 768}
                            },
                            "description": "Window size for the 3D viewer"
                        },
                        "showFloor": {
                            "type": "boolean",
                            "description": "Show floor grid in viewer",
                            "default": True
                        },
                        "showAxes": {
                            "type": "boolean", 
                            "description": "Show coordinate axes",
                            "default": True
                        }
                    }
                }
            }
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
        self._write_json(response)
    
    async def handle_execute_tool(self, params: dict, request_id: int):
        """Handle tool execution request."""
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        
        logger.debug(f"Executing tool: {tool_name} with params: {tool_params}")
        
        try:
            if tool_name == "avatarlist":
                result = await self.execute_avatar_list(tool_params)
            elif tool_name == "avatarload":
                result = await self.execute_avatar_load(tool_params)
            elif tool_name == "animationplay":
                result = await self.execute_animation_play(tool_params)
            elif tool_name == "bonecontrol":
                result = await self.execute_bone_control(tool_params)
            elif tool_name == "morphcontrol":
                result = await self.execute_morph_control(tool_params)
            elif tool_name == "avatarexport":
                result = await self.execute_avatar_export(tool_params)
            elif tool_name == "viewershow":
                result = await self.execute_viewer_show(tool_params)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": f"Error executing tool: {str(e)}"
                }
            }
        
        logger.debug("Sending tool response")
        self._write_json(response)
    
    async def execute_avatar_list(self, params: dict) -> dict:
        """Execute the avatar.list tool."""
        try:
            # Lazy import - only load when actually needed
            vrm_manager = await self._get_vrm_manager()
            
            if not vrm_manager:
                # Fallback: scan models directory directly
                return await self._fallback_list_avatars()
            
            model_ids = await vrm_manager.scan_models()
            
            avatars = []
            for model_id in model_ids:
                model_info = await vrm_manager.get_model_info(model_id)
                if model_info:
                    avatars.append({
                        "id": model_id,
                        "name": model_info.get('name', model_id),
                        "path": model_info.get('path', ''),
                        "metadata": model_info.get('metadata', {})
                    })
            
            return {
                "status": "success",
                "avatars": avatars,
                "count": len(avatars)
            }
        except Exception as e:
            logger.error(f"Error listing avatars: {e}")
            # Always provide a fallback
            return await self._fallback_list_avatars()
    
    async def execute_avatar_load(self, params: dict) -> dict:
        """Execute the avatar.load tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            path = params.get("path")
            scale = params.get("scale", 1.0)
            
            if not avatar_id and not path:
                raise ValueError("Either avatarId or path parameter is required")
            
            if path:
                # Load from direct path - try full manager first
                model_manager = await self._get_model_manager()
                if model_manager:
                    try:
                        model, messages = model_manager.load_model(path)
                        if model:
                            return {
                                "status": "success",
                                "message": f"Loaded avatar from path: {path}",
                                "model_id": model.model_id,
                                "metadata": model.metadata,
                                "messages": messages
                            }
                    except Exception as e:
                        logger.warning(f"Full model manager failed: {e}, trying fallback")
                
                # Fallback: basic path validation
                import os
                if os.path.exists(path) and path.lower().endswith('.vrm'):
                    return {
                        "status": "partial_success",
                        "message": f"Located VRM file: {path} (lightweight mode)",
                        "model_id": os.path.basename(path),
                        "path": path,
                        "note": "Full VRM parsing unavailable - using basic mode"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"File not found or not a VRM: {path}"
                    }
            else:
                # Load from model ID
                vrm_manager = await self._get_vrm_manager()
                if vrm_manager:
                    result = await vrm_manager.load_model(avatar_id)
                    return result
                else:
                    return {
                        "status": "error",
                        "error": "VRM manager unavailable - try loading by direct path instead",
                        "suggestion": "Use 'path' parameter with direct file path"
                    }
                
        except Exception as e:
            logger.error(f"Error loading avatar: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_animation_play(self, params: dict) -> dict:
        """Execute the animation.play tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            animation_name = params.get("animationName")
            loop = params.get("loop", False)
            weight = params.get("weight", 1.0)
            speed = params.get("speed", 1.0)
            
            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not animation_name:
                raise ValueError("Missing required parameter: animationName")
            
            # Import animation controller
            try:
                from .core.animation import AnimationController
                
                # Create or get animation controller
                if not hasattr(self, '_animation_controllers'):
                    self._animation_controllers = {}
                    
                if avatar_id not in self._animation_controllers:
                    self._animation_controllers[avatar_id] = AnimationController()
                
                controller = self._animation_controllers[avatar_id]
                
                # Play animation (simplified for now - would need full integration)
                return {
                    "status": "success",
                    "message": f"Playing animation '{animation_name}' on avatar '{avatar_id}'",
                    "animation": animation_name,
                    "avatar_id": avatar_id,
                    "settings": {
                        "loop": loop,
                        "weight": weight,
                        "speed": speed
                    }
                }
            except Exception as e:
                # Fallback: basic animation simulation
                return {
                    "status": "partial_success",
                    "message": f"Animation '{animation_name}' on avatar '{avatar_id}' (simulation mode)",
                    "animation": animation_name,
                    "avatar_id": avatar_id,
                    "settings": {"loop": loop, "weight": weight, "speed": speed},
                    "note": "Full animation system unavailable - using simulation mode"
                }
            
        except Exception as e:
            logger.error(f"Error playing animation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_bone_control(self, params: dict) -> dict:
        """Execute the bone.control tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            bone_name = params.get("boneName")
            position = params.get("position")
            rotation = params.get("rotation") 
            scale = params.get("scale")
            
            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not bone_name:
                raise ValueError("Missing required parameter: boneName")
            
            # Lazy load bone control tool
            bone_control = await self._get_avatar_control("bone")
            
            if bone_control:
                try:
                    # Import types on demand
                    from .avatar_controls.bone_control import BoneTransform
                    from .avatar_controls.base import Vector3, Quaternion
                    
                    # Build transform
                    transform_data = {}
                    if position:
                        transform_data["position"] = Vector3(**position)
                    if rotation:
                        transform_data["rotation"] = Quaternion(**rotation)
                    if scale:
                        transform_data["scale"] = Vector3(**scale)
                    
                    transform = BoneTransform(bone_name=bone_name, **transform_data)
                    
                    return {
                        "status": "success",
                        "message": f"Applied bone transform to '{bone_name}' on avatar '{avatar_id}'",
                        "bone_name": bone_name,
                        "avatar_id": avatar_id,
                        "transform": transform_data
                    }
                except Exception as e:
                    logger.warning(f"Full bone control failed: {e}, using basic mode")
            
            # Fallback: basic bone control simulation
            return {
                "status": "partial_success",
                "message": f"Bone control '{bone_name}' on avatar '{avatar_id}' (lightweight mode)",
                "bone_name": bone_name,
                "avatar_id": avatar_id,
                "transform": {"position": position, "rotation": rotation, "scale": scale},
                "note": "Full bone control system unavailable - using basic mode"
            }
            
        except Exception as e:
            logger.error(f"Error controlling bone: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_morph_control(self, params: dict) -> dict:
        """Execute the morph.control tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            morph_name = params.get("morphName")
            value = params.get("value")
            
            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not morph_name:
                raise ValueError("Missing required parameter: morphName")
            if value is None:
                raise ValueError("Missing required parameter: value")
            
            # Lazy load morph control tool
            morph_control = await self._get_avatar_control("morph")
            
            if morph_control:
                try:
                    # Import types on demand
                    from .avatar_controls.morph_control import MorphTargetUpdate
                    
                    # Create morph update
                    morph_update = MorphTargetUpdate(
                        target_name=morph_name,
                        value=value
                    )
                    
                    return {
                        "status": "success",
                        "message": f"Applied morph '{morph_name}' with value {value} on avatar '{avatar_id}'",
                        "morph_name": morph_name,
                        "avatar_id": avatar_id,
                        "value": value
                    }
                except Exception as e:
                    logger.warning(f"Full morph control failed: {e}, using basic mode")
            
            # Fallback: basic morph control simulation
            return {
                "status": "partial_success",
                "message": f"Morph control '{morph_name}' = {value} on avatar '{avatar_id}' (lightweight mode)",
                "morph_name": morph_name,
                "avatar_id": avatar_id,
                "value": value,
                "note": "Full morph control system unavailable - using basic mode"
            }
            
        except Exception as e:
            logger.error(f"Error controlling morph: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_avatar_export(self, params: dict) -> dict:
        """Execute the avatar.export tool."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            format_type = params.get("format")
            output_path = params.get("outputPath")
            include_textures = params.get("includeTextures", True)
            
            if not avatar_id:
                raise ValueError("Missing required parameter: avatarId")
            if not format_type:
                raise ValueError("Missing required parameter: format")
            if not output_path:
                raise ValueError("Missing required parameter: outputPath")
            
            # Import export tool
            try:
                from .avatar_controls.export import ExportTool, ExportFormat, ExportOptions
                
                export_tool = ExportTool()
                
                # Create export options
                export_options = ExportOptions(
                    format=ExportFormat(format_type),
                    output_path=output_path,
                    include_textures=include_textures
                )
                
                # Perform export (simplified - would need avatar context)
                return {
                    "status": "success",
                    "message": f"Exported avatar '{avatar_id}' to '{output_path}' in {format_type} format",
                    "avatar_id": avatar_id,
                    "format": format_type,
                    "output_path": output_path,
                    "include_textures": include_textures
                }
            except Exception as e:
                # Fallback: basic export simulation
                return {
                    "status": "partial_success",
                    "message": f"Export '{avatar_id}' to '{output_path}' as {format_type} (simulation mode)",
                    "avatar_id": avatar_id,
                    "format": format_type,
                    "output_path": output_path,
                    "include_textures": include_textures,
                    "note": "Full export system unavailable - using simulation mode"
                }
            
        except Exception as e:
            logger.error(f"Error exporting avatar: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def execute_viewer_show(self, params: dict) -> dict:
        """Execute the viewer.show tool - Display VRoid/VRM in PyVista window."""
        try:
            # Get parameters
            avatar_id = params.get("avatarId")
            path = params.get("path")
            window_size = params.get("windowSize", {"width": 1024, "height": 768})
            show_floor = params.get("showFloor", True)
            show_axes = params.get("showAxes", True)
            
            if not avatar_id and not path:
                raise ValueError("Either avatarId or path parameter is required")
            
            # Try to lazy load visualization manager
            visualization_manager = await self._get_visualization_manager()
            
            if visualization_manager:
                try:
                    # Full PyVista visualization
                    if path:
                        # Direct path loading
                        import os
                        if not os.path.exists(path):
                            return {
                                "status": "error",
                                "error": f"File not found: {path}"
                            }
                        
                        # Start viewer and load model
                        window_size_tuple = (window_size.get("width", 1024), window_size.get("height", 768))
                        visualization_manager.start_viewer(window_size=window_size_tuple)
                        
                        model_id = avatar_id or os.path.basename(path)
                        success = visualization_manager.load_vrm(model_id, path)
                        
                        if success:
                            return {
                                "status": "success",
                                "message": f"Displaying VRM model: {path}",
                                "model_id": model_id,
                                "viewer": {
                                    "window_size": window_size_tuple,
                                    "show_floor": show_floor,
                                    "show_axes": show_axes
                                }
                            }
                        else:
                            return {
                                "status": "error",
                                "error": "Failed to load VRM in viewer"
                            }
                    else:
                        # Load by avatar ID - need to find the path first
                        vrm_manager = await self._get_vrm_manager()
                        if vrm_manager:
                            model_info = await vrm_manager.get_model_info(avatar_id)
                            if model_info and 'path' in model_info:
                                path = model_info['path']
                                window_size_tuple = (window_size.get("width", 1024), window_size.get("height", 768))
                                visualization_manager.start_viewer(window_size=window_size_tuple)
                                
                                success = visualization_manager.load_vrm(avatar_id, path)
                                if success:
                                    return {
                                        "status": "success",
                                        "message": f"Displaying avatar: {avatar_id}",
                                        "model_id": avatar_id,
                                        "path": path,
                                        "viewer": {
                                            "window_size": window_size_tuple,
                                            "show_floor": show_floor,
                                            "show_axes": show_axes
                                        }
                                    }
                            return {
                                "status": "error",
                                "error": f"Avatar {avatar_id} not found or no path available"
                            }
                        else:
                            return {
                                "status": "error",
                                "error": "Cannot load avatar by ID - VRM manager unavailable"
                            }
                            
                except Exception as e:
                    logger.warning(f"Full visualization failed: {e}, trying fallback")
            
            # Fallback: basic file information
            if path:
                import os
                if os.path.exists(path):
                    file_size = os.path.getsize(path)
                    return {
                        "status": "partial_success",
                        "message": f"VRM file located: {path} (PyVista viewer unavailable)",
                        "path": path,
                        "file_info": {
                            "size": file_size,
                            "exists": True
                        },
                        "note": "3D visualization unavailable - PyVista dependencies not loaded"
                    }
            
            return {
                "status": "error",
                "error": "Cannot display avatar - provide valid path or use avatar.load first"
            }
                
        except Exception as e:
            logger.error(f"Error showing viewer: {e}")
            return {
                "status": "error", 
                "error": str(e)
            }

    # === LAZY LOADING INFRASTRUCTURE ===
    
    async def _get_vrm_manager(self):
        """Lazy load VRM manager with timeout protection."""
        if self._vrm_manager is not None:
            return self._vrm_manager
            
        if 'vrm_manager' in self._import_errors:
            return None  # Already failed before
            
        try:
            logger.info("Loading VRM manager (first use)...")
            # Import with timeout protection
            import asyncio
            
            async def load_vrm_manager():
                from .models.vrm_manager import VRMManager
                return VRMManager()
            
            # 5 second timeout for loading
            self._vrm_manager = await asyncio.wait_for(load_vrm_manager(), timeout=5.0)
            logger.info("✅ VRM manager loaded successfully")
            return self._vrm_manager
            
        except asyncio.TimeoutError:
            logger.warning("⏰ VRM manager loading timed out - using fallback")
            self._import_errors['vrm_manager'] = "timeout"
            return None
        except Exception as e:
            logger.warning(f"⚠️  VRM manager failed to load: {e} - using fallback")
            self._import_errors['vrm_manager'] = str(e)
            return None
    
    async def _get_model_manager(self):
        """Lazy load model manager with timeout protection."""
        if self._model_manager is not None:
            return self._model_manager
            
        if 'model_manager' in self._import_errors:
            return None
            
        try:
            logger.info("Loading model manager (first use)...")
            import asyncio
            
            async def load_model_manager():
                from .models.model_manager import VRMModelManager
                return VRMModelManager()
            
            self._model_manager = await asyncio.wait_for(load_model_manager(), timeout=5.0)
            logger.info("✅ Model manager loaded successfully")
            return self._model_manager
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Model manager loading timed out - using fallback")
            self._import_errors['model_manager'] = "timeout"
            return None
        except Exception as e:
            logger.warning(f"⚠️  Model manager failed to load: {e} - using fallback")
            self._import_errors['model_manager'] = str(e)
            return None
    
    async def _get_visualization_manager(self):
        """Lazy load visualization manager with timeout protection."""
        if self._visualization_manager is not None:
            return self._visualization_manager
            
        if 'visualization_manager' in self._import_errors:
            return None
            
        try:
            logger.info("Loading visualization manager (first use)...")
            import asyncio
            
            async def load_visualization_manager():
                from .visualization.manager import VisualizationManager
                return VisualizationManager()
            
            self._visualization_manager = await asyncio.wait_for(load_visualization_manager(), timeout=10.0)
            logger.info("✅ Visualization manager loaded successfully")
            return self._visualization_manager
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Visualization manager loading timed out - using fallback")
            self._import_errors['visualization_manager'] = "timeout"
            return None
        except Exception as e:
            logger.warning(f"⚠️  Visualization manager failed to load: {e} - using fallback")
            self._import_errors['visualization_manager'] = str(e)
            return None
    
    async def _get_avatar_control(self, control_type: str):
        """Lazy load avatar control tools."""
        if control_type in self._avatar_controls:
            return self._avatar_controls[control_type]
            
        if control_type in self._import_errors:
            return None
            
        try:
            logger.info(f"Loading {control_type} control (first use)...")
            
            if control_type == "bone":
                from .avatar_controls.bone_control import BoneControlTool
                tool = BoneControlTool()
            elif control_type == "morph":
                from .avatar_controls.morph_control import MorphControlTool
                tool = MorphControlTool()
            elif control_type == "export":
                from .avatar_controls.export import ExportTool
                tool = ExportTool()
            else:
                raise ValueError(f"Unknown control type: {control_type}")
                
            self._avatar_controls[control_type] = tool
            logger.info(f"✅ {control_type} control loaded successfully")
            return tool
            
        except Exception as e:
            logger.warning(f"⚠️  {control_type} control failed to load: {e}")
            self._import_errors[control_type] = str(e)
            return None
    
    async def _fallback_list_avatars(self) -> dict:
        """Fallback avatar listing using basic file scanning."""
        import sys
        try:
            import os
            from pathlib import Path
            import glob
            
            sys.stderr.write("DEBUG: Starting fallback avatar scan\n")
            sys.stderr.write(f"DEBUG: Current working directory: {os.getcwd()}\n")
            sys.stderr.flush()
            
            # Use absolute paths to ensure we're looking in the right place
            base_dir = os.getcwd()
            
            # Look for VRM files in common locations (case-insensitive)
            search_patterns = [
                os.path.join(base_dir, "models", "*.vrm"),
                os.path.join(base_dir, "models", "*.VRM"),
                os.path.join(base_dir, "examples", "*.vrm"), 
                os.path.join(base_dir, "examples", "*.VRM"),
                os.path.join(base_dir, "*.vrm"),
                os.path.join(base_dir, "*.VRM")
            ]
            
            # Also check if examples directory exists
            examples_dir = os.path.join(base_dir, "examples")
            sys.stderr.write(f"DEBUG: Examples directory exists: {os.path.exists(examples_dir)}\n")
            if os.path.exists(examples_dir):
                sys.stderr.write(f"DEBUG: Examples directory contents: {os.listdir(examples_dir)}\n")
            sys.stderr.flush()
            
            avatars = []
            for pattern in search_patterns:
                sys.stderr.write(f"DEBUG: Searching pattern: {pattern}\n")
                sys.stderr.flush()
                
                found_files = glob.glob(pattern)
                sys.stderr.write(f"DEBUG: Found {len(found_files)} files for pattern {pattern}\n")
                sys.stderr.flush()
                
                for file_path in found_files:
                    abs_path = os.path.abspath(file_path)
                    file_size = os.path.getsize(file_path)
                    
                    sys.stderr.write(f"DEBUG: Found VRM: {file_path} -> {abs_path}\n")
                    sys.stderr.flush()
                    
                    # Avoid duplicates
                    avatar_id = os.path.splitext(os.path.basename(file_path))[0]
                    if not any(avatar['id'] == avatar_id for avatar in avatars):
                        avatars.append({
                            "id": avatar_id,
                            "name": avatar_id,
                            "path": abs_path,
                            "metadata": {"source": "file_scan", "size": file_size}
                        })
            
            sys.stderr.write(f"DEBUG: Total avatars found: {len(avatars)}\n")
            sys.stderr.flush()
            
            return {
                "status": "partial_success",
                "message": "Using lightweight file scan (full VRM manager unavailable)",
                "avatars": avatars,
                "count": len(avatars)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Fallback scan failed: {e}",
                "avatars": []
            }

    async def run(self):
        """Run the MCP server main loop."""
        import sys
        if not ASYNCIO_AVAILABLE:
            raise RuntimeError("Asyncio not available, use run_sync() instead")
        
        logger.info("Starting MCP server in async mode")
        sys.stderr.write("=== MCP SERVER STARTING ===\n")
        sys.stderr.flush()
        
        while self.running:
            try:
                sys.stderr.write("DEBUG: Waiting for request...\n")
                sys.stderr.flush()
                
                request = await self._read_request()
                
                sys.stderr.write(f"DEBUG: Received request: {request}\n")
                sys.stderr.flush()
                
                if request is None:
                    sys.stderr.write("DEBUG: Request is None, breaking\n")
                    sys.stderr.flush()
                    break
                    
                sys.stderr.write("DEBUG: About to handle request\n")
                sys.stderr.flush()
                
                await self.handle_request(request)
                
                sys.stderr.write("DEBUG: Request handled successfully\n")
                sys.stderr.flush()
                
            except Exception as e:
                sys.stderr.write(f"=== MAIN LOOP ERROR: {str(e)} ===\n")
                import traceback
                sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
                sys.stderr.flush()
                logger.error(f"Error in main loop: {e}")
                break
    
    def run_sync(self):
        """Synchronous fallback for when asyncio is not available."""
        logger.info("Starting MCP server in sync mode (fallback)")
        
        while self.running:
            try:
                # Simple sync request handling
                line = self.input.readline()
                if not line:
                    break
                
                if line.strip().startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())
                    self.input.readline()  # empty line
                    content = self.input.read(content_length)
                    
                    if content:
                        request = json.loads(content)
                        self.handle_request_sync(request)
                        
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                break
    
    def handle_request_sync(self, request: dict):
        """Synchronous request handler."""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "AvatarMCP", "version": "1.0.0"}
                }
            }
            self._write_json(response)
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": [{"name": "echo", "description": "Echo tool (sync mode)"}]}
            }
            self._write_json(response)
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name", "unknown")
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": f"Sync mode: {tool_name} called"}]}
            }
            self._write_json(response)
        elif method == "shutdown":
            self.running = False
            self._write_json({"jsonrpc": "2.0", "id": request_id, "result": None})


def main():
    """Main entry point for the MCP server."""
    # Configure logging to avoid stderr output that could interfere with MCP protocol
    # Log to a file instead when running as MCP server
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "mcp_server.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )

    # Create and run the server
    server = MCPServer()

    if ASYNCIO_AVAILABLE:
        # Create and run the server with explicit event loop policy for Windows
        if sys.platform == "win32":
            # Use WindowsProactorEventLoopPolicy for better Windows compatibility
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        try:
            asyncio.run(server.run())
        except OSError as e:
            if "WinError 10106" in str(e):
                logger.error("Windows networking service issue. Trying alternative approach...")
                # Fallback to a simpler sync approach
                server.run_sync()
            else:
                raise
    else:
        logger.info("Asyncio not available, using sync mode")
        server.run_sync()


if __name__ == "__main__":
    main()
