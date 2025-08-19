"""
Simple script to start the AvatarMCP server with debug output.
"""
import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path at the very beginning
src_dir = str(Path(__file__).parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

def print_environment():
    """Print environment information for debugging."""
    logger.info("Python version: %s", sys.version)
    logger.info("Python path: %s", sys.path)
    logger.info("Current working directory: %s", os.getcwd())
    logger.info("Environment variables:")
    for key, value in os.environ.items():
        if 'python' in key.lower() or 'path' in key.lower() or 'home' in key.lower():
            logger.info("  %s: %s", key, value)

def main():
    """Main entry point for the server."""
    print_environment()
    
    try:
        # Try to import the server module
        logger.info("Attempting to import avatarmcp.server...")
        from avatarmcp.server import main as server_main
        
        # List available modules for debugging
        logger.info("Successfully imported avatarmcp.server")
        
        # Start the server
        logger.info("Starting AvatarMCP server...")
        return server_main()
        
    except ImportError as e:
        logger.error("Failed to import required module: %s", e, exc_info=True)
        logger.error("Module search paths: %s", sys.path)
        
        # Try to list the src/avatarmcp directory
        try:
            avatarmcp_path = Path(__file__).parent / "src" / "avatarmcp"
            if avatarmcp_path.exists():
                logger.info("Contents of %s:", avatarmcp_path)
                for f in avatarmcp_path.glob("*"):
                    logger.info("  - %s", f.name)
        except Exception as dir_err:
            logger.error("Failed to list avatarmcp directory: %s", dir_err)
            
        return 1
    except Exception as e:
        logger.error("Error starting server: %s", e, exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
