# 3D Visualization Guide

## Overview

The 3D viewport in AvatarMCP provides a real-time, interactive environment to visualize and manipulate your VRM avatars. This guide covers all aspects of the visualization system.

## Getting Started

### Enabling Visualization

By default, the 3D viewport is enabled. To disable it:

```python
# When initializing AvatarMCP
app = AvatarMCP(enable_visualization=False)
```

### System Requirements

- OpenGL 3.3+ compatible graphics card
- 1920x1080 minimum display resolution recommended
- Hardware-accelerated graphics recommended for best performance

## Viewport Controls

### Navigation

| Action | Mouse | Keyboard |
|--------|-------|----------|
| Rotate | Left-click + drag | Arrow keys |
| Pan | Right-click + drag | Shift + Arrow keys |
| Zoom | Scroll wheel | + / - keys |
| Reset View | Double-click viewport | Home key |
| Toggle Fullscreen | Double-click title | F11 |

### View Modes

1. **Solid (Default)**
   - Full textured rendering
   - Best for normal use

2. **Wireframe**
   - Shows mesh structure
   - Useful for debugging

3. **Shaded**
   - Flat shading
   - Good for examining mesh topology

4. **X-Ray**
   - See through the model
   - Great for complex rigs

### Camera Views

- **Perspective (P)**: 3D view with perspective
- **Front (1)**: Orthographic front view
- **Side (2)**: Orthographic side view
- **Top (3)**: Orthographic top view
- **Orbit (O)**: Orbiting camera around selection

## Lighting & Environment

### Light Controls

- **Intensity**: Adjust overall brightness
- **Direction**: Change light angle
- **Color**: Set light color temperature
- **Shadows**: Toggle shadow rendering

### Environment

- **Background**: Change viewport background
- **Grid**: Toggle ground grid
- **Axis**: Show/hide coordinate axes
- **Environment Map**: Load custom HDRIs

## Avatar Visualization

### Visual Aids

- **Bone Display**: Toggle bone visualization
- **Mesh Normals**: Show surface normals
- **Vertex Weights**: Visualize skinning weights
- **Morph Targets**: Highlight active morphs

### Performance Modes

1. **Full Quality**
   - Maximum detail
   - Best for final adjustments

2. **Performance**
   - Reduced quality
   - Better for older hardware

3. **Wireframe**
   - Minimal rendering
   - For slow systems

## Troubleshooting

### Common Issues

1. **Black Screen**
   - Check graphics drivers
   - Try disabling anti-aliasing

2. **Low FPS**
   - Reduce viewport quality
   - Close other 3D applications

3. **Missing Textures**
   - Check texture paths
   - Verify VRM material setup

## Advanced Features

### Multi-View Layouts

Choose from different viewport layouts:
- Single
- Two Panes (horizontal/vertical)
- Four Panes (quad)
- Custom split views

### Camera Bookmarking

Save and recall camera positions:
```python
# Save current camera position
app.visualization.save_camera("front_view")

# Recall saved position
app.visualization.load_camera("front_view")
```

### Screenshot & Recording

- Save high-res screenshots
- Record viewport animations
- Export image sequences

## Integration with Tools

### MCP Commands

Control visualization via MCP:
```json
{
  "command": "set_visualization",
  "params": {
    "mode": "wireframe",
    "show_grid": true,
    "camera": "perspective"
  }
}
```

### Python API

Direct Python control:
```python
# Get viewport instance
viewport = app.visualization.viewport

# Change settings
viewport.set_mode("wireframe")
viewport.set_background_color((0.1, 0.1, 0.1))

# Take screenshot
viewport.capture_screenshot("screenshot.png")
```

## Performance Optimization

### For Low-End Systems

1. Disable shadows
2. Reduce viewport resolution
3. Use simplified materials
4. Hide unnecessary elements

### For High-End Systems

1. Enable anti-aliasing
2. Increase shadow quality
3. Enable ambient occlusion
4. Use high-res textures

## Customization

### Themes

Choose from built-in color themes or create your own:
- Dark (default)
- Light
- High Contrast
- Custom

### Key Bindings

Remap controls in `config/visualization.json`:
```json
{
  "key_bindings": {
    "rotate": "left_mouse",
    "pan": "right_mouse",
    "zoom": "mouse_wheel"
  }
}
```

## Best Practices

1. **Organization**
   - Group related controls
   - Use consistent naming
   - Keep UI clean

2. **Performance**
   - Update only what changes
   - Batch similar operations
   - Use level of detail (LOD)

3. **Usability**
   - Provide visual feedback
   - Include tooltips
   - Support multiple input methods
