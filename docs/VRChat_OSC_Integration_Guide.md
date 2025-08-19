# VRChat Avatar Integration with OSC Control: Complete Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Toolchain Overview](#toolchain-overview)
3. [Detailed Tool Descriptions](#detailed-tool-descriptions)
4. [VRChat Account Setup](#vrchat-account-setup)
5. [Development Environment Setup](#development-environment-setup)
6. [VRM to VRChat Conversion](#vrm-to-vrchat-conversion)
7. [OSC Integration](#osc-integration)
8. [Animation System](#animation-system)
9. [Testing & Deployment](#testing--deployment)
10. [Advanced Topics](#advanced-topics)
11. [Troubleshooting](#troubleshooting)
12. [Example Projects](#example-projects)

## Introduction

This guide provides a comprehensive walkthrough of integrating a VRM avatar into VRChat with OSC control. It covers everything from initial setup to advanced customization, including detailed descriptions of all tools and their configurations.

## Toolchain Overview

### Core Tools
1. **Unity 2019.4.31f1** - Game engine for avatar development
2. **VRChat Creator Companion (VCC)** - Project and dependency management
3. **VRM to VRChat Converter** - Converts VRM avatars to VRChat format
4. **OSC Clients** - For sending control signals to VRChat
5. **Blender** - Optional but recommended for model adjustments

### Development Workflow
1. Prepare VRM model
2. Set up Unity project with VRChat SDK
3. Import and convert VRM to VRChat format
4. Configure avatar parameters and animations
5. Set up OSC control interface
6. Test and optimize
7. Deploy to VRChat

## Detailed Tool Descriptions

### 1. Unity 2019.4.31f1
- **Purpose**: Game engine for avatar creation and animation
- **Download**: [Unity Download Archive](https://unity3d.com/get-unity/download/archive)
- **Installation**:
  1. Download Unity Hub
  2. Install Unity 2019.4.31f1 with these modules:
     - Windows Build Support (IL2CPP)
     - WebGL Build Support
     - Android Build Support (for Quest)
- **Configuration**:
  - Set up license (Personal/Plus/Pro)
  - Configure external tools (Git, VS Code/Visual Studio)

### 2. VRChat Creator Companion (VCC)
- **Purpose**: Manages VRChat project dependencies and SDKs
- **Download**: [GitHub Releases](https://github.com/vrchat-community/creator-companion/releases)
- **Features**:
  - Project templates
  - Dependency management
  - One-click SDK installation
  - Project validation
- **Installation**:
  1. Download latest release
  2. Run installer
  3. Log in with VRChat account

### 3. VRM to VRChat Conversion Tools

#### UniVRM
- **Purpose**: Import/export VRM models in Unity
- **Installation**:
  ```
  Window > Package Manager > + > Add package from git URL
  https://github.com/vrm-c/UniVRM.git?path=/Assets/UniVRM
  ```
- **Key Features**:
  - VRM model validation
  - Humanoid rig configuration
  - Material conversion

#### VRM4U (Alternative)
- **Purpose**: Advanced VRM import/export with additional features
- **GitHub**: [VRM4U](https://github.com/izayoijiichan/VRM4U)
- **Benefits**:
  - Better material conversion
  - Advanced animation features
  - More import/export options

### 4. OSC Tools

#### TouchOSC
- **Purpose**: Mobile/Desktop OSC controller
- **Platforms**: iOS, Android, macOS, Windows
- **Features**:
  - Customizable interface
  - MIDI support
  - Template editor
- **Setup**:
  1. Install on device
  2. Connect to same network as PC
  3. Set IP to PC's local IP
  4. Set port to 9000 (VRChat default)

#### OSCulator (macOS/Windows)
- **Purpose**: Advanced OSC/MIDI routing
- **Features**:
  - Message routing
  - Signal processing
  - Preset management
- **Use Case**: Complex OSC setups with multiple controllers

#### Python-OSC
- **Purpose**: Custom OSC solutions
- **Installation**: `pip install python-osc`
- **Example Use**:
  ```python
  from pythonosc import udp_client
  client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
  client.send_message("/avatar/parameters/Dance", 1)
  ```

### 5. Blender (Optional but Recommended)
- **Purpose**: 3D modeling and rigging
- **Download**: [blender.org](https://www.blender.org/download/)
- **Key Add-ons**:
  - CATS Blender Plugin
  - VRM Add-on
  - Rigify
- **Use Cases**:
  - Model adjustments
  - Weight painting
  - Custom animations

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Unity Setup](#unity-setup)
3. [VRM to VRChat Conversion](#vrm-to-vrchat-conversion)
4. [OSC Configuration](#osc-configuration)
5. [Animation Controller Setup](#animation-controller-setup)
6. [Testing & Deployment](#testing--deployment)
7. [Troubleshooting](#troubleshooting)
8. [Example OSC Commands](#example-osc-commands)

## Prerequisites

### Software Requirements

### Account Requirements for Development
1. **Rank Progression**
   - New User (default) - Limited uploads
   - User (2+ weeks old, 10+ hours in-game) - Standard uploads
   - Known User (1+ month, 50+ hours) - Increased limits
   - Trusted User (3+ months, 250+ hours) - Maximum privileges

2. **Developer Settings**
   - Enable "Developer Mode" in VRChat settings
   - Configure security settings for API access
   - Set up VRChat home location

3. **Content Management**
   - Create avatar base
   - Set up content folders
   - Configure privacy settings

## Development Environment Setup

### 1. Unity Configuration

#### 1.1 Unity Hub Setup
1. **Installation**
   - Download Unity Hub from [unity.com](https://unity.com/download)
   - Run installer with default settings
   - Log in with Unity account (Personal/Plus/Pro)

2. **Editor Installation**
   - Navigate to Installs > Install Editor
   - Select 2019.4.31f1 (LTS)
   - Install these modules:
     - Windows Build Support (IL2CPP)
     - WebGL Build Support
     - Android Build Support (for Quest)
     - Microsoft Visual Studio Community 2019
     - Windows 10 SDK (10.0.19041.0)
     - Documentation

3. **Project Templates**
   - 3D (Core)
   - Universal Render Pipeline (URP)
   - High Definition RP (HDRP) - Optional

### 2. VRChat Development Setup

#### 2.1 VCC Installation
1. **Download**
   - Get latest VCC from [GitHub](https://github.com/vrchat-community/creator-companion/releases)
   - Run installer with admin privileges

2. **Configuration**
   - Log in with VRChat account
   - Set default project location
   - Configure Git integration
   - Set up backup preferences

#### 2.2 Project Creation
1. **New Project**
   - Launch VCC
   - Click "New Project"
   - Select "VRChat Avatar" template
   - Configure:
     - Project Name: `MyVRChatAvatar`
     - Location: `C:\VRChat\Projects\`
     - Unity Version: 2019.4.31f1
     - Render Pipeline: Standard
     - Enable VRCSDK3 - Avatars

2. **Initial Setup**
   - Wait for project generation
   - Open project in Unity
   - Import required SDKs through VCC
   - Set up version control (Git)

### 3. Essential Packages

#### 3.1 Core Packages
1. **VRChat SDK**
   - Avatars 3.0
   - Worlds 3.0 (optional)
   - UdonSharp (for advanced scripting)

2. **VRM Integration**
   - UniVRM (latest stable)
   - VRM Shaders (for material conversion)
   - VRM SpringBone (for hair/cloth physics)

3. **Utility Packages**
   - Final IK (for better IK)
   - DOTween Pro (for smooth animations)
   - Odin Inspector (for better editor tools)

### 4. Development Tools

#### 4.1 Code Editors
1. **Visual Studio 2019**
   - Install with Unity workload
   - Configure as default script editor
   - Install Unity Tools extension

2. **VS Code** (Alternative)
   - Install C# extension
   - Install Unity Debugger
   - Configure OmniSharp path

#### 4.2 Version Control
1. **Git Setup**
   - Install Git for Windows
   - Configure global .gitignore for Unity
   - Set up Git LFS for large files

2. **GitHub Desktop**
   - Install from [desktop.github.com](https://desktop.github.com/)
   - Log in with GitHub account
   - Clone repository

### 5. Performance Tools

#### 5.1 Profiling
- Unity Profiler
- VRChat SDK Control Panel
- Udon Profiler

#### 5.2 Optimization
- Mesh Baker (for combining meshes)
- Simplygon (for LOD generation)
- TexturePacker (for atlas generation)

### 6. Testing Environment

#### 6.1 Local Testing
- Unity Play Mode
- VRChat SDK Play Mode
- Local Build Testing

#### 6.2 Multiplayer Testing
- VRChat Test Builds
- Private Instances
- Friends-Only Worlds

### 7. Documentation

#### 7.1 Local Documentation
- Project README.md
- Changelog.md
- Documentation/ folder

#### 7.2 Online Resources
- VRChat Docs
- Unity Manual
- Community Forums

### 8. Backup Strategy

#### 8.1 Local Backups
- Daily project backups
- Versioned asset storage
- Cloud sync (OneDrive/Dropbox)

#### 8.2 Version Control
- Regular commits
- Feature branches
- Release tags

## VRM to VRChat Conversion

1. **Import VRM Model**
   - In Unity, go to Window > Package Manager
   - Click "+" > "Add package from git URL"
   - Enter: `https://github.com/vrm-c/UniVRM.git?path=/Assets/UniVRM`
   - Import your VRM file (drag into Project window)

2. **Configure Humanoid Rig**
   - Select your VRM in Project window
   - In Inspector, go to Rig tab
   - Set Animation Type to "Humanoid"
   - Click "Configure" and ensure all bones are mapped correctly
   - Click "Apply"

3. **Set Up VRChat Avatar**
   - Drag VRM model into Scene
   - Select the model in Hierarchy
   - Add Component > VRChat > SDK > Avatar Descriptor
   - Configure View Position (eye height)
   - Set up lip sync and eye look settings

## OSC Configuration

1. **Enable OSC in VRChat**
   - Go to VRChat Settings > OSC
   - Enable OSC
   - Note the port numbers (default: 9000 for receiving, 9001 for sending)

2. **Set Up OSC Parameters**
   - In Unity, select your avatar
   - In VRC Avatar Descriptor, go to "Parameters"
   - Add parameters for each animation you want to control:
     - `anim_bool` for toggles (e.g., `Dance`, `Wave`)
     - `anim_float` for blends (e.g., `Mood`, `Energy`)

3. **OSC Client Setup**
   - Install an OSC client (e.g., TouchOSC, OSCeleton, or custom script)
   - Configure to send to `127.0.0.1` on port 9000
   - Map controls to VRChat parameters

## Animation Controller Setup

1. **Create Animation Controller**
   - Right-click in Project > Create > Animator Controller
   - Name it (e.g., `Avatar_OSC_Controller`)
   - Double-click to open Animator window

2. **Set Up States**
   - Right-click in Animator > Create State > Empty
   - Name states (e.g., `Idle`, `Dance`, `Wave`)
   - Create transitions between states
   - Set up parameters for transitions

3. **Connect to VRChat**
   - Select your avatar
   - In Animator component, drag your new controller to Controller field
   - Ensure "Apply Root Motion" is unchecked

## Testing & Deployment

1. **Test in Unity**
   - Enter Play mode
   - Use OSC client to send test messages
   - Verify animations trigger correctly

2. **Build & Upload**
   - Go to VRChat SDK > Build & Test
   - Sign in if prompted
   - Click "Build & Publish"
   - Set avatar name and description
   - Click "Upload"

3. **Test in VRChat**
   - Launch VRChat
   - Go to Menu > Avatars
   - Find your uploaded avatar
   - Select and confirm
   - Test OSC controls

## Troubleshooting

### Common Issues
1. **Avatar Not Appearing**
   - Check VRChat SDK is installed correctly
   - Verify avatar scale is not too large/small
   - Ensure all required components are attached

2. **OSC Not Working**
   - Check VRChat OSC settings
   - Verify correct IP (127.0.0.1) and port (9000)
   - Ensure no firewall is blocking the connection

3. **Animations Not Playing**
   - Check animator controller setup
   - Verify parameter names match exactly
   - Ensure animation states have valid clips

## Example OSC Commands

### Toggle Animation (Bool)
```
/avatar/parameters/Dance 1  # Start dance
/avatar/parameters/Dance 0  # Stop dance
```

### Control Float Parameter
```
/avatar/parameters/Mood 0.5  # Set mood to 50%
```

### Trigger Animation (One-shot)
```
/avatar/parameters/TriggerWave  # No value needed for triggers
```

### Multiple Parameters
```
/avatar/parameters/Mood 0.8
/avatar/parameters/Energy 0.6
```

## Advanced: Python OSC Control Example

```python
from pythonosc import udp_client

def send_osc(address: str, value):
    client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
    
    if isinstance(value, bool):
        client.send_message(f"/avatar/parameters/{address}", int(value))
    elif isinstance(value, (int, float)):
        client.send_message(f"/avatar/parameters/{address}", float(value))
    else:
        client.send_message(f"/avatar/parameters/{address}", value)

# Example usage
send_osc("Dance", True)  # Start dancing
send_osc("Mood", 0.8)    # Set mood to 80%
```

## Next Steps
- Create custom animations in Unity
- Set up more complex animation layers
- Implement gesture controls
- Add audio-reactive elements
- Create custom shaders for visual effects

## Support
For additional help, refer to:
- [VRChat Documentation](https://docs.vrchat.com/)
- [VRChat Discord](https://discord.gg/vrchat)
- [OSC Protocol Documentation](https://docs.vrchat.com/docs/osc-overview)
