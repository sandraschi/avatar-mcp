"""Main entry point for AvatarMCP FastAPI server."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from avatarmcp.api.v1 import api_router
from avatarmcp.config import settings

app = FastAPI(title="AvatarMCP API", description="REST interface for AvatarMCP tools", version="1.0.0")

# Enable CORS for the webapp
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:10792", "http://127.0.0.1:10792",
        "http://localhost:10793", "http://127.0.0.1:10793",
        "http://tauri.localhost", "https://tauri.localhost", "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "avatarmcp"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
