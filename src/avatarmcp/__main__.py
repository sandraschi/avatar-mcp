#!/usr/bin/env python3
"""
AvatarMCP - Main entry point for the Avatar Model Control Protocol server.

This module serves as the entry point for the AvatarMCP server when run as a module.
It initializes and starts the FastMCP 2.12.0+ compatible server with VRChat OSC integration.
"""
# Redirect stdout to stderr before any imports
import sys
import os
import asyncio
import signal
import logging
import argparse
from typing import Optional, Any, Dict

# Configure logging before any imports to catch early messages
from .utils.logging_utils import setup_logging

import os
from logging.handlers import RotatingFileHandler
import logging
import sys

# Don't set up logging here, we'll do it after parsing arguments
logger = logging.getLogger(__name__)

# Now import the rest of the application
from .server import AvatarMCPServer, run_server

# Global server instance
mcp_server: Optional[AvatarMCPServer] = None

async def shutdown(signal: signal.Signals) -> None:
    """Handle shutdown signals."""
    logger.info(f"Received exit signal {signal.name}...")
    
    if mcp_server:
        await mcp_server.stop()
    
    logger.info("Server stopped successfully")
    sys.exit(0)

def handle_exception(loop: asyncio.AbstractEventLoop, context: Dict[str, Any]) -> None:
    """Handle uncaught exceptions."""
    # Log the exception
    logger.error(f"Unhandled exception: {context}", exc_info=context.get('exception'))
    
    # Schedule the shutdown
    asyncio.create_task(shutdown(signal.SIGTERM))

async def main() -> None:
    """Main entry point for the AvatarMCP server."""
    global mcp_server, osc_server
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AvatarMCP - Avatar Model Control Protocol Server')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Host to bind the MCP server to')
    parser.add_argument('--port', type=int, default=0,
                       help='Port to bind the MCP server to (0 for random)')
    parser.add_argument('--osc-host', type=str, default='127.0.0.1',
                       help='Host to bind the OSC server to')
    parser.add_argument('--osc-port', type=int, default=9000,
                       help='Port to bind the OSC server to')
    parser.add_argument('--vrc-osc-host', type=str, default='127.0.0.1',
                       help='VRChat OSC host to send messages to')
    parser.add_argument('--vrc-osc-port', type=int, default=9001,
                       help='VRChat OSC port to send messages to')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--log-file', type=str, default='avatarmcp.log',
                       help='Path to log file (default: avatarmcp.log)')
    
    args = parser.parse_args()
    
    # Set up logging with the correct level and log file
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    # Ensure log directory exists
    log_dir = os.path.dirname(os.path.abspath(args.log_file))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging with final settings
    setup_logging(
        log_level=log_level,
        log_file=args.log_file,
        console=False,  # No console output
        force_stderr=True,  # Force all logging to stderr
        max_bytes=10*1024*1024,  # 10MB per file
        backup_count=5,  # Keep 5 backup files
        force_stderr=True  # Ensure all console output goes to stderr
    )
    
    logger.info("Starting AvatarMCP server...")
    logger.debug(f"Command line arguments: {sys.argv}")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Running on platform: {sys.platform}")
    
    try:
        # Create the MCP server with default configuration
        mcp_server = AvatarMCPServer(
            host=args.host,
            port=args.port,
            osc_host=args.osc_host,
            osc_port=args.osc_port,
            vrc_osc_host=args.vrc_osc_host,
            vrc_osc_port=args.vrc_osc_port
        )
        
        # Register signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(shutdown(s))
                )
            except (NotImplementedError, RuntimeError) as e:
                logger.warning(f"Could not add signal handler for {sig}: {e}")
        
        # Set exception handler
        loop.set_exception_handler(handle_exception)
        
        # Start the MCP server
        await mcp_server.start()
        
        # Log server addresses
        if hasattr(mcp_server, 'server') and mcp_server.server is not None:
            for sock in mcp_server.server.sockets:
                logger.info(f"MCP server listening on {sock.getsockname()}")
        
        logger.info(f"OSC server configured for {args.vrc_osc_host}:{args.vrc_osc_port}")
        
        # Keep the server running
        await asyncio.Future()
        
    except Exception as e:
        logger.exception("Fatal error in main loop")
        return 1
    finally:
        # Ensure clean shutdown
        if 'mcp_server' in globals() and mcp_server:
            await mcp_server.stop()
    
    return 0

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unhandled exception in main")
        sys.exit(1)
