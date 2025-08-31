"""
Test script for AvatarMCP server.
"""
import asyncio
import logging
import sys
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('test_server')

async def test_server():
    """Test the AvatarMCP server."""
    try:
        # Import here to ensure logging is configured first
        from avatarmcp import AvatarMCP
        
        logger.info("Creating AvatarMCP instance...")
        app = AvatarMCP()
        
        logger.info("Starting server...")
        await app.start()
        
        try:
            # Keep the server running until interrupted
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return 1
        finally:
            await app.stop()
            
    except ImportError as e:
        logger.error(f"Failed to import AvatarMCP: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(test_server()))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
