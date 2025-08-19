""
Test cases for the AvatarMCP API endpoints.
"""
import pytest
import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
import os

# Test configuration
TEST_MODEL_PATH = Path("tests/test_assets/sample.vrm")  # Update this path as needed
BASE_URL = "http://localhost:8080/api/v1"
WS_URL = "ws://localhost:8080/ws"

# Test data
TEST_AVATAR_DATA = {
    "name": "test_avatar",
    "model_id": "",  # Will be set during tests
    "position": {"x": 0, "y": 0, "z": 0},
    "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
    "scale": 1.0,
    "metadata": {"test": "data"}
}

# Helper functions
async def upload_test_model(client: httpx.AsyncClient) -> str:
    """Upload a test model and return its ID."""
    if not TEST_MODEL_PATH.exists():
        pytest.skip(f"Test model not found at {TEST_MODEL_PATH}")
    
    with open(TEST_MODEL_PATH, "rb") as f:
        files = {"file": (TEST_MODEL_PATH.name, f, "application/octet-stream")}
        response = await client.post(f"{BASE_URL}/models", files=files)
    
    assert response.status_code == 201
    return response.json()["id"]

# Test classes
class TestModelAPI:
    """Test cases for the Model API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_models_empty(self, test_client):
        """Test listing models when no models are present."""
        response = await test_client.get(f"{BASE_URL}/models")
        assert response.status_code == 200
        assert response.json() == []
    
    @pytest.mark.asyncio
    async def test_upload_model(self, test_client):
        """Test uploading a model."""
        model_id = await upload_test_model(test_client)
        assert model_id is not None
        
        # Verify the model was uploaded
        response = await test_client.get(f"{BASE_URL}/models/{model_id}")
        assert response.status_code == 200
        model_data = response.json()
        assert model_data["id"] == model_id
        assert "name" in model_data
        
        # Clean up
        await test_client.delete(f"{BASE_URL}/models/{model_id}")

class TestAvatarAPI:
    """Test cases for the Avatar API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_avatar(self, test_client, test_model_id):
        """Test creating an avatar."""
        avatar_data = TEST_AVATAR_DATA.copy()
        avatar_data["model_id"] = test_model_id
        
        response = await test_client.post(
            f"{BASE_URL}/avatars",
            json=avatar_data
        )
        
        assert response.status_code == 201
        avatar = response.json()
        assert avatar["name"] == avatar_data["name"]
        assert avatar["model_id"] == test_model_id
        
        return avatar["id"]
    
    @pytest.mark.asyncio
    async def test_get_avatar(self, test_client, test_avatar_id):
        """Test retrieving an avatar."""
        response = await test_client.get(f"{BASE_URL}/avatars/{test_avatar_id}")
        assert response.status_code == 200
        avatar = response.json()
        assert avatar["id"] == test_avatar_id

class TestAnimationAPI:
    """Test cases for the Animation API endpoints."""
    
    @pytest.mark.asyncio
    async def test_play_animation(self, test_client, test_avatar_id):
        """Test playing an animation on an avatar."""
        animation_data = {
            "animation_name": "idle",
            "loop": True,
            "speed": 1.0,
            "blend_time": 0.2
        }
        
        response = await test_client.post(
            f"{BASE_URL}/avatars/{test_avatar_id}/animation/play",
            json=animation_data
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "playing"
    
    @pytest.mark.asyncio
    async def test_stop_animation(self, test_client, test_avatar_id):
        """Test stopping an animation."""
        response = await test_client.post(
            f"{BASE_URL}/avatars/{test_avatar_id}/animation/stop"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "idle"

class TestWebSocketAPI:
    """Test cases for the WebSocket API."""
    
    @pytest.mark.asyncio
    async def test_websocket_updates(self, test_client, test_avatar_id):
        """Test receiving WebSocket updates for avatar changes."""
        import websockets
        
        # Connect to WebSocket
        async with websockets.connect(f"{WS_URL}/avatars/{test_avatar_id}") as websocket:
            # Send a position update
            new_position = {"x": 1, "y": 2, "z": 3}
            await test_client.patch(
                f"{BASE_URL}/avatars/{test_avatar_id}",
                json={"position": new_position}
            )
            
            # Verify the update is received via WebSocket
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            update = json.loads(message)
            assert update["type"] == "avatar_updated"
            assert update["data"]["id"] == test_avatar_id
            assert update["data"]["position"] == new_position

# Fixtures
@pytest.fixture
async def test_client():
    """Create a test client for the API."""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.fixture
async def test_model_id(test_client):
    """Fixture to create a test model and clean up afterward."""
    model_id = await upload_test_model(test_client)
    yield model_id
    await test_client.delete(f"{BASE_URL}/models/{model_id}")

@pytest.fixture
async def test_avatar(test_client, test_model_id):
    """Fixture to create a test avatar and clean up afterward."""
    avatar_data = TEST_AVATAR_DATA.copy()
    avatar_data["model_id"] = test_model_id
    
    response = await test_client.post(f"{BASE_URL}/avatars", json=avatar_data)
    assert response.status_code == 201
    avatar = response.json()
    
    yield avatar
    
    # Clean up
    await test_client.delete(f"{BASE_URL}/avatars/{avatar['id']}")

@pytest.fixture
async def test_avatar_id(test_avatar):
    """Fixture to get the ID of a test avatar."""
    return test_avatar["id"]
