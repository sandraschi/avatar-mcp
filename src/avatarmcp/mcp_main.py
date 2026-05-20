#!/usr/bin/env python3
"""
Dedicated MCP server entry point for Claude Desktop integration.
Uses the canonical server.py (AvatarMCPServer).
"""

import logging
import os
import sys

try:
    import asyncio
    ASYNCIO_AVAILABLE = True
except OSError as e:
    if "WinError 10106" in str(e):
        ASYNCIO_AVAILABLE = False
        asyncio = None
    else:
        raise


def main():
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "mcp_server.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting FastMCP server (AvatarMCP)")

    try:
        from avatarmcp.server import AvatarMCPServer

        server = AvatarMCPServer(enable_osc=False)

        if ASYNCIO_AVAILABLE:
            try:
                server.mcp.run(show_banner=False)
            except OSError as e:
                if "WinError 10106" in str(e):
                    logger.error("Asyncio networking error - Windows compatibility issue")
                    raise
                else:
                    raise
        else:
            logger.error("Asyncio not available - cannot run FastMCP server")
            sys.stderr.write("ERROR: Asyncio required for FastMCP server\n")
            sys.exit(1)

    except Exception as e:
        sys.stderr.write(f"CRITICAL ERROR in FastMCP server: {e!s}\n")
        sys.stderr.flush()
        logger.error(f"Error in FastMCP server: {e!s}", exc_info=True)
        import traceback
        sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
