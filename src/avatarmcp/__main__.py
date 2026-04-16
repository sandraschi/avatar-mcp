#!/usr/bin/env python3
"""
AvatarMCP - Main entry point for the Avatar Model Control Protocol server.

This module serves as the entry point for the AvatarMCP server when run as a module.
It initializes and starts the FastMCP 2.12.0+ compatible server with VRChat OSC integration.
"""

# For stdio MCP, patch stdout before any imports so no log/banner corrupts JSON-RPC.
import argparse
import logging
import os
import sys

if "--stdio" in sys.argv or "--mcp" in sys.argv:
    _stdio_original_stdout = sys.stdout

    class _DevNullStdout:
        def write(self, s: str) -> int:
            return len(s)

        def flush(self) -> None:
            pass

        def isatty(self) -> bool:
            return False

    sys.stdout = _DevNullStdout()

from .server import AvatarMCPServer, run_server

# Configure logging before any imports to catch early messages
from .utils.logging_utils import setup_logging

# Don't set up logging here, we'll do it after parsing arguments
logger = logging.getLogger(__name__)


def mcp_main() -> int:
    """Run the MCP server for Claude/Cursor (stdio). Uses canonical FastMCP 3.1 server."""
    log_level = logging.DEBUG if "--debug" in sys.argv else logging.INFO
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "mcp_main.log")
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except OSError:
        pass
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=log_file,
        filemode="a",
    )
    try:
        server = AvatarMCPServer(enable_osc=False)
        # Restore stdout so FastMCP can send JSON-RPC on it; nothing else must write to it.
        if "--stdio" in sys.argv or "--mcp" in sys.argv:
            sys.stdout = _stdio_original_stdout
            sys.stdout.flush()
        server.mcp.run(show_banner=False)
        return 0
    except Exception as e:
        logging.getLogger(__name__).error("MCP server error: %s", e, exc_info=True)
        return 1


def main() -> int:
    """Main entry point for the AvatarMCP server."""
    if "--mcp" in sys.argv or "--stdio" in sys.argv:
        return mcp_main()

    parser = argparse.ArgumentParser(description="AvatarMCP - Avatar Model Control Protocol Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the MCP server to")
    parser.add_argument("--port", type=int, default=10793, help="Port for HTTP MCP server")
    parser.add_argument("--osc-host", default="127.0.0.1", help="Host to bind the OSC server to")
    parser.add_argument("--osc-port", type=int, default=9001, help="Port to run the OSC server on")
    parser.add_argument("--vrc-osc-host", default="127.0.0.1", help="VRChat OSC client host")
    parser.add_argument("--vrc-osc-port", type=int, default=9000, help="VRChat OSC client port")
    parser.add_argument("--models-dir", help="Directory containing avatar models")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--mcp", action="store_true", help="Run in MCP mode (stdio)")
    parser.add_argument("--stdio", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--enable-osc", action="store_true", help="Enable OSC server")

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "avatarmcp.log")
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except OSError:
        pass
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        max_bytes=10 * 1024 * 1024,
        backup_count=5,
    )

    logger.info("Starting AvatarMCP server...")
    return run_server(
        host=args.host,
        port=args.port,
        enable_osc=args.enable_osc,
    )


if __name__ == "__main__":
    try:
        if "--mcp" in sys.argv or "--stdio" in sys.argv:
            sys.exit(mcp_main())
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        # If logging is configured, use it; otherwise fall back to stderr
        try:
            logger = logging.getLogger(__name__)
            logger.error(f"Fatal error: {e!s}", exc_info=True)
        except Exception:
            import traceback

            sys.stderr.write(f"Fatal error: {e!s}\n")
            sys.stderr.write(traceback.format_exc() + "\n")
        sys.exit(1)
