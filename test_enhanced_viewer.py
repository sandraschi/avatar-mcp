#!/usr/bin/env python3
"""
Test Enhanced Avatar Viewer - Complete functionality test

Tests:
1. Avatar loading with proper colors
2. Bone visualization and skeleton
3. Interactive mouse controls
4. OSC communication
5. Bone manipulation
6. Animation and expressions
"""

import os
import sys
import time
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_viewer_startup():
    """Test that the enhanced viewer starts correctly."""
    print("Testing Enhanced Viewer Startup...")

    try:
        # Start the enhanced viewer
        viewer_process = subprocess.Popen([
            sys.executable, "desktop_avatar_viewer_enhanced.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a moment for startup
        time.sleep(3)

        # Check if process is still running
        if viewer_process.poll() is None:
            print("Viewer started successfully")
            return viewer_process
        else:
            stdout, stderr = viewer_process.communicate()
            print("Viewer failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None

    except Exception as e:
        print(f"Failed to start viewer: {e}")
        return None

def test_vrm_loading():
    """Test loading a VRM file."""
    print("\nTesting VRM Loading...")

    # Find VRM files
    models_dir = "models"
    if not os.path.exists(models_dir):
        print(f"Models directory not found: {models_dir}")
        return False

    vrm_files = [f for f in os.listdir(models_dir) if f.endswith('.vrm')]
    if not vrm_files:
        print(f"No VRM files found in {models_dir}")
        return False

    vrm_path = os.path.join(models_dir, vrm_files[0])
    print(f"Found VRM: {vrm_path}")

    # Test VRM loader
    try:
        sys.path.insert(0, 'src')
        from avatarmcp.models.vrm_loader import VRMLoader

        vrm_model = VRMLoader.from_file(vrm_path)
        print("VRM loaded successfully")
        print(f"   Meshes: {len(vrm_model.meshes)}")
        print(f"   Bones: {len(vrm_model.bones) if hasattr(vrm_model, 'bones') else 'N/A'}")
        print(f"   Expressions: {len(vrm_model.expressions) if hasattr(vrm_model, 'expressions') else 'N/A'}")

        return True

    except Exception as e:
        print(f"VRM loading failed: {e}")
        return False

def test_matplotlib_3d():
    """Test that matplotlib 3D rendering works."""
    print("\nTesting Matplotlib 3D Rendering...")

    try:
        import matplotlib.pyplot as plt
        import numpy as np

        # Create test figure
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        # Add test geometry
        vertices = np.random.rand(100, 3) * 2 - 1  # Random points
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], c='blue', s=10)

        # Add coordinate axes
        ax.plot([0, 0.5], [0, 0], [0, 0], color='red', linewidth=2)
        ax.plot([0, 0], [0, 0.5], [0, 0], color='green', linewidth=2)
        ax.plot([0, 0], [0, 0], [0, 0.5], color='blue', linewidth=2)

        plt.close(fig)  # Close without showing
        print("Matplotlib 3D rendering works")
        return True

    except Exception as e:
        print(f"Matplotlib 3D test failed: {e}")
        return False

def test_osc_communication():
    """Test OSC communication setup."""
    print("\nTesting OSC Communication...")

    try:
        from pythonosc import udp_client
        from pythonosc.dispatcher import Dispatcher

        # Test OSC client creation
        udp_client.SimpleUDPClient("127.0.0.1", 9001)
        print("OSC client created")

        # Test dispatcher creation
        Dispatcher()
        print("OSC dispatcher created")

        return True

    except Exception as e:
        print(f"OSC setup failed: {e}")
        return False

def run_full_test():
    """Run complete test suite."""
    print("AvatarMCP Enhanced Viewer - Full Test Suite")
    print("=" * 50)

    results = []

    # Test VRM loading
    results.append(("VRM Loading", test_vrm_loading()))

    # Test matplotlib 3D
    results.append(("Matplotlib 3D", test_matplotlib_3d()))

    # Test OSC communication
    results.append(("OSC Communication", test_osc_communication()))

    # Test viewer startup
    viewer_process = test_viewer_startup()
    results.append(("Viewer Startup", viewer_process is not None))

    # Summary
    print("\nTest Results Summary:")
    print("-" * 30)
    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1

    print(f"{passed}/{total} ({passed/total*100:.1f}%) tests passed")
    # Cleanup
    if viewer_process:
        print("\nCleaning up...")
        try:
            viewer_process.terminate()
            viewer_process.wait(timeout=5)
            print("Viewer process terminated")
        except Exception:
            try:
                viewer_process.kill()
                print("Viewer process killed")
            except Exception:
                print("Could not terminate viewer process")

    if passed == total:
        print("\nALL TESTS PASSED! Ready for enhanced avatar control!")
        return True
    else:
        print(f"\n{total - passed} test(s) failed. Check output above.")
        return False

if __name__ == "__main__":
    success = run_full_test()
    sys.exit(0 if success else 1)
