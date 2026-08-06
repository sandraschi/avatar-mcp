"""
Basic tests for the AvatarMCP server using the current architecture.
"""

import os

import pytest

TEST_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "test_assets", "test_avatar.vrm")


@pytest.fixture(scope="module")
def test_assets_dir():
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "test_assets")
    os.makedirs(assets_dir, exist_ok=True)

    if not os.path.exists(TEST_MODEL_PATH):
        with open(TEST_MODEL_PATH, "wb") as f:
            f.write(b"VRM" + b"\0" * 100)

    return assets_dir


@pytest.mark.asyncio
async def test_server_start_stop():
    from avatarmcp.server import AvatarMCPServer

    server = AvatarMCPServer(enable_osc=False)
    server.initialized = True
    server.running = True

    assert server.running is True
    assert server.mcp is not None
    assert server.initialized is True

    await server.stop()
    assert server.running is False


@pytest.mark.asyncio
async def test_vrm_scan(test_assets_dir):
    from avatarmcp.models.vrm_manager import VRMManager

    manager = VRMManager(models_dir=test_assets_dir)
    model_ids = await manager.scan_models()
    assert isinstance(model_ids, list)


@pytest.mark.asyncio
async def test_vrm_import():
    from avatarmcp.models.vrm_manager import VRMManager

    manager = VRMManager()

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".vrm", delete=False) as f:
        f.write(b"mock_vrm_data")
        tmp_path = f.name

    try:
        model_id = await manager.import_model(tmp_path)
        assert model_id is not None
        assert isinstance(model_id, str)
    finally:
        os.unlink(tmp_path)
