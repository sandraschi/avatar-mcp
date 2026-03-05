"""
Simple test script to verify the AvatarMCP server can be imported and started.
"""

import logging
import os
import sys
from pathlib import Path

# Configure logging to see all output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def main():
    print("Python version:", sys.version)
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)

    # Add the src directory to the Python path
    src_dir = str(Path(__file__).parent / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    print("\nTrying to import avatarmcp...")
    try:
        import avatarmcp

        print("Successfully imported avatarmcp")
        print("Module location:", avatarmcp.__file__)

        print("\nTrying to import server...")
        from avatarmcp import server

        print("Successfully imported server")

        print("\nStarting server...")
        server.main()

    except ImportError as e:
        print(f"Import error: {e}")
        import traceback

        traceback.print_exc()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
