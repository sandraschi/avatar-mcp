# AvatarMCP Desktop Avatar

A next-generation desktop avatar system that brings your VRM avatars to life on your desktop. Part of the AvatarMCP ecosystem, this solution provides a powerful, extensible platform for interactive 3D avatars in a desktop environment.

## 🚀 Quick Start

1. **Download** the latest release from [GitHub Releases](../../releases)
2. **Extract** all files to a folder
3. **Run** `DesktopAvatar.exe`
4. **Load an avatar** using OSC: `/avatar/load "path/to/avatar.vrm"`
5. **Control** via OSC messages on port 9000

See [Getting Started](Docs/GETTING_STARTED.md) for detailed instructions.

## 🌟 Key Features

### Core Functionality

- **High-Performance Rendering**
  - Real-time 3D avatar rendering with Unity URP
  - Advanced shaders for realistic materials and effects
  - Dynamic lighting and shadows

- **VRM 1.0 Support**
  - Full VRM specification compliance
  - Runtime VRM loading and instantiation
  - Blend shapes and bone animations

- **Window Management**
  - Transparent, non-rectangular windows
  - Click-through and always-on-top modes
  - Multi-monitor support
  - Window snapping and positioning

### Animation System

- **Full-Body IK**
  - Natural-looking poses and movements
  - Foot placement and ground adaptation
  - Hand tracking integration

- **Facial Expressions**
  - Blend shape controls
  - Viseme support for lip-sync
  - Eye tracking and blinking

- **Gestures & Emotes**
  - Predefined gesture library
  - Custom gesture recording
  - Emote wheel interface

### Integration & Extensibility

- **Open Sound Control (OSC)**
  - Bidirectional OSC communication
  - VRChat-compatible API
  - Custom message routing

- **Plugin System**
  - Extend functionality with C# plugins
  - Hot-reloading support
  - Sandboxed execution

- **API & SDK**
  - Comprehensive developer documentation
  - Example projects
  - Community plugin marketplace

### Performance & Optimization

- **Dynamic LOD System**
  - Automatic detail adjustment
  - CPU/GPU performance profiling
  - Background resource management

- **Memory Management**
  - Efficient asset loading
  - Object pooling
  - Garbage collection optimization

## 🚀 Getting Started

### System Requirements

#### Minimum
- **OS**: Windows 10 64-bit (20H2 or later)
- **CPU**: Intel i5-4590 / AMD FX 8350 equivalent or greater
- **GPU**: NVIDIA GTX 970 / AMD R9 290 or greater
- **RAM**: 8GB
- **Disk Space**: 5GB available space

#### Recommended
- **OS**: Windows 11 64-bit (22H2 or later)
- **CPU**: Intel i7-9700K / AMD Ryzen 7 3700X or greater
- **GPU**: NVIDIA RTX 2070 / AMD RX 6700 XT or greater
- **RAM**: 16GB or more
- **Disk**: SSD with 10GB+ available space

### Installation

#### Prerequisites

1. **Unity Hub** with Unity 2022.3.11f1 LTS
2. **Git LFS** (for handling large binary files)
3. **Python 3.8+** (for MCP Core Components)

#### Quick Start

```bash
# Clone the repository (including submodules)
git clone --recurse-submodules https://github.com/yourusername/unity-desktop-avatar.git
cd unity-desktop-avatar

# Install Python dependencies
pip install -r requirements.txt

# Launch Unity Hub with the project
start unityhub://"D:/path/to/unity-desktop-avatar"
```

#### Project Setup

1. Open the project in Unity 2022.3.11f1 LTS

2. Import required packages:
   - Universal RP
   - VRM 1.0
   - ExtOSC
   - TextMeshPro (Essential)

3. Open the `Assets/Scenes/Main.unity` scene

4. Configure build settings for Windows platform

5. Click "Build & Run"

## Configuration

### Project Structure

```text
unity-desktop-avatar/
├── Assets/
│   ├── Animations/        # Animation clips and controllers
│   ├── Materials/         # Custom shaders and materials
│   ├── Prefabs/           # Reusable prefabs
│   ├── Resources/         # Runtime resources
│   ├── Scenes/            # Unity scenes
│   ├── Scripts/           # C# source code
│   │   ├── Core/          # Core systems
│   │   ├── UI/            # User interface
│   │   ├── VRM/           # VRM integration
│   │   └── Plugins/       # Plugin system
│   └── StreamingAssets/   # VRM models and assets
├── Docs/                  # Documentation
├── Plugins/               # Native plugins
└── ProjectSettings/       # Unity project settings
```

### Configuration Files

#### `config.json`

```json
{
  "window": {
    "width": 800,
    "height": 1200,
    "transparent": true,
    "clickThrough": false,
    "alwaysOnTop": true,
    "position": {
      "x": 0,
      "y": 0
    }
  },
  "avatar": {
    "defaultPath": "StreamingAssets/Avatars/default.vrm",
    "scale": 1.0,
    "autoLoad": true
  },
  "osc": {
    "enabled": true,
    "port": 9000,
    "address": "127.0.0.1"
  },
  "performance": {
    "targetFPS": 60,
    "vSyncCount": 1,
    "physicsRate": 0.02
  }
}
```

## 📚 Documentation

### Getting Started
- [Quick Start Guide](Docs/GETTING_STARTED.md)
- [Installation](Docs/INSTALLATION.md)
- [Configuration](Docs/CONFIGURATION.md)

### User Guide
- [Basic Controls](Docs/GUIDE_BASICS.md)
- [Avatar Setup](Docs/GUIDE_AVATAR.md)
- [OSC Integration](Docs/GUIDE_OSC.md)
- [Advanced Features](Docs/GUIDE_ADVANCED.md)

### Developer Documentation
- [Architecture Overview](Docs/ARCHITECTURE.md)
- [API Reference](Docs/API_REFERENCE.md)
- [Plugin Development](Docs/PLUGIN_DEVELOPMENT.md)
- [Performance Optimization](Docs/PERFORMANCE.md)

### Community & Support
- [FAQ](Docs/FAQ.md)
- [Troubleshooting](Docs/TROUBLESHOOTING.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## 🌐 OSC API Reference

### Base Address
All OSC messages should be prefixed with `/avatar` for avatar control or `/window` for window management.

### Avatar Control

#### Loading & Management
- `/avatar/load [path]` - Load a VRM avatar from the specified path
- `/avatar/unload` - Unload the current avatar
- `/avatar/reset` - Reset avatar to default state
- `/avatar/visibility [0-1]` - Set avatar visibility (0=hidden, 1=visible)

#### Transform
- `/avatar/position [x] [y] [z]` - Set world position
- `/avatar/rotation [x] [y] [z] [w]` - Set rotation (quaternion)
- `/avatar/scale [value]` - Uniform scale
- `/avatar/lookat [x] [y] [z]` - Make avatar look at point

#### Animation
- `/avatar/animation/play [name] [loop] [speed]` - Play animation
- `/avatar/animation/stop [name]` - Stop specific animation
- `/avatar/animation/stop_all` - Stop all animations
- `/avatar/animation/crossfade [name] [duration] [layer]` - Smooth transition
- `/avatar/animation/parameter [name] [value]` - Set animation parameter

#### Expressions
- `/avatar/expression/set [preset] [value]` - Set expression by preset
- `/avatar/expression/blendshape [name] [value]` - Set blend shape value
- `/avatar/expression/reset` - Reset all expressions
- `/avatar/expression/eyebrow [left] [right]` - Set eyebrow position
- `/avatar/expression/eye [left] [right]` - Set eye openness
- `/avatar/expression/mouth [shape] [value]` - Control mouth shapes

#### Movement
- `/avatar/movement/walk [direction] [speed]` - Walk in direction
- `/avatar/movement/run [direction] [speed]` - Run in direction
- `/avatar/movement/turn [degrees] [speed]` - Rotate avatar
- `/avatar/movement/jump [height]` - Make avatar jump
- `/avatar/movement/stop` - Stop all movement

#### Gestures
- `/avatar/gesture/play [name] [intensity]` - Play gesture
- `/avatar/gesture/stop [name]` - Stop gesture
- `/avatar/gesture/record/start [name]` - Start recording
- `/avatar/gesture/record/stop` - Stop recording

### Window Control

#### Positioning
- `/window/position [x] [y]` - Set window position
- `/window/size [width] [height]` - Set window size
- `/window/move [dx] [dy]` - Move window relative
- `/window/center` - Center window on screen
- `/window/monitor [index]` - Move to monitor

#### Appearance
- `/window/opacity [0-1]` - Set window opacity
- `/window/clickthrough [0/1]` - Toggle click-through
- `/window/alwaysontop [0/1]` - Toggle always on top
- `/window/visibility [0/1]` - Show/hide window
- `/window/border [0/1]` - Toggle window border

#### Behavior
- `/window/focus` - Bring window to front
- `/window/minimize` - Minimize window
- `/window/maximize` - Maximize window
- `/window/restore` - Restore window
- `/window/close` - Close application

### System
- `/system/status` - Get status (returns JSON)
- `/system/version` - Get version info
- `/system/restart` - Restart application
- `/system/exit` - Exit application

## 🚀 Advanced Usage

### Example: Complex Animation Sequence
```
# Load avatar
/avatar/load "C:/Avatars/my_avatar.vrm"

# Position and scale
/avatar/position 0 0 0
/avatar/scale 1.2

# Play animation with parameters
/avatar/animation/play "dance" 1 1.0
/avatar/animation/parameter "dance_speed" 1.5

# Set expressions
/avatar/expression/set "happy" 0.8
/avatar/expression/eyebrow 0.2 0.1

# Window setup
/window/position 100 100
/window/size 800 1200
/window/opacity 0.95
/window/alwaysontop 1
```

### Example: Interactive Controls
```
# Make window draggable
/window/clickthrough 0

# Set up hotkeys
# (These would be handled by your input system)
# F1: Toggle visibility
# F2: Next avatar
# F3: Previous avatar
# F4: Toggle click-through
```

## 🛠 Development

### Building from Source

#### Prerequisites
- Unity 2022.3.11f1 LTS with:
  - Windows Build Support
  - Universal Windows Platform Build Support
  - Android Build Support (optional)
  - iOS Build Support (optional)
- Git LFS
- Python 3.8+

#### Build Process
1. Clone the repository with submodules:
   ```bash
   git clone --recurse-submodules https://github.com/yourusername/unity-desktop-avatar.git
   cd unity-desktop-avatar
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Open the project in Unity
4. Build from `File > Build Settings`

### Project Structure

#### Core Modules
- **AvatarSystem**: VRM loading, animation, and expression handling
- **WindowManager**: Transparent window and input handling
- **OSCService**: Communication layer for OSC messages
- **UIManager**: User interface and controls
- **PluginSystem**: Extensibility framework

#### Directory Structure

```text
Assets/
├── Animations/        # Animation controllers and clips
│   ├── Controllers/   # Animator controllers
│   ├── Clips/         # Animation clips
│   └── Avatars/       # Avatar-specific animations
│
├── Materials/         # Custom shaders and materials
│   ├── Shaders/       # Custom shader files
│   ├── Textures/      # Texture assets
│   └── Presets/       # Material presets
│
├── Prefabs/           # Reusable prefabs
│   ├── UI/            # UI elements
│   ├── Avatars/       # Avatar prefabs
│   └── Effects/       # Visual effects
│
├── Resources/         # Runtime resources
│   ├── Config/        # Configuration files
│   ├── Localization/  # Localization strings
│   └── Presets/       # Default presets
│
├── Scenes/            # Unity scenes
│   ├── Main.unity     # Main application scene
│   ├── Setup.unity    # First-time setup
│   └── Tests/         # Test scenes
│
├── Scripts/           # C# source code
│   ├── Core/          # Core systems
│   │   ├── Animation/ # Animation system
│   │   ├── Audio/     # Audio processing
│   │   ├── Network/   # Networking
│   │   └── Utils/     # Utility classes
│   │
│   ├── UI/            # User interface
│   │   ├── Controls/  # UI controls
│   │   ├── Windows/   # Window managers
│   │   └── Themes/    # UI themes
│   │
│   ├── VRM/           # VRM integration
│   │   ├── Loaders/   # VRM loaders
│   │   └── Shaders/   # VRM shaders
│   │
│   └── Plugins/       # Plugin system
│       ├── API/       # Public API
│       └── SDK/       # SDK components
│
└── StreamingAssets/   # Files included in build
    ├── Avatars/       # Default avatars
    ├── Plugins/       # Bundled plugins
    └── Resources/     # Additional resources
```

### Dependencies

#### Core Dependencies
- **Unity 2022.3.11f1 LTS**: Game engine
- **UniVRM 0.107.0**: VRM format support
- **ExtOSC 2.0**: OSC communication
- **DOTween Pro**: Animation tweening
- **Newtonsoft.Json**: JSON processing
- **UniTask**: Async/await support

#### Development Dependencies
- **GitVersion**: Version management
- **Unity Test Framework**: Unit testing
- **GitHub for Unity**: Version control
- **Odin Inspector**: Enhanced inspector

### Testing

#### Unit Tests
```bash
# Run all unit tests
./test.ps1

# Run specific test category
./test.ps1 -filter "FullyQualifiedName~AvatarTests"
```

#### Integration Tests
1. Build the test runner
2. Run the test scene in Unity
3. View results in the Test Runner window

### Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

### Code Style
- Follow the [C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- Use XML documentation comments
- Keep methods focused and small
- Write unit tests for new features

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- **Unity Technologies** for the amazing game engine
- **VRM Consortium** for the VRM standard
- **Open-source contributors** who made this possible
- **Community** for feedback and support

## 📚 Resources

- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [VRM Specification](https://vrm.dev/)
- [OSC Protocol](https://opensoundcontrol.stanford.edu/)
- [C# Documentation](https://docs.microsoft.com/en-us/dotnet/csharp/)

## 🌟 Show Your Support

If you find this project useful, please consider giving it a ⭐️ on GitHub!
