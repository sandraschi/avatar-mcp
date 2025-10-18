# Resonite Integration Setup Guide

## Overview

This guide provides step-by-step instructions for integrating Resonite with AvatarMCP for advanced avatar control and social VR experiences.

## Prerequisites

### Software Requirements
- **Resonite**: Latest version from [resonite.com](https://resonite.com)
- **AvatarMCP**: Running MCP server
- **Python 3.8+**: For MCP server
- **OSC Support**: Enabled in Resonite settings

### System Requirements
- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Dedicated GPU recommended for complex avatars
- **Network**: Stable internet connection for cloud features

## Step 1: Install and Configure Resonite

### 1.1 Download and Install
1. Visit [resonite.com](https://resonite.com)
2. Download the appropriate version for your platform
3. Install and run Resonite
4. Create or log into your account

### 1.2 Configure OSC Settings
1. Open Resonite
2. Go to **Settings** → **Network** → **OSC**
3. Enable OSC: ✅ **Enabled**
4. Set **Port**: `9000`
5. Set **Address**: `127.0.0.1` (localhost)
6. **Save settings**

### 1.3 Test OSC Connection
1. In Resonite, create a new empty world
2. Add an **OSC Receiver** component to any object
3. Set the receiver to listen on port 9000
4. Use external OSC tools to test connectivity

## Step 2: Set Up AvatarMCP Server

### 2.1 Install Dependencies
```bash
cd /path/to/avatarmcp
pip install -r requirements.txt
```

### 2.2 Configure Claude Desktop
Update your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "avatarmcp": {
      "command": "python",
      "args": ["-m", "avatarmcp.mcp_main"],
      "cwd": "D:/Dev/repos/avatarmcp/src",
      "env": {
        "PYTHONPATH": "D:/Dev/repos/avatarmcp/src"
      }
    }
  }
}
```

### 2.3 Start the MCP Server
```bash
# Navigate to project directory
cd D:/Dev/repos/avatarmcp

# Start MCP server
python -m avatarmcp.mcp_main
```

## Step 3: Create Avatar Control Worlds

### 3.1 Download Pre-built Worlds
Download pre-configured worlds from the AvatarMCP repository:
- `AvatarMCP-Studio.resonite` - Basic avatar control studio
- `AvatarMCP-Stage.resonite` - Performance stage
- `AvatarMCP-Collaborative.resonite` - Multi-user collaboration space

### 3.2 Manual World Creation
If creating worlds manually:

1. **Create New World**
   - Open Resonite
   - Create → New World → Empty

2. **Add OSC Infrastructure**
   - Add **OSC Receiver** component to root object
   - Configure for port 9000
   - Add ProtoFlux scripts for avatar control

3. **Set Up Avatar Slots**
   - Create 8 avatar anchor points
   - Add avatar loading/unloading logic
   - Configure OSC addresses for each slot

4. **Add Control Interfaces**
   - UI panels for avatar selection
   - Control surfaces for manipulation
   - Status displays for feedback

## Step 4: Test Integration

### 4.1 Basic Connection Test
In Claude, use:
```
resonite_session_start
```

Expected response:
```json
{
  "status": "success",
  "session_id": "resonite_20241213_143000",
  "osc_connected": true,
  "capabilities": ["avatar_control", "world_management", "real_time_sync"]
}
```

### 4.2 Load a World
```
resonite_world_load {"world_path": "resonite://AvatarMCP-Studio"}
```

### 4.3 Load an Avatar
```
avatar_load D:/Dev/repos/avatarmcp/models/Nekomimi-chan.vrm
```

### 4.4 Test Avatar Control
```
bone_control {"bone_name": "Head", "rotation": {"x": 0.1, "y": 0.0, "z": 0.0, "w": 0.995}}
```

### 4.5 Test Animation
```
animation_play idle
```

## Step 5: Advanced Features

### 5.1 Multi-User Collaboration
1. Invite friends to your Resonite world
2. Each user can control different avatar aspects
3. Real-time synchronization of all changes

### 5.2 Performance Recording
```bash
# Start recording
resonite_performance_record {"recording_name": "my_performance", "duration_seconds": 60}

# Control avatars during recording
bone_control {"bone_name": "LeftArm", "rotation": {"x": 0.3, "y": 0, "z": 0, "w": 0.95}}
animation_play dance

# Recording saves automatically
```

### 5.3 ProtoFlux Integration
Create custom ProtoFlux scripts for:
- Automated avatar behaviors
- Environmental interactions
- Complex animation sequences
- User interface controls

## Step 6: Optimization and Troubleshooting

### 6.1 Performance Optimization
- **Avatar Complexity**: Use lower polygon counts for better performance
- **Sync Settings**: Adjust sync interval based on network conditions
- **World Size**: Keep worlds reasonably sized for stability
- **OSC Traffic**: Monitor and optimize OSC message frequency

### 6.2 Common Issues

#### OSC Connection Failed
```
Error: Failed to initialize OSC client
```
**Solutions:**
- Verify Resonite OSC settings
- Check port 9000 is not blocked by firewall
- Ensure Resonite is running
- Try different port if 9000 is in use

#### Avatar Not Loading
```
Error: VRM file not found
```
**Solutions:**
- Verify file path is correct
- Ensure VRM file is not corrupted
- Check file permissions
- Try absolute paths instead of relative

#### World Load Failed
```
Error: Invalid world path format
```
**Solutions:**
- Use correct format: `resonite://WorldName`
- Verify world exists and is accessible
- Check Resonite permissions
- Try creating a new world first

#### Sync Issues
```
Warning: High latency detected
```
**Solutions:**
- Check network connection stability
- Reduce sync frequency if needed
- Close bandwidth-intensive applications
- Consider local network setup

### 6.3 Debug Mode
Enable debug logging:
```json
{
  "resonite": {
    "debug": {
      "log_osc_messages": true,
      "show_sync_metrics": true,
      "enable_profiling": true
    }
  }
}
```

## Step 7: Production Deployment

### 7.1 Headless Server Setup
For 24/7 operation:
1. Set up dedicated server hardware
2. Configure Resonite headless mode
3. Use `resonite_session_start` with headless option
4. Monitor performance and stability

### 7.2 Multi-World Management
- Create separate worlds for different purposes
- Use consistent naming conventions
- Implement world switching logic
- Backup important worlds regularly

### 7.3 User Management
- Set up user permissions appropriately
- Create moderator roles for large events
- Implement content guidelines
- Monitor for abuse and safety issues

## OSC Message Reference

### Avatar Control
- `/avatar/load [path]` - Load VRM avatar
- `/avatar/bone/[name]/rotation [x,y,z,w]` - Set bone rotation
- `/avatar/bone/[name]/translation [x,y,z]` - Set bone position
- `/avatar/expression/blendshape [name] [weight]` - Set blend shape
- `/avatar/animation/play [name] [loop] [speed]` - Play animation

### World Control
- `/world/load [path]` - Load world
- `/world/reset` - Reset world state
- `/world/save [name]` - Save world

### Session Management
- `/session/start` - Start AvatarMCP session
- `/session/status` - Get session status
- `/session/end` - End session

## Best Practices

### Performance
- Keep avatar polygon count under 50K triangles
- Use texture atlasing for better performance
- Implement LOD (Level of Detail) systems
- Monitor frame rate and optimize accordingly

### Networking
- Use wired connections for best stability
- Keep OSC message frequency reasonable (< 100Hz)
- Implement error handling for network issues
- Use compression for large data transfers

### Content Creation
- Follow Resonite community guidelines
- Test content thoroughly before public release
- Provide clear documentation for custom worlds
- Consider accessibility in world design

### Security
- Be cautious with external OSC connections
- Validate all input data
- Use appropriate permission systems
- Monitor for unusual activity

## Getting Help

### Resources
- **Resonite Wiki**: [wiki.resonite.com](https://wiki.resonite.com)
- **Resonite Discord**: Community support
- **AvatarMCP Docs**: Local documentation
- **GitHub Issues**: Report bugs and request features

### Support Channels
1. **AvatarMCP Issues**: GitHub repository
2. **Resonite Support**: Official channels
3. **Community Forums**: VRChat and Resonite communities
4. **Discord Servers**: Various VR communities

## Next Steps

With Resonite integration complete, you can now:

1. **Create Amazing Experiences**: Build interactive avatar performances
2. **Collaborate in Real-time**: Work with others on avatar animations
3. **Record Performances**: Capture and share avatar shows
4. **Extend Functionality**: Create custom ProtoFlux scripts
5. **Scale Up**: Deploy headless servers for 24/7 operation

**Welcome to the future of avatar control!** 🎭✨

---

*This guide is maintained alongside AvatarMCP development. Check for updates regularly.*


