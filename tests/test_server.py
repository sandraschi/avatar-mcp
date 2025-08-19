"""
Tests for the MCP server implementation.
"""
import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from fastmcp import FastMCP, MCPServer, MCPTool, MCPRequest, MCPResponse

class TestMCPServer:
    """Tests for the MCP server implementation."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock AvatarService."""
        service = MagicMock()
        service.load_vrm = AsyncMock(return_value={"id": "test_avatar", "name": "Test Avatar"})
        service.play_animation = AsyncMock(return_value={"status": "playing"})
        service.stop_animation = AsyncMock(return_value={"status": "stopped"})
        service.set_pose = AsyncMock(return_value={"status": "pose_set"})
        service.get_avatar_info = AsyncMock(return_value={"name": "Test Avatar", "bones": ["Hips"]})
        return service
    
    @pytest.fixture
    def server(self, mock_service):
        """Create an instance of the MCP server for testing."""
        from avatarmcp.server import AvatarMCPServer
        return AvatarMCPServer(mock_service)
    
    @pytest.fixture
    def mcp_server(self, server):
        """Create a FastMCP server instance for testing."""
        mcp = FastMCP("test_server")
        server.register_tools(mcp)
        return mcp
    
    @pytest.mark.asyncio
    async def test_load_vrm_tool(self, mcp_server, mock_service):
        """Test the load_vrm tool."""
        # Create a test request
        request = MCPRequest(
            id="test_request",
            tool="load_vrm",
            parameters={"file_path": "test.vrm"}
        )
        
        # Process the request
        response = await mcp_server.process_request(request)
        
        # Assertions
        assert response.result == {"id": "test_avatar", "name": "Test Avatar"}
        mock_service.load_vrm.assert_called_once_with("test.vrm")
    
    @pytest.mark.asyncio
    async def test_play_animation_tool(self, mcp_server, mock_service):
        """Test the play_animation tool."""
        # Create a test request
        request = MCPRequest(
            id="test_request",
            tool="play_animation",
            parameters={"avatar_id": "test_avatar", "animation_name": "wave"}
        )
        
        # Process the request
        response = await mcp_server.process_request(request)
        
        # Assertions
        assert response.result == {"status": "playing"}
        mock_service.play_animation.assert_called_once_with("test_avatar", "wave", loop=False, speed=1.0, blend_duration=0.2)
    
    @pytest.mark.asyncio
    async def test_stop_animation_tool(self, mcp_server, mock_service):
        """Test the stop_animation tool."""
        # Create a test request
        request = MCPRequest(
            id="test_request",
            tool="stop_animation",
            parameters={"avatar_id": "test_avatar"}
        )
        
        # Process the request
        response = await mcp_server.process_request(request)
        
        # Assertions
        assert response.result == {"status": "stopped"}
        mock_service.stop_animation.assert_called_once_with("test_avatar")
    
    @pytest.mark.asyncio
    async def test_set_pose_tool(self, mcp_server, mock_service):
        """Test the set_pose tool."""
        # Create test pose data
        pose_data = {
            "Hips": {
                "position": [0, 1, 0],
                "rotation": [0, 0, 0, 1]
            }
        }
        
        # Create a test request
        request = MCPRequest(
            id="test_request",
            tool="set_pose",
            parameters={"avatar_id": "test_avatar", "pose_data": pose_data}
        )
        
        # Process the request
        response = await mcp_server.process_request(request)
        
        # Assertions
        assert response.result == {"status": "pose_set"}
        mock_service.set_pose.assert_called_once_with("test_avatar", pose_data)
    
    @pytest.mark.asyncio
    async def test_get_avatar_info_tool(self, mcp_server, mock_service):
        """Test the get_avatar_info tool."""
        # Create a test request
        request = MCPRequest(
            id="test_request",
            tool="get_avatar_info",
            parameters={"avatar_id": "test_avatar"}
        )
        
        # Process the request
        response = await mcp_server.process_request(request)
        
        # Assertions
        assert response.result == {"name": "Test Avatar", "bones": ["Hips"]}
        mock_service.get_avatar_info.assert_called_once_with("test_avatar")
