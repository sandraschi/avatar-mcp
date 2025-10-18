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
from .server import OSCConfig, AvatarMCPServer


# Don't set up logging here, we'll do it after parsing arguments
logger = logging.getLogger(__name__)

# Now import the rest of the application

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

async def mcp_main():
    """Run the MCP server for Claude desktop integration."""
    # Configure logging to file for debugging - DO NOT log to stderr in MCP mode
    log_level = logging.DEBUG if "--debug" in sys.argv else logging.INFO
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "mcp_main.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Set up logging to file only to avoid interfering with MCP protocol
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )
    
    # Do NOT redirect stdout - let the MCP server handle its own I/O
    
    # Create and run the MCP server
    try:
        from .mcp_server_clean import MCPServer
        server = MCPServer()
        await server.run()
    except Exception as e:
        # Log errors to the file instead of stderr to avoid MCP protocol issues
        logger = logging.getLogger(__name__)
        logger.error(f"Error in MCP server: {str(e)}", exc_info=True)
        sys.exit(1)

def main():
    """Main entry point for the AvatarMCP server."""
    # For backward compatibility, check if we're running in MCP mode
    if "--mcp" in sys.argv or "--stdio" in sys.argv:
        asyncio.run(mcp_main())
        return 0
    
    # Original command-line argument parsing for standalone mode
    parser = argparse.ArgumentParser(description="AvatarMCP - Avatar Model Control Protocol Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the MCP server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the MCP server on")
    parser.add_argument("--osc-host", default="127.0.0.1", help="Host to bind the OSC server to")
    parser.add_argument("--osc-port", type=int, default=9001, help="Port to run the OSC server on")
    parser.add_argument("--vrc-osc-host", default="127.0.0.1", help="VRChat OSC client host")
    parser.add_argument("--vrc-osc-port", type=int, default=9000, help="VRChat OSC client port")
    parser.add_argument("--models-dir", help="Directory containing avatar models")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--mcp", action="store_true", help="Run in MCP mode (for Claude desktop integration)")
    parser.add_argument("--stdio", action="store_true", help=argparse.SUPPRESS)  # Hidden flag for MCP mode
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "avatarmcp.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Set up logging to both file and stderr
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        max_bytes=10*1024*1024,  # 10MB per file
        backup_count=5  # Keep 5 backup files
    )
    
    logger.info("Starting AvatarMCP server...")
    logger.debug(f"Command line arguments: {sys.argv}")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Running on platform: {sys.platform}")
    
    try:
        # Create the OSC configuration
        osc_config = OSCConfig(
            client_address=args.vrc_osc_host,
            client_port=args.vrc_osc_port,
            server_address=args.osc_host,
            server_port=args.osc_port
        )
        
        # Create the MCP server with OSC configuration
        AvatarMCPServer(
            osc_config=osc_config,
            enable_osc=True
        )
        
        # Register signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
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
        
        # Log server initialization
        logger.info("AvatarMCP server initialized")
        logger.info(f"OSC server configured for {args.vrc_osc_host}:{args.vrc_osc_port}")
        
        # Keep the server running
        loop.run_forever()
            
    except asyncio.CancelledError:
        logger.info("Shutting down...")
    except Exception:
        logger.exception("Fatal error in main loop")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        # Check if we're running in MCP mode (for Claude desktop)
        if "--mcp" in sys.argv or "--stdio" in sys.argv:
            asyncio.run(mcp_main())
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        # If logging is configured, use it; otherwise fall back to stderr
        try:
            logger = logging.getLogger(__name__)
            logger.error(f"Fatal error: {str(e)}", exc_info=True)
        except Exception:
            import traceback
            sys.stderr.write(f"Fatal error: {str(e)}\n")
            sys.stderr.write(traceback.format_exc() + "\n")
        sys.exit(1)
