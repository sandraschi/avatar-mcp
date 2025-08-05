# AvatarMCP DXT Package

This document provides instructions for building, installing, and using the AvatarMCP DXT package.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- Windows, macOS, or Linux

## Building the DXT Package

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/sandraschi/avatarmcp.git
   cd avatarmcp
   ```

2. **Build the DXT package** using the provided build script:
   ```powershell
   # Windows (PowerShell)
   .\build_dxt.ps1
   
   # Linux/macOS
   chmod +x build_dxt.ps1
   pwsh -File build_dxt.ps1
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies
   - Run tests (can be skipped with `-NoTests`)
   - Generate the DXT package in the `dist` directory

3. **Verify the DXT package** was created:
   ```
   dist/avatarmcp-{version}.dxt
   ```

## Installing the DXT Package

1. **Copy the DXT file** to your Claude Desktop packages directory:
   - Windows: `%APPDATA%\Claude\packages\`
   - macOS: `~/Library/Application Support/Claude/packages/`
   - Linux: `~/.config/claude/packages/`

2. **Restart Claude Desktop** to load the new package

3. **Verify installation** by checking the Claude Desktop logs or using the MCP client to list available services

## Using the AvatarMCP Service

Once installed, you can interact with the AvatarMCP service using the Claude Desktop MCP client or any HTTP client.

### Example: Loading an Avatar

```python
# Using Python requests
import requests

response = requests.post(
    "http://localhost:8000/load_avatar",
    json={
        "path": "/path/to/avatar.vrm",
        "name": "my_avatar"
    }
)
print(response.json())
```

### Example: Playing an Animation

```python
response = requests.post(
    "http://localhost:8000/play_animation",
    json={
        "avatar_name": "my_avatar",
        "animation_name": "wave",
        "loop": True,
        "speed": 1.0
    }
)
```

## Available Prompts

The following prompts are available for natural language interaction:

- **Load Avatar**: "Load the avatar from {path} and name it {name}"
- **Play Animation**: "Play the {animation_name} animation on {avatar_name} with {speed}x speed"
- **Set Expression**: "Set the {expression_name} expression on {avatar_name} with {intensity}% intensity"
- **Move Avatar**: "Move {avatar_name} to position {x}, {y}, {z}"
- **Export Avatar**: "Export the avatar named {name} to {path}"

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   - Ensure all dependencies are installed by running `pip install -e .[dev]`

2. **Port Conflicts**:
   - The default port is 8000. If this is in use, update the `dxt_manifest.json` file

3. **VRM Loader Issues**:
   - Ensure VRM files are valid and not corrupted
   - Check the logs for specific error messages

### Viewing Logs

Logs can be found in the standard Claude Desktop log location:
- Windows: `%APPDATA%\Claude\logs\`
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.local/share/claude/logs/`

## Development

### Testing Changes

1. Make your changes to the code
2. Run tests:
   ```bash
   pytest -v
   ```
3. Rebuild the DXT package
4. Copy to Claude Desktop packages directory and restart

### Directory Structure

```
avatarmcp/
├── avatarmcp/           # Main package
│   ├── __init__.py     # Package initialization
│   ├── service.py      # Main service implementation
│   ├── models.py       # Data models
│   └── vrm_loader.py   # VRM file handling
├── tests/              # Test files
├── dxt_build.py        # DXT package builder
├── build_dxt.ps1       # Build script (PowerShell)
├── dxt_manifest.json   # DXT package manifest
└── pyproject.toml      # Project configuration
```

## License

MIT License - See [LICENSE](LICENSE) for details.
