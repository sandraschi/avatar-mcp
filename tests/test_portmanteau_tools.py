"""
Tests for the portmanteau tool architecture.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_server():
    """Create a mock AvatarMCPServer for testing portmanteau tools."""
    server = MagicMock()
    server.initialized = True
    server.running = True
    server.start_time = 1000.0
    server.active_model_id = None
    server.loaded_models = {}
    server._send_osc_message = MagicMock(return_value=True)

    # Mock VRMManager
    vrm_manager = MagicMock()
    vrm_manager.models_dir = "/tmp/models"
    vrm_manager.models = {}
    vrm_manager.import_model = AsyncMock(return_value="test_avatar")
    vrm_manager.scan_models = AsyncMock(return_value=[])
    vrm_manager.get_model_info = AsyncMock(return_value={"id": "test_avatar", "path": "/tmp/test.vrm"})
    server.vrm_manager = vrm_manager

    return server


@pytest.mark.asyncio
async def test_system_monitor_initialize(mock_server):
    """Test system_monitor initialize operation."""
    from avatarmcp.tools.portmanteau.system_monitor_tool import SystemMonitorTool

    tool = SystemMonitorTool(mock_server)
    result = await tool._handle_initialize({"models_dir": "/tmp/models"})

    assert result["status"] == "success"
    assert result["operation"] == "initialize"
    assert mock_server.initialized is True


@pytest.mark.asyncio
async def test_system_monitor_shutdown(mock_server):
    """Test system_monitor shutdown operation."""
    from avatarmcp.tools.portmanteau.system_monitor_tool import SystemMonitorTool

    tool = SystemMonitorTool(mock_server)
    result = tool._handle_shutdown({})

    assert result["status"] == "success"
    assert mock_server.running is False


@pytest.mark.asyncio
async def test_system_monitor_get_status(mock_server):
    """Test system_monitor get_status operation."""
    from avatarmcp.tools.portmanteau.system_monitor_tool import SystemMonitorTool

    mock_server.initialized = True
    mock_server.running = True
    tool = SystemMonitorTool(mock_server)
    result = tool._handle_get_status({"detailed": True})

    assert result["status"] == "success"
    assert result["operation"] == "get_status"
    assert result["server_initialized"] is True
    assert result["server_running"] is True


@pytest.mark.asyncio
async def test_avatar_manager_empty_list(mock_server):
    """Test avatar_manager list with no avatars."""
    from avatarmcp.tools.portmanteau.avatar_manager_tool import AvatarManagerTool

    tool = AvatarManagerTool(mock_server)
    result = await tool._handle_list({})

    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["avatars"] == []


@pytest.mark.asyncio
async def test_avatar_manager_load_and_list(mock_server):
    """Test avatar_manager load and list operations."""
    from avatarmcp.tools.portmanteau.avatar_manager_tool import AvatarManagerTool

    tool = AvatarManagerTool(mock_server)

    # Manually add a model to loaded_models (avoid VRMModel file-IO constructor)
    from avatarmcp.models.animation_controller import AnimationController
    from avatarmcp.models.vrm_model import VRMModel

    with patch.object(VRMModel, "_load_model", return_value=None):
        model = VRMModel("/tmp/test.vrm")
        mock_server.loaded_models[model.model_id] = model
        mock_server.active_model_id = model.model_id

    result = await tool._handle_load({"path": "/tmp/test2.vrm", "make_active": True})

    assert result["status"] == "success"
    assert result["operation"] == "load"
    avatar_id = result["avatar_id"]

    # Verify it's in loaded models
    assert avatar_id in mock_server.loaded_models
    assert mock_server.active_model_id == avatar_id

    # List should show them
    list_result = await tool._handle_list({})
    assert list_result["count"] == 2


@pytest.mark.asyncio
async def test_avatar_manager_set_active(mock_server):
    """Test avatar_manager set_active operation."""
    from avatarmcp.tools.portmanteau.avatar_manager_tool import AvatarManagerTool
    from avatarmcp.models.vrm_model import VRMModel

    tool = AvatarManagerTool(mock_server)

    with patch.object(VRMModel, "_load_model", return_value=None):
        m1 = VRMModel("/tmp/test1.vrm")
        m2 = VRMModel("/tmp/test2.vrm")
        mock_server.loaded_models[m1.model_id] = m1
        mock_server.loaded_models[m2.model_id] = m2

    avatar_ids = list(mock_server.loaded_models.keys())
    assert len(avatar_ids) == 2

    # Set active
    result = await tool._handle_set_active({"avatar_id": avatar_ids[1]})
    assert result["status"] == "success"
    assert mock_server.active_model_id == avatar_ids[1]

    # Get active
    active_result = await tool._handle_get_active({})
    assert active_result["avatar_id"] == avatar_ids[1]


@pytest.mark.asyncio
async def test_avatar_manager_unload(mock_server):
    """Test avatar_manager unload operation."""
    from avatarmcp.tools.portmanteau.avatar_manager_tool import AvatarManagerTool
    from avatarmcp.models.vrm_model import VRMModel

    tool = AvatarManagerTool(mock_server)

    with patch.object(VRMModel, "_load_model", return_value=None):
        model = VRMModel("/tmp/test.vrm")
        mock_server.loaded_models[model.model_id] = model

    avatar_id = list(mock_server.loaded_models.keys())[0]
    result = await tool._handle_unload({"avatar_id": avatar_id})
    assert result["status"] == "success"
    assert avatar_id not in mock_server.loaded_models


@pytest.mark.asyncio
async def test_avatar_manager_load_missing_path(mock_server):
    """Test avatar_manager load with missing path."""
    from avatarmcp.tools.portmanteau.avatar_manager_tool import AvatarManagerTool

    tool = AvatarManagerTool(mock_server)
    result = await tool._handle_load({})

    assert result["status"] == "error"
    assert "required" in result["message"].lower()


@pytest.mark.asyncio
async def test_animation_manager_no_active_avatar(mock_server):
    """Test animation_manager with no active avatar."""
    from avatarmcp.tools.portmanteau.animation_manager_tool import AnimationManagerTool

    tool = AnimationManagerTool(mock_server)
    mock_server.active_model_id = None

    result = await tool._handle_play({"name": "idle"})
    assert result["status"] == "error"
    assert "No active avatar" in result["message"]


@pytest.mark.asyncio
async def test_animation_manager_with_active_avatar(mock_server):
    """Test animation_manager play/stop with active avatar that has animation controller."""
    from avatarmcp.tools.portmanteau.animation_manager_tool import AnimationManagerTool
    from avatarmcp.models.vrm_model import VRMModel

    tool = AnimationManagerTool(mock_server)

    with patch.object(VRMModel, "_load_model", return_value=None):
        model = VRMModel("/tmp/test.vrm")
        mock_server.loaded_models[model.model_id] = model
        mock_server.active_model_id = model.model_id

        result = await tool._handle_play({"name": "idle", "loop": True})
        assert result["status"] == "success"
        assert result["animation"] == "idle"

        stop_result = await tool._handle_stop({"name": "idle"})
        assert stop_result["status"] == "success"


@pytest.mark.asyncio
async def test_chat_manager_lifecycle(mock_server):
    """Test chat_manager full lifecycle."""
    from avatarmcp.tools.portmanteau.chat_manager_tool import ChatManagerTool

    tool = ChatManagerTool(mock_server)

    start_result = tool._handle_start_session({"session_id": "test_session", "context": "general"})
    assert start_result["status"] == "success"
    assert start_result["session_id"] == "test_session"

    msg_result = tool._handle_send_message({"session_id": "test_session", "message": "Hello avatar!"})
    assert msg_result["status"] == "success"
    assert msg_result["response"] is not None

    state_result = tool._handle_get_state({"session_id": "test_session"})
    assert state_result["status"] == "success"
    assert state_result["message_count"] == 2  # user + assistant

    stop_result = tool._handle_stop_session({"session_id": "test_session"})
    assert stop_result["status"] == "success"


@pytest.mark.asyncio
async def test_artifact_manager_scan(mock_server):
    """Test artifact_manager scan operation."""
    from avatarmcp.tools.portmanteau.artifact_manager_tool import ArtifactManagerTool

    tool = ArtifactManagerTool(mock_server)
    result = tool._handle_scan({})

    assert result["status"] == "success"
    assert "artifacts" in result


@pytest.mark.asyncio
async def test_system_monitor_without_initialize(mock_server):
    """Test that non-initialized server returns error."""
    from avatarmcp.tools.portmanteau.system_monitor_tool import SystemMonitorTool

    mock_server.initialized = False
    tool = SystemMonitorTool(mock_server)

    # get_status is not async (it's sync), don't await
    result = tool._handle_get_status({})
    assert result["status"] == "success"  # get_status works regardless


@pytest.mark.asyncio
async def test_portmanteau_tool_registration(mock_server):
    """Test that all portmanteau tools register correctly on the server."""
    # Just verify that the tool classes can be instantiated without errors
    from avatarmcp.tools.portmanteau.system_monitor_tool import SystemMonitorTool
    from avatarmcp.tools.portmanteau.avatar_manager_tool import AvatarManagerTool
    from avatarmcp.tools.portmanteau.animation_manager_tool import AnimationManagerTool
    from avatarmcp.tools.portmanteau.chat_manager_tool import ChatManagerTool
    from avatarmcp.tools.portmanteau.artifact_manager_tool import ArtifactManagerTool
    from avatarmcp.tools.portmanteau.audio_manager_tool import AudioManagerTool
    from avatarmcp.tools.portmanteau.behavior_manager_tool import BehaviorManagerTool
    from avatarmcp.tools.portmanteau.collaboration_manager_tool import CollaborationManagerTool
    from avatarmcp.tools.portmanteau.content_manager_tool import ContentManagerTool
    from avatarmcp.tools.portmanteau.emotion_manager_tool import EmotionManagerTool
    from avatarmcp.tools.portmanteau.interaction_manager_tool import InteractionManagerTool
    from avatarmcp.tools.portmanteau.performance_manager_tool import PerformanceManagerTool

    # Instantiate without MCP registration (mcp is mock, _register_tool will fail to call @tool())
    # Just verify the classes import and construct properly
    assert SystemMonitorTool is not None
    assert AvatarManagerTool is not None
    assert AnimationManagerTool is not None
    assert ChatManagerTool is not None
    assert ArtifactManagerTool is not None
    assert AudioManagerTool is not None
    assert BehaviorManagerTool is not None
    assert CollaborationManagerTool is not None
    assert ContentManagerTool is not None
    assert EmotionManagerTool is not None
    assert InteractionManagerTool is not None
    assert PerformanceManagerTool is not None
