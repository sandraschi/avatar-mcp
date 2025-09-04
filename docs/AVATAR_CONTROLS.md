# Avatar Controls for AvatarMCP

This document provides comprehensive documentation for the advanced avatar controls available in AvatarMCP.

## Table of Contents
- [Overview](#overview)
- [Bone Control](#bone-control)
- [Morph Target Control](#morph-target-control)
- [Export Tools](#export-tools)
- [API Reference](#api-reference)
- [Examples](#examples)

## Overview

The AvatarMCP system now includes advanced controls for manipulating avatars at a fine-grained level. These controls are organized into three main categories:

1. **Bone Control**: Precise manipulation of individual bones
2. **Morph Target Control**: Control over blendshapes and morph targets
3. **Export Tools**: Export avatars to various formats

## Bone Control

### Features
- Transform individual bones (position, rotation, scale)
- Support for local and world space transformations
- Hierarchical bone manipulation

### Usage

```python
# Import the bone control tool
from avatarmcp.avatar_controls import BoneControlTool

# Create a bone control instance
bone_control = BoneControlTool()

# Move a bone
await bone_control.execute(
    bone_name="LeftHand",
    transform={
        "position": {"x": 0.1, "y": 0, "z": 0},
        "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
        "space": "local"
    }
)
```

## Morph Target Control

### Features
- Control blend shape weights (0.0 to 1.0)
- Batch updates for multiple morph targets
- Reset functionality for non-specified targets

### Usage

```python
from avatarmcp.avatar_controls import MorphControlTool

morph_control = MorphControlTool()

# Update morph targets
await morph_control.execute(
    targets=[
        {"name": "Blink_Left", "weight": 0.8},
        {"name": "Smile", "weight": 0.5}
    ],
    reset_others=True
)
```

## Export Tools

### Features
- Export to FBX format
- Export as Unity package
- VRChat SDK integration
- Animation export support

### Usage

```python
from avatarmcp.avatar_controls import ExportTool

export_tool = ExportTool()

# Export to FBX
await export_tool.execute(
    format="fbx",
    include_animations=True,
    optimize_meshes=True,
    platform="vrc"
)
```

## API Reference

### BoneControlTool

#### Methods
- `execute(bone_name: str, transform: Dict) -> ControlResult`
  - Applies the specified transform to the bone

### MorphControlTool

#### Methods
- `execute(targets: List[Dict], reset_others: bool = False) -> ControlResult`
  - Updates the specified morph targets
  - If `reset_others` is True, resets all other morphs to zero

### ExportTool

#### Methods
- `execute(format: str, **options) -> ControlResult`
  - Exports the avatar in the specified format
  - Additional options include `include_animations`, `optimize_meshes`, etc.

## Examples

### Complex Bone Animation

```python
# Create a waving animation
import asyncio

async def wave_animation(bone_control):
    for i in range(10):
        angle = (i / 10.0) * 3.14159 * 2
        await bone_control.execute(
            bone_name="RightHand",
            transform={
                "position": {"x": 0, "y": 0.2 * (1 + math.sin(angle)), "z": 0},
                "rotation": {
                    "x": math.sin(angle) * 0.5,
                    "y": 0,
                    "z": 0,
                    "w": math.cos(angle) * 0.5 + 0.5
                }
            }
        )
        await asyncio.sleep(0.1)
```

### Exporting for VRChat

```python
# Export a VRChat-ready avatar
result = await export_tool.execute(
    format="vrcsdk",
    platform="vrc",
    include_animations=True,
    optimize_meshes=True,
    output_dir="exports"
)

if result.success:
    print(f"Exported to: {result.data['output_path']}")
else:
    print(f"Export failed: {result.error}")
```

## Integration with FastMCP 2.12+

All controls are fully compatible with FastMCP 2.12+ and can be accessed through the MCP protocol:

```python
# Example of using bone control through MCP
response = await mcp_client.send_command(
    "bone_control",
    {
        "bone_name": "Head",
        "transform": {
            "rotation": {"x": 0, "y": 0.5, "z": 0, "w": 0.9}
        }
    }
)
```
