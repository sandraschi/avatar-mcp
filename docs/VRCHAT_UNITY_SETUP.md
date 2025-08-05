# VRChat and Unity 3D Integration Guide

## Table of Contents

$11. [System Requirements](#system-requirements)

$11. [Installation](#installation)


$11. [Project Setup](#project-setup)

$11. [Avatar Configuration](#avatar-configuration)


$11. [OSC Integration](#osc-integration)

$11. [Testing](#testing)


$11. [Troubleshooting](#troubleshooting)

$11. [Best Practices](#best-practices)



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

$11. Download from [unity.com/download](https://unity.com/download)

$11. Run installer and follow setup wizard


$11. Sign in with Unity ID

### 2. Unity Editor

$11. Open Unity Hub

$11. Go to "Installs" â†’ "Install Editor"


$11. Install **Unity 2022.3.11f1** (LTS)

   - Select modules:


     - Windows Build Support

     - Android Build Support


     - iOS Build Support (optional)

     - WebGL Build Support


     - Documentation

### 3. VRChat Creator Companion (VCC)

$11. Download from [vcc.docs.vrchat.com](https://vcc.docs.vrchat.com/vpm/install-vcc)

$11. Run installer


$11. Launch VCC and sign in with VRChat account

## Project Setup

### 1. Create New Project

$11. In VCC, click "New Project"

$11. Choose "Avatars" template


$11. Select Unity 2022.3.11f1

$11. Name your project


$11. Choose location (no spaces/special chars)

$11. Click "Create Project"



### 2. Install Required Packages

$11. In Unity, go to "VRChat" â†’ "Show Control Panel"

$11. Navigate to "Installed Packages"


$11. Install:

   - VRChat SDK3 - Avatars


   - VRM 0.112.0+

   - Poiyomi Toon Shader (recommended)



## Avatar Configuration

### 1. Import VRM Avatar

$11. Copy `.vrm` file to `Assets` folder

$11. Right-click â†’ "Import as VRM"


$11. In import window:

   - Check "Extract Materials and Textures"


   - Set "Normal Import" for humanoid

   - Click "Import"



### 2. Configure Avatar

$11. Select avatar in Project window

$11. In Inspector:


   - Set "Rig" â†’ "Animation Type" to "Humanoid"

   - Click "Apply"


$11. Go to "Configure" tab:

   - Set up humanoid bones


   - Configure blend shapes

   - Set up materials



## OSC Integration

### 1. VRChat OSC Setup

$11. Launch VRChat

$11. Go to Settings â†’ OSC


$11. Enable:

   - [x] OSC


   - [x] Allow External Control

$11. Note ports (default: 9000/9001)



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

$11. Create `test_osc.py` with example code

$11. Run script:



   ```powershell
   python test_osc.py
   ```

$11. Verify avatar responds to OSC commands

## Troubleshooting

### Common Issues

$11. **Avatar Not Moving**

   - Check VRC_AvatarDescriptor


   - Verify rig configuration

   - Ensure proper upload



$11. **OSC Not Working**

   - Verify ports match (9000/9001)


   - Check firewall settings

   - Ensure OSC enabled in VRChat



$11. **Performance Issues**

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
