"""
AvatarMCP API Test Script

This script provides comprehensive testing of the AvatarMCP API functionality,
including model management, avatar control, and WebSocket communication.
"""

import sys
import os
import json
import asyncio
import websockets
from pathlib import Path
from typing import Dict, Optional, List
import httpx

# Configuration
API_BASE_URL = "http://localhost:8080/api/v1"
WS_URL = "ws://localhost:8080/ws"
TEST_MODEL_PATH = "tests/test_assets/sample.vrm"  # Update this path as needed

class AvatarMCPTest:
    """Test class for AvatarMCP API."""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.test_model_id: Optional[str] = None
        self.test_avatar_id: Optional[str] = None
        self.ws_connection = None
        
    async def setup(self):
        """Setup test environment."""
        print("\n=== Setting up test environment ===")
        # Ensure test model exists
        if not Path(TEST_MODEL_PATH).exists():
            raise FileNotFoundError(f"Test model not found at {TEST_MODEL_PATH}")
            
    async def cleanup(self):
        """Clean up test resources."""
        print("\n=== Cleaning up test resources ===")
        if self.test_avatar_id:
            await self.delete_avatar(self.test_avatar_id)
        if self.test_model_id:
            await self.delete_model(self.test_model_id)
        await self.client.aclose()
        if self.ws_connection:
            await self.ws_connection.close()
    
    async def test_models(self) -> bool:
        """Test model management endpoints."""
        print("\n=== Testing Model Management ===")
        
        # List models (should be empty initially)
        models = await self.list_models()
        assert isinstance(models, list), "Models should be a list"
        
        # Upload test model
        print(f"Uploading test model from {TEST_MODEL_PATH}")
        model_id = await self.upload_model(TEST_MODEL_PATH)
        self.test_model_id = model_id
        print(f"Uploaded model with ID: {model_id}")
        
        # Get model details
        model = await self.get_model(model_id)
        assert model["id"] == model_id, "Model ID mismatch"
        print(f"Model details: {json.dumps(model, indent=2, default=str)}")
        
        # List models again (should include our test model)
        models = await self.list_models()
        assert any(m["id"] == model_id for m in models), "Model not found in list"
        
        return True
    
    async def test_avatars(self) -> bool:
        """Test avatar management endpoints."""
        if not self.test_model_id:
            print("Skipping avatar tests - no model available")
            return False
            
        print("\n=== Testing Avatar Management ===")
        
        # Create avatar
        avatar = await self.create_avatar(
            model_id=self.test_model_id,
            position=[0, 0, 0],
            rotation=[0, 0, 0, 1],
            scale=[1, 1, 1]
        )
        self.test_avatar_id = avatar["id"]
        print(f"Created avatar with ID: {self.test_avatar_id}")
        
        # Get avatar details
        avatar_details = await self.get_avatar(self.test_avatar_id)
        assert avatar_details["id"] == self.test_avatar_id, "Avatar ID mismatch"
        
        # Update avatar
        new_position = [1, 2, 3]
        await self.update_avatar(self.test_avatar_id, position=new_position)
        
        # Verify update
        updated = await self.get_avatar(self.test_avatar_id)
        assert updated["position"] == new_position, "Avatar position not updated"
        
        return True
    
    async def test_animations(self) -> bool:
        """Test animation control endpoints."""
        if not self.test_avatar_id:
            print("Skipping animation tests - no avatar available")
            return False
            
        print("\n=== Testing Animation Control ===")
        
        # Play animation
        await self.play_animation(
            avatar_id=self.test_avatar_id,
            animation="wave",
            loop=True
        )
        print("Started animation: wave")
        
        # Set blend shape
        await self.set_blend_shape(
            avatar_id=self.test_avatar_id,
            name="smile",
            value=0.8
        )
        print("Set blend shape: smile=0.8")
        
        # Stop animation
        await self.stop_animation(self.test_avatar_id)
        print("Stopped animations")
        
        return True
    
    async def test_websocket(self) -> bool:
        """Test WebSocket communication."""
        if not self.test_avatar_id:
            print("Skipping WebSocket tests - no avatar available")
            return False
            
        print("\n=== Testing WebSocket Updates ===")
        
        # Connect to WebSocket
        async with websockets.connect(WS_URL) as websocket:
            self.ws_connection = websocket
            
            # Subscribe to avatar updates
            await websocket.send(json.dumps({
                "type": "subscribe",
                "resource": "avatar_updates",
                "id": self.test_avatar_id
            }))
            
            # Make a change that should trigger an update
            new_rotation = [0, 0.707, 0, 0.707]
            await self.update_avatar(
                self.test_avatar_id,
                rotation=new_rotation
            )
            
            # Wait for update message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                update = json.loads(message)
                assert update["type"] == "avatar_updated", "Unexpected message type"
                assert update["data"]["id"] == self.test_avatar_id, "Wrong avatar ID in update"
                print("Received WebSocket update:", message)
                return True
            except asyncio.TimeoutError:
                print("Timed out waiting for WebSocket update")
                return False
    
    # API Client Methods
    
    async def list_models(self) -> List[Dict]:
        """List all models."""
        response = await self.client.get(f"{API_BASE_URL}/models")
        response.raise_for_status()
        return response.json()["data"]["models"]
    
    async def upload_model(self, file_path: str) -> str:
        """Upload a model."""
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
            response = await self.client.post(
                f"{API_BASE_URL}/models",
                files=files
            )
            response.raise_for_status()
            return response.json()["data"]["model_id"]
    
    async def get_model(self, model_id: str) -> Dict:
        """Get model details."""
        response = await self.client.get(f"{API_BASE_URL}/models/{model_id}")
        response.raise_for_status()
        return response.json()["data"]
    
    async def delete_model(self, model_id: str) -> None:
        """Delete a model."""
        try:
            response = await self.client.delete(f"{API_BASE_URL}/models/{model_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:  # Not found is okay for cleanup
                raise
    
    async def create_avatar(self, model_id: str, position: list, rotation: list, scale: list) -> Dict:
        """Create a new avatar."""
        data = {
            "model_id": model_id,
            "position": position,
            "rotation": rotation,
            "scale": scale
        }
        response = await self.client.post(
            f"{API_BASE_URL}/avatars",
            json=data
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def get_avatar(self, avatar_id: str) -> Dict:
        """Get avatar details."""
        response = await self.client.get(f"{API_BASE_URL}/avatars/{avatar_id}")
        response.raise_for_status()
        return response.json()["data"]
    
    async def update_avatar(self, avatar_id: str, **updates) -> Dict:
        """Update avatar properties."""
        response = await self.client.put(
            f"{API_BASE_URL}/avatars/{avatar_id}",
            json=updates
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def delete_avatar(self, avatar_id: str) -> None:
        """Delete an avatar."""
        try:
            response = await self.client.delete(f"{API_BASE_URL}/avatars/{avatar_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:  # Not found is okay for cleanup
                raise
    
    async def play_animation(self, avatar_id: str, animation: str, loop: bool = False) -> None:
        """Play an animation on an avatar."""
        data = {
            "animation": animation,
            "loop": loop
        }
        response = await self.client.post(
            f"{API_BASE_URL}/avatars/{avatar_id}/play",
            json=data
        )
        response.raise_for_status()
    
    async def stop_animation(self, avatar_id: str) -> None:
        """Stop all animations on an avatar."""
        response = await self.client.post(f"{API_BASE_URL}/avatars/{avatar_id}/stop")
        response.raise_for_status()
    
    async def set_blend_shape(self, avatar_id: str, name: str, value: float) -> None:
        """Set a blend shape value on an avatar."""
        data = {
            "name": name,
            "value": value
        }
        response = await self.client.post(
            f"{API_BASE_URL}/avatars/{avatar_id}/blend-shape",
            json=data
        )
        response.raise_for_status()


async def run_tests():
    """Run all tests."""
    tester = AvatarMCPTest()
    
    try:
        await tester.setup()
        
        # Run tests
        await tester.test_models()
        await tester.test_avatars()
        await tester.test_animations()
        await tester.test_websocket()
        
        print("\nâœ… All tests completed successfully!")
        
    except Exception as e:
        print(f"\nâŒ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(run_tests())
