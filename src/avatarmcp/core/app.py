"""
AvatarMCP - Main application class for managing VRM avatars with FastMCP 2.10.1+ and VRChat OSC
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from fastmcp import FastMCP

from ..models.vrm_model import VRMModel
from ..models.animation_controller import AnimationController
from ..network.osc.vrc_connector import VRChatOSC
from .mcp_server import MCPServer
from .mcp_tools import MCPTools

class AvatarMCP:
    """Main application class for AvatarMCP server."""
    
    def __init__(self):
        """Initialize the AvatarMCP application."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize VRChat OSC connector
        self.osc = VRChatOSC()
        
        # Initialize MCP server
        self.mcp = MCPServer(self)
        
        # Initialize MCP tools
        self.tools = MCPTools(self.mcp, self.osc)
        
        # State
        self.models: Dict[str, VRMModel] = {}
        self.animation_controllers: Dict[str, AnimationController] = {}
        self.running = False
    
    async def start(self):
        """Start the AvatarMCP server."""
        if self.running:
            return
            
        self.logger.info("Starting AvatarMCP server...")
        
        try:
            # Start VRChat OSC
            await self.osc.start()
            
            # Start MCP server
            await self.mcp.start()
            
            self.running = True
            self.logger.info("AvatarMCP server started successfully")
            
            # Keep the server running
            while self.running:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            self.logger.info("Shutting down...")
        except Exception as e:
            self.logger.error(f"Error in server: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the AvatarMCP server."""
        if not self.running:
            return
            
        self.logger.info("Stopping AvatarMCP server...")
        self.running = False
        
        # Stop all animations
        for controller in self.animation_controllers.values():
            controller.stop_all_animations()
        
        # Stop MCP server
        if hasattr(self.mcp, 'stop'):
            await self.mcp.stop()
        
        # Stop OSC
        if hasattr(self.osc, 'stop'):
            await self.osc.stop()
        
        self.logger.info("AvatarMCP server stopped")
    
    async def load_model(self, model_id: str, path: str, scale: float = 1.0) -> Dict[str, Any]:
        """Load a VRM model.
        
        Args:
            model_id: Unique ID for the model
            path: Path to the VRM file
            scale: Scale factor for the model
            
        Returns:
            Information about the loaded model
        """
        if model_id in self.models:
            return {'status': 'error', 'error': f"Model with ID '{model_id}' already exists"}
        
        try:
            model = VRMModel.load(path)
            if scale != 1.0:
                model.scale(scale)
            
            self.models[model_id] = model
            self.animation_controllers[model_id] = AnimationController()
            
            return {
                'status': 'success',
                'model_id': model_id,
                'path': path,
                'scale': scale,
                'bones': len(model.bone_names),
                'blend_shapes': len(model.blend_shape_names)
            }
            
        except Exception as e:
            return {'status': 'error', 'error': f"Failed to load model: {str(e)}"}
    
    async def unload_model(self, model_id: str) -> Dict[str, Any]:
        """Unload a VRM model.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            Confirmation of the unload operation
        """
        if model_id not in self.models:
            return {'status': 'error', 'error': f"No model with ID '{model_id}' is loaded"}
        
        # Stop any running animations
        if model_id in self.animation_controllers:
            del self.animation_controllers[model_id]
        
        # Remove the model
        del self.models[model_id]
        
        return {'status': 'success', 'model_id': model_id}
    
    async def list_models(self) -> Dict[str, Any]:
        """List all loaded models.
        
        Returns:
            Information about all loaded models
        """
        return {
            'status': 'success',
            'models': [
                {
                    'model_id': model_id,
                    'bones': len(model.bone_names),
                    'blend_shapes': len(model.blend_shape_names)
                }
                for model_id, model in self.models.items()
            ]
        }
    
    def get_model(self, model_id: str) -> Tuple[VRMModel, AnimationController]:
        """Get a model and its animation controller.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            Tuple of (model, animation_controller)
            
        Raises:
            ValueError: If model is not found
        """
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
            
        if model_id not in self.animation_controllers:
            self.animation_controllers[model_id] = AnimationController()
            
        return self.models[model_id], self.animation_controllers[model_id]
