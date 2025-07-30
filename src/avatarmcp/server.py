"""
AvatarMCP Server

FastMCP 2.10+ server implementation for AvatarMCP.
"""
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import uvicorn
from fastmcp import FastMCP, mcp_tool

from .service import AvatarService, VRMModel

class AvatarMCP:
    """MCP server for managing VRM avatars."""
    
    def __init__(self):
        """Initialize the AvatarMCP server."""
        self.service = AvatarService()
        self.mcp = FastMCP(
            name="AvatarMCP",
            description="MCP server for managing and animating VRM avatars",
            version="0.1.0"
        )
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all MCP tools."""
        self.mcp.tool()(self.load_vrm)
        self.mcp.tool()(self.play_animation)
        self.mcp.tool()(self.update_pose)
        self.mcp.tool()(self.list_animations)
    
    async def load_vrm(self, file_path: str) -> Dict[str, Any]:
        """
        Load a VRM model from file.
        
        Args:
            file_path: Path to the .vrm file
            
        Returns:
            Dict containing model metadata
        """
        try:
            model = self.service.load_vrm(file_path)
            return {
                "status": "success",
                "model_id": file_path,
                "metadata": model.metadata
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def play_animation(self, model_id: str, animation_name: str, loop: bool = False) -> Dict[str, Any]:
        """
        Play an animation on a loaded VRM model.
        
        Args:
            model_id: ID of the loaded model (file path)
            animation_name: Name of the animation to play
            loop: Whether to loop the animation (default: False)
            
        Returns:
            Dict containing status information
        """
        if model_id not in self.service.avatars:
            return {"status": "error", "error": f"Model not found: {model_id}"}
            
        try:
            self.service.play_animation(self.service.avatars[model_id], animation_name, loop)
            return {
                "status": "success",
                "animation": animation_name,
                "loop": loop
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_pose(self, model_id: str, pose_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the pose of a loaded VRM model.
        
        Args:
            model_id: ID of the loaded model (file path)
            pose_data: Dictionary containing pose information
            
        Returns:
            Dict containing status information
        """
        if model_id not in self.service.avatars:
            return {"status": "error", "error": f"Model not found: {model_id}"}
            
        try:
            self.service.update_pose(self.service.avatars[model_id], pose_data)
            return {
                "status": "success",
                "pose_updated": True
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def list_animations(self) -> Dict[str, Any]:
        """
        List all available animations.
        
        Returns:
            Dict containing list of animation names
        """
        return {
            "status": "success",
            "animations": list(self.service.animations.keys())
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the MCP server.
        
        Args:
            host: Host to bind to (default: 0.0.0.0)
            port: Port to listen on (default: 8000)
        """
        app = self.mcp.app
        
        @app.on_event("startup")
        async def startup():
            print(f"AvatarMCP server starting on http://{host}:{port}")
        
        uvicorn.run(app, host=host, port=port)

def main():
    """Entry point for the AvatarMCP server."""
    server = AvatarMCP()
    server.run()

if __name__ == "__main__":
    main()
