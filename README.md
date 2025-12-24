# AvatarMCP

**By FlowEngineer sandraschi**

> FastMCP 2.12+ compatible VRM avatar management and animation server with VRChat OSC integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![FastMCP 2.12](https://img.shields.io/badge/FastMCP-2.12+-brightgreen)](https://fastmcp.readthedocs.io/)
[![VRChat OSC](https://img.shields.io/badge/VRChat-OSC-9cf)](docs/VRChat_OSC_Integration_Guide.md)
[![Portmanteau Tools](https://img.shields.io/badge/Tools-Portmanteau-blueviolet)](docs/architecture/PORTMANTEAU_TOOLS_PLAN.md)

## 🚀 Features

### Core Features

- **Portmanteau Tools Architecture**: Consolidated 15 portmanteau tools following FastMCP 2.12 standards
  - Reduces tool explosion from 28 individual tools to 15 unified interfaces
  - Operation-based design with comprehensive multiline docstrings
  - Clean, maintainable architecture with focused tool classes

- **FastMCP 2.12+ Compatible**: Fully implements the MCP protocol over stdio transport with enhanced features
- **VRM 2.0 Support**: Load and manage VRM 2.0 avatar models with real-time manipulation
- **VRChat OSC Integration**: Seamless communication with VRChat for avatar control
- **Advanced Animation System**: Play, blend, and manage animations with support for loops, varying speeds, and real-time recording
- **Advanced Bone Control**: Precise control over avatar bones with local/world space transforms and hierarchical manipulation
- **Morph Target Control**: Fine-grained control over blend shapes and morph targets with batch updates
- **Unity Desktop Integration**: Full Unity desktop avatar control with window management
- **Chat System**: Interactive chatbot functionality with session management

### Secondary Features

- **MCPB Packaging**: Easy deployment and integration with MCP-compatible applications
- **Type Annotated**: Fully type-annotated code for better development experience
- **Modular Design**: Clean architecture with separate components for VRM loading, animation, and MCP server
- **System Monitoring**: Comprehensive system health and diagnostics
- **Debug Tools**: Built-in debugging and testing utilities

## 🏗️ Portmanteau Tools Architecture

AvatarMCP uses a revolutionary portmanteau tools architecture that consolidates related functionality into unified interfaces, following FastMCP 2.12 standards.

### Benefits

- **47% Tool Reduction**: From 28 individual tools to 15 consolidated portmanteau tools
- **Better Organization**: Related functionality logically grouped together
- **Easier Maintenance**: Single class per functional area
- **Improved Discoverability**: Clearer tool purposes and operations
- **Standards Compliance**: FastMCP 2.12 compliant with multiline docstrings
- **Cleaner API**: More intuitive tool structure with operation-based design

### Architecture Overview

Each portmanteau tool uses an operation-based design where a single tool handles multiple related operations:

```python
# Example: avatar_manager tool
await avatar_manager({
    "operation": "load",           # Operation type
    "path": "models/avatar.vrm",   # Operation-specific parameters
    "make_active": True
})

await avatar_manager({
    "operation": "list"            # Different operation, same tool
})
```

### Tool Categories

1. **Core Tools** (6 implemented): Essential functionality
2. **Management Tools** (4 planned): System and resource management  
3. **Advanced Tools** (5 planned): Specialized functionality

For detailed architecture documentation, see [Portmanteau Tools Plan](docs/architecture/PORTMANTEAU_TOOLS_PLAN.md).

## 📚 Documentation

### Core Components

- `MCPServer`: FastMCP 2.13.0-compatible server implementation
- `VRChatOSC`: OSC integration with VRChat for avatar control
- `VRMModel`: VRM 2.0 model loading and management
- `AnimationController`: Manage and play animations on avatars
- `MCPTools`: MCP command handlers for avatar control

## 💬 Available Prompts

AvatarMCP supports natural language interaction through the following commands:

### Avatar Management
- **Load Avatar**: "Load the VRM model from {path} as {avatar_name}"
- **Unload Avatar**: "Unload the avatar named {avatar_name}"
- **List Avatars**: "Show all loaded avatars"
- **Set Active Avatar**: "Set {avatar_name} as the active avatar"

### Animation Control
- **Play Animation**: "Play {animation_name} on {avatar_name} at {speed}x speed"
- **Stop Animation**: "Stop current animation on {avatar_name}"
- **Pause Animation**: "Pause animation on {avatar_name}"
- **Resume Animation**: "Resume paused animation on {avatar_name}"
- **Blend Animations**: "Blend from {anim1} to {anim2} over {duration} seconds on {avatar_name}"
- **Set Animation Parameter**: "Set {parameter} to {value} on {avatar_name}'s animation"

### Bone Control
- **Rotate Bone**: "Rotate {bone_name} to X:{x} Y:{y} Z:{z} on {avatar_name}"
- **Reset Bone**: "Reset {bone_name} rotation on {avatar_name}"
- **List Bones**: "Show all bones for {avatar_name}"

### Morph/BlendShape Control
- **Set Morph**: "Set {morph_name} to {value} on {avatar_name}"
- **Reset Morph**: "Reset {morph_name} on {avatar_name}"
- **List Morphs**: "Show available morphs for {avatar_name}"

### Export
- **Export Avatar**: "Export {avatar_name} to {file_path} as {format}"
- **Take Screenshot**: "Take a screenshot of {avatar_name} and save to {file_path}"

### System
- **Get System Info**: "Show system information"
- **Get Logs**: "Show recent logs"
- **Search Web**: "Search the web for {query}"
- **Query Knowledge Base**: "Search knowledge base for {query}"

### Advanced
- **Send OSC Message**: "Send OSC message {address} with {value} to {ip}:{port}"
- **Run Script**: "Run script {script_name} with parameters {params}"

### 3D Visualization & Controls

AvatarMCP features a powerful 3D viewport system for intuitive avatar manipulation:

- **Interactive 3D Viewport**: Real-time rendering of your avatar with multiple camera angles
- **View Controls**:
  - Rotate: Click and drag with left mouse button
  - Pan: Right-click and drag
  - Zoom: Mouse wheel or right-click + drag up/down
  - Reset View: Double-click the viewport
- **Visualization Modes**:
  - Solid: Full textured rendering
  - Wireframe: See underlying mesh structure
  - Shaded: Flat shading for better shape visualization
  - X-Ray: See through the model for complex rigs

### Advanced Avatar Controls

- **Bone Control**: Precise manipulation of individual bones with support for local and world space transformations
- **Morph Target Control**: Fine-grained control over blend shapes and morph targets with real-time preview
- **Export Tools**: Export avatars to various formats including FBX and Unity packages

For detailed documentation, see [AVATAR_CONTROLS.md](docs/AVATAR_CONTROLS.md).

### MCP Protocol Support

AvatarMCP implements the following portmanteau tools following FastMCP 2.12 standards:

#### Core Portmanteau Tools

- **`avatar_manager`**: Comprehensive avatar lifecycle management
  - Operations: `load`, `unload`, `list`, `set_active`, `get_active`, `get_metadata`
- **`animation_controller`**: Animation control and management
  - Operations: `play`, `stop`, `list`
- **`osc_communicator`**: OSC communication hub
  - Operations: `send`, `receive`
- **`unity_integration`**: Unity desktop avatar control
  - Operations: `status`, `load_avatar`, `set_expression`, `control_animation`
- **`chat_manager`**: Chat session management
  - Operations: `start_session`, `send_message`, `stop_session`, `get_state`
- **`system_monitor`**: System health and diagnostics
  - Operations: `get_status`, `get_health`, `get_metrics`

#### Additional Portmanteau Tools

- **`parameter_manager`**: Avatar parameter control
- **`unity_window_manager`**: Unity window control
- **`unity_config_manager`**: Unity configuration management
- **`server_controller`**: Server lifecycle management
- **`debug_tools`**: Debug and testing utilities
- **`viewer_manager`**: 3D viewer control
- **`file_manager`**: File and asset management
- **`network_manager`**: Network and connection management
- **`config_manager`**: Configuration and settings management

#### Usage Examples

```python
# Avatar management
await avatar_manager({
    "operation": "load",
    "path": "models/my_avatar.vrm",
    "make_active": True
})

# Animation control
await animation_controller({
    "operation": "play",
    "name": "wave",
    "loop": True,
    "speed": 1.2
})

# OSC communication
await osc_communicator({
    "operation": "send",
    "address": "/avatar/parameters/Emotion",
    "value": 0.8
})

# Unity integration
await unity_integration({
    "operation": "set_expression",
    "expression": "Happy",
    "strength": 0.9
})
```

For complete MCP protocol documentation, see [FastMCP Documentation](https://fastmcp.readthedocs.io/).

### VRChat OSC Integration

See [VRChat OSC Integration Guide](docs/VRChat_OSC_Integration_Guide.md) for details on how to configure and use the OSC integration.

## 📦 Installation

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- [VRChat](https://vrchat.com/) (for VRChat OSC integration)

### Quick Start

```bash
# Install from PyPI (recommended)
pip install avatarmcp

# Or install from source
git clone https://github.com/yourusername/avatarmcp.git
cd avatarmcp
pip install -e .

# Install required dependencies
pip install python-osc pyvrm
```

### Dependencies

Core dependencies (automatically installed):

- `python-osc`: For VRChat OSC communication
- `pyvrm`: For VRM model loading and manipulation
- `numpy`: For animation math
- `fastmcp`: MCP protocol implementation

Optional dependencies (for development and testing):

- `fastapi`: For the optional REST API
- `uvicorn`: ASGI server for the REST API

```bash

## 🚀 Quick Start

### Running the Server

```bash
# Start the MCP server
python -m avatarmcp
```

The server will start and listen for MCP commands on stdin/stdout. You can interact with it using any MCP 2.12.0-compatible client.

### Example MCP Commands

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "avatar.load",
  "params": {
    "id": "my_avatar",
    "path": "/path/to/avatar.vrm",
    "scale": 1.0
  }
}

{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "animation.play",
  "params": {
    "avatar_id": "my_avatar",
    "animation": "wave_hand",
    "loop": false
  }
}
```

### Optional REST API

For testing purposes, you can start the optional REST API server:

```bash
uvicorn avatarmcp.api:app --host 0.0.0.0 --port 8000
```

**Note:** The REST API is provided for testing and development purposes only and should not be used in production.

```python
from avatarmcp import VRChatAvatarController

import asyncio

async def main():
    # Create and initialize the controller
    controller = VRChatAvatarController("path/to/your/model.vrm")
    await controller.initialize()
    
    try:
        # Set a facial expression
        await controller.osc_integrator.set_expression("happy", 1.0)
        
        # Set a hand gesture
        await controller.osc_integrator.set_gesture("left", "peace")
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await controller.close()

asyncio.run(main())

```


### Running the Example

```bash

# Run the VRChat control example


python examples/vrchat_avatar_control.py --vrm path/to/your/model.vrm --demo

```


## ðŸ”§ Configuration

### OSC Settings

By default, AvatarMCP uses these OSC ports:

- **Receive Port**: 9000 (for receiving parameters from VRChat)

- **Send Port**: 9001 (for sending parameters to VRChat)



You can customize these in the `AvatarOSCConfig`:

```python
from avatarmcp import AvatarOSCConfig






config = AvatarOSCConfig(
    receive_port=9000,
    send_port=9001,
    server_ip="127.0.0.1"
)

```


### Parameter Mappings

You can define custom parameter mappings for your avatar:

```python
config.parameter_mappings = {





    "BlendShape.A": "VRC_AA",
    "BlendShape.E": "VRC_E",
    # Add more mappings as needed
}

```


## ðŸ¤– Integration with Other MCP Services

### OSCMCP Integration

AvatarMCP can be integrated with OSCMCP for advanced routing and processing:

```python
from fastmcp import FastMCP





from avatarmcp import AvatarOSCIntegrator

# Initialize MCP client
mcp = FastMCP("http://localhost:8000/mcp")






# Create and start the integrator
integrator = AvatarOSCIntegrator(mcp)





await integrator.start()

# Now you can control the avatar through OSCMCP
await integrator.set_expression("happy", 1.0)





```

## ðŸ“š API Reference

### VRChatOSCServer

Core OSC server for VRChat communication.

**Methods:**

- `start()`: Start the OSC server

- `stop()`: Stop the OSC server


- `set_gesture(hand, gesture, strength=1.0)`: Set a hand gesture

- `set_expression(expression, strength=1.0)`: Set a facial expression


- `set_viseme(viseme, strength=1.0)`: Set a viseme for lip sync

### VRMLoader

Load and parse VRM 2.0 models.

**Methods:**

- `from_file(file_path)`: Load a VRM model from file

- `get_blend_shape_names()`: Get all blend shape names


- `get_bone_names()`: Get all bone names

- `get_material_names()`: Get all material names



### AvatarOSCIntegrator

High-level integration with MCP ecosystem.

**Methods:**

- `start()`: Start the integrator

- `stop()`: Stop the integrator


- `load_vrm(file_path)`: Load a VRM model

- `set_gesture(hand, gesture, strength=1.0)`: Set a hand gesture


- `set_expression(expression, strength=1.0)`: Set a facial expression

## ðŸ›  Development

### Setup

```bash

# Clone the repository


git clone https://github.com/yourusername/avatarmcp.git
cd avatarmcp

# Install development dependencies
pip install -e ".[dev]"






# Install pre-commit hooks
pre-commit install





```

### Testing

```bash

# Run tests


pytest

# Run with coverage report
pytest --cov=avatarmcp tests/






# Run specific test file
pytest tests/test_osc_server.py -v





```

### Code Style

```bash

# Format code


black .

# Sort imports
isort .






# Check code style
flake8





```

## ðŸ¤ Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## ðŸ“„ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ðŸ“œ Credits

- VRM Consortium for the [VRM specification](https://vrm.dev/)

- VRChat for the amazing social VR platform


- The MCP community for building awesome tools

---

Made with â¤ï¸ by [Your Name] | [GitHub](https://github.com/yourusername)
