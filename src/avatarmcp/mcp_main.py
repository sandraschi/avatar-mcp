#!/usr/bin/env python3
"""
Dedicated MCP server entry point that avoids importing heavy dependencies.
This is specifically for Claude Desktop integration.
"""

import logging
import os
import sys

# Handle Windows asyncio issues
try:
    import asyncio

    ASYNCIO_AVAILABLE = True
except OSError as e:
    if "WinError 10106" in str(e):
        # Windows networking service issue
        ASYNCIO_AVAILABLE = False
        asyncio = None
    else:
        raise


def main():
    """Main entry point for MCP server using FastMCP."""
    # Configure logging to file only to avoid interfering with MCP protocol
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "mcp_server.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging to stderr only (MCP best practice)
    # MCP protocol requires stdout for JSON-RPC only
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # Send to stderr for Claude Desktop logs
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting FastMCP server (AvatarMCP)")

    try:
        # Import the clean FastMCP server implementation
        # Use absolute import to avoid relative import issues
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        import importlib.util

        mcp_server_path = os.path.join(current_dir, "mcp_server_clean.py")
        spec = importlib.util.spec_from_file_location("mcp_server_clean", mcp_server_path)
        mcp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_module)

        # Create the FastMCP server instance
        server = mcp_module.MCPServer()

        if ASYNCIO_AVAILABLE:
            try:
                # Run the FastMCP server
                server.run()
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
        # Write error to stderr so it appears in Claude Desktop logs
        sys.stderr.write(f"CRITICAL ERROR in FastMCP server: {e!s}\n")
        sys.stderr.flush()
        logger.error(f"Error in FastMCP server: {e!s}", exc_info=True)
        import traceback

        sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
