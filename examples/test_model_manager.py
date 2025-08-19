"""
Test script for the VRM Model Manager

This script demonstrates the usage of the VRM model manager with caching,
validation, and resource management features.
"""
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import avatarmcp
sys.path.append(str(Path(__file__).parent.parent))

from avatarmcp import (
    AvatarService,
    load_vrm,
    unload_model,
    clear_model_cache,
    get_cache_info,
    validate_vrm_file
)

def print_separator():
    print("\n" + "="*80 + "\n")

def test_model_loading():
    """Test basic model loading functionality."""
    print("Testing model loading...")
    
    # Get a sample VRM file path (replace with actual path)
    sample_vrm = input("Enter path to a VRM file: ").strip('"')
    
    if not os.path.exists(sample_vrm):
        print(f"Error: File not found: {sample_vrm}")
        return
    
    # Test validation
    print("\nValidating VRM file...")
    is_valid, issues = validate_vrm_file(sample_vrm)
    if is_valid:
        print("✅ VRM file is valid")
    else:
        print("❌ VRM file validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return
    
    # Load the model
    print("\nLoading model...")
    model = load_vrm(sample_vrm, validate=True)
    
    if model is None:
        print("❌ Failed to load model")
        return
    
    print(f"✅ Successfully loaded model: {sample_vrm}")
    print(f"  - Meshes: {len(model.meshes)}")
    print(f"  - Materials: {len(model.materials)}")
    print(f"  - Bones: {len(model.bones)}")
    print(f"  - Blend Shapes: {len(model.blend_shapes)}")
    
    # Load again to test caching
    print("\nLoading model again (should use cache)...")
    start_time = time.time()
    model_cached = load_vrm(sample_vrm)
    load_time = time.time() - start_time
    
    if model_cached is model:
        print(f"✅ Used cached model (took {load_time:.4f} seconds)")
    else:
        print(f"❌ Caching not working as expected")
    
    # Force reload
    print("\nForce reloading model...")
    start_time = time.time()
    model_reloaded = load_vrm(sample_vrm, force_reload=True)
    load_time = time.time() - start_time
    
    if model_reloaded is not model:
        print(f"✅ Successfully reloaded model (took {load_time:.4f} seconds)")
    else:
        print("❌ Force reload didn't create a new instance")
    
    # Test unloading
    print("\nTesting model unloading...")
    if unload_model(sample_vrm):
        print("✅ Successfully unloaded model from cache")
    else:
        print("❌ Failed to unload model")
    
    # Check cache info
    cache_info = get_cache_info()
    print("\nCache info:")
    for key, value in cache_info.items():
        print(f"  - {key}: {value}")
    
    # Clear cache
    print("\nClearing cache...")
    clear_model_cache()
    print("✅ Cache cleared")
    
    # Final cache info
    cache_info = get_cache_info()
    print("\nFinal cache info:")
    for key, value in cache_info.items():
        print(f"  - {key}: {value}")

def test_avatar_service():
    """Test the AvatarService with model management."""
    print("\nTesting AvatarService with model management...")
    
    # Get a sample VRM file path (replace with actual path)
    sample_vrm = input("Enter path to a VRM file: ").strip('"')
    
    if not os.path.exists(sample_vrm):
        print(f"Error: File not found: {sample_vrm}")
        return
    
    # Create a new service
    service = AvatarService()
    
    # Load an avatar
    print("\nLoading avatar...")
    avatar_id = "test_avatar"
    metadata = service.load_vrm(sample_vrm, avatar_id=avatar_id)
    
    if metadata:
        print(f"✅ Successfully loaded avatar: {avatar_id}")
        print("Avatar metadata:")
        for key, value in metadata.items():
            if key != 'cache_info':  # Skip cache info for now
                print(f"  - {key}: {value}")
    else:
        print("❌ Failed to load avatar")
        return
    
    # List loaded avatars
    print("\nLoaded avatars:")
    avatars = service.list_loaded_avatars(include_cache_info=True)
    for avatar in avatars:
        print(f"- {avatar['id']} (cached: {avatar.get('cached', False)})")
    
    # Get cache info
    cache_info = service.get_cache_info()
    print("\nService cache info:")
    for key, value in cache_info.items():
        print(f"  - {key}: {value}")
    
    # Unload avatar
    print("\nUnloading avatar...")
    if service.unload_avatar(avatar_id, remove_from_cache=True):
        print("✅ Successfully unloaded avatar and removed from cache")
    else:
        print("❌ Failed to unload avatar")
    
    # Clear service cache
    print("\nClearing service cache...")
    result = service.clear_cache()
    print(f"Result: {result['status']} - {result['message']}")

def main():
    """Main test function."""
    print("VRM Model Manager Test")
    print("======================")
    
    try:
        test_model_loading()
        print_separator()
        test_avatar_service()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
