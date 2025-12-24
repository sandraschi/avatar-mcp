"""Test script for VRM loading functionality."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from avatarmcp.server import list_blend_shapes, list_bones, load_vrm


def test_vrm_loading(vrm_path):
    """Test loading a VRM file and list its contents."""
    print(f"\nTesting VRM: {vrm_path}")

    # Load VRM
    result = load_vrm(vrm_path)
    if result.get("status") != "success":
        print(f"❌ Failed to load VRM: {result.get('error')}")
        return

    model_id = result["model_id"]
    print(f"✅ Loaded VRM. Model ID: {model_id}")

    # List bones
    bones = list_bones(model_id)
    if bones.get("status") == "success":
        print(f"\nBones ({len(bones.get('bones', []))}):")
        print(f"Root bones: {', '.join(bones.get('root_bones', [])[:3])}...")

    # List blend shapes
    blend_shapes = list_blend_shapes(model_id)
    if blend_shapes.get("status") == "success":
        print(f"\nBlend Shapes ({len(blend_shapes.get('blend_shapes', {}))}):")
        print(", ".join(list(blend_shapes["blend_shapes"].keys())[:5]) + "...")


if __name__ == "__main__":
    vrm_path = sys.argv[1] if len(sys.argv) > 1 else "Nekomimi-chan.vrm"
    test_vrm_loading(vrm_path)
