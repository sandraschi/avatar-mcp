# AvatarMCP

> Advanced VRM avatar management and animation server with VRChat integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- **VRM 2.0 Support**: Load and manage VRM 2.0 avatar models
- **VRChat Integration**: Seamless control of VRChat avatars via OSC
- **OSCMCP Integration**: Connect with other MCP services
- **Real-time Control**: Manipulate avatar parameters in real-time
- **Blend Shapes & Bones**: Full support for facial expressions and skeletal animation
- **Gesture System**: Predefined gestures and custom mappings
- **Expression Mapping**: Map expressions to avatar parameters
- **DXT Packaging**: Easy deployment and integration

## 📖 Documentation

- [VRChat & Unity 3D Setup Guide](docs/VRCHAT_UNITY_SETUP.md) - Comprehensive guide for setting up VRChat, Unity, and OSC integration
- [API Reference](docs/API.md) - Detailed API documentation

## 📦 Installation

### Prerequisites

- Python 3.9+
- pip
- [VRChat](https://vrchat.com/) (for VRChat integration)


### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/avatarmcp.git
cd avatarmcp

# Install with dependencies
pip install -e .

# Install optional dependencies for VRM parsing
pip install pygltflib numpy
```

## 🎮 Quick Start

### Basic Usage

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

## 🔧 Configuration

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

## 🤖 Integration with Other MCP Services

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

## 📚 API Reference

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


## 🛠 Development

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

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📜 Credits

- VRM Consortium for the [VRM specification](https://vrm.dev/)
- VRChat for the amazing social VR platform
- The MCP community for building awesome tools

---

Made with ❤️ by [Your Name] | [GitHub](https://github.com/yourusername)
