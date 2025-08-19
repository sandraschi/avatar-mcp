"""
AvatarMCP - Main Entry Point

This module serves as the entry point for the AvatarMCP server when run as a module.
It initializes and starts the FastMCP 2.10.1+ compatible server with VRChat OSC integration.
"""
import asyncio
import signal
import sys
import logging
from typing import Optional, Any, Dict

# Configure logging before any imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Import after logging is configured
from .core.app import AvatarMCP  # noqa: E402

logger = logging.getLogger(__name__)

class ServerRunner:
    """Helper class to run the AvatarMCP server with proper signal handling."""
    
    def __init__(self):
        """Initialize the server runner."""
        self.app: Optional[AvatarMCP] = None
        self.shutdown_event = asyncio.Event()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signal.Signals(signum).name}, shutting down...")
        self.shutdown_event.set()
    
    async def run(self):
        """Run the AvatarMCP server."""
        logger.info("Starting AvatarMCP server...")
        
        try:
            # Initialize the application
            self.app = AvatarMCP()
            
            # Start the application
            server_task = asyncio.create_task(self.app.start())
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            # Shut down the application
            logger.info("Shutting down AvatarMCP server...")
            await self.app.stop()
            
            # Wait for the server task to complete
            await asyncio.wait_for(server_task, timeout=5.0)
            
        except asyncio.CancelledError:
            logger.info("Server task cancelled")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            # Ensure cleanup
            if self.app:
                await self.app.stop()

def main() -> int:
    """
    Entry point for the AvatarMCP server.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # Set up asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create and run the server
        runner = ServerRunner()
        return loop.run_until_complete(runner.run())
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        # Clean up the event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.stop()
            if not loop.is_closed():
                loop.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)

if __name__ == "__main__":
    sys.exit(main())
