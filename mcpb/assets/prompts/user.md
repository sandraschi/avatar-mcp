# Avatar MCP User Guide

## Getting Started

1. **Load an Avatar**: Use `avatar_manager` tool to load VRM models
2. **Create Sampling Workflows**: Use natural language to orchestrate complex behaviors
3. **Animation Control**: Use `animation_controller` for precise animation management
4. **OSC Control**: Configure OSC settings with `osc_communicator` tool
5. **Unity Integration**: Connect to Unity desktop applications

## Revolutionary Sampling Workflows

AvatarMCP introduces **agentic sampling workflows** - a breakthrough feature using FastMCP 2.14.3's SEP-1577 specification that allows LLMs to autonomously orchestrate complex avatar behaviors.

### Quick Sampling Examples

```javascript
// Emotional response
await avatar_sampling({
  "workflow_prompt": "Show genuine happiness with a warm smile and friendly wave",
  "avatar_id": "companion",
  "available_operations": ["set_morph", "play_animation", "control_bone"],
  "max_iterations": 3
})

// Complex dance performance
await avatar_sampling({
  "workflow_prompt": "Perform a 20-second celebratory dance with emotional peaks",
  "avatar_id": "performer",
  "available_operations": ["play_animation", "set_emotion", "blend_animations", "wait"],
  "max_iterations": 8,
  "context": {"duration": 20, "style": "joyful"}
})

// Interactive storytelling
await avatar_sampling({
  "workflow_prompt": "React dramatically to surprising news with wide eyes and expressive gestures",
  "avatar_id": "character",
  "available_operations": ["set_emotion", "control_bone", "play_animation"],
  "max_iterations": 5,
  "context": {"reaction_type": "shock", "intensity": "high"}
})
```

## Portmanteau Tool Workflows

### Basic Avatar Control (Portmanteau Tools)
```javascript
1. Load avatar: await avatar_manager({"operation": "load", "path": "model.vrm", "make_active": true})
2. Get metadata: await avatar_manager({"operation": "get_metadata", "avatar_id": "loaded_avatar"})
3. Play animation: await animation_controller({"operation": "play", "name": "walk_cycle", "speed": 1.2})
4. Adjust parameters: await parameter_manager({"operation": "set", "parameter": "expression_intensity", "value": 0.8})
```

### OSC Communication (Portmanteau Tools)
```javascript
1. Configure OSC: await osc_communicator({"operation": "configure", "enabled": true, "port": 9000})
2. Send messages: await osc_communicator({"operation": "send", "address": "/avatar/eyeBlink", "value": 1.0})
3. Receive data: await osc_communicator({"operation": "receive"})
4. Monitor status: await osc_communicator({"operation": "get_status"})
```

### Unity Desktop Integration (Portmanteau Tools)
```javascript
1. Load Unity avatar: await unity_integration({"operation": "load_avatar", "path": "model.vrm"})
2. Control window: await unity_window_manager({"operation": "set_position", "x": 100, "y": 100, "width": 400, "height": 600})
3. Set transparency: await unity_window_manager({"operation": "set_transparency", "level": 0.8})
4. Configure bridge: await unity_config_manager({"operation": "enable_osc_bridge"})
```

## Troubleshooting

### Avatar and Animation Issues
- **Avatar not loading**: Check VRM file format and path, use `avatar_manager({"operation": "load", ...})`
- **OSC not working**: Verify port configurations and network settings with `osc_communicator`
- **Unity connection failed**: Ensure Unity application is running and accessible
- **Animation issues**: Check animation file compatibility and timing settings with `animation_controller`

### Sampling Workflow Issues
- **Sampling not working**: Ensure FastMCP 2.14.3+ is installed and avatar is loaded
- **Workflow too complex**: Reduce `max_iterations` or simplify `workflow_prompt`
- **Avatar not responding**: Check avatar_id is correct and avatar is active
- **Performance issues**: Limit available_operations to essential ones only

### Portmanteau Tool Issues
- **Tool not found**: Use consolidated portmanteau tools instead of individual functions
- **Parameter errors**: Check operation names and required parameters for each tool
- **Configuration issues**: Use `config_manager` for settings and `system_monitor` for diagnostics



