"""
Test script for AvatarMCP FastMCP server.
This script sends commands to the running AvatarMCP server using FastMCP stdio communication.
"""
import json
import sys
import time
from pathlib import Path

def send_command(command: str, **params) -> dict:
    """Send a command to the FastMCP server via stdio."""
    # Create the command message
    message = {
        "jsonrpc": "2.0",
        "method": command,
        "params": params,
        "id": 1
    }
    
    # Print the message to stdout (which is read by FastMCP)
    print(json.dumps(message), flush=True)
    
    # Read the response from stdin
    response = json.loads(sys.stdin.readline())
    
    # Check for errors
    if "error" in response:
        print(f"Error: {response['error']}", file=sys.stderr)
    
    return response

def main():
    """Main test function."""
    print("Testing AvatarMCP FastMCP server...")
    
    # Test list_models (should be empty initially)
    print("\nListing models (should be empty):")
    response = send_command("list_models")
    print(json.dumps(response, indent=2))
    
    # Test loading a VRM model (update the path to a valid VRM file)
    vrm_path = input("\nEnter path to a VRM file to test with (or press Enter to skip): ")
    if vrm_path and Path(vrm_path).exists():
        print(f"\nLoading VRM model from {vrm_path}...")
        response = send_command("load_vrm", file_path=vrm_path)
        print(json.dumps(response, indent=2))
        
        if "result" in response and "model_id" in response["result"]:
            model_id = response["result"]["model_id"]
            
            # List models again to see the loaded model
            print("\nListing models after loading:")
            response = send_command("list_models")
            print(json.dumps(response, indent=2))
            
            # Test playing an animation
            print("\nTesting animation playback:")
            response = send_command(
                "play_animation",
                model_id=model_id,
                animation_name="idle",
                loop=True
            )
            print(json.dumps(response, indent=2))
            
            # Wait a bit to see the animation
            print("\nAnimation playing for 5 seconds...")
            time.sleep(5)
            
            # Stop the animation
            print("\nStopping animation:")
            response = send_command(
                "play_animation",
                model_id=model_id,
                animation_name=""  # Empty string to stop animation
            )
            print(json.dumps(response, indent=2))
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
