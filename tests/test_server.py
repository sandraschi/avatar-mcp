"""
Tests for the AvatarMCPServer implementation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def server():
    """Create an AvatarMCPServer instance for testing."""
    with patch("avatarmcp.server.OSCManager") as mock_osc_cls:
        mock_osc = MagicMock()
        mock_osc.initialize = AsyncMock()
        mock_osc.start = AsyncMock()
        mock_osc.stop = AsyncMock()
        mock_osc.enabled = False
        mock_osc.initialized = False
        mock_osc_cls.return_value = mock_osc

        from avatarmcp.server import AvatarMCPServer

        srv = AvatarMCPServer(enable_osc=False)
        srv.initialized = True
        srv.running = True
        return srv


@pytest.mark.asyncio
async def test_server_start_stop(server):
    """Test server start and stop lifecycle."""
    assert server.running is True
    assert server.initialized is True
    assert server.mcp is not None


@pytest.mark.asyncio
async def test_server_has_portmanteau_tools(server):
    """Test that server initializes all portmanteau tool classes."""
    assert server.avatar_manager_tool is not None
    assert server.animation_manager_tool is not None
    assert server.system_monitor_tool is not None
    assert server.chat_manager_tool is not None
    assert server.artifact_manager_tool is not None
    assert server.audio_manager_tool is not None
    assert server.behavior_manager_tool is not None
    assert server.collaboration_manager_tool is not None
    assert server.content_manager_tool is not None
    assert server.emotion_manager_tool is not None
    assert server.interaction_manager_tool is not None
    assert server.performance_manager_tool is not None
    assert server.unity_integration_tool is not None
    assert server.unity_window_manager_tool is not None
    assert server.unity_config_manager_tool is not None


@pytest.mark.asyncio
async def test_server_has_vrm_manager(server):
    """Test that server initializes VRMManager."""
    assert server.vrm_manager is not None


@pytest.mark.asyncio
async def test_server_send_osc_message(server):
    """Test _send_osc_message helper."""
    # No OSC client -> returns False
    server.osc_manager.osc_client = None
    result = server._send_osc_message("/test/address", 1, 2, 3)
    assert result is False


@pytest.mark.asyncio
async def test_server_load_empty(server):
    """Test server starts with empty loaded models."""
    assert server.loaded_models == {}
    assert server.active_model_id is None
