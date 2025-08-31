"""
AvatarMCP - Main Entry Point

This module serves as the entry point for the AvatarMCP server when run as a module.
It initializes and starts the FastMCP 2.10.1+ compatible server with VRChat OSC integration.
"""
import asyncio
import signal
import sys
import logging
import argparse
from typing import Optional, Any, Dict

# Configure logging before any imports
logging.basicConfig(
    level=logging.DEBUG,  # More verbose logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('avatarmcp.log', mode='w')
    ]
)

# Set higher log level for asyncio to reduce noise
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Import after logging is configured
from .core.app import AvatarMCP  # noqa: E402

logger = logging.getLogger(__name__)

class ServerRunner:
    """Helper class to run the AvatarMCP server with proper signal handling."""
    
    def __init__(self, enable_visualization: bool = True):
        """Initialize the server runner.
        
        Args:
            enable_visualization: Whether to enable 3D visualization
        """
        self.app: Optional[AvatarMCP] = None
        self.enable_visualization = enable_visualization
        self.shutdown_event = asyncio.Event()
        self._shutdown_requested = False
        
        # Set up signal handlers
        if sys.platform != 'win32':
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        if self._shutdown_requested:
            return
            
        self._shutdown_requested = True
        logger.info(f"Received signal {signal.Signals(signum).name}, shutting down...")
        
        # Schedule the shutdown on the event loop
        if hasattr(self, '_shutdown_handle') and self._shutdown_handle:
            self._shutdown_handle.cancel()
            
        loop = asyncio.get_running_loop()
        self._shutdown_handle = loop.call_soon_threadsafe(self.shutdown_event.set)
    
    async def run(self):
        """Run the AvatarMCP server."""
        logger.info("Starting AvatarMCP server...")
        
        try:
            # Create the application with visualization enabled/disabled
            self.app = AvatarMCP(enable_visualization=self.enable_visualization)
            
            # Start the application with visualization
            await self.app.start(start_visualization=self.enable_visualization)
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}", exc_info=True)
            return 1
        finally:
            if self.app:
                await self.app.stop()
            logger.info("Shutting down AvatarMCP server...")
            if self.app:
                await self.app.stop()
            logger.info("Server stopped")
        
        return 0

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='AvatarMCP - VRM Avatar Management Server')
    parser.add_argument('--no-visualization', 
                        action='store_true',
                        help='Disable 3D visualization')
    parser.add_argument('--log-level',
                        default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    return parser.parse_args()

def main() -> int:
    """
    Entry point for the AvatarMCP server.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    args = parse_args()
    
    # Update logging level based on command line argument
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Configure asyncio for Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Create and set the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Create the server runner with visualization enabled/disabled
        runner = ServerRunner(enable_visualization=not args.no_visualization)
        
        # Run the server in the main event loop
        return loop.run_until_complete(runner.run())
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        # Ensure we clean up properly
        if 'runner' in locals() and runner.app:
            try:
                loop.run_until_complete(runner.app.stop())
            except Exception as e:
                logger.error(f"Error during cleanup: {e}", exc_info=True)
        loop.close()

if __name__ == "__main__":
    sys.exit(main())
