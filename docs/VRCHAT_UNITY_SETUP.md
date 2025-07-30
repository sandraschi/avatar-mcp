# VRChat and Unity 3D Integration Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Project Setup](#project-setup)
4. [Avatar Configuration](#avatar-configuration)
5. [OSC Integration](#osc-integration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## System Requirements

### Minimum Specifications

- **OS**: Windows 10/11 64-bit
- **CPU**: Intel i5-4590 / AMD FX 8350 or better
- **RAM**: 8GB+
- **GPU**: NVIDIA GTX 970 / AMD R9 290 or better
- **Storage**: 10GB free space (SSD recommended)

### Recommended Specifications

- **OS**: Windows 11 64-bit
- **CPU**: Intel i7-9700K / AMD Ryzen 7 3700X or better
- **RAM**: 16GB+
- **GPU**: NVIDIA RTX 2070 / AMD RX 5700 XT or better
- **Storage**: NVMe SSD with 20GB+ free space

## Installation

### 1. Unity Hub

1. Download from [unity.com/download](https://unity.com/download)
2. Run installer and follow setup wizard
3. Sign in with Unity ID

### 2. Unity Editor

1. Open Unity Hub
2. Go to "Installs" → "Install Editor"
3. Install **Unity 2022.3.11f1** (LTS)
   - Select modules:
     - Windows Build Support
     - Android Build Support
     - iOS Build Support (optional)
     - WebGL Build Support
     - Documentation

### 3. VRChat Creator Companion (VCC)

1. Download from [vcc.docs.vrchat.com](https://vcc.docs.vrchat.com/vpm/install-vcc)
2. Run installer
3. Launch VCC and sign in with VRChat account

## Project Setup

### 1. Create New Project

1. In VCC, click "New Project"
2. Choose "Avatars" template
3. Select Unity 2022.3.11f1
4. Name your project
5. Choose location (no spaces/special chars)
6. Click "Create Project"

### 2. Install Required Packages

1. In Unity, go to "VRChat" → "Show Control Panel"
2. Navigate to "Installed Packages"
3. Install:
   - VRChat SDK3 - Avatars
   - VRM 0.112.0+
   - Poiyomi Toon Shader (recommended)

## Avatar Configuration

### 1. Import VRM Avatar

1. Copy `.vrm` file to `Assets` folder
2. Right-click → "Import as VRM"
3. In import window:
   - Check "Extract Materials and Textures"
   - Set "Normal Import" for humanoid
   - Click "Import"

### 2. Configure Avatar

1. Select avatar in Project window
2. In Inspector:
   - Set "Rig" → "Animation Type" to "Humanoid"
   - Click "Apply"
3. Go to "Configure" tab:
   - Set up humanoid bones
   - Configure blend shapes
   - Set up materials

## OSC Integration

### 1. VRChat OSC Setup

1. Launch VRChat
2. Go to Settings → OSC
3. Enable:
   - [x] OSC
   - [x] Allow External Control
4. Note ports (default: 9000/9001)

### 2. Python Environment

```powershell
# Create and activate venv
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install deps
pip install python-osc pygltflib numpy
```

## Testing

### 1. Run Test Script

1. Create `test_osc.py` with example code
2. Run script:

   ```powershell
   python test_osc.py
   ```

3. Verify avatar responds to OSC commands

## Troubleshooting

### Common Issues

1. **Avatar Not Moving**
   - Check VRC_AvatarDescriptor
   - Verify rig configuration
   - Ensure proper upload

2. **OSC Not Working**
   - Verify ports match (9000/9001)
   - Check firewall settings
   - Ensure OSC enabled in VRChat

3. **Performance Issues**
   - Optimize polygon count
   - Use LOD groups
   - Optimize materials

## Best Practices

### Version Control

- Use Git LFS for binary files
- Maintain clean project structure
- Document parameters

### Performance

- Keep polycount under 70k for Quest
- Use texture atlases
- Optimize blend shapes

### Documentation

- Document all parameters
- Maintain changelog
- Include setup instructions
