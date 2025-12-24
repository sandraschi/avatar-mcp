"""
Test script to verify server startup and basic functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_server_startup():
    """Test that the server can start up and shut down cleanly."""
    try:
        from avatarmcp.core.app import AvatarMCP

        logger.info("Creating AvatarMCP instance...")
        app = AvatarMCP(enable_visualization=False)

        logger.info("Starting server...")
        await app.start()

        # Verify server is running
        assert hasattr(app, "is_running") and app.is_running() is True
        logger.info("Server started successfully")

        # Keep the server running for a short time
        logger.info("Server running for 5 seconds...")
        await asyncio.sleep(5)

    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error during server test: {e}", exc_info=True)
        return 1
    finally:
        if "app" in locals() and hasattr(app, "stop"):
            logger.info("Stopping server...")
            await app.stop()
            logger.info("Server stopped")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_server_startup())
    sys.exit(exit_code)
