# Getting Started with AvatarMCP Desktop Avatar

## Overview

The AvatarMCP Desktop Avatar is a Unity-based application that brings your VRM avatars to life on your desktop. It provides a transparent, interactive window that displays 3D avatars with real-time animation and OSC control.

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 64-bit (20H2 or later)
- **CPU**: Intel i5-4590 / AMD FX 8350 or equivalent
- **GPU**: NVIDIA GTX 970 / AMD R9 290 or equivalent
- **RAM**: 8GB
- **Storage**: 5GB available space

### Recommended Requirements
- **OS**: Windows 11 64-bit (22H2 or later)
- **CPU**: Intel i7-9700K / AMD Ryzen 7 3700X or equivalent
- **GPU**: NVIDIA RTX 2070 / AMD RX 6700 XT or equivalent
- **RAM**: 16GB or more
- **Storage**: SSD with 10GB+ available space

## Quick Start

### 1. Download and Extract

1. Download the latest release from the [releases page](../../releases)
2. Extract all files to a folder of your choice
3. Ensure the folder structure remains intact

### 2. First Run

1. Run `DesktopAvatar.exe` from the extracted folder
2. The application will start in a transparent window
3. You should see the default avatar (if available) or an empty scene

### 3. Load Your Avatar

#### Using OSC
Send this OSC message to load an avatar:
```
/avatar/load "C:/Path/To/Your/Avatar.vrm"
```

#### Using Files
1. Place your `.vrm` files in the `DesktopAvatar_Data/StreamingAssets/Avatars/` folder
2. Update the `config.json` file to point to your avatar
3. Restart the application

### 4. Control Your Avatar

The avatar can be controlled via OSC messages. Here are some basic commands:

```bash
# Load avatar
/avatar/load "StreamingAssets/Avatars/myavatar.vrm"

# Set position
/avatar/position 0 0 0

# Play animation
/avatar/animation/play "idle" 1 1.0

# Set expression
/avatar/expression/set "happy" 1.0

# Control window
/window/position 100 200
/window/opacity 0.8
```

## Configuration

### Basic Configuration

Edit `DesktopAvatar_Data/Config/config.json`:

```json
{
  "window": {
    "width": 800,
    "height": 1200,
    "transparent": true,
    "clickThrough": false,
    "alwaysOnTop": true,
    "position": {
      "x": 100,
      "y": 100
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

### Window Settings

- **transparent**: Makes the window background transparent
- **clickThrough**: Allows mouse clicks to pass through the window
- **alwaysOnTop**: Keeps the window above other applications
- **width/height**: Window dimensions in pixels
- **position**: Window position on screen

### Avatar Settings

- **defaultPath**: Path to the VRM file to load on startup
- **scale**: Uniform scale multiplier for the avatar
- **autoLoad**: Whether to load the default avatar on startup

### OSC Settings

- **enabled**: Enable/disable OSC control
- **port**: UDP port for OSC communication (default: 9000)
- **address**: IP address to listen on (default: 127.0.0.1)

## OSC Control

### OSC Basics

OSC (Open Sound Control) is a protocol for communication between multimedia applications. The desktop avatar listens for OSC messages on the configured port.

### Message Format

OSC messages have the format:
```
/address value1 value2 value3 ...
```

### Avatar Control Addresses

#### Loading & Management
- `/avatar/load [path]` - Load a VRM avatar from path
- `/avatar/unload` - Unload current avatar
- `/avatar/reset` - Reset avatar to default state
- `/avatar/visibility [0-1]` - Set avatar visibility

#### Transform
- `/avatar/position [x] [y] [z]` - Set world position
- `/avatar/rotation [x] [y] [z]` - Set rotation (Euler angles)
- `/avatar/scale [value]` - Set uniform scale
- `/avatar/lookat [x] [y] [z]` - Make avatar look at point

#### Animation
- `/avatar/animation/play [name] [loop] [speed]` - Play animation
- `/avatar/animation/stop [name]` - Stop specific animation
- `/avatar/animation/stop_all` - Stop all animations
- `/avatar/animation/crossfade [name] [duration]` - Smooth transition

#### Expressions
- `/avatar/expression/set [preset] [value]` - Set expression preset
- `/avatar/expression/blendshape [name] [value]` - Set blend shape
- `/avatar/expression/reset` - Reset all expressions
- `/avatar/expression/eyebrow [left] [right]` - Set eyebrow positions
- `/avatar/expression/eye [left] [right]` - Set eye openness
- `/avatar/expression/mouth [shape] [value]` - Control mouth shapes

### Window Control Addresses

#### Positioning
- `/window/position [x] [y]` - Set window position
- `/window/size [width] [height]` - Set window size
- `/window/move [dx] [dy]` - Move window relative
- `/window/center` - Center window on screen
- `/window/monitor [index]` - Move to specific monitor

#### Appearance
- `/window/opacity [0-1]` - Set window opacity
- `/window/clickthrough [0/1]` - Toggle click-through
- `/window/alwaysontop [0/1]` - Toggle always-on-top
- `/window/visibility [0/1]` - Show/hide window
- `/window/border [0/1]` - Toggle window border

#### State
- `/window/focus` - Bring window to front
- `/window/minimize` - Minimize window
- `/window/maximize` - Maximize window
- `/window/restore` - Restore window
- `/window/close` - Close application

### System Addresses

- `/system/status` - Get system status
- `/system/version` - Get version info
- `/system/restart` - Restart application
- `/system/exit` - Exit application

## Troubleshooting

### Common Issues

#### Avatar Not Loading
1. Check that the VRM file path is correct
2. Ensure the VRM file is not corrupted
3. Check the application log for error messages

#### Window Not Transparent
1. Ensure your graphics drivers are up to date
2. Check that transparency is enabled in config.json
3. Some applications may interfere with transparency

#### OSC Not Working
1. Verify the port (default 9000) is not in use
2. Check firewall settings
3. Ensure the OSC sender is configured correctly

#### Performance Issues
1. Lower the target FPS in config.json
2. Reduce avatar complexity (fewer polygons)
3. Close other applications
4. Update graphics drivers

### Log Files

The application creates log files in:
- `DesktopAvatar_Data/output_log.txt` - Unity log
- `logs/avatar_system.log` - Avatar system log
- `logs/osc_receiver.log` - OSC communication log

### Getting Help

If you encounter issues:
1. Check the log files for error messages
2. Verify your configuration files
3. Test with the default settings
4. Check the [troubleshooting guide](TROUBLESHOOTING.md)

## Next Steps

Now that you have the desktop avatar running, you can:

1. **Customize the appearance** by editing configuration files
2. **Add more avatars** by placing VRM files in the avatars folder
3. **Create custom animations** using Unity's animation system
4. **Develop plugins** to extend functionality
5. **Integrate with other applications** using OSC

For more advanced features, see the [user guide](GUIDE_ADVANCED.md) and [developer documentation](../ARCHITECTURE.md).
