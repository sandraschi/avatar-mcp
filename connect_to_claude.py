"""
Script to connect a VRoid avatar to Claude Desktop using AvatarMCP.
"""
import os
import sys
import json
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_avatar(avatar_path):
    """Load the VRM avatar into the AvatarMCP server."""
    try:
        from avatarmcp.server import load_vrm
        
        logger.info(f"Loading avatar: {avatar_path}")
        result = load_vrm(avatar_path)
        
        if result.get("status") == "success":
            model_id = result.get('model_id')
            logger.info(f"Successfully loaded avatar with ID: {model_id}")
            return model_id
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Failed to load avatar: {error_msg}")
            return None
            
    except Exception as e:
        logger.error(f"Error loading avatar: {str(e)}", exc_info=True)
        return None

def main():
    logger.info("=== Claude Desktop VRM Avatar Setup ===")
    
    # Path to the VRM file
    vrm_path = Path("examples/Nekomimi-chan.vrm")
    
    if not vrm_path.exists():
        logger.error(f"VRM file not found at {vrm_path}")
        logger.error("Please make sure the VRM file exists in the examples directory.")
        return
    
    logger.info(f"Found VRM avatar: {vrm_path.name}")
    logger.info("\nMake sure the AvatarMCP server is running in another terminal.")
    logger.info("You can start it with: python -m avatarmcp.server\n")
    
    input("Press Enter to load the avatar into the server...")
    
    # Load the avatar
    avatar_id = load_avatar(str(vrm_path.absolute()))
    
    if not avatar_id:
        logger.error("\nFailed to load the avatar. Please check the error messages above.")
        return
    
    logger.info("\n=== Setup Complete! ===")
    logger.info("The avatar is now loaded in the AvatarMCP server.")
    logger.info("\nIn Claude Desktop, use these settings to connect:")
    logger.info(f"- MCP Server: localhost:8080")
    logger.info(f"- Avatar ID: {avatar_id}")
    logger.info("\nMake sure to enable MCP support in Claude Desktop settings.")

if __name__ == "__main__":
    main()
