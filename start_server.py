"""
Simple script to start the AvatarMCP server with debug output.
"""
import os
import sys
import logging
from pathlib import Path
import os

# Add the src directory to the Python path at the very beginning
src_dir = str(Path(__file__).parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'avatarmcp.log')
    ]
)

# Set higher log level for asyncio to reduce noise
logging.getLogger('asyncio').setLevel(logging.WARNING)

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
        logger.info("Attempting to import avatarmcp...")
        try:
            import avatarmcp
            logger.info("Successfully imported avatarmcp from: %s", avatarmcp.__file__)
            
            # Get the directory containing avatarmcp
            import pathlib
            avatarmcp_path = pathlib.Path(avatarmcp.__file__).parent
            logger.info("Contents of %s:", avatarmcp_path)
            for f in avatarmcp_path.glob("*"):
                logger.info("  - %s", f.name)
                
            # Try to import the server components
            try:
                from avatarmcp.core.app import AvatarMCP
                logger.info("Successfully imported AvatarMCP class")
                
                # Create and start the server
                logger.info("Creating AvatarMCP instance...")
                app = AvatarMCP()
                
                logger.info("Starting the server...")
                import asyncio
                
                # Get the event loop
                try:
                    loop = asyncio.get_event_loop()
                    logger.info("Using existing event loop")
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    logger.info("Created new event loop")
                    
                # Run the server
                logger.info("Running server...")
                loop.run_until_complete(app.start())
                
                try:
                    # Keep the server running
                    loop.run_forever()
                except KeyboardInterrupt:
                    logger.info("Shutting down server...")
                finally:
                    loop.run_until_complete(app.stop())
                    loop.close()
                
                logger.info("Server stopped successfully")
                return 0
                
            except ImportError as e:
                logger.error("Failed to import AvatarMCP: %s", e)
                logger.error("Available modules in avatarmcp: %s", dir(avatarmcp))
                return 1
                
        except ImportError as e:
            logger.error("Failed to import avatarmcp: %s", e)
            logger.error("Python path: %s", sys.path)
            return 1
            
    except Exception as e:
        logger.exception("Unexpected error in main:")
        return 1

if __name__ == "__main__":
    sys.exit(main())
