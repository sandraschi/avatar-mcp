
## [Unreleased]

### Added
- Browser-based VRM viewer — three.js + @pixiv/three-vrm, renders VRM models directly in the webapp
- New Viewer page (`/viewer`) — load any model from models/, toggle spin, built-in model buttons
- `GET /api/vrm/view` — serves VRM files to the browser for three.js loading
- `GET /api/avatar.vrm` — same endpoint, alias for API consistency
- VRM files copied to `~/.avatarmcp/models/` — shared depot for avatar-mcp, resonite-mcp, vrchat-mcp

### Changed
- package.json: added three@0.185.1 and @pixiv/three-vrm@3.5.5

## [Unreleased] — 2026-06-14

### Added
- Tauri 2.0 native wrapper with `bundle.resources` + `std::process::Command`
- PyInstaller frozen backend embedded in NSIS installer
- CUA-NSIS smoke test (`scripts/cua-smoke.py`, `scripts/cua-nsis-config.json`)
- `just cua-nsis-test` recipe
- Tauri CORS: `tauri://localhost` origins for WebView API access
- `GET /api/v1/diagnostics` endpoint for CUA verification
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Prometheus metrics port**: Moved from **10791** to **10790** (`METRICS_PORT` env). Port 10791 is reserved for mcp-central-docs fleet starts UI; metrics on 10791 caused docs_mcp / Hermes docsops connectivity failures.


### Added
- **Real avatar export**: `export_avatar` tool now wired to blender-mcp. Calls `blender_import` (VRM → scene) then `blender_export_presets` (platform-specific export) via the `/tool` HTTP bridge on port 10849. Falls back to simulated export if blender-mcp unreachable.
- Export format routing: `vrc` → VRChat FBX, `unity` → Unity FBX, `generic` → Resonite GLB.

### Fixed
- **Version consistency**: `pyproject.toml` and `__init__.py` now both read `0.3.0` (previously mismatched at 0.1.0 / 0.2.0).

---

## [0.2.0] / Unreleased (prior) - 2026-05

### Added
- **Webapp Settings (web_sota)**: Ollama model selection UI.
  - Backend: `GET/PUT /api/v1/settings/llm`, `GET /api/v1/settings/ollama/status`, `GET /api/v1/settings/ollama/models` (Ollama discovery via `OLLAMA_BASE_URL`, default 127.0.0.1:11434).
  - Settings page: dynamic Ollama connection status, dropdown of discovered models, persist selection.
- **System monitor portmanteau**: Bootstrap operations for portmanteau-only mode.
  - `system_monitor(operation="initialize", models_dir=...)`: bootstrap server, scan VRM models; call first.
  - `system_monitor(operation="shutdown")`: request server shutdown.
- **Backend intelligence endpoint**: Added `GET /api/v1/intelligence/trifecta` to http_server for the Intelligence page.
- **Docker Compose**: Full infrastructure stack (app + Prometheus + Loki + Grafana + Promtail).
- **Portmanteau tool tests**: 19 new test cases across `test_portmanteau_tools.py` and `test_server.py`.
- **`AnimationController` on VRMModel**: Every `VRMModel` now includes an `animation_controller` attribute.
- **Server-level OSC helper**: Added `AvatarMCPServer._send_osc_message()` for OSC tool fallback.

### Changed
- **Portmanteau-only tool surface**: MCP and HTTP tool list now expose only the 16 portmanteau tools.
  - Removed registration of `CoreAvatarTools`, `CoreSystemTools`, `CoreUnityIntegrationTools`.
  - Clients must call `system_monitor(operation="initialize")` before using other portmanteau tools.
- **`avatar_manager_tool.py` → fully async**: All handlers converted to `async def` with proper `await` on VRMManager calls.
- **`animation_manager_tool.py` → fully async**: All handlers converted to `async def`; uses `AnimationController` from the active model instead of raw OSC.
- **`mcp_main.py` → canonical server import**: Now imports `AvatarMCPServer` directly from `server.py` instead of the deleted `mcp_server_clean.py`.
- **CI pipeline**: Python version matrix changed to `["3.12", "3.13"]` (was `["3.10", "3.11", "3.12"]`). Uses `uv` for dependency management.
- **`release.yml` simplified**: Replaced deprecated `actions/create-release@v1` and `actions/upload-release-asset@v1` with `softprops/action-gh-release@v2`.
- **`build-mcpb.yml`**: Fixed manifest validation path from `mcpb/manifest.json` to `mcpb.json`.
- **`pyproject.toml`**: Runtime deps cleaned — `ruff`, `pyvista`, `prefab-ui` moved to dev; `psutil` added; Python classifiers updated to 3.12/3.13; mypy `python_version` set to `3.12`.
- **`mcpb.json`**: `entry_point` fixed to `src/avatarmcp/server.py`; version aligned to `0.1.0`; deps expanded to full list.
- **`__main__.py`**: Logging consolidated into shared `_configure_logging()` helper with `force=True`; `_stdio_original_stdout` declared at module level with `None` guard.
- **`justfile`**: `Set-Location` replaced with `uv run --directory` for web commands; `cd` for security commands.
- **`web_sota/intelligence.tsx`**: Changed hardcoded `http://127.0.0.1:10793/api/v1/intelligence/trifecta` to proxied `/api/v1/intelligence/trifecta`.
- **All legacy tests rewritten**: `test_avatar_mcp.py`, `test_basic.py`, `test_integration.py`, `test_vrm_loader.py`, `test_api.py` — unified to test current architecture.

### Fixed
- **Portmanteau tools not awaiting async calls**: `avatar_manager_tool.py` and `animation_manager_tool.py` had sync `def` calling async `vrm_manager` methods without `await`. Converted to `async def` with proper `await` on all calls. This was the root cause of all portmanteau operations being non-functional.
- **Missing `_send_osc_message` on server**: OSC portmanteau tools (`audio_manager`, `emotion_manager`, `behavior_manager`, `collaboration_manager`, `content_manager`, `interaction_manager`, `performance_manager`) called `self.mcp_server._send_osc_message()` which didn't exist on `AvatarMCPServer`. Added the method.
- **`mcpb.json` entry point**: Pointed to `src/avatar_mcp/server.py` (wrong path with underscore). Fixed to `src/avatarmcp/server.py`.
- **`__main__.py` `NameError`**: `_stdio_original_stdout` could be referenced before assignment. Now declared at module level with `None` guard.
- **`mcp_main.py` stale import**: Used `importlib` to load deleted `mcp_server_clean.py`. Now imports canonical `AvatarMCPServer`.
- **CI Python version conflict**: CI tested 3.10/3.11 but `pyproject.toml` required `>=3.12`. Matrix fixed to `["3.12", "3.13"]`.
- **Dependabot disabled**: Renamed `.github/dependabot.yml.disabled` → `dependabot.yml`.
- **`test_api.py` silent skip**: All tests wrapped in `except ConnectError: pytest.skip()`. Replaced with `TestClient` fixture from the actual FastAPI app.
- **Legacy test failures**: 10 failing tests across `test_avatar_mcp.py`, `test_basic.py`, `test_integration.py`, `test_vrm_loader.py` — all rewritten to match current API and mocks.
- **Web_SOTA stale files**: Deleted 3 `.backup` files from `web_sota/src/pages/` and `web_sota/avatarmcp.log`.

### Removed
- **Dead code**: Deleted `tools/core/*` (9 files, ~2,500 LOC), `tools/unity/unity_tools.py` (empty placeholder), `server_fixed.py`, `mcp_enhanced.py`, `simple_mcp_server.py`, `mcp_server_clean.py`, `server.py.backup`.
- **Old requirements files**: Deleted `requirements-updated.txt`, `requirements-ai-npc.txt`, `requirements-visualization.txt`.
- **Personal git scripts**: Deleted `setup_git.bat`, `push_to_github.bat`, `git_commit_push.bat`.

### Security
- **Dependabot re-enabled**: Automated weekly dependency scanning for pip, GitHub Actions, and npm.
- **Bandit security scanning**: Added to CI pipeline.
- **Trivy vulnerability scanning**: Added to CI for filesystem SARIF reporting.

---

## [1.2.0] - 2026-02-24

### Added
- **New Portmanteau Managers**: Consolidated all remaining tools into professional manager interfaces:
  - `emotion_manager`: Unified emotion, micro-expressions, and personality profiles.
  - `audio_manager`: Unified audio playback and singing synthesis.
  - `behavior_manager`: Unified AI conversation, adaptation, and learning behaviors.
  - `animation_manager`: Unified animation play/stop, sequences, and layering.
  - `collaboration_manager`: Unified multi-user sync and session management.
  - `content_manager`: Unified asset creation, listing, and publishing.
  - `interaction_manager`: Unified tactical triggers and interactive gestures.
  - `performance_manager`: Unified VRM optimization and profiling.

### Changed
- **Architecture Refactoring**: Complete purge of redundant tools and bridge logic in `server.py`.
- **Fleet Alignment**: Removed OSC and Resonite-specific tools now handled by dedicated fleet servers.
- **Portmanteau Consolidation**: Reduced tool footprint by 50% while maintaining full feature parity.

### Fixed
- **Registration Errors**: Resolved `NameError` in `server.py` and improved modular tool loading.

---


### Added
- **Agentic Sampling Workflows**: Revolutionary FastMCP 2.14.3 sampling capabilities (SEP-1577)
  - `avatar_sampling`: New portmanteau tool for agentic avatar orchestration
  - LLM-driven autonomous workflow execution without manual sequencing
  - Intelligent choreography with emotional intelligence and timing control
  - Available operations: load_avatar, play_animation, set_morph, control_bone, send_osc, set_emotion, create_sequence, blend_animations, get_status, wait
- **16th Portmanteau Tool**: Expanded from 15 to 16 tools with sampling capabilities
- **Sampling Workflow Examples**: Comprehensive examples for emotional performances, dance choreography, and interactive storytelling
- **Advanced Usage Tips**: Best practices for prompt engineering, operation selection, and creative applications

### Changed
- **FastMCP Upgrade**: Upgraded from 2.12.0+ to 2.14.3 with sampling support
- **Tool Architecture**: Now 16 consolidated portmanteau tools (50% reduction from original 28)
- **Documentation**: Enhanced with sampling workflow guides and extended usage examples

### Technical
- **SEP-1577 Compliance**: Full implementation of "sampling with tools" specification
- **Async Orchestration**: Proper timing and sequencing for complex avatar behaviors
- **Context Awareness**: Workflow parameters with environmental and timing context
- **Safety Controls**: Configurable iteration limits (1-20) to prevent infinite loops

## [1.0.0] - 2025-10-22

### Added
- **Portmanteau Tools Architecture**: Consolidated 28 individual tools into 15 portmanteau tools
  - `avatar_manager`: Comprehensive avatar lifecycle management (load, unload, list, set_active, get_active, get_metadata)
  - `animation_controller`: Animation control and management (play, stop, list)
  - `osc_communicator`: OSC communication hub (send, receive)
  - `unity_integration`: Unity desktop avatar control (status, load_avatar, set_expression, control_animation)
  - `chat_manager`: Chat session management (start_session, send_message, stop_session, get_state)
  - `system_monitor`: System health and diagnostics (get_status, get_health, get_metrics)
- **FastMCP 2.12 Standards Compliance**: All tools follow FastMCP 2.12 standards with multiline docstrings
- **Real Tool Implementations**: All core tools now have actual working functionality instead of mock responses
- **Unity Desktop Integration**: Full Unity desktop avatar control with OSC communication
- **Chat System**: Interactive chatbot functionality with session management
- **System Monitoring**: Comprehensive system health and diagnostics with performance metrics
- **MCPB Packaging**: Production-ready MCPB package with proper configuration
- **Comprehensive Error Handling**: Robust error handling throughout all tools
- **Type Annotations**: Full type hints throughout the codebase

### Changed
- **Architecture Refactoring**: Moved from individual tool handlers to modular portmanteau tool classes
- **Tool Count Reduction**: Reduced from 28 individual tools to 15 consolidated portmanteau tools (47% reduction)
- **Code Organization**: Clean separation of concerns with focused tool classes
- **Documentation**: Updated README and documentation to reflect new architecture
- **Linting**: Switched from black to ruff for faster, more comprehensive linting
- **Server Structure**: Cleaned up server.py by moving tool logic to dedicated classes

### Fixed
- **Ruff Linting Errors**: Fixed all 47 linting errors including line length and duplicate exception blocks
- **Test Failures**: Fixed all failing tests including API integration tests and avatar MCP tests
- **Import Issues**: Resolved all import and module loading issues
- **Mock Tool Issues**: Replaced all mock implementations with real, working functionality
- **Error Handling**: Improved error handling and logging throughout the system

### Removed
- **Mock Implementations**: Removed all mock tool implementations in favor of real functionality
- **Bloated Server Code**: Removed large tool implementations from server.py
- **Deprecated Tools**: Consolidated deprecated individual tools into portmanteau tools

## [0.1.0] - 2025-10-21

### Added
- Initial release
- Core functionality implemented
- Documentation created

### Changed
- N/A

### Fixed
- N/A

### Removed
- N/A

---

## How to Update This File

When making changes, add them under the appropriate section:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

