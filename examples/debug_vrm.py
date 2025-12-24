import os
import sys
import traceback
from pathlib import Path


def debug_script():
    print("=== Python Environment ===")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")

    try:
        # Test basic imports
        print("\n=== Testing Imports ===")
        from pygltflib import GLTF2

        print("✓ All required imports successful")

        # Test file access
        print("\n=== Testing File Access ===")
        vrm_path = Path(__file__).parent / "Nekomimi-chan.vrm"
        print(f"VRM file exists: {vrm_path.exists()}")
        print(f"VRM file size: {vrm_path.stat().st_size} bytes")

        # Try to load the VRM file
        print("\n=== Attempting to load VRM file ===")
        temp_glb = vrm_path.with_suffix(".glb")
        try:
            # Try to rename the file
            vrm_path.rename(temp_glb)
            print("✓ Successfully renamed to .glb")

            try:
                gltf = GLTF2().load(temp_glb.as_posix())
                print("✓ Successfully loaded GLTF file")

                # Try to access VRM extension
                if hasattr(gltf, "extensions") and gltf.extensions:
                    print("✓ GLTF extensions found")
                    if "VRM" in gltf.extensions:
                        print("✓ VRM extension found")
                        vrm_ext = gltf.extensions["VRM"]
                        print(
                            f"VRM Version: {vrm_ext.specVersion if hasattr(vrm_ext, 'specVersion') else 'Not specified'}"
                        )
                    else:
                        print("⚠ No VRM extension found in GLTF")
                else:
                    print("⚠ No extensions found in GLTF")

            except Exception as e:
                print(f"❌ Failed to load GLTF: {str(e)}")
                print("\n=== Traceback ===")
                traceback.print_exc()

            finally:
                # Always try to rename back
                try:
                    temp_glb.rename(vrm_path)
                    print("✓ Successfully renamed back to .vrm")
                except Exception as e:
                    print(f"⚠ Failed to rename back to .vrm: {str(e)}")

        except Exception as e:
            print(f"❌ Failed to rename file: {str(e)}")
            print("\n=== Traceback ===")
            traceback.print_exc()

    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("\n=== Traceback ===")
        traceback.print_exc()
        print("\n=== Possible Solutions ===")
        print("1. Make sure you have activated the virtual environment")
        print("2. Install required packages: pip install pygltflib")
        print("3. Check your Python environment")


if __name__ == "__main__":
    debug_script()
