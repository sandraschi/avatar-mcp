#!/usr/bin/env python3
"""
Dedicated MCP server entry point that avoids importing heavy dependencies.
This is specifically for Claude Desktop integration.
"""
import sys
import os
import logging

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
    """Main entry point for MCP server only."""
    # Configure logging to file only to avoid interfering with MCP protocol
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", "mcp_server.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting MCP server (dedicated entry point)")
    
    try:
        # Import only the MCP server implementation
        import importlib.util
        import pathlib
        
        # Get the path to mcp_server_clean.py
        mcp_server_path = pathlib.Path(__file__).parent / "mcp_server_clean.py"
        
        # Load the clean module directly
        spec = importlib.util.spec_from_file_location("mcp_server_clean", mcp_server_path)
        mcp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_module)
        
        # Create and run the server
        server = mcp_module.MCPServer()
        
        if ASYNCIO_AVAILABLE:
            try:
                asyncio.run(server.run())
            except OSError as e:
                if "WinError 10106" in str(e):
                    logger.warning("Asyncio failed, falling back to sync mode")
                    server.run_sync()
                else:
                    raise
        else:
            logger.info("Asyncio not available, using sync mode")
            server.run_sync()
        
    except Exception as e:
        # Write error to stderr so it appears in Claude Desktop logs
        import sys
        sys.stderr.write(f"CRITICAL ERROR in MCP server: {str(e)}\n")
        sys.stderr.flush()
        logger.error(f"Error in MCP server: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
