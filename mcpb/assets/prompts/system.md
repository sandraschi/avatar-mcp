# AvatarMCP System Guide

AvatarMCP is a comprehensive Model Context Protocol (MCP) server for managing, animating, and controlling VRM avatars. It provides tools for avatar lifecycle management, animation control, OSC (Open Sound Control) communication, VRChat integration, Unity desktop avatar integration, chat sessions, and system monitoring.

## Tools Reference

### `initialize`
Initializes the AvatarMCP server and scans for VRM models in the configured models directory.

**Parameters:** None
**Returns:**
```json
{
  "success": true,
  "message": "AvatarMCP server initialized",
  "models_found": 5,
  "models_dir": "/home/user/.avatarmcp/models"
}
```

### `shutdown`
Gracefully shuts down the AvatarMCP server, cleaning up all resources including loaded avatars, OSC connections, and chat sessions.

**Parameters:** None
**Returns:**
```json
{
  "success": true,
  "message": "Server shutdown complete"
}
```

### `avatar_load`
Load a VRM avatar model from a file path into the system.

**Parameters:**
- `id` (str, required): Unique identifier for the avatar
- `path` (str, required): Filesystem path to the VRM file (.vrm format)
- `scale` (float, optional, default: 1.0): Scale factor for the avatar model
- `auto_play_animations` (bool, optional, default: True): Whether to automatically play default animations

**Returns:**
```json
{
  "success": true,
  "avatar": {
    "id": "my_avatar",
    "path": "/models/avatar.vrm",
    "scale": 1.0,
    "status": "loaded",
    "bones": [],
    "materials": [],
    "blend_shapes": [],
    "auto_play_animations": true,
    "loaded_at": "2026-06-19T10:00:00"
  },
  "message": "Successfully loaded avatar 'my_avatar'"
}
```

### `avatar_unload`
Unload a VRM avatar from the system and clean up associated resources including animation controllers.

**Parameters:**
- `id` (str, required): Unique identifier of the avatar to unload

**Returns:**
```json
{
  "success": true,
  "message": "Successfully unloaded avatar 'my_avatar'",
  "avatar_id": "my_avatar"
}
```

### `avatar_list`
List all currently loaded avatars with basic metadata including bone count, blend shape count, and names.

**Parameters:** None
**Returns:**
```json
{
  "avatars": [
    {
      "id": "my_avatar",
      "name": "Unnamed Avatar",
      "bones": 78,
      "blend_shapes": 52
    }
  ]
}
```

### `avatar_set_active`
Set the active avatar model for animation and control operations.

**Parameters:**
- `avatar_id` (str, required): ID of the avatar to set as active

**Returns:**
```json
{
  "success": true,
  "message": "Set active avatar to my_avatar",
  "avatar_id": "my_avatar"
}
```

### `avatar_get_active`
Get the currently active avatar model ID and metadata.

**Parameters:** None
**Returns:**
```json
{
  "success": true,
  "message": "Active avatar is my_avatar",
  "avatar_id": "my_avatar"
}
```

### `avatar_get_metadata`
Get detailed metadata for an avatar including blend shapes, bone hierarchy, materials, and animation information.

**Parameters:**
- `avatar_id` (str, optional): ID of the avatar. Defaults to active avatar if omitted.

**Returns:**
```json
{
  "success": true,
  "message": "Retrieved metadata for avatar my_avatar",
  "avatar_id": "my_avatar",
  "metadata": {
    "blend_shapes": ["Joy", "Angry", "Sad", "Blink"],
    "bones": ["Hips", "Spine", "Chest", "Neck", "Head"],
    "materials": ["BodyMat", "FaceMat", "HairMat"],
    "animations": ["idle", "walk", "run", "wave"]
  }
}
```

### `animation_play`
Play an animation on a loaded avatar with configurable looping, blend weight, and speed.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `animation` (str, required): Name of the animation to play
- `loop` (bool, optional, default: False): Whether to loop the animation
- `weight` (float, optional, default: 1.0): Blend weight (0.0 to 1.0)
- `speed` (float, optional, default: 1.0): Playback speed multiplier (0.1 to 10.0)

**Returns:**
```json
{
  "status": "playing",
  "avatar_id": "my_avatar",
  "animation": "wave",
  "loop": false,
  "weight": 1.0,
  "speed": 1.0
}
```

### `animation_stop`
Stop a currently playing animation on an avatar. Can stop a specific animation or all animations.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `animation` (str, optional): Name of the animation to stop. If omitted, stops all animations.
- `fade_out` (float, optional, default: 0.0): Fade-out duration in seconds

**Returns:**
```json
{
  "status": "stopped",
  "avatar_id": "my_avatar",
  "animation": "wave"
}
```

### `animation_list`
List available animations for a loaded avatar.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar

**Returns:**
```json
{
  "avatar_id": "my_avatar",
  "animations": ["idle", "walk", "run", "wave", "dance", "jump", "sit"]
}
```

### `parameter_set`
Set an avatar parameter value for real-time control of blend shapes, toggles, and numeric parameters.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `name` (str, required): Name of the parameter to set
- `value` (str | int | float | bool | None, required): New value for the parameter

**Returns:**
```json
{
  "status": "set",
  "avatar_id": "my_avatar",
  "parameter": "Blink",
  "value": 0.5
}
```

### `parameter_get`
Get the current value of an avatar parameter.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `name` (str, required): Name of the parameter to retrieve

**Returns:**
```json
{
  "status": "success",
  "parameter": "Blink",
  "value": 0.5,
  "value_type": "float"
}
```

### `osc_send`
Send a raw OSC message to an external application (VRChat, Unity, etc.) for real-time avatar control.

**Parameters:**
- `address` (str, required): OSC address pattern (e.g., /avatar/parameters/ParameterName)
- `args` (list, optional): List of OSC arguments (strings, numbers, booleans)

**Returns:**
```json
{
  "status": "sent",
  "address": "/avatar/parameters/Blink",
  "args": [0.5]
}
```

### `osc_receive`
Receive and inspect incoming OSC messages from external applications. Returns the message buffer and server status.

**Parameters:** None
**Returns:**
```json
{
  "status": "success",
  "message": "OSC receive functionality available",
  "messages": [],
  "server_running": true,
  "server_address": "127.0.0.1:9001"
}
```

### `chat_start`
Start a new chat session with the avatar chatbot. Multiple sessions can run concurrently.

**Parameters:**
- `session_id` (str, optional): Custom session ID (auto-generated if omitted)
- `personality` (str, optional, default: "friendly"): Chatbot personality style
- `context` (str, optional, default: "general"): Conversation context

**Returns:**
```json
{
  "status": "success",
  "message": "Chat session 'chat_1' started",
  "session_id": "chat_1",
  "context": "general",
  "active_sessions": 1
}
```

### `chat_send_message`
Send a message in an active chat session and receive the avatar chatbot response.

**Parameters:**
- `message` (str, required): The message text to send
- `session_id` (str, optional): Session ID (uses most recent active session if omitted)

**Returns:**
```json
{
  "status": "success",
  "message": "Message processed",
  "session_id": "chat_1",
  "response": "Hello! I'm your avatar assistant. How can I help you today?",
  "message_count": 2
}
```

### `chat_stop`
Stop a chat session or all active sessions.

**Parameters:**
- `session_id` (str, optional): Session ID to stop. If omitted, stops all active sessions.

**Returns:**
```json
{
  "status": "success",
  "message": "Chat session 'chat_1' stopped",
  "session_id": "chat_1"
}
```

### `chat_get_state`
Get the current state of chat sessions including message count, duration, and active status.

**Parameters:**
- `session_id` (str, optional): Session ID to query. If omitted, returns summary of all sessions.

**Returns:**
```json
{
  "status": "success",
  "message": "Retrieved state for session 'chat_1'",
  "session_id": "chat_1",
  "active": true,
  "context": "general",
  "message_count": 5,
  "start_time": 1718800000.0,
  "duration": 120.5
}
```

### `system_status`
Get comprehensive system status and diagnostics including server uptime, loaded avatars, OSC status, and performance metrics.

**Parameters:**
- `detailed` (bool, optional, default: False): Include detailed performance metrics

**Returns:**
```json
{
  "success": true,
  "server_initialized": true,
  "server_running": true,
  "uptime_seconds": 3600,
  "loaded_avatars": 2,
  "active_avatar_id": "avatar_1",
  "osc_enabled": true,
  "osc_initialized": true,
  "timestamp": 1718800000.0
}
```

### `debug_echo`
Echo a debug message for testing connectivity and server responsiveness.

**Parameters:**
- `message` (str, required): Message to echo back

**Returns:**
```json
{
  "success": true,
  "echo": "test message",
  "timestamp": 1718800000.0
}
```

### `tools.discover`
List all available MCP tools with their metadata, parameter schemas, and version information.

**Parameters:** None
**Returns:**
```json
{
  "tools": [
    {
      "name": "avatar.load",
      "description": "Load a VRM avatar model into the system",
      "async": true,
      "parameters": {
        "id": {"type": "str", "required": true},
        "path": {"type": "str", "required": true},
        "scale": {"type": "float", "required": false, "default": 1.0}
      }
    }
  ],
  "version": "2.12.0"
}
```

### Movement Tools

#### `movement.walk`
Start a walking animation on the specified avatar with configurable direction and speed.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `direction` (str, optional, default: "forward"): Direction ("forward", "backward", "left", "right")
- `speed` (float, optional, default: 1.0): Movement speed (0.1 to 5.0)

**Returns:** `{"status": "walking", "avatar_id": "my_avatar", "movement": "walk", "direction": "forward", "speed": 1.0}`

#### `movement.run`
Start a running animation on the specified avatar.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `direction` (str, optional, default: "forward"): Direction
- `speed` (float, optional, default: 2.0): Running speed (0.5 to 10.0)

#### `movement.turn`
Turn the avatar left or right by a specified angle.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `direction` (str, optional, default: "left"): "left" or "right"
- `angle` (float, optional, default: 45.0): Turn angle in degrees (1.0 to 360.0)
- `speed` (float, optional, default: 1.0): Turn speed (0.1 to 5.0)

#### `movement.jump`
Make the avatar perform a jump animation.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `height` (float, optional, default: 1.0): Jump height (0.1 to 5.0)

#### `movement.curtsy`
Make the avatar perform a curtsy animation with configurable style and intensity.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar
- `style` (str, optional, default: "default"): "default", "formal", "playful", or "respectful"
- `intensity` (float, optional, default: 1.0): Intensity (0.1 to 2.0)

#### `movement.stop`
Stop all movement animations for the specified avatar.

**Parameters:**
- `avatar_id` (str, required): ID of the target avatar

### VRChat OSC Tools

#### `vrchat_osc.set_gesture`
Set a hand gesture on the VRChat avatar via OSC. Supports Fist, Open, Point, Peace, RockNRoll, Gun, ThumbsUp.

**Parameters:**
- `hand` (str, required): "left" or "right"
- `gesture` (str, required): Gesture name (e.g., "Fist", "Open", "Point")
- `strength` (float, optional, default: 1.0): Gesture intensity (0.0 to 1.0)

#### `vrchat_osc.set_expression`
Set a facial expression on the VRChat avatar via OSC. Supports 14+ expressions.

**Parameters:**
- `expression` (str, required): Expression name (e.g., "Happy", "Angry", "Sad", "Surprised")
- `strength` (float, optional, default: 1.0): Expression intensity (0.0 to 1.0)

#### `vrchat_osc.set_viseme`
Set a lip sync viseme on the VRChat avatar for mouth animation during speech.

**Parameters:**
- `viseme` (str, required): Viseme name (e.g., "aa", "E", "I", "O", "U", "PP", "SS")
- `strength` (float, optional, default: 1.0): Viseme intensity (0.0 to 1.0)

#### `vrchat_osc.set_parameter`
Set a custom avatar parameter via OSC for advanced animation control.

**Parameters:**
- `name` (str, required): Parameter name
- `value` (any, required): Parameter value (int, float, bool, or string)

#### `vrchat_osc.get_parameter`
Get the current value of a VRChat avatar parameter.

**Parameters:**
- `name` (str, required): Parameter name to query

#### `vrchat_osc.list_parameters`
List all available parameters for the current VRChat avatar, categorized by type.

**Parameters:** None

#### `vrchat_osc.load_vrm`
Load and analyze a VRM file for VRChat compatibility, extracting blend shapes, bone structure, and metadata.

**Parameters:**
- `file_path` (str, required): Path to the VRM file

### Unity Desktop Avatar Tools

#### `unity_system_status`
Get the Unity desktop avatar system status including app running state, OSC connectivity, and configuration.

**Parameters:**
- `detailed` (bool, optional, default: False): Include detailed configuration

#### `unity_window_position`
Control the Unity desktop avatar window position and size on the desktop.

**Parameters:**
- `x` (int, required): X position in pixels
- `y` (int, required): Y position in pixels
- `width` (int, optional): Window width
- `height` (int, optional): Window height

#### `unity_window_transparency`
Control the Unity desktop avatar window transparency/opacity.

**Parameters:**
- `transparency` (float, required): Transparency level (0.0 = fully opaque, 1.0 = fully transparent)

#### `unity_window_visibility`
Show or hide the Unity desktop avatar window.

**Parameters:**
- `visible` (bool, required): True to show, False to hide

#### `unity_window_mode`
Set the Unity desktop avatar window interaction mode (click-through, always-on-top, etc.).

**Parameters:**
- `mode` (str, required): "normal", "click_through", "always_on_top"

#### `unity_avatar_load`
Load a VRM avatar into the Unity desktop avatar system.

**Parameters:**
- `path` (str, required): Path to the VRM file
- `make_active` (bool, optional, default: True): Set as active avatar on load

#### `unity_avatar_expression`
Control facial expressions on the Unity desktop avatar.

**Parameters:**
- `expression` (str, required): Expression name
- `strength` (float, optional, default: 1.0): Expression intensity (0.0 to 1.0)

#### `unity_avatar_animation`
Control animations on the Unity desktop avatar (play, stop, pause).

**Parameters:**
- `action` (str, required): "play", "stop", or "pause"
- `animation_name` (str, optional): Animation name for play action
- `loop` (bool, optional, default: False): Loop the animation

#### `unity_osc_bridge`
Configure the OSC communication bridge for the Unity avatar system.

**Parameters:**
- `enable_bridge` (bool, optional): Enable or disable the OSC bridge
- `server_port` (int, optional): OSC server port
- `client_port` (int, optional): OSC client port

#### `unity_plugin_load`
Load a plugin into the Unity desktop avatar system.

**Parameters:**
- `plugin_name` (str, required): Name of the plugin to load
- `plugin_path` (str, optional): Path to the plugin file

#### `unity_config_update`
Update configuration settings for the Unity desktop avatar.

**Parameters:**
- `config` (dict, required): Configuration dictionary with settings to update

### Portmanteau Tools

#### `avatar_manager`
Unified portmanteau tool for all avatar lifecycle operations.

**Parameters:**
- `params` (dict, required): Dictionary with:
  - `operation` (str, required): "load", "unload", "list", "set_active", "get_active", "get_metadata"
  - Additional fields per operation

#### `animation_controller`
Unified portmanteau tool for all animation control operations.

**Parameters:**
- `params` (dict, required): Dictionary with:
  - `operation` (str, required): "play", "stop", "list"
  - Additional fields per operation

#### `osc_communicator`
Unified portmanteau tool for OSC communication.

**Parameters:**
- `params` (dict, required): Dictionary with:
  - `operation` (str, required): "send", "receive"
  - `address` (str, required for send): OSC address pattern
  - `value` (any, required for send): OSC value

#### `chat_manager`
Unified portmanteau tool for chat session management.

**Parameters:**
- `params` (dict, required): Dictionary with:
  - `operation` (str, required): "start_session", "send_message", "stop_session", "get_state"
  - Additional fields per operation

#### `unity_integration`
Unified portmanteau tool for Unity desktop avatar integration.

**Parameters:**
- `params` (dict, required): Dictionary with:
  - `operation` (str, required): "status", "load_avatar", "set_expression", "control_animation"
  - Additional fields per operation

#### `unity_config_manager`
Unified portmanteau tool for Unity desktop avatar configuration.

**Parameters:**
- `params` (dict, required): Dictionary with:
  - `operation` (str, required): "get_config", "update_config", "osc_bridge", "plugin_load", "plugin_list"
  - Additional fields per operation

#### `system_monitor`
Unified portmanteau tool for system monitoring and diagnostics.

**Parameters:**
- `params` (dict, required): Dictionary with:
  - `operation` (str, required): "get_status", "get_health", "get_metrics"
  - Additional fields per operation

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server bind address |
| PORT | 8000 | Server port |
| DEBUG | false | Enable debug mode |
| LOG_LEVEL | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| MODELS_DIR | ~/.avatarmcp/models | Directory containing VRM model files |
| OSC_CLIENT_ADDRESS | 127.0.0.1 | OSC client (sending) IP address |
| OSC_CLIENT_PORT | 9000 | OSC client (sending) port |
| OSC_SERVER_ADDRESS | 127.0.0.1 | OSC server (receiving) IP address |
| OSC_SERVER_PORT | 9001 | OSC server (receiving) port |
| WEBSOCKET_ENABLED | true | Enable WebSocket server |
| WEBSOCKET_PATH | /ws | WebSocket endpoint path |
| API_KEYS | (empty) | Comma-separated API keys for authentication |
| ENABLE_LOKI | false | Enable Loki logging integration |
| LOKI_URL | http://localhost:3100 | Loki server URL |

### Prometheus Metrics

The server exposes Prometheus metrics on the configured METRICS_PORT. Available metrics include:

- `avatarmcp_requests_total`: Counter of requests by method, endpoint, and status
- `avatarmcp_request_duration_seconds`: Histogram of request durations
- `avatarmcp_avatars_loaded`: Gauge of currently loaded avatars
- `avatarmcp_avatar_operations_total`: Counter of avatar operations
- `avatarmcp_chat_messages_total`: Counter of chat messages
- `avatarmcp_animation_operations_total`: Counter of animation operations
- `avatarmcp_system_uptime_seconds`: Gauge of server uptime

## Error Handling

All tools return errors as structured dictionaries with the following format:

```json
{
  "success": false,
  "error": "Descriptive error message",
  "error_type": "validation | runtime | connection | not_found | timeout"
}
```

Common errors:
- `ValueError`: Invalid parameters, missing required fields, avatar not found
- `FileNotFoundError`: VRM file path does not exist
- `RuntimeError`: Server not initialized or dependency unavailable
- `ConnectionError`: OSC connection failed, Unity app not running
- `NotImplementedError`: Feature not yet implemented
- `ImportError`: Required Python package not installed

The server validates all inputs and clamps numeric parameters to their documented ranges. Paths are automatically expanded and normalized. OSC messages use fire-and-forget semantics - network errors are logged but do not crash the server.

## System Requirements

- Python 3.10+
- FastMCP >= 2.12.0
- python-osc >= 1.8.0 (for OSC/VRChat integration)
- psutil (optional, for system monitoring)
- prometheus_client (optional, for metrics)
- pywin32 (optional, Windows-only for Unity integration)
- pyvrm (optional, for VRM model loading)

## Workflow Sequences

### Basic Avatar Control Flow
1. Call `initialize()` to start the server and scan for models
2. Call `avatar_load(id="my_avatar", path="models/avatar.vrm")` to load a VRM model
3. Call `avatar_list()` to verify the avatar is loaded
4. Call `animation_play(avatar_id="my_avatar", animation="idle")` to start an animation
5. Call `avatar_get_active()` to confirm active state
6. Call `parameter_set(avatar_id="my_avatar", name="Blink", value=0.5)` for real-time control
7. Call `animation_stop(avatar_id="my_avatar", animation="idle")` to stop animation
8. Call `avatar_unload(id="my_avatar")` to clean up
9. Call `shutdown()` to stop the server

### VRChat OSC Control Sequence
1. Ensure OSC is enabled in configuration (`AVATARMCP_OSC_ENABLED=true`)
2. Launch VRChat with OSC feature enabled in settings
3. Call `vrchat_osc_list_parameters()` to discover available avatar parameters
4. Call `vrchat_osc_set_gesture(hand="left", gesture="Fist")` for hand control
5. Call `vrchat_osc_set_expression(expression="Happy")` for facial expressions
6. Call `vrchat_osc_set_viseme(viseme="aa", strength=0.8)` for lip sync
7. Call `vrchat_osc_set_parameter(name="CustomParam", value=true)` for advanced control
8. Call `vrchat_osc_get_parameter(name="GestureLeft")` to read current state

### Unity Desktop Avatar Sequence
1. Ensure `unity-desktop-avatar` application is installed
2. Call `unity_system_status()` to check if Unity is running
3. If not running, call `unity_window_visibility(visible=true)` to launch
4. Call `unity_avatar_load(path="models/avatar.vrm")` to load a model
5. Call `unity_window_position(x=100, y=100, width=800, height=600)` for placement
6. Call `unity_window_transparency(transparency=0.3)` for effect
7. Call `unity_avatar_expression(expression="Happy", strength=1.0)` for expressions
8. Call `unity_avatar_animation(action="play", animation_name="wave")` for animations
9. Call `unity_osc_bridge(enable_bridge=true)` for external control

### Multiple Avatar Management
1. Load multiple avatars with unique IDs:
   - `avatar_load(id="avatar_a", path="models/char1.vrm")`
   - `avatar_load(id="avatar_b", path="models/char2.vrm")`
   - `avatar_load(id="avatar_c", path="models/char3.vrm")`
2. List all loaded: `avatar_list()` returns array of all three
3. Switch active: `avatar_set_active(avatar_id="avatar_b")`
4. Each avatar maintains independent state, animations, and parameters
5. Unload individually: `avatar_unload(id="avatar_a")`
6. Bulk unload: call `shutdown()` to clean up all avatars

### Chat Interaction Workflow
1. Start session: `chat_start(session_id="support", context="technical")`
2. Send message: `chat_send_message(session_id="support", message="Load my avatar")`
3. Receive response with contextual guidance
4. Continue conversation with follow-up messages
5. Check state: `chat_get_state(session_id="support")` for message history
6. Stop session: `chat_stop(session_id="support")`

### System Monitoring Workflow
1. Basic check: `system_status()` returns server health overview
2. Detailed check: `system_status(detailed=true)` includes memory and CPU
3. Portmanteau health: `system_monitor(params={"operation": "get_health"})`
4. Performance metrics: `system_monitor(params={"operation": "get_metrics", "metric_type": "performance"})`
5. For Prometheus, expose metrics endpoint on configurable port

## Data Types

### Avatar ID
String identifier used to reference loaded avatars. Must be unique within a server session. Auto-generated or user-provided at load time.

### Animation Name
Case-sensitive string matching the animation key defined in the VRM model or animation controller. Common names: "idle", "walk", "run", "wave", "dance", "jump", "sit".

### Parameter Value
Supports multiple types for flexible avatar control:
- `str`: String values for text-based parameters
- `int`: Integer values for discrete controls
- `float`: Float values for continuous parameters (blend shapes, weights)
- `bool`: Boolean values for toggles and switches
- `null`: None/null for resetting parameters

Values are automatically validated and clamped to documented ranges. String values like "true"/"false" are auto-converted to boolean for VRChat parameters.

### OSC Address Pattern
Standard OSC address format starting with "/". Common patterns:
- `/avatar/parameters/{ParameterName}` - VRChat avatar parameters
- `/chatbox/input` - VRChat chat box messages
- `/unity/avatar/{command}` - Unity desktop avatar commands
- `/avatar/transform/{property}` - Avatar transform control

## Tool Dependency Graph

Some tools depend on server state managed by other tools. Understanding these dependencies helps avoid common errors:

- `avatar_load` must precede all animation and parameter tools. Without a loaded avatar, animation_play, movement.walk, parameter_set, etc. will fail with "No avatar with ID" errors.
- `initialize` must be called before any tool. All tools check `self.mcp_server.initialized` and return an error if the server is not initialized.
- OSC tools require active OSC configuration. If OSC is not enabled at startup, vrchat_osc.* tools return "OSC tools not initialized".
- Unity tools require the Unity desktop avatar application to be running. The server attempts auto-launch but may fail if the viewer script is not found.
- Chat sessions must be started with `chat_start` before `chat_send_message` can be called. Sessions persist until explicitly stopped.

## Tool Parameter Validation Rules

All tools enforce parameter validation to prevent invalid states:

- **avatar_id**: Must reference a loaded avatar. Lookup is case-sensitive. Returns ValueError with "No avatar with ID" if not found.
- **path**: Must be a valid filesystem path. Auto-expands user home (~). Resolves to absolute path. Raises ValueError if file does not exist.
- **scale**: Clamped to range [0.01, 100.0]. Must be positive.
- **weight**: Clamped to [0.0, 1.0]. Values outside range are silently clamped.
- **speed**: Clamped to [0.1, 10.0] for animations, [0.1, 5.0] for walking, [0.5, 10.0] for running.
- **angle**: Clamped to [1.0, 360.0] degrees. Negative values are adjusted.
- **height**: Clamped to [0.1, 5.0] for jump operations.
- **intensity**: Clamped to [0.1, 2.0] for curtsy operations.
- **expression/gesture/viseme**: Validated against supported lists. Case-sensitive. Returns ValueError with supported options on mismatch.
- **osc_send address**: Must start with "/". Must be a non-empty string. Args are converted to serializable types.
- **osc_send args**: Each arg is validated to be str, int, float, bool, or None. Other types are stringified.
- **direction**: Must be one of the defined enum values (forward/backward/left/right for walk/run, left/right for turn).
- **style**: Must be one of the defined curtsy styles (default/formal/playful/respectful).
- **operation**: For portmanteau tools, must be a valid operation name. Returns error listing valid operations on mismatch.

## Thread Safety Considerations

The server handles multiple concurrent requests through FastMCP's async event loop:

- Avatar state (loaded models, animation controllers) is stored in Python dictionaries accessed by avatar_id. Concurrent reads are safe. Concurrent writes to the same avatar_id should be avoided.
- OSC message sending uses a single UDP client. Messages are fire-and-forget with no ordering guarantees.
- Chat sessions are stored in memory with dict access. Each session has independent message history.
- System status metrics use time.time() for uptime tracking. No shared mutable state between requests.
- Unity OSC commands use a single client connection. Commands should not be sent in rapid succession.
- Portmanteau tools (avatar_manager, animation_controller, etc.) delegate to internal methods that are not re-entrant. They should not be called recursively.
- The server does not use threading for tool execution. All tools run in the async event loop.

## State Management

The server maintains several state dictionaries:

- **self.avatars**: dict[avatar_id, avatar_data] - Loaded VRM models with metadata
- **self.animation_controllers**: dict[avatar_id, AnimationController] - Per-avatar animation state
- **self.chat_sessions**: dict[session_id, session_data] - Active chat conversations
- **self._parameters**: dict[parameter_name, value] - OSC-tracked parameter values
- **self._callbacks**: dict[parameter_name, list[callbacks]] - OSC change listeners

State is reset on server restart. There is no persistent storage across sessions. All state is in-memory and will be lost when the server process terminates.

## Protocol Details

### OSC Communication Protocol
The server uses UDP-based OSC (Open Sound Control) for real-time communication:
- **Transport**: UDP (connectionless, unreliable)
- **Encoding**: OSC 1.0 specification
- **Client Port**: Default 9000 (sends to VRChat/Unity)
- **Server Port**: Default 9001 (receives from VRChat/Unity)
- **Address Pattern**: /avatar/parameters/{name} for avatar control
- **Data Types**: Supports int, float, string, boolean, and null
- **Latency**: < 1ms on localhost
- **Reliability**: Fire-and-forget (no ACK/retry)

### MCP Protocol Details
The server implements the Model Context Protocol:
- **Transport**: STDIO (JSON-RPC over stdin/stdout)
- **Protocol Version**: 2024-11-05
- **Tool Registration**: Via @mcp.tool() decorator at import time
- **Tool Discovery**: tools/list and tools_discover() for runtime enumeration
- **Error Handling**: JSON-RPC error objects with code, message, and data fields
- **Logging**: Sent to stderr to avoid interfering with JSON-RPC on stdout

### Prometheus Metrics Protocol
When enabled, metrics are exposed via HTTP:
- **Endpoint**: /metrics on METRICS_PORT
- **Format**: Prometheus text-based exposition format
- **Scraping**: Configurable scrape interval via Prometheus config
- **Histogram Buckets**: 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0

## Prompt Templates

The server registers MCP prompt templates for guided interactions:

### `avatar_setup_guide`
Complete guide for setting up and managing VRM avatars. Provides a quick-start sequence: avatar_list -> avatar_load -> animation_play for basic control, and references unity_* tools for desktop integration.

### `unity_desktop_setup`
Guide for Unity desktop avatar integration covering installation, OSC configuration, avatar loading, and window positioning. Provides step-by-step instructions with specific tool calls and configuration values.

## Performance Considerations

- Loading multiple large VRM files increases memory usage proportionally to file sizes
- Animation playback uses minimal CPU for state tracking
- OSC messages are fire-and-forget with no delivery guarantee
- Chat sessions maintain message history in memory
- Prometheus metrics collection adds negligible overhead
- Unity integration requires the desktop avatar viewer process
- System monitoring with psutil adds minimal polling overhead
- File paths are validated and normalized for cross-platform compatibility
