import sys
import os
from pathlib import Path

def main():
    print("=== Environment Test ===")
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Test file access
    test_file = Path(__file__).parent / "examples" / "Nekomimi-chan.vrm"
    print(f"\n=== File Access Test ===")
    print(f"File exists: {test_file.exists()}")
    if test_file.exists():
        print(f"File size: {test_file.stat().st_size} bytes")
    
    # Test imports
    print("\n=== Import Test ===")
    try:
        import pygltflib
        print(f"pygltflib version: {pygltflib.__version__}")
    except ImportError:
        print("pygltflib not installed. Please run: pip install pygltflib")
    except Exception as e:
        print(f"Error importing pygltflib: {e}")

if __name__ == "__main__":
    main()
