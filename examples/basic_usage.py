"""
Basic Usage Example for AvatarMCP

This script demonstrates how to use AvatarMCP to load a VRM model,
apply animations, and update the avatar's pose programmatically.
"""
import asyncio
from pathlib import Path
from avatarmcp import AvatarService

async def main():
    # Initialize the AvatarService
    service = AvatarService()
    
    # Load a VRM model
    vrm_path = Path("path/to/your/avatar.vrm")
    if not vrm_path.exists():
        print(f"Error: VRM file not found at {vrm_path}")
        print("Please update the path to point to a valid .vrm file")
        return
    
    try:
        print(f"Loading VRM model from {vrm_path}...")
        avatar = service.load_vrm(str(vrm_path))
        print(f"Successfully loaded {avatar.metadata.get('title', 'Unnamed Avatar')}")
        print(f"Author: {avatar.metadata.get('author', 'Unknown')}")
        
        # Display available animations
        print("\nAvailable animations:")
        for anim in ["idle", "wave", "nod", "shake", "point"]:
            print(f"- {anim}")
        
        # Play some animations
        print("\nPlaying animations...")
        for anim in ["wave", "nod", "shake"]:
            print(f"Playing {anim} animation...")
            service.play_animation(avatar, anim)
            await asyncio.sleep(2)  # Wait for animation to complete
        
        # Update pose directly
        print("\nUpdating pose...")
        service.update_pose(avatar, {
            "head": {"rotation": {"x": 0.1, "y": 0.0, "z": 0.0}},
            "right_hand": {"gesture": "point"}
        })
        
        print("\nExample completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
