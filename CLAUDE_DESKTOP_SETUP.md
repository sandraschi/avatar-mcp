# Claude Desktop Integration with AvatarMCP

This guide explains how to set up Claude Desktop to work with the AvatarMCP server.

## Prerequisites

1. Docker and Docker Compose installed
2. Claude Desktop application installed
3. Git (for cloning the repository if not already done)

## Setup Instructions

### 1. Start the AvatarMCP Server

First, ensure the AvatarMCP server is running:

```bash
# In the project root directory
docker-compose up -d
```

### 2. Configure Claude Desktop

1. Open Claude Desktop
2. Go to Settings (gear icon in the top-right corner)
3. Navigate to the "Advanced" section
4. Under "Custom Tools", add a new tool configuration with these settings:

```json
{
  "name": "AvatarMCP",
  "description": "Control VRM avatars via MCP protocol",
  "type": "http",
  "baseUrl": "http://localhost:7100",
  "endpoints": {
    "load_avatar": {
      "method": "POST",
      "path": "/api/avatars/load",
      "description": "Load a VRM avatar"
    },
    "list_avatars": {
      "method": "GET",
      "path": "/api/avatars",
      "description": "List available avatars"
    },
    "animate": {
      "method": "POST",
      "path": "/api/animations/play",
      "description": "Play an animation"
    }
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
```

### 3. Configure Avatar Settings

Update the `claude_desktop_config.json` file with your VRM model path and desired settings:

```json
{
  "avatar": {
    "type": "vrm",
    "path": "models/your-avatar.vrm",
    "scale": 1.0,
    "position": {"x": 0, "y": 0, "z": 0}
  },
  "animations": {
    "idle": "idle",
    "talking": "talking",
    "listening": "listening"
  },
  "mcp": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 7100
  }
}
```

### 4. Place Your VRM File

Place your VRM file in the `models` directory:

```bash
mkdir -p models
# Copy your VRM file to the models directory
# Example: cp /path/to/your/avatar.vrm models/
```

### 5. Start the Services

```bash
docker-compose up -d
```

### 6. Verify the Connection

1. Open Claude Desktop
2. The avatar should automatically connect to the MCP server
3. You can test the connection by starting a conversation - the avatar should animate when Claude is speaking

## Troubleshooting

- **Avatar not appearing**: Check the Docker logs with `docker-compose logs -f`
- **Connection refused**: Ensure the MCP server is running and the port (7100) is accessible
- **VRM loading issues**: Verify the VRM file exists at the specified path and is a valid VRM file

## Using the MCP API

You can also interact with the MCP server directly:

```python
import requests

# List available avatars
response = requests.get("http://localhost:7100/api/avatars")
print(response.json())

# Load an avatar
response = requests.post("http://localhost:7100/api/avatars/load", json={
    "path": "models/your-avatar.vrm"
})
print(response.json())
```

## Stopping the Services

When you're done, you can stop the services with:

```bash
docker-compose down
```
