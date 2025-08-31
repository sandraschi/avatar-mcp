"""
Animation Box Demo

This script demonstrates how to control the animation box for avatar positioning and scaling.
"""
import asyncio
import logging
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.avatarmcp.core.app import AvatarMCPApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Initialize the MCP application
    app = AvatarMCPApp()
    
    try:
        # Start the MCP server
        await app.initialize()
        mcp = app.mcp_server
        
        # Show the visualization window
        await mcp.handle_message({
            "jsonrpc": "2.0",
            "method": "visualization.show",
            "params": {
                "model_id": "vrm1",
                "window_size": [1280, 720]
            },
            "id": "show1"
        })
        
        # Load a VRM model (replace with your VRM file path)
        vrm_path = "path/to/your/model.vrm"
        if Path(vrm_path).exists():
            await mcp.handle_message({
                "jsonrpc": "2.0",
                "method": "visualization.load_model",
                "params": {
                    "model_id": "vrm1",
                    "file_path": vrm_path
                },
                "id": "load1"
            })
        
        # Set up animation box
        await mcp.handle_message({
            "jsonrpc": "2.0",
            "method": "animation_box.set",
            "params": {
                "position": [0, 1.0, 0],  # Center at y=1.0 (roughly human height)
                "size": [0.8, 1.8, 0.8],   # Width, Height, Depth in meters
                "visible": True
            },
            "id": "box1"
        })
        
        # Make the avatar dance within the box
        await mcp.handle_message({
            "jsonrpc": "2.0",
            "method": "visualization.dance",
            "params": {
                "model_id": "vrm1",
                "intensity": 1.2,
                "duration": 30  # 30 seconds
            },
            "id": "dance1"
        })
        
        # Demonstrate adjusting the box size
        for i in range(5):
            # Make box wider
            await asyncio.sleep(5)
            await mcp.handle_message({
                "jsonrpc": "2.0",
                "method": "animation_box.set",
                "params": {
                    "size": [1.2, 1.8, 0.8],
                    "visible": True
                },
                "id": f"box_adjust_{i}"
            })
            
            # Make box taller
            await asyncio.sleep(5)
            await mcp.handle_message({
                "jsonrpc": "2.0",
                "method": "animation_box.set",
                "params": {
                    "size": [1.2, 2.2, 0.8],
                    "visible": True
                },
                "id": f"box_adjust_{i+1}"
            })
            
        # Hide the box but keep constraints
        await mcp.handle_message({
            "jsonrpc": "2.0",
            "method": "animation_box.hide",
            "params": {},
            "id": "hide_box"
        })
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.exception("An error occurred:")
    finally:
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
