# Webapp bridge and backend

## Bridge (implemented and working)

- **Backend**: `avatarmcp.http_server:app` (FastAPI) on port **10793**; exposes `/api/v1/health`, `/api/v1/status`, `/api/v1/tools`, `/api/v1/tools/execute`, `/api/v1/avatars`, `/api/v1/fleet/launch`.
- **Frontend**: Vite dev server on **10792**; proxies `/api` to `http://127.0.0.1:10793`.
- **Start**: Run `web_sota/start.ps1` from repo root. It starts the Python backend (uvicorn) then the Vite frontend. Frontend uses relative URLs (`/api/v1/...`) so the proxy forwards to the backend.

**Test the bridge** (backend must be running on 10793):

```powershell
.\scripts\test-bridge.ps1
```

## Universal gateway pattern (FastMCP 3)

This MCP server **does not** use the FastMCP 3 "universal gateway" pattern. It is a **single FastMCP instance** with locally registered tools (decorators and portmanteau classes). The gateway pattern would use `add_provider()`, `create_proxy()`, or similar to aggregate multiple backend MCP servers or expose one transport via another; that is not used here.

## Locked file in .venv (unblock uv sync)

The project **does not** install an `avatarmcp.exe` console script (to avoid uv sync failing when that file is locked). Run the server with:

```powershell
uv run python -m avatarmcp
```

For MCP client config, use command `uv run` with args `python`, `-m`, `avatarmcp` (and set cwd to the repo).

If you still see "file is being used" (the exe was created by an old install):

1. **Recommended**: Close **Cursor** (and any terminal that ran the backend), then run:
   ```powershell
   .\scripts\fix-venv-lock.ps1 -Recreate
   ```
   This deletes `.venv` and runs `uv sync`. A new venv is created without any script exe, so the lock cannot recur.

2. **Alternatively**: Run `.\scripts\fix-venv-lock.ps1 -Kill` to stop processes that might be using the venv, then `uv sync`. If the lock persists, use `-Recreate`.
