"""FastAPI backend with logging support."""
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request
from web_sota.backend.routes.logging import router as logging_router
from web_sota.backend.log_buffer import activity_log

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.activity_log = activity_log
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    activity_log.start_file_watch(log_dir / "server.log")
    activity_log.info("server", "Server started")
    yield

app = FastAPI(title="Avatar MCP", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:10792","http://127.0.0.1:10792","http://tauri.localhost","https://tauri.localhost","tauri://localhost"], allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$", allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(logging_router)

@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok", "server": "Avatar MCP", "version": "0.1.0"}

@app.get("/api/avatar.vrm")
@app.get("/api/vrm/view")
async def serve_vrm(model: str = "Nekomimi-chan"):
    """Serve a VRM file for the three.js viewer."""
    repo_root = Path(__file__).resolve().parents[2]
    # Search models/ and examples/ directories
    for sub in ("models", "examples", "test_assets"):
        path = repo_root / sub / f"{model}.vrm"
        if path.is_file():
            return FileResponse(str(path), media_type="application/octet-stream")
    return JSONResponse({"error": f"VRM '{model}' not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
