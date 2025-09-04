"""
Basic tests for the AvatarMCP server.

These tests verify that the server can start up and handle basic operations.
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "test_assets", "test_avatar.vrm"
)

@pytest.fixture(scope="module")
def test_assets_dir():
    """Create a test assets directory if it doesn't exist."""
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "test_assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create a dummy VRM file if it doesn't exist
    if not os.path.exists(TEST_MODEL_PATH):
        with open(TEST_MODEL_PATH, 'wb') as f:
            f.write(b"VRM" + b"\0" * 100)  # Minimal VRM header
    
    return assets_dir

@pytest.fixture(scope="module")
def test_app():
    """Create a test instance of the AvatarMCP application."""
    from avatarmcp.core.app import AvatarMCP
    
    # Disable visualization for tests
    app = AvatarMCP(enable_visualization=False)
    return app

@pytest.mark.asyncio
async def test_server_startup(test_app):
    """Test that the server can start up and shut down cleanly."""
    try:
        # Start the server
        await test_app.start()
        
        # Verify server is running
        assert test_app.is_running() is True
        
        # Test basic functionality
        assert test_app.osc is not None
        assert test_app.mcp is not None
        
    finally:
        # Clean up
        await test_app.stop()
        assert test_app.is_running() is False

@pytest.mark.asyncio
async def test_vrm_loading(test_app, test_assets_dir):
    """Test loading a VRM model."""
    try:
        # Start the server
        await test_app.start()
        
        # Load a test model
        model = await test_app.load_vrm_model(TEST_MODEL_PATH)
        assert model is not None
        
        # Verify the model was loaded
        assert model.model_id in test_app.models
        assert test_app.active_model_id == model.model_id
        
        # List models
        models = await test_app.list_models()
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Unload the model
        await test_app.unload_model(model.model_id)
        assert model.model_id not in test_app.models
        
    finally:
        # Clean up
        await test_app.stop()

if __name__ == "__main__":
    # Run tests
    import sys
    sys.exit(pytest.main(["-v", "-s", __file__]))
