"""
Script to connect a VRoid avatar to Claude Desktop using AvatarMCP.
"""
import os
import sys
import json
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_avatar(avatar_path):
    """Load the VRM avatar into the AvatarMCP server."""
    try:
        from avatarmcp.server import load_vrm
        
        print(f"Loading avatar: {avatar_path}")
        result = load_vrm(avatar_path)
        
        if result.get("status") == "success":
            print(f"Successfully loaded avatar with ID: {result.get('model_id')}")
            return result["model_id"]
        else:
            print(f"Failed to load avatar: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error loading avatar: {str(e)}")
        return None

def main():
    print("=== Claude Desktop VRM Avatar Setup ===\n")
    
    # Path to the VRM file
    vrm_path = Path("examples/Nekomimi-chan.vrm")
    
    if not vrm_path.exists():
        print(f"Error: VRM file not found at {vrm_path}")
        print("Please make sure the VRM file exists in the examples directory.")
        return
    
    print(f"Found VRM avatar: {vrm_path.name}")
    print("\nMake sure the AvatarMCP server is running in another terminal.")
    print("You can start it with: python -m avatarmcp.server\n")
    
    input("Press Enter to load the avatar into the server...")
    
    # Load the avatar
    avatar_id = load_avatar(str(vrm_path.absolute()))
    
    if not avatar_id:
        print("\nFailed to load the avatar. Please check the error messages above.")
        return
    
    print("\n=== Setup Complete! ===")
    print("The avatar is now loaded in the AvatarMCP server.")
    print("\nIn Claude Desktop, use these settings to connect:")
    print(f"- MCP Server: localhost:8080")
    print(f"- Avatar ID: {avatar_id}")
    print("\nMake sure to enable MCP support in Claude Desktop settings.")

if __name__ == "__main__":
    main()
