"""
AvatarMCP Command Line Interface

This module provides a command-line interface for the AvatarMCP server.
"""

import argparse
import logging
import uvicorn
from pathlib import Path

from . import __version__

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AvatarMCP - VRM Avatar Management and Animation Server")
    
    # Server configuration
    server_group = parser.add_argument_group('Server Configuration')
    server_group.add_argument('--host', type=str, default='0.0.0.0',
                            help='Host to bind the server to (default: 0.0.0.0)')
    server_group.add_argument('-p', '--port', type=int, default=8080,
                            help='Port to run the server on (default: 8080)')
    server_group.add_argument('--reload', action='store_true',
                            help='Enable auto-reload for development')
    server_group.add_argument('--workers', type=int, default=1,
                            help='Number of worker processes (default: 1)')
    
    # Logging
    logging_group = parser.add_argument_group('Logging')
    logging_group.add_argument('-v', '--verbose', action='count', default=0,
                             help='Increase verbosity (can be used multiple times)')
    logging_group.add_argument('--log-level', type=str, default='info',
                             choices=['critical', 'error', 'warning', 'info', 'debug'],
                             help='Logging level (default: info)')
    
    # Model management
    model_group = parser.add_argument_group('Model Management')
    model_group.add_argument('--model-dir', type=Path, default='models',
                           help='Directory to store VRM models (default: ./models)')
    
    # API version
    parser.add_argument('--version', action='version',
                      version=f'AvatarMCP {__version__}')
    
    return parser.parse_args()

def configure_logging(verbosity: int, log_level: str) -> None:
    """Configure logging based on verbosity and log level."""
    import logging
    
    log_levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    
    # Set the root logger level
    log_level = getattr(logging, log_level.upper())
    if verbosity > 0:
        log_level = log_levels.get(min(verbosity, 2), logging.DEBUG)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    configure_logging(args.verbose, args.log_level)
    
    # Ensure model directory exists
    args.model_dir.mkdir(parents=True, exist_ok=True)
    
    # Import here to avoid circular imports
    from ..network.api import app
    
    # Configure the app
    app.state.model_dir = args.model_dir
    
    # Log startup banner
    logger.info("=" * 50)
    logger.info(f"AvatarMCP Server v{__version__}".center(50))
    logger.info(f"Listening on http://{args.host}:{args.port}".center(50))
    logger.info(f"Model directory: {args.model_dir.absolute()}".center(50))
    logger.info("=" * 50)
    
    # Start the server
    uvicorn.run(
        "avatarmcp.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()
