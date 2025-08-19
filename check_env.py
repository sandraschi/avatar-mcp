"""
Environment checker for AvatarMCP server.
"""
import os
import sys
import platform
import importlib
import traceback
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*50}")
    print(f" {title}".ljust(50, '='))
    print(f"{'='*50}")

def check_python():
    """Check Python version and environment."""
    print_section("Python Environment")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Working Directory: {os.getcwd()}")
    print("\nPython Path:")
    for p in sys.path:
        print(f"  {p}")

def check_imports():
    """Check if required modules can be imported."""
    print_section("Checking Imports")
    
    required_modules = [
        'fastmcp',
        'numpy',
        'aiohttp',
        'aiohttp.web',
        'aiohttp_cors',
        'fastapi',
        'uvicorn',
        'pyvrm',
        'trimesh',
        'pygltflib'
    ]
    
    for module in required_modules:
        try:
            mod = importlib.import_module(module)
            print(f"✓ {module}: {mod.__file__}")
        except ImportError as e:
            print(f"✗ {module}: {e}")

def check_avatarmcp():
    """Check if avatarmcp can be imported."""
    print_section("Checking AvatarMCP")
    
    # Add src to path if not already there
    src_dir = str(Path(__file__).parent / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    try:
        import avatarmcp
        print(f"✓ avatarmcp imported from: {avatarmcp.__file__}")
        
        # Try to import server
        try:
            from avatarmcp import server
            print("✓ avatarmcp.server imported successfully")
            return True
        except ImportError as e:
            print(f"✗ Failed to import avatarmcp.server: {e}")
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import avatarmcp: {e}")
        traceback.print_exc()
        return False

def run_server():
    """Try to run the server."""
    print_section("Starting Server")
    
    # Add src to path if not already there
    src_dir = str(Path(__file__).parent / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    try:
        from avatarmcp.server import main
        print("✓ Server main function found")
        print("Starting server... (Press Ctrl+C to stop)")
        main()
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        traceback.print_exc()

def main():
    """Main function."""
    check_python()
    check_imports()
    
    if check_avatarmcp():
        if input("\nDo you want to try starting the server? (y/n): ").lower() == 'y':
            run_server()

if __name__ == "__main__":
    main()
