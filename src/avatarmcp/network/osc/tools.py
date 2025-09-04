"""
OSC Tools for VRChat Avatar Control

This module provides MCP tools for controlling VRChat avatars using OSC.
It builds on top of the existing OSC server and integration code.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from fastmcp import FastMCP, mcp_tool
from ..network.osc.server import VRChatOSCServer
from ..network.mcp.integration import AvatarOSCIntegrator, AvatarOSCConfig

logger = logging.getLogger(__name__)

# Default OSC configuration
DEFAULT_OSC_CONFIG = {
    "receive_port": 9000,
    "send_port": 9001,
    "server_ip": "127.0.0.1"
}

class VRChatOSCTools:
    """MCP tools for VRChat OSC control."""
    
    def __init__(self, mcp: FastMCP, config: Optional[Dict[str, Any]] = None):
        """Initialize the VRChat OSC tools.
        
        Args:
            mcp: The FastMCP instance to register tools with
            config: Optional configuration dictionary
        """
        self.mcp = mcp
        self.config = {**DEFAULT_OSC_CONFIG, **(config or {})}
        self.osc_integrator: Optional[AvatarOSCIntegrator] = None
        self.osc_server: Optional[VRChatOSCServer] = None
        self._running = False
        
        # Register MCP tools
        self._register_tools()
    
    async def start(self):
        """Start the OSC server and integrator."""
        if self._running:
            return
            
        # Create and start the OSC server
        self.osc_server = VRChatOSCServer(
            ip=self.config["server_ip"],
            receive_port=self.config["receive_port"],
            send_port=self.config["send_port"]
        )
        
        # Create and start the OSC integrator
        osc_config = AvatarOSCConfig(
            receive_port=self.config["receive_port"],
            send_port=self.config["send_port"],
            server_ip=self.config["server_ip"]
        )
        
        self.osc_integrator = AvatarOSCIntegrator(self.mcp, osc_config)
        await self.osc_integrator.start()
        
        self._running = True
        logger.info("VRChat OSC Tools started")
    
    async def stop(self):
        """Stop the OSC server and integrator."""
        if not self._running:
            return
            
        if self.osc_integrator:
            await self.osc_integrator.stop()
            
        self._running = False
        logger.info("VRChat OSC Tools stopped")
    
    def _register_tools(self):
        """Register MCP tools for OSC control."""
        
        @mcp_tool("vrchat_osc.set_gesture")
        async def set_gesture(hand: str, gesture: str, strength: float = 1.0) -> Dict[str, Any]:
            """Set a hand gesture for the avatar.
            
            Args:
                hand: 'left' or 'right'
                gesture: Gesture name (e.g., 'Fist', 'Open', 'Point', etc.)
                strength: Gesture strength (0.0 to 1.0, default: 1.0)
                
            Returns:
                Dict with status and message
            """
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                await self.osc_integrator.set_gesture(hand, gesture, strength)
                return {"status": "success", "message": f"Set {hand} hand to {gesture}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp_tool("vrchat_osc.set_expression")
        async def set_expression(expression: str, strength: float = 1.0) -> Dict[str, Any]:
            """Set a facial expression for the avatar.
            
            Args:
                expression: Expression name (e.g., 'Happy', 'Angry', 'Blink', etc.)
                strength: Expression strength (0.0 to 1.0, default: 1.0)
                
            Returns:
                Dict with status and message
            """
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                await self.osc_integrator.set_expression(expression, strength)
                return {"status": "success", "message": f"Set expression to {expression}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp_tool("vrchat_osc.set_viseme")
        async def set_viseme(viseme: str, strength: float = 1.0) -> Dict[str, Any]:
            """Set a viseme for lip sync.
            
            Args:
                viseme: Viseme name (e.g., 'aa', 'E', 'O', etc.)
                strength: Viseme strength (0.0 to 1.0, default: 1.0)
                
            Returns:
                Dict with status and message
            """
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                await self.osc_integrator.set_viseme(viseme, strength)
                return {"status": "success", "message": f"Set viseme to {viseme}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp_tool("vrchat_osc.set_parameter")
        async def set_parameter(name: str, value: Any) -> Dict[str, Any]:
            """Set a custom parameter on the avatar.
            
            Args:
                name: Parameter name
                value: Parameter value (int, float, or bool)
                
            Returns:
                Dict with status and message
            """
            if not self._running or not self.osc_integrator or not self.osc_server:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                # Convert value to appropriate type
                if isinstance(value, str):
                    if value.lower() in ('true', 'false', 't', 'f'):
                        value = value.lower() in ('true', 't')
                    else:
                        try:
                            value = float(value)
                            if value.is_integer():
                                value = int(value)
                        except ValueError:
                            pass
                
                # Set the parameter
                self.osc_server.set_parameter(name, value)
                return {"status": "success", "message": f"Set {name} to {value}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp_tool("vrchat_osc.get_parameter")
        async def get_parameter(name: str) -> Dict[str, Any]:
            """Get the current value of a parameter.
            
            Args:
                name: Parameter name
                
            Returns:
                Dict with status, message, and value if successful
            """
            if not self._running or not self.osc_server:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                value = self.osc_server.get_parameter(name)
                if value is None:
                    return {"status": "not_found", "message": f"Parameter {name} not found"}
                return {"status": "success", "value": value}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @mcp_tool("vrchat_osc.list_parameters")
        async def list_parameters() -> Dict[str, Any]:
            """List all available parameters.
            
            Returns:
                Dict with status and list of parameters
            """
            # This would need to be populated based on the actual parameters
            # available in the current avatar
            standard_params = [
                "GestureLeft", "GestureRight", "GestureLeftWeight", "GestureRightWeight",
                "Viseme", "VisemeWeight", "Voice", "VoiceVolume", "IsLocal"
            ]
            
            # Add expression parameters
            expressions = [
                "Neutral", "Happy", "Angry", "Sad", "Surprised", "Blink", "BlinkLeft",
                "BlinkRight", "EyesWide", "Squint", "LookDown", "LookLeft", "LookRight", "LookUp"
            ]
            
            # Add any custom parameters from the config
            custom_params = []
            if self.osc_integrator and self.osc_integrator.config.parameter_mappings:
                custom_params = list(self.osc_integrator.config.parameter_mappings.keys())
            
            return {
                "status": "success",
                "parameters": {
                    "standard": standard_params,
                    "expressions": expressions,
                    "custom": custom_params
                }
            }
        
        @mcp_tool("vrchat_osc.load_vrm")
        async def load_vrm(file_path: str) -> Dict[str, Any]:
            """Load a VRM model and extract parameters.
            
            Args:
                file_path: Path to the VRM file
                
            Returns:
                Dict with status and loaded VRM info
            """
            if not self._running or not self.osc_integrator:
                return {"status": "error", "message": "OSC tools not initialized"}
                
            try:
                vrm_loader = self.osc_integrator.load_vrm(file_path)
                if not vrm_loader:
                    return {"status": "error", "message": "Failed to load VRM file"}
                
                # Get blend shapes and bones
                blend_shapes = vrm_loader.get_blend_shape_names()
                bones = vrm_loader.get_bone_names()
                
                return {
                    "status": "success",
                    "blend_shapes": blend_shapes,
                    "bones": bones,
                    "message": f"Loaded VRM: {file_path}"
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        # Register the tool functions as instance methods
        self.set_gesture = set_gesture
        self.set_expression = set_expression
        self.set_viseme = set_viseme
        self.set_parameter = set_parameter
        self.get_parameter = get_parameter
        self.list_parameters = list_parameters
        self.load_vrm = load_vrm


# Example usage
if __name__ == "__main__":
    async def main():
        # Example of how to use the VRChatOSCTools
        mcp = FastMCP()
        osc_tools = VRChatOSCTools(mcp)
        
        try:
            # Start the OSC tools
            await osc_tools.start()
            
            # Example: Set a gesture
            result = await osc_tools.set_gesture("left", "Fist", 1.0)
            logger.info("Set gesture result: %s", result)
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping OSC tools...")
        finally:
            await osc_tools.stop()
    
    asyncio.run(main())
