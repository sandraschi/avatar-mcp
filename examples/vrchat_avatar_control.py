"""
VRChat Avatar Control Example

This example demonstrates how to use AvatarMCP to control a VRChat avatar
using OSC messages. It shows how to set up the OSC server, load a VRM model,
and control various avatar parameters.
"""
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import AvatarMCP components
try:
    from avatarmcp.osc_server import VRChatOSCServer
    from avatarmcp.vrm_loader import VRMLoader
    from avatarmcp.oscmcp_integration import AvatarOSCIntegrator, AvatarOSCConfig
    from fastmcp import FastMCP
except ImportError:
    # If running from the examples directory, add the parent directory to path
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from src.avatarmcp.osc_server import VRChatOSCServer
    from src.avatarmcp.vrm_loader import VRMLoader
    from src.avatarmcp.oscmcp_integration import AvatarOSCIntegrator, AvatarOSCConfig
    from fastmcp import FastMCP

class VRChatAvatarController:
    """Controller for VRChat avatar using AvatarMCP."""
    
    def __init__(self, vrm_path: Optional[str] = None):
        """Initialize the controller."""
        self.vrm_path = vrm_path
        self.vrm_loader: Optional[VRMLoader] = None
        self.osc_server: Optional[VRChatOSCServer] = None
        self.mcp: Optional[FastMCP] = None
        self.osc_integrator: Optional[AvatarOSCIntegrator] = None
        
    async def initialize(self):
        """Initialize the controller and all components."""
        logger.info("Initializing VRChat Avatar Controller...")
        
        # Initialize MCP client
        self.mcp = FastMCP("http://localhost:8000/mcp")
        
        # Initialize OSC server configuration
        config = AvatarOSCConfig(
            receive_port=9000,
            send_port=9001,
            server_ip="127.0.0.1",
            parameter_mappings={
                # Common parameters
                "BlendShape.A": "VRC_AA",
                "BlendShape.E": "VRC_E",
                "BlendShape.I": "VRC_I",
                "BlendShape.O": "VRC_O",
                "BlendShape.U": "VRC_U",
                "BlendShape.Blink": "VRC_Blink",
                "BlendShape.BlinkLeft": "VRC_BlinkLeft",
                "BlendShape.BlinkRight": "VRC_BlinkRight",
                "BlendShape.LookUp": "VRC_LookUp",
                "BlendShape.LookDown": "VRC_LookDown",
                "BlendShape.LookLeft": "VRC_LookLeft",
                "BlendShape.LookRight": "VRC_LookRight",
                "BlendShape.Brows": "VRC_Brows",
                "BlendShape.MouthOpen": "VRC_MouthOpen",
                "BlendShape.JawOpen": "VRC_JawOpen",
                "BlendShape.LipO": "VRC_LipO",
                "BlendShape.LipFunnel": "VRC_LipFunnel",
                "BlendShape.LipPucker": "VRC_LipPucker",
                "BlendShape.CheekPuff": "VRC_CheekPuff",
                "BlendShape.TongueOut": "VRC_TongueOut",
                # Add more mappings as needed
            },
            gesture_mappings={
                "fist": {"left": "Fist", "right": "Fist"},
                "open": {"left": "Open", "right": "Open"},
                "point": {"left": "Point", "right": "Point"},
                "peace": {"left": "Peace", "right": "Peace"},
                "rock": {"left": "RockNRoll", "right": "RockNRoll"},
                "gun": {"left": "Gun", "right": "Gun"},
                "thumbsup": {"left": "ThumbsUp", "right": "ThumbsUp"},
            },
            expression_mappings={
                "neutral": "Neutral",
                "happy": "Happy",
                "sad": "Sad",
                "angry": "Angry",
                "surprised": "Surprised",
                "blink": "Blink",
                "blink_left": "BlinkLeft",
                "blink_right": "BlinkRight",
            }
        )
        
        # Initialize OSC integrator
        self.osc_integrator = AvatarOSCIntegrator(self.mcp, config)
        
        # Load VRM model if path is provided
        if self.vrm_path:
            await self.load_vrm_model()
        
        # Start the OSC server
        await self.osc_integrator.start()
        
        # Register parameter change handlers
        self._register_handlers()
        
        logger.info("VRChat Avatar Controller initialized")
    
    async def load_vrm_model(self):
        """Load a VRM model and update parameter mappings."""
        if not self.vrm_path:
            logger.warning("No VRM path provided")
            return
            
        logger.info(f"Loading VRM model: {self.vrm_path}")
        self.vrm_loader = VRMLoader.from_file(self.vrm_path)
        
        # Update parameter mappings based on the VRM model
        if self.osc_integrator:
            self.osc_integrator.load_vrm(self.vrm_path)
            
        logger.info(f"Loaded VRM model with {len(self.vrm_loader.get_blend_shape_names())} blend shapes and {len(self.vrm_loader.get_bone_names())} bones")
    
    def _register_handlers(self):
        """Register parameter change handlers."""
        if not self.osc_integrator:
            return
            
        # Example: Register a handler for all parameter changes
        @self.osc_integrator.on_parameter_change("*")
        async def on_parameter_change(parameter: str, value: Any):
            logger.debug(f"Parameter changed: {parameter} = {value}")
    
    async def run_demo(self):
        """Run a demo sequence to test avatar controls."""
        if not self.osc_integrator:
            logger.error("OSC integrator not initialized")
            return
            
        logger.info("Starting demo sequence...")
        
        try:
            # Test expressions
            expressions = ["happy", "sad", "angry", "surprised", "neutral"]
            for expr in expressions:
                logger.info(f"Setting expression: {expr}")
                await self.osc_integrator.set_expression(expr, 1.0)
                await asyncio.sleep(2.0)
            
            # Test gestures
            gestures = ["fist", "open", "point", "peace", "rock", "gun", "thumbsup"]
            for gesture in gestures:
                logger.info(f"Setting left hand gesture: {gesture}")
                await self.osc_integrator.set_gesture("left", gesture, 1.0)
                await asyncio.sleep(1.0)
                
                logger.info(f"Setting right hand gesture: {gesture}")
                await self.osc_integrator.set_gesture("right", gesture, 1.0)
                await asyncio.sleep(1.0)
            
            # Reset to neutral
            await self.osc_integrator.set_expression("neutral", 0.0)
            await self.osc_integrator.set_gesture("left", "neutral")
            await self.osc_integrator.set_gesture("right", "neutral")
            
            logger.info("Demo sequence completed")
            
        except Exception as e:
            logger.error(f"Error in demo sequence: {e}")
    
    async def close(self):
        """Clean up resources."""
        logger.info("Shutting down VRChat Avatar Controller...")
        
        if self.osc_integrator:
            await self.osc_integrator.stop()
            
        logger.info("VRChat Avatar Controller shut down")

async def main():
    """Main function to run the example."""
    parser = argparse.ArgumentParser(description="VRChat Avatar Control Example")
    parser.add_argument("--vrm", type=str, help="Path to VRM model file")
    parser.add_argument("--demo", action="store_true", help="Run demo sequence")
    args = parser.parse_args()
    
    # Create and initialize the controller
    controller = VRChatAvatarController(args.vrm)
    
    try:
        await controller.initialize()
        
        if args.demo:
            await controller.run_demo()
        else:
            # Keep the application running
            logger.info("VRChat Avatar Controller running. Press Ctrl+C to exit.")
            while True:
                await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await controller.close()

if __name__ == "__main__":
    asyncio.run(main())
