"""
Environment checker for AvatarMCP server.
"""

import importlib
import logging
import os
import platform
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def log_section(title):
    """Log a section header."""
    logger.info("\n" + "=" * 50)
    logger.info(f" {title} ".center(50, "="))
    logger.info("=" * 50)


def check_python():
    """Check Python version and environment."""
    log_section("Python Environment")
    logger.info(f"Python Executable: {sys.executable}")
    logger.info(f"Python Version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Current Working Directory: {os.getcwd()}")
    logger.info("Python Path:")
    for p in sys.path:
        logger.info(f"  {p}")


def check_imports():
    """Check if required modules can be imported."""
    log_section("Checking Imports")

    required_modules = [
        "fastmcp",
        "numpy",
        "aiohttp",
        "aiohttp.web",
        "aiohttp_cors",
        "fastapi",
        "uvicorn",
        "pyvrm",
        "trimesh",
        "pygltflib",
    ]

    for module in required_modules:
        try:
            mod = importlib.import_module(module)
            logger.info(f"✓ {module}: {mod.__file__}")
        except ImportError as e:
            logger.error(f"✗ {module}: {e}")


def check_avatarmcp():
    """Check if avatarmcp can be imported."""
    log_section("Checking AvatarMCP")

    # Add src to path if not already there
    src_dir = str(Path(__file__).parent / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    try:
        import avatarmcp

        logger.info(f"✓ avatarmcp imported from: {avatarmcp.__file__}")

        # Try to import server
        try:
            import avatarmcp.server

            logger.info("✓ avatarmcp.server imported successfully")
            return True
        except ImportError as e:
            logger.error(f"✗ Failed to import avatarmcp.server: {e}")
            logger.debug("Traceback:", exc_info=True)
            return False

    except ImportError as e:
        logger.error(f"✗ Failed to import avatarmcp: {e}")
        logger.debug("Traceback:", exc_info=True)
        return False


def run_server():
    """Try to run the server."""
    log_section("Testing Server")

    # Add src to path if not already there
    src_dir = str(Path(__file__).parent / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    try:
        from avatarmcp.server import main

        logger.info("✓ Server main function found")
        logger.info("Starting server... (Press Ctrl+C to stop)")
        main()
    except Exception as e:
        logger.error(f"✗ Failed to start server: {e}")
        logger.debug("Traceback:", exc_info=True)


def main():
    """Main function."""
    check_python()
    check_imports()
    if check_avatarmcp():
        if input("\nStart the server? (y/n): ").lower() == "y":
            run_server()


if __name__ == "__main__":
    main()
