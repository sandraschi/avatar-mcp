"""Universal Tool API for AvatarMCP.

Exposes FastMCP tools through a standardized REST interface.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from avatarmcp.api.state import get_server

logger = logging.getLogger(__name__)

router = APIRouter(tags=["tools"])


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str | None = None
    required: bool = True


class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameter] = []


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


class ToolCallResponse(BaseModel):
    status: str
    result: Any = None
    message: str | None = None


@router.get("/", response_model=list[ToolInfo])
async def list_tools() -> list[ToolInfo]:
    """List all registered MCP tools."""
    try:
        server_instance = get_server()
        mcp = server_instance.mcp

        tools: list[ToolInfo] = []

        # FastMCP 2.14.3 tool manager access
        tool_sources = []
        if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "tools"):
            tool_sources = list(mcp._tool_manager.tools.values())
        elif hasattr(mcp, "_tools"):
            tool_sources = list(mcp._tools.values())

        for tool in tool_sources:
            params = []
            if hasattr(tool, "parameters") and tool.parameters:
                schema = tool.parameters.get("properties", {})
                required_list = tool.parameters.get("required", [])

                for p_name, p_info in schema.items():
                    params.append(
                        ToolParameter(
                            name=p_name,
                            type=p_info.get("type", "any"),
                            description=p_info.get("description"),
                            required=p_name in required_list,
                        )
                    )

            tools.append(ToolInfo(name=tool.name, description=tool.description or "", parameters=params))

        return tools

    except Exception as e:
        logger.error(f"Error listing tools: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tools: {e!s}",
        )


@router.post("/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """Execute a registered MCP tool."""
    try:
        logger.info(f"Calling tool via API: {request.name} with args: {request.arguments}")

        server_instance = get_server()
        mcp = server_instance.mcp

        # Execute tool via FastMCP instance
        result = await mcp.call_tool(request.name, request.arguments)

        return ToolCallResponse(status="success", result=result, message=f"Tool {request.name} executed successfully")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error calling tool {request.name}: {e!s}", exc_info=True)
        return ToolCallResponse(status="error", message=str(e))
