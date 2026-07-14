# AvatarMCP User Guide

AvatarMCP is a comprehensive Model Context Protocol (MCP) server for managing and animating VRM avatars. It provides tools for controlling avatars in VRChat via OSC, managing Unity desktop avatars, running chat sessions, and monitoring system health.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- Git (for cloning the repository)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/avatarmcp.git
cd avatarmcp

# Install dependencies
pip install -e .

# Or using uv (recommended)
uv sync
```

### MCP Client Configuration

**Claude Desktop (claude_desktop_config.json):**
```json
{
  "mcpServers": {
    "avatarmcp": {
      "command": "python",
      "args": ["src/avatarmcp/mcp_main.py"],
      "env": {
        "AVATARMCP_MODELS_DIR": "C:/Users/me/Avatars",
        "AVATARMCP_OSC_ENABLED": "true",
        "AVATARMCP_OSC_CLIENT_PORT": "9000"
      }
    }
  }
}
```

**Cursor IDE:**
```json
{
  "mcpServers": {
    "avatarmcp": {
      "command": "python",
      "args": ["src/avatarmcp/mcp_main.py"]
    }
  }
}
```

### Environment Variables

Create a `.env` file in the project root:

```
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=INFO
MODELS_DIR=./models
OSC_CLIENT_ADDRESS=127.0.0.1
OSC_CLIENT_PORT=9000
OSC_SERVER_ADDRESS=127.0.0.1
OSC_SERVER_PORT=9001
WEBSOCKET_ENABLED=true
API_KEYS=
```

## Tutorials

### Tutorial 1: Loading and Listing Avatars

Load a VRM avatar and verify it is loaded:

```python
# Load an avatar
result = await avatar_load(
    id="my_avatar",
    path="C:/Avatars/my_model.vrm",
    scale=1.0
)
print(result["message"])  # "Successfully loaded avatar 'my_avatar'"

# List loaded avatars
available = await avatar_list()
for avatar in available["avatars"]:
    print(f"  - {avatar['id']}: {avatar['bones']} bones")
```

Expected response for list:
```json
{
  "avatars": [
    {
      "id": "my_avatar",
      "name": "My Custom Avatar",
      "bones": 78,
      "blend_shapes": 52
    }
  ]
}
```

### Tutorial 2: Playing and Stopping Animations

Load an avatar and play a dance animation with looping:

```python
# Load the avatar
await avatar_load(id="dancer", path="models/dancer.vrm")

# Play a looping dance animation
result = await animation_play(
    avatar_id="dancer",
    animation="dance",
    loop=True,
    weight=1.0,
    speed=1.2
)
print(f"Status: {result['status']}")  # "playing"

# List available animations
animations = await animation_list(avatar_id="dancer")
print(f"Available: {animations['animations']}")

# Stop the animation after some time
await animation_stop(avatar_id="dancer", animation="dance")
```

### Tutorial 3: Setting Avatar Parameters

Control avatar blink and mouth parameters:

```python
# Set blink parameter
result = await parameter_set(
    avatar_id="my_avatar",
    name="Blink",
    value=0.5
)
print(f"Set {result['parameter']} to {result['value']}")

# Set mouth openness
await parameter_set(avatar_id="my_avatar", name="MouthOpen", value=0.3)

# Read back a parameter
value = await parameter_get(avatar_id="my_avatar", name="Blink")
print(f"Current blink value: {value['value']}")
```

### Tutorial 4: VRChat Hand Gestures

Control hand gestures on a VRChat avatar via OSC:

```python
# Make a fist with left hand
result = await vrchat_osc_set_gesture(
    hand="left",
    gesture="Fist",
    strength=1.0
)

# Wave with right hand (Open gesture)
await vrchat_osc_set_gesture(hand="right", gesture="Open", strength=0.8)

# Sequence: fist -> open -> thumbs up
await vrchat_osc_set_gesture("left", "Fist", 1.0)
await vrchat_osc_set_gesture("left", "Open", 1.0)
await vrchat_osc_set_gesture("left", "ThumbsUp", 1.0)
```

Expected gesture response:
```json
{
  "status": "success",
  "hand": "left",
  "gesture": "Fist",
  "strength": 1.0
}
```

### Tutorial 5: VRChat Facial Expressions

Animate facial expressions on a VRChat avatar:

```python
# Happy expression at full intensity
await vrchat_osc_set_expression(expression="Happy", strength=1.0)

# Subtle surprised look
await vrchat_osc_set_expression(expression="Surprised", strength=0.3)

# Emotional sequence: Sad -> Happy -> Neutral
await vrchat_osc_set_expression("Sad", 1.0)
await vrchat_osc_set_expression("Happy", 1.0)
await vrchat_osc_set_expression("Neutral", 1.0)

# Eye control sequence
await vrchat_osc_set_expression("LookLeft", 0.8)
await vrchat_osc_set_expression("LookRight", 0.8)
await vrchat_osc_set_expression("Neutral", 1.0)
```

### Tutorial 6: Lip Sync Visemes

Create realistic lip sync animations:

```python
# Say "hello" using viseme sequence
# H sound - neutral mouth
await vrchat_osc_set_viseme("PP", 0.8)

# EH sound
await vrchat_osc_set_viseme("E", 1.0)
await vrchat_osc_set_viseme("DD", 0.9)

# O sound
await vrchat_osc_set_viseme("O", 1.0)

# Back to neutral
await vrchat_osc_set_viseme("aa", 0.0)

# Consonant emphasis
await vrchat_osc_set_viseme("PP", 1.0)  # P/B sounds
await vrchat_osc_set_viseme("KK", 1.0)  # K/G sounds
await vrchat_osc_set_viseme("SS", 1.0)  # S/Z sounds
```

Expected viseme response:
```json
{
  "status": "success",
  "viseme": "aa",
  "strength": 0.8
}
```

### Tutorial 7: Custom VRChat Parameters

Control custom avatar parameters beyond standard gestures and expressions:

```python
# Set a boolean toggle
await vrchat_osc_set_parameter(name="DanceMode", value=True)

# Set numeric parameters
await vrchat_osc_set_parameter(name="DanceSpeed", value=0.8)
await vrchat_osc_set_parameter(name="ColorR", value=255)

# Menu system control
await vrchat_osc_set_parameter(name="MenuOpen", value=True)
await vrchat_osc_set_parameter(name="SelectedItem", value=3)

# Auto-conversion: strings to bools and numbers
await vrchat_osc_set_parameter(name="Enabled", value="true")    # -> boolean True
await vrchat_osc_set_parameter(name="Scale", value="1.5")       # -> float 1.5
await vrchat_osc_set_parameter(name="Count", value="42")        # -> int 42

# Read parameter values
result = await vrchat_osc_get_parameter(name="DanceMode")
if result["status"] == "success":
    print(f"DanceMode is {result['value']}")
```

### Tutorial 8: Listing VRChat Parameters

Discover all available parameters on the current avatar:

```python
result = await vrchat_osc_list_parameters()
if result["status"] == "success":
    params = result["parameters"]
    print(f"Total parameters: {result['total_count']}")
    print(f"Standard: {params['standard']}")
    print(f"Expressions: {params['expressions']}")
    print(f"Gestures: {params['gestures']}")
    print(f"Visemes: {params['visemes']}")
    print(f"Custom: {params['custom']}")
```

Expected response:
```json
{
  "status": "success",
  "parameters": {
    "standard": ["GestureLeft", "GestureRight", "Viseme", "VoiceVolume"],
    "expressions": ["Happy", "Angry", "Sad", "Surprised", "Blink"],
    "gestures": ["Fist", "Open", "Point", "Peace", "RockNRoll"],
    "visemes": ["aa", "E", "I", "O", "U", "PP", "SS", "TH"],
    "custom": ["DanceMode", "MyToggle"]
  }
}
```

### Tutorial 9: Loading VRM Files for Compatibility Checking

Analyze VRM files before using them:

```python
# Load and analyze a VRM file
result = await vrchat_osc_load_vrm(file_path="models/new_avatar.vrm")
if result["status"] == "success":
    print(f"Blend shapes: {len(result['blend_shapes'])}")
    print(f"Bones: {len(result['bones'])}")
    print(f"First 5 bones: {result['bones'][:5]}")

# Check avatar capabilities
vrm_info = await vrchat_osc_load_vrm("models/hero.vrm")
required = ["Neutral", "Happy", "Angry"]
missing = [bs for bs in required if bs not in vrm_info["blend_shapes"]]
if missing:
    print(f"Missing blend shapes: {missing}")
```

### Tutorial 10: Chat Sessions with Avatar Chatbot

Interact with the avatar chatbot:

```python
# Start a chat session
session = await chat_start(
    session_id="my_chat",
    context="general"
)
print(f"Session: {session['session_id']}")

# Send messages
reply = await chat_send_message(
    session_id="my_chat",
    message="Hello! Can you help me control my avatar?"
)
print(f"Bot: {reply['response']}")

# Ask about animations
reply = await chat_send_message(
    session_id="my_chat",
    message="What animations can I play?"
)
print(f"Bot: {reply['response']}")

# Check session state
state = await chat_get_state(session_id="my_chat")
print(f"Messages so far: {state['message_count']}")

# Stop the session
await chat_stop(session_id="my_chat")
```

### Tutorial 11: Movement Controls

Control avatar movement:

```python
# Walk forward
await movement_walk(avatar_id="my_avatar", direction="forward", speed=1.0)

# Turn right 90 degrees
await movement_turn(avatar_id="my_avatar", direction="right", angle=90)

# Run
await movement_run(avatar_id="my_avatar", direction="forward", speed=3.0)

# Jump
await movement_jump(avatar_id="my_avatar", height=1.5)

# Perform a formal curtsy
await movement_curtsy(avatar_id="my_avatar", style="formal", intensity=1.2)

# Stop all movement
await movement_stop(avatar_id="my_avatar")
```

### Tutorial 12: Sending Raw OSC Messages

Send raw OSC messages for custom integrations:

```python
# Control a parameter via raw OSC
await osc_send(
    address="/avatar/parameters/Blink",
    args=[0.5]
)

# Send multiple values
await osc_send(
    address="/avatar/transform/position",
    args=[1.5, 0.0, 2.3]
)

# Send chat message to VRChat
await osc_send(
    address="/chatbox/input",
    args=["Hello VRChat!", True]
)

# Control external lighting
await osc_send(
    address="/lighting/intensity",
    args=[0.7]
)

# Check received messages
received = await osc_receive()
print(f"Server running: {received.get('server_running')}")
```

### Tutorial 13: Unity Desktop Avatar Integration

Control Unity desktop avatars:

```python
# Check Unity system status
status = await unity_system_status(detailed=True)
print(f"Unity running: {status['unity_running']}")
print(f"OSC connected: {status['osc_connected']}")

# Set window position and size
await unity_window_position(x=100, y=100, width=800, height=600)

# Set window transparency (50% transparent)
await unity_window_transparency(transparency=0.5)

# Set window to always-on-top mode
await unity_window_mode(mode="always_on_top")

# Show the window
await unity_window_visibility(visible=True)

# Load a VRM avatar into Unity
await unity_avatar_load(path="models/avatar.vrm", make_active=True)

# Set expression on Unity avatar
await unity_avatar_expression(expression="Happy", strength=1.0)

# Play animation on Unity avatar
await unity_avatar_animation(action="play", animation_name="wave", loop=False)
```

Expected Unity status response:
```json
{
  "status": "success",
  "unity_running": true,
  "osc_connected": true,
  "osc_enabled": true,
  "timestamp": 1718800000.0
}
```

### Tutorial 14: Unity Configuration and Plugins

Manage Unity desktop avatar configuration:

```python
# Get current configuration
config = await unity_config_manager(params={
    "operation": "get_config"
})
print(f"OSC config: {config['config'].get('osc')}")

# Update OSC bridge settings
await unity_config_manager(params={
    "operation": "osc_bridge",
    "enabled": True,
    "server_port": 9000,
    "client_port": 9001
})

# List available plugins
plugins = await unity_config_manager(params={
    "operation": "plugin_list"
})
for plugin in plugins["plugins"]:
    print(f"  - {plugin['name']}: {plugin['description']}")

# Load a plugin
await unity_config_manager(params={
    "operation": "plugin_load",
    "plugin_name": "gesture_recognition"
})
```

### Tutorial 15: System Monitoring and Diagnostics

Monitor server health and performance:

```python
# Basic system status
status = await system_status()
print(f"Uptime: {status['uptime_seconds']}s")
print(f"Loaded avatars: {status['loaded_avatars']}")
print(f"OSC enabled: {status['osc_enabled']}")

# Detailed metrics
detailed = await system_status(detailed=True)
if "memory_usage" in detailed:
    print(f"Memory: {detailed['memory_usage'].get('rss_mb', 'N/A')} MB")
if "system_load" in detailed:
    print(f"CPU: {detailed['system_load'].get('cpu_percent', 'N/A')}%")

# Health check via system_monitor portmanteau
health = await system_monitor(params={"operation": "get_health"})
print(f"Server health: {health.get('server_health', 'unknown')}")
print(f"VRM manager health: {health.get('vrm_manager_health', 'unknown')}")
print(f"OSC health: {health.get('osc_health', 'unknown')}")

# Performance metrics
metrics = await system_monitor(params={
    "operation": "get_metrics",
    "metric_type": "all"
})
```

### Tutorial 16: Avatar Manager Portmanteau

Use the unified avatar manager for all avatar operations:

```python
# Load an avatar
result = await avatar_manager(params={
    "operation": "load",
    "path": "models/avatar.vrm",
    "make_active": True
})
print(f"Loaded: {result['avatar_id']}")

# List all loaded avatars
result = await avatar_manager(params={"operation": "list"})
print(f"Total avatars: {result['count']}")
for avatar in result['avatars']:
    print(f"  - {avatar['id']}")

# Get active avatar
active = await avatar_manager(params={"operation": "get_active"})
print(f"Active: {active.get('avatar_id', 'none')}")

# Get metadata for specific avatar
meta = await avatar_manager(params={
    "operation": "get_metadata",
    "avatar_id": result['avatars'][0]['id']
})
```

### Tutorial 17: Tool Discovery

Discover all available tools with their parameters:

```python
# Discover all tools
tools = await tools_discover()
print(f"FastMCP version: {tools['version']}")
for tool in tools['tools']:
    print(f"\n{tool['name']}:")
    print(f"  Description: {tool['description']}")
    print(f"  Async: {tool['async']}")
    print(f"  Parameters:")
    for name, info in tool['parameters'].items():
        req = "required" if info['required'] else f"optional, default: {info.get('default', 'N/A')}"
        print(f"    {name}: {info['type']} ({req})")
```

## REST API Reference

The AvatarMCP server exposes REST endpoints when run with HTTP transport.

### GET /health
Server health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "server": "avatarmcp",
  "version": "0.1.0",
  "uptime_s": 3600.0
}
```

### GET /api/status
Get server status, loaded avatars, OSC status, and metrics.

**Response:**
```json
{
  "status": "ok",
  "initialized": true,
  "loaded_avatars": 2,
  "osc_enabled": true,
  "uptime_seconds": 3600,
  "memory_mb": 150.5
}
```

### POST /api/avatar/load
Load a VRM avatar.

**Request:**
```json
{
  "id": "my_avatar",
  "path": "/models/avatar.vrm",
  "scale": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "avatar_id": "my_avatar",
  "message": "Avatar loaded successfully"
}
```

### POST /api/avatar/unload
Unload an avatar.

**Request:** `{"id": "my_avatar"}`

### GET /api/avatar/list
List all loaded avatars.

### POST /api/animation/play
Play an animation.

**Request:**
```json
{
  "avatar_id": "my_avatar",
  "animation": "wave",
  "loop": true,
  "weight": 1.0,
  "speed": 1.0
}
```

### POST /api/animation/stop
Stop an animation.

**Request:** `{"avatar_id": "my_avatar", "animation": "wave"}`

### GET /api/animation/list
List available animations.

**Query:** `?avatar_id=my_avatar`

### POST /api/osc/send
Send an OSC message.

**Request:**
```json
{
  "address": "/avatar/parameters/Blink",
  "args": [0.5]
}
```

### POST /api/osc/receive
Receive OSC message buffer.

### POST /api/chat/start
Start a chat session.

**Request:** `{"session_id": "chat_1", "context": "general"}`

### POST /api/chat/message
Send a chat message.

**Request:** `{"session_id": "chat_1", "message": "Hello"}`

### GET /api/chat/state
Get chat session state.

**Query:** `?session_id=chat_1`

### POST /api/chat/stop
Stop a chat session.

**Request:** `{"session_id": "chat_1"}`

### GET /api/system/status
Get system status and diagnostics.

### GET /metrics
Prometheus metrics endpoint (if enabled).

### GET /api/tools
List all available tools.

### POST /api/tools/{tool_name}
Execute a specific tool by name.

**Request:** `{"arguments": {...}}`

### POST /api/v1/control/tool
Execute any tool dynamically.

**Request:**
```json
{
  "tool": "avatar_load",
  "arguments": {
    "id": "my_avatar",
    "path": "models/avatar.vrm"
  }
}
```

### GET /api/v1/download/{filename}
Download a file from the system.

### WebSocket /ws
WebSocket endpoint for real-time events and streaming.

## Troubleshooting

### Issue 1: "Server not initialized" error
Call `initialize()` before using any other tool. The server must be initialized first.

### Issue 2: OSC messages not being sent
Ensure OSC is enabled in the configuration (`OSC_ENABLED=true`). Check that the target application (VRChat, Unity) is running and listening on the correct port. Verify the OSC server and client ports are not blocked by a firewall.

### Issue 3: VRM file fails to load
Verify the file exists at the specified path and is a valid VRM 1.0 format file. Check file permissions. The server logs details to `logs/mcp_server.log` in the install directory.

### Issue 4: Unity avatar not responding
Ensure the Unity desktop avatar application is running. The server attempts to auto-launch `desktop_avatar_viewer.py`. OSC communication requires the python-osc library to be installed. Check that the avatar viewer process is running in Task Manager.

### Issue 5: Chatbot gives generic responses
The built-in chatbot uses keyword matching. For advanced responses, consider integrating with an LLM API. The `Chatbot` class in `ai/chatbot.py` can be extended with custom response logic.

### Issue 6: VRChat parameters not changing
Confirm VRChat's OSC feature is enabled in the VRChat settings (Action Menu > Options > OSC). Verify the OSC port matches VRChat's configuration (default: 9000 send, 9001 receive). Check that the parameter name exactly matches your avatar's parameter list.

### Issue 7: Animation not playing
Verify the avatar has animation data loaded. Use `animation_list` to check available animations. Animation names are case-sensitive. Ensure the avatar has an animation controller initialized. Weights and speeds are clamped to valid ranges.

### Issue 8: Slow performance
Large VRM files with complex bones and blend shapes take longer to load. Use `system_status` with `detailed=True` to monitor memory usage. Reduce the number of concurrently loaded avatars. Consider simplifying models for better performance.

### Issue 9: Port conflicts on startup
The OSC server tries ports starting from the configured base port. If the default port is in use, it auto-increments to find an available port. Check what is listening on ports 9000-9011 with `netstat -an | findstr 900`. Kill conflicting processes or change the OSC port configuration.

### Issue 10: Python import errors
Ensure all dependencies are installed: `pip install fastmcp python-osc psutil prometheus-client`. For Unity integration on Windows, `pywin32` may be needed. Run `uv sync` to install all project dependencies from pyproject.toml.

### Issue 11: Metrics not appearing
Prometheus metrics are exposed on the configured `METRICS_PORT`. Ensure `prometheus_client` is installed. In test environments, metrics collection is disabled. Set `enabled=true` in the `MetricsCollector` initialization.

### Issue 12: "WinError 10106" on Windows
This is a Windows networking compatibility issue. The server includes fallback handling, but it may limit certain features. Ensure Windows is up to date. Try running from a Command Prompt with administrator privileges.

## FAQ

### What is AvatarMCP?
AvatarMCP is a Model Context Protocol server that enables AI agents to control VRM avatars in real-time through VRChat OSC communication and Unity integration.

### What file formats are supported?
VRM 1.0 format files (.vrm). The server reads VRM files to extract blend shapes, bones, materials, and animation data for avatar control.

### Can I use this with VRChat?
Yes. The server includes dedicated VRChat OSC tools for gestures, expressions, visemes, and custom parameters. VRChat must have OSC enabled in its settings.

### How do I set up OSC for VRChat?
Enable OSC in VRChat: Menu > Options > OSC > Enable. Default ports are 9000 (send) and 9001 (receive). Configure the AvatarMCP OSC_CLIENT_PORT and OSC_SERVER_PORT to match.

### Can I control multiple avatars simultaneously?
Yes. Multiple avatars can be loaded with different IDs. Each avatar maintains its own state, animation controller, and parameter set. Use the avatar_id parameter to target specific avatars.

### Does this work with Unity?
Yes. The server includes tools for Unity desktop avatar integration. The Unity avatar system communicates with the MCP server via OSC. Plugin loading and configuration management are supported.

### Can I create custom animations?
The server provides low-level parameter control and movement tools. Custom animations require VRM-compatible animation data. Blend shape and bone parameters can be controlled individually for custom poses.

### Is there a REST API?
Yes. When running with HTTP transport, the server exposes REST endpoints for avatar control, animation management, OSC messaging, and chat sessions. See the REST API Reference section for full documentation.

### How do I check what tools are available?
Use the `tools_discover()` or `system_status()` tools to list all registered tools and their parameters. The `help` command also provides documentation.

### Can I use this without VRChat?
Yes. The core avatar management, animation control, and Unity integration work independently of VRChat. OSC is optional and can be disabled via `OSC_ENABLED=false`.

### What performance impact does this have?
Each loaded avatar uses memory proportional to its VRM file size. The server is designed to be lightweight. Use `system_status` to monitor resource usage. Typically 100-200 MB RAM for 1-2 avatars.

### How do I troubleshoot connection issues?
Check that the target application is running and accepting OSC connections. Verify port configurations match. Use `debug_echo` to test server connectivity. Check the server log file at `logs/mcp_server.log`.

### Can I contribute or extend the server?
Yes. The codebase is modular with tools organized in the `tools/portmanteau/` and `handlers/` directories. Follow the FastMCP tool patterns used in existing implementations. Add new tool modules following the existing structure.

### Is there a web dashboard?
An optional web interface is available when running with HTTP transport. Navigate to the configured HOST:PORT in a browser. The web interface provides visual avatar management and real-time monitoring.

### What about security?
The server supports optional API key authentication via the `API_KEYS` environment variable. OSC communication is localhost-only by default. WebSocket and REST endpoints can be secured with authentication in production deployments.

### What are the default OSC ports?
Client (sending): 9000. Server (receiving): 9001. VRChat uses the same defaults. If you change AvatarMCP ports, update VRChat OSC settings to match.

### Can I run the server as a system service?
Yes. Use NSSM on Windows or systemd on Linux. Set environment variables in the service configuration. Ensure the working directory is set to the project root.

### Does the server support HTTP proxy?
Yes. REST API and WebSocket endpoints are available. The server can be placed behind a reverse proxy (nginx, Caddy) for network access.

### Can I use this with VSeeFace?
The OSC tools are designed for VRChat's parameter system. VSeeFace uses different OSC addresses. Customize osc_send with VSeeFace-specific addresses for compatibility.

### What is the maximum number of loaded avatars?
Limited only by available memory. Each VRM file typically uses 50-200 MB. Monitor with system_status detailed metrics. Performance degrades when memory usage exceeds available RAM.

### How do I contribute new tools?
Add tool modules in the tools/ or handlers/ directory following the existing patterns. Register tools using @mcp.tool() decorator. Create portmanteau tools by adding operation enums to existing modules.

### Is there a test suite?
Run tests with: `uv run pytest`. Tests cover tool registration, parameter validation, error handling, OSC message formatting, and basic workflow sequences.

## Session Management Reference

### Chat Session Lifecycle
1. Call `chat_start(session_id="unique_name", context="general")` to create a session
2. Session ID is auto-generated if not provided (format: chat_N)
3. Context parameter initializes the conversation topic
4. Messages are stored in order with timestamps
5. Each message pair (user + assistant) increments message_count
6. Duration tracks from session start to current time
7. Call `chat_stop(session_id="unique_name")` to end session
8. Stopped sessions remain in state for history but are marked inactive
9. Call `chat_get_state()` without session_id for overview of all sessions
10. Chat state is lost on server restart (in-memory only)

### OSC Parameter Tracking
The server maintains a dictionary of OSC parameter values that are updated in real-time as messages arrive. Parameters are identified by their last path component when the address starts with /avatar/parameters/. Callbacks can be registered via the on_parameter_change decorator for reactive programming patterns.

## Parameter Type Conversion for VRChat
When setting VRChat parameters via vrchat_osc.set_parameter, string values are automatically converted:
- "true" / "t" -> boolean True
- "false" / "f" -> boolean False
- "1.5" -> float 1.5
- "42" -> int 42
- Other strings are passed as-is as string values

## API Change Log

### v0.1.0 (Initial Release)
- Avatar lifecycle management (load, unload, list, set active)
- Animation playback control (play, stop, list)
- Parameter get/set for avatar controls
- OSC send/receive for VRChat integration
- VRChat OSC tools: gestures, expressions, visemes, parameters
- Unity desktop avatar integration
- Chat sessions with keyword-based chatbot
- System monitoring and diagnostics
- Portmanteau tools for unified interfaces
- Prometheus metrics collection
- MCP prompt templates for guided setup

## Deployment Configuration Reference

### Environment File (.env)
```ini
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=INFO
MODELS_DIR=C:/Avatars
OSC_CLIENT_ADDRESS=127.0.0.1
OSC_CLIENT_PORT=9000
OSC_SERVER_ADDRESS=127.0.0.1
OSC_SERVER_PORT=9001
WEBSOCKET_ENABLED=true
API_KEYS=
ENABLE_LOKI=false
```

### Production Checklist
- Set LOG_LEVEL=WARNING for reduced log volume
- Configure API_KEYS for authentication
- Set secure OSC addresses (localhost only)
- Enable Loki logging for centralized logs
- Configure Prometheus metrics endpoint
- Set appropriate MODELS_DIR with read-only access
- Test all avatar operations before deployment
- Verify OSC connectivity with target applications
- Configure firewall rules for required ports
- Set up log rotation for mcp_server.log

## Quick Troubleshooting Decision Tree

1. Server won't start? Check Python 3.10+ and pip install. Verify dependencies with `uv sync`.
2. Tools not loading? Call `initialize()` first. Check logs for import errors.
3. Avatar won't load? Verify path exists and is valid VRM format. Check logs/mcp_server.log.
4. Animation won't play? Verify avatar_id is correct. Use `animation_list` to check available animations.
5. OSC not working? Check OSC_ENABLED=true. Verify VRChat OSC settings match ports.
6. Unity not responding? Ensure desktop_avatar_viewer.py exists. Check OSC availability.
7. Chat not responding? Start session with `chat_start`. Verify session_id matches.
8. Performance issues? Use `system_status(detailed=True)`. Reduce loaded avatars.
9. Port conflicts? Check netstat for ports 9000-9011. Configure custom ports.
10. Empty responses? Set LOG_LEVEL=DEBUG for verbose output. Check stderr logs.

## Quick Start Summary
1. Initialize: `initialize()`
2. Load avatar: `avatar_load(id="v1", path="model.vrm")`
3. List avatars: `avatar_list()`
4. Play animation: `animation_play(avatar_id="v1", animation="idle")`
5. Set expression: `vrchat_osc_set_expression("Happy")`
6. Send gesture: `vrchat_osc_set_gesture("left", "Wave")`
7. Chat: `chat_start()` then `chat_send_message(message="Hi")`
8. Monitor: `system_status()`
9. Cleanup: `shutdown()`

## Additional Integration Examples

### Creating a Simple Avatar Control UI
```python
import tkinter as tk

def load_avatar():
    path = entry_path.get()
    result = await avatar_load(id="ui_avatar", path=path)
    status_label.config(text=result["message"])

def set_expression(expr):
    result = await vrchat_osc_set_expression(expression=expr, strength=1.0)
    status_label.config(text=result["message"])

# UI setup
root = tk.Tk()
root.title("Avatar Control")
entry_path = tk.Entry(root, width=50)
entry_path.pack()
tk.Button(root, text="Load Avatar", command=load_avatar).pack()
tk.Button(root, text="Happy", command=lambda: set_expression("Happy")).pack()
tk.Button(root, text="Sad", command=lambda: set_expression("Sad")).pack()
status_label = tk.Label(root, text="Ready")
status_label.pack()
```

### Voice-Controlled Avatar
```python
async def voice_control_loop():
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio).lower()
            if "happy" in text:
                await vrchat_osc_set_expression("Happy", 1.0)
            elif "wave" in text:
                await animation_play(avatar_id="my_avatar", animation="wave")
            elif "stop" in text:
                await animation_stop(avatar_id="my_avatar", animation="wave")
```

## Tool Reference Card

### Avatar Tools
| Tool | Parameters | Purpose |
|------|-----------|---------|
| avatar_load | id, path, scale, auto_play | Load VRM model |
| avatar_unload | id | Remove loaded avatar |
| avatar_list | none | Show all loaded avatars |
| avatar_set_active | avatar_id | Change active avatar |
| avatar_get_active | none | Show current active avatar |
| avatar_get_metadata | avatar_id | Get avatar details |

### Animation Tools
| Tool | Parameters | Purpose |
|------|-----------|---------|
| animation_play | avatar_id, animation, loop, weight, speed | Start animation |
| animation_stop | avatar_id, animation, fade_out | Stop animation |
| animation_list | avatar_id | Show available animations |

### Movement Tools
| Tool | Parameters | Purpose |
|------|-----------|---------|
| movement.walk | avatar_id, direction, speed | Start walking |
| movement.run | avatar_id, direction, speed | Start running |
| movement.turn | avatar_id, direction, angle, speed | Turn avatar |
| movement.jump | avatar_id, height | Jump animation |
| movement.curtsy | avatar_id, style, intensity | Curtsy animation |
| movement.stop | avatar_id | Stop all movement |

### VRChat OSC Tools
| Tool | Parameters | Purpose |
|------|-----------|---------|
| set_gesture | hand, gesture, strength | Hand gesture control |
| set_expression | expression, strength | Facial expression |
| set_viseme | viseme, strength | Lip sync control |
| set_parameter | name, value | Custom parameter |
| get_parameter | name | Read parameter value |
| list_parameters | none | Discover parameters |
| load_vrm | file_path | Analyze VRM file |

### Unity Tools
| Tool | Parameters | Purpose |
|------|-----------|---------|
| unity_system_status | detailed | Unity app status |
| unity_window_position | x, y, width, height | Window placement |
| unity_window_transparency | transparency | Window opacity |
| unity_window_visibility | visible | Show/hide window |
| unity_window_mode | mode | Interaction mode |
| unity_avatar_load | path, make_active | Load into Unity |
| unity_avatar_expression | expression, strength | Face control |
| unity_avatar_animation | action, animation_name, loop | Animation control |
| unity_osc_bridge | enable_bridge, server_port, client_port | OSC config |
| unity_plugin_load | plugin_name, plugin_path | Plugin management |
| unity_config_update | config | Settings update |

### System Tools
| Tool | Parameters | Purpose |
|------|-----------|---------|
| initialize | none | Start server |
| shutdown | none | Stop server |
| system_status | detailed | Server health |
| debug_echo | message | Connectivity test |
| tools.discover | none | List all tools |

### Can I use this for commercial projects?
Yes, the server is MIT licensed. Commercial use is permitted. Ensure your VRM models have appropriate licenses for commercial use in your target application.

### How do I update to the latest version?
Pull the latest changes from git: `git pull origin main && uv sync`. Check the CHANGELOG for breaking changes. The MCP protocol is backward compatible within major versions.

### What is the difference between individual tools and portmanteau tools?
Individual tools (avatar_load, animation_play) are atomic operations for fine-grained control. Portmanteau tools (avatar_manager, animation_controller) bundle multiple operations into a single interface with an operation parameter for convenience.

### Does this support VRM 0.x models?
The server is primarily designed for VRM 1.0. VRM 0.x models may work but are not guaranteed to have full blend shape and bone compatibility. Convert VRM 0.x to 1.0 using the official VRM converter.

### How do I reset all avatar state?
Call `shutdown()` followed by `initialize()` to reset the server completely. All loaded avatars, animations, chat sessions, and OSC state are cleared.

### Can I run the server as a Windows service?
Yes. Use NSSM (Non-Sucking Service Manager) to register the Python script as a Windows service. Ensure the working directory and environment variables are correctly configured.

### What logging is available?
The server writes logs to stderr (visible in Claude Desktop logs) and to `logs/mcp_server.log` in the install directory. Set LOG_LEVEL=DEBUG for maximum verbosity during troubleshooting.

### Is there a Docker image?
Not currently. The server runs natively on Python and requires access to the filesystem for VRM loading. Docker support may be added in a future release.

## REST API Complete Reference

### GET /api/version
Returns server version information.
**Response:** `{"name": "avatarmcp", "version": "0.1.0", "fastmcp_version": "2.12.0"}`

### POST /api/animation/batch
Execute multiple animation operations in one request.
**Request:**
```json
{
  "operations": [
    {"avatar_id": "my_avatar", "animation": "wave", "action": "play"},
    {"avatar_id": "my_avatar", "animation": "dance", "action": "play", "loop": true}
  ]
}
```

### POST /api/vrm/info
Get VRM file metadata without loading it.
**Request:** `{"path": "models/avatar.vrm"}`
**Response:** `{"title": "My Avatar", "author": "Creator", "blend_shapes": 52, "bones": 78, "materials": 3}`

### GET /api/osc/status
Get OSC server and client status.
**Response:** `{"server_running": true, "client_connected": true, "server_port": 9001, "client_port": 9000, "parameters_tracked": 25}`

### GET /api/chat/sessions
List all chat sessions.
**Response:** `{"sessions": [{"id": "chat_1", "active": true, "message_count": 5}], "total": 1}`

### POST /api/system/health
Comprehensive health check with component status.
**Response:** `{"server": "healthy", "vrm_manager": "healthy", "osc": "enabled", "memory_mb": 150.5, "uptime_s": 3600}`

## Deployment Guide

### Production Configuration
```bash
# Recommended production environment
export LOG_LEVEL=WARNING
export HOST=127.0.0.1
export PORT=8000
export API_KEYS=key1,key2,key3
export OSC_CLIENT_ADDRESS=127.0.0.1
export ENABLE_LOKI=true
export LOKI_URL=http://localhost:3100
```

### Monitoring Setup
1. Enable Prometheus metrics in configuration
2. Point Prometheus to scrape METRICS_PORT (default 8000)
3. Configure Grafana dashboard using available metrics
4. Set up Loki logging for centralized log aggregation
5. Configure alerts for server health status changes

### Backup and Recovery
1. VRM model files should be backed up separately
2. Server state does not persist across restarts
3. Chat session history is in-memory only
4. Log files can be archived for audit purposes
5. Configuration is stored in .env file or environment variables

## Integration Patterns

### VRChat Streaming Setup
1. Start AvatarMCP server
2. Launch VRChat with OSC enabled
3. Use vrchat_osc tools to control avatar in real-time
4. Expression and gesture changes appear immediately
5. Viseme sequence tracks speech for lip sync

### Multi-Application Control
1. Load avatar in VRChat via OSC
2. Same avatar can be loaded in Unity desktop viewer
3. Use parameter_set to synchronize state
4. Each application maintains independent animation state
5. Chat sessions provide personality layer

### Development Workflow
1. Use simulation mode for testing without VRM files
2. Test animations with debug_echo and system_status
3. Use tools_discover to verify tool registration
4. Check logs at DEBUG level for troubleshooting
5. Iterate on avatar parameters using parameter_set/get
