"""
AvatarMCP - Main Entry Point

This module serves as the entry point for the AvatarMCP server when run as a module.
It initializes and starts the FastMCP 2.10 compatible server.
"""
import sys
from .server import main

if __name__ == "__main__":
    sys.exit(main())
