# AvatarMCP Tools Reference

This document provides a reference for the avatar control tools available in the AvatarMCP system.

## Table of Contents
- [Animation Control Tool](#animation-control-tool)
- [Avatar Control Tool](#avatar-control-tool)
- [System Info Tool](#system-info-tool)

## Animation Control Tool

Controls avatar animations and movements.

### Endpoints
- `POST /api/animations/play` - Play an animation
  - Parameters:
    - `animation_name` (string): Name of the animation to play (e.g., "idle", "talking", "listening")
    - `loop` (boolean, optional): Whether to loop the animation (default: false)
    - `speed` (float, optional): Playback speed multiplier (default: 1.0)

- `POST /api/animations/stop` - Stop current animation
  - Parameters: None

## Avatar Control Tool

Manages avatar properties and states.

### Endpoints
- `POST /api/avatars/load` - Load a VRM avatar
  - Parameters:
    - `path` (string): Path to the VRM file (relative to the models directory)
    - `scale` (float, optional): Initial scale of the avatar (default: 1.0)
    - `position` (object, optional): Initial position {x, y, z} (default: {0, 0, 0})

- `GET /api/avatars` - List available avatars
  - Returns: Array of available avatar configurations

- `POST /api/avatars/unload` - Unload current avatar
  - Parameters: None

## System Info Tool

Provides system and avatar status information.

### Endpoints
- `GET /api/system/status` - Get system and avatar status
  - Returns: Status information including loaded avatar and animation state

- `GET /api/system/animations` - List available animations
  - Returns: Array of available animation names and their properties

## Error Handling

All endpoints return JSON responses with the following structure:
```json
{
  "status": "success|error",
  "data": {},
  "error": "Error message if status is error"
}
```

## Examples

### Loading an Avatar
```bash
curl -X POST http://localhost:7100/api/avatars/load \
  -H "Content-Type: application/json" \
  -d '{"path": "my-avatar.vrm", "scale": 1.0, "position": {"x": 0, "y": 0, "z": 0}}'
```

### Playing an Animation
```bash
# Play a wave animation once
curl -X POST http://localhost:7100/api/animations/play \
  -H "Content-Type: application/json" \
  -d '{"animation_name": "wave", "loop": false, "speed": 1.0}'

# Start idle animation loop
curl -X POST http://localhost:7100/api/animations/play \
  -H "Content-Type: application/json" \
  -d '{"animation_name": "idle", "loop": true}'

# Stop current animation
curl -X POST http://localhost:7100/api/animations/stop
```

### Getting System Status
```bash
curl http://localhost:7100/api/system/status
```
