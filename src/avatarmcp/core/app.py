"""
AvatarMCP - Main application class for managing VRM avatars with FastMCP 2.10.1+ and VRChat OSC
"""
import asyncio
import logging
import threading
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from fastmcp import FastMCP

from ..models.vrm_model import VRMModel
from ..models.animation_controller import AnimationController
from ..network.osc.vrc_connector import VRChatOSC
from ..visualization.manager import VisualizationManager
from .mcp_server import MCPServer
from .enhanced_mcp_tools import EnhancedMCPTools
from ..visualization.mcp_tools import VisualizationTools

class AvatarMCP:
    """Main application class for AvatarMCP server."""
    
    def __init__(self, enable_visualization: bool = True):
        """Initialize the AvatarMCP application.
        
        Args:
            enable_visualization: Whether to enable 3D visualization
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize VRChat OSC connector
        self.osc = VRChatOSC()
        
        # Initialize MCP server
        self.mcp = MCPServer(self)
        
        # Initialize visualization first if enabled
        self.visualization = None
        if enable_visualization:
            try:
                from ..visualization.manager import VisualizationManager
                from ..visualization.mcp_tools import VisualizationTools
                
                self.visualization = VisualizationManager()
                self.logger.info("3D visualization enabled")
                
                # Initialize enhanced MCP tools with visualization support
                self.tools = EnhancedMCPTools(self.mcp, self.osc)
                # Initialize visualization tools with the enhanced tools
                self.visualization_tools = VisualizationTools(self.mcp, self.osc, self.visualization)
            except ImportError as e:
                self.logger.warning(f"Failed to initialize 3D visualization: {e}")
                self.tools = EnhancedMCPTools(self.mcp, self.osc)
                self.visualization_tools = None
                self.logger.info("3D visualization disabled, using enhanced MCP tools")
        else:
            # Initialize enhanced MCP tools without visualization
            self.tools = EnhancedMCPTools(self.mcp, self.osc)
            self.visualization_tools = None
            self.logger.info("3D visualization disabled, using enhanced MCP tools")
        
        # State
        self.models: Dict[str, VRMModel] = {}
        self.animation_controllers: Dict[str, AnimationController] = {}
        self.running = False
    
    async def start(self, start_visualization: bool = True):
        """Start the AvatarMCP server.
        
        Args:
            start_visualization: Whether to start the 3D visualization window
        """
        if self.running:
            return
            
        self.logger.info("Starting AvatarMCP server...")
        
        try:
            # Start VRChat OSC
            await self.osc.start()
            
            # Start MCP server
            await self.mcp.start()
            
            # Start visualization if enabled
            if self.visualization and start_visualization:
                # Run in a separate thread to avoid blocking the event loop
                def start_visualization_thread():
                    import time
                    # Small delay to ensure MCP server is fully started
                    time.sleep(1.0)
                    self.visualization.start_viewer()
                    
                thread = threading.Thread(target=start_visualization_thread, daemon=True)
                thread.start()
            
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
        
        # Stop visualization
        if hasattr(self, 'visualization') and self.visualization:
            self.visualization.stop_viewer()
        
        # Stop all animations
        for controller in self.animation_controllers.values():
            controller.stop_all_animations()
        
        # Stop MCP server
        if hasattr(self, 'mcp') and self.mcp:
            await self.mcp.stop()
            
        # Stop VRChat OSC
        if hasattr(self, 'osc') and self.osc:
            await self.osc.stop()
            
        self.running = False
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
