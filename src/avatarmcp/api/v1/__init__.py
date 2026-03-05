"""API v1 module for AvatarMCP."""

from fastapi import APIRouter

from .endpoints import intelligence, proxy, tools

api_router = APIRouter()
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(proxy.router, tags=["proxy"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
