"""
AvatarMCP Command Line Interface
"""
import sys
import asyncio
import logging
from typing import Optional

from .core.app import AvatarMCP

logger = logging.getLogger(__name__)

async def async_main():
    """Async entry point for the CLI."""
    try:
        app = AvatarMCP()
        await app.start()
        
        # Keep the application running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    finally:
        if 'app' in locals():
            await app.stop()
    return 0

def main():
    """Main entry point for the CLI."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('avatarmcp.log', mode='w')
        ]
    )
    
    # Set higher log level for asyncio to reduce noise
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    try:
        # Run the async main function
        return asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
