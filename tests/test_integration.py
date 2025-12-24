"""
Integration tests for the AvatarMCP server.

These tests verify that the server can start up and handle basic operations.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "test_assets", "test_avatar.vrm")


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI application."""
    from avatarmcp.server import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def test_assets_dir():
    """Create a test assets directory if it doesn't exist."""
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "test_assets")
    os.makedirs(assets_dir, exist_ok=True)
    return assets_dir


@pytest.mark.asyncio
async def test_server_startup():
    """Test that the server can start up and shut down cleanly."""
    from avatarmcp.server import AvatarMCPServer

    server = AvatarMCPServer()
    try:
        # Start the server
        await server.start()

        # Verify server is running
        assert server.running is True

        # Test basic API endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    finally:
        # Clean up
        await server.stop()
        assert server.running is False


@pytest.mark.asyncio
async def test_vrm_loading(test_assets_dir: str):
    """Test loading a VRM model."""
    from avatarmcp.models.vrm_manager import VRMManager

    # Create a test VRM file if it doesn't exist
    test_vrm_path = os.path.join(test_assets_dir, "test_avatar.vrm")
    if not os.path.exists(test_vrm_path):
        logger.warning("Test VRM file not found, creating a placeholder")
        with open(test_vrm_path, "wb") as f:
            f.write(b"VRM" + b"\0" * 100)  # Minimal VRM header

    # Initialize VRM manager
    manager = VRMManager(models_dir=test_assets_dir)

    # Scan for models
    model_ids = await manager.scan_models()
    assert isinstance(model_ids, list)

    # If we have a test model, try to load it
    if model_ids:
        model_id = model_ids[0]
        model = await manager.load_model(model_id)
        assert model is not None
        # Check that model is a dict with expected keys
        assert isinstance(model, dict)
        assert "model_id" in model or "id" in model

        # Test getting model info
        model_info = await manager.get_model_info(model_id)
        assert model_info is not None
        assert "id" in model_info
        assert model_info["id"] == model_id


@pytest.mark.asyncio
async def test_osc_communication():
    """Test OSC communication with the server."""
    from pythonosc import dispatcher, udp_client
    from pythonosc.osc_server import AsyncIOOSCUDPServer

    # Test configuration
    server_port = 9001
    client_port = 9000

    # Create OSC client
    osc_client = udp_client.SimpleUDPClient("127.0.0.1", server_port)

    # Set up OSC server for testing
    received_messages = []

    def handle_osc_message(address: str, *args):
        received_messages.append({"address": address, "args": args})

    # Create dispatcher and server
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.set_default_handler(handle_osc_message)

    # Start OSC server
    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer(("127.0.0.1", client_port), osc_dispatcher, loop)
    transport, protocol = await server.create_serve_endpoint()

    try:
        # Send test OSC message
        test_address = "/avatar/parameters/TestParam"
        test_value = 1.0
        osc_client.send_message(test_address, test_value)

        # Wait for message to be received
        await asyncio.sleep(0.1)

        # Check if message was received
        assert len(received_messages) > 0
        assert received_messages[0]["address"] == test_address
        assert received_messages[0]["args"][0] == test_value

    finally:
        # Clean up
        transport.close()


if __name__ == "__main__":
    # Run tests
    import sys

    sys.exit(pytest.main(["-v", "-s", __file__]))
