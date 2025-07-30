# AvatarMCP

> MCP server for managing and animating VRM avatars

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- 🚀 Load and manage VRM avatars
- 🎭 Apply animations and expressions
- ⚡ FastMCP 2.10+ compliant
- 📦 Easy installation and setup

## Installation

```bash
pip install -e .
```

## Usage

```python
from avatarmcp import AvatarService

# Initialize the service
service = AvatarService()

# Load a VRM model
avatar = service.load_vrm("path/to/model.vrm")

# Apply an animation
service.play_animation(avatar, "wave")
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```

## License

MIT
