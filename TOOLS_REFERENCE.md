# AvatarMCP Tools Reference

This document provides a reference for the avatar control tools available in the AvatarMCP system.

## Table of Contents
- [Animation Control Tool](#animation-control-tool)
- [Avatar Control Tool](#avatar-control-tool)
- [Avatar Sampling Tool](#avatar-sampling-tool)
- [System Info Tool](#system-info-tool)

## Animation Control Tool

Controls avatar animations and movements.

### Endpoints
- `POST /api/animations/play` - Play an animation
  - Parameters:
    - `animation_name` (string): Name of the animation to play (e.g., "idle", "talking", "listening")
    - `loop` (boolean, optional): Whether to loop the animation (default: false)
    - `speed` (float, optional): Playback speed multiplier (default: 1.0)

- `POST /api/animations/stop` - Stop current animation
  - Parameters: None

## Avatar Control Tool

Manages avatar properties and states.

### Endpoints
- `POST /api/avatars/load` - Load a VRM avatar
  - Parameters:
    - `path` (string): Path to the VRM file (relative to the models directory)
    - `scale` (float, optional): Initial scale of the avatar (default: 1.0)
    - `position` (object, optional): Initial position {x, y, z} (default: {0, 0, 0})

- `GET /api/avatars` - List available avatars
  - Returns: Array of available avatar configurations

- `POST /api/avatars/unload` - Unload current avatar
  - Parameters: None

## Avatar Sampling Tool

Implements FastMCP 2.14.3 sampling capabilities for agentic avatar workflows. Enables LLMs to autonomously orchestrate complex avatar operations without client round-trips.

### Tool Name
`avatar_agentic_workflow`

### Parameters
- `workflow_prompt` (string, required): Natural language description of desired workflow
  - Examples: "Create a joyful dance routine", "Express happiness with gestures", "Perform dramatic entrance"
- `avatar_id` (string, required): Target avatar identifier (must be loaded)
- `available_operations` (array, optional): List of allowed operations
  - Default: All operations
  - Options: `load_avatar`, `play_animation`, `set_morph`, `control_bone`, `send_osc`, `set_emotion`, `create_sequence`, `blend_animations`, `get_status`, `wait`
- `max_iterations` (integer, optional): Maximum tool calls (default: 5, max: 20)
- `context` (object, optional): Additional workflow context
- `strict_mode` (boolean, optional): Enforce operation validation (default: true)

### Response Format
```json
{
  "success": true,
  "workflow_prompt": "Create a joyful dance routine",
  "avatar_id": "dancer_bot",
  "operations_executed": ["set_emotion", "play_animation", "control_bone"],
  "results": [...],
  "total_iterations": 3,
  "execution_time_seconds": 2.45
}
```

### Workflow Examples

#### Basic Emotional Response
```javascript
{
  "workflow_prompt": "Show happiness with a smile and friendly wave",
  "avatar_id": "companion_bot",
  "available_operations": ["set_morph", "play_animation", "control_bone"],
  "max_iterations": 3
}
```

#### Advanced Dance Choreography
```javascript
{
  "workflow_prompt": "Perform a 30-second joyful dance with smooth emotional transitions",
  "avatar_id": "dancer",
  "available_operations": ["play_animation", "set_emotion", "blend_animations", "wait"],
  "max_iterations": 10,
  "context": {
    "duration": 30,
    "style": "joyful",
    "intensity": "high"
  }
}
```

#### Interactive Conversation Response
```javascript
{
  "workflow_prompt": "React to surprising good news with genuine excitement and gestures",
  "avatar_id": "listener",
  "available_operations": ["set_emotion", "control_bone", "send_osc", "play_animation"],
  "max_iterations": 5,
  "context": {
    "reaction_type": "surprise",
    "intensity": "medium"
  }
}
```

#### Storytelling Performance
```javascript
{
  "workflow_prompt": "Tell a dramatic story with changing emotions and gestures",
  "avatar_id": "storyteller",
  "available_operations": ["set_emotion", "control_bone", "play_animation", "wait", "send_osc"],
  "max_iterations": 15,
  "context": {
    "narrative_arc": ["calm", "excited", "dramatic", "resolution"],
    "timing": "dramatic"
  }
}
```

### Usage Tips & Best Practices

#### 🎯 **Prompt Engineering**
- **Be Specific**: "Express joy with a smile and wave" works better than "be happy"
- **Include Timing**: Mention duration for complex sequences ("30-second dance")
- **Specify Style**: "joyful", "dramatic", "subtle", "exaggerated"
- **Context Matters**: Include environmental factors ("in a crowd", "during conversation")

#### ⚙️ **Operation Selection**
- **Start Minimal**: Use 2-4 operations for simple workflows
- **Layer Complexity**: Add operations incrementally for complex behaviors
- **Match Intent**: Choose operations that align with your workflow goal
- **Performance Balance**: More operations = richer behavior but slower execution

#### 🔧 **Configuration Optimization**
- **Iteration Limits**: 3-5 for simple, 10-15 for complex workflows
- **Context Dictionary**: Use for timing, style, and environmental parameters
- **Strict Mode**: Enable for production, disable for experimental workflows
- **Error Handling**: Monitor results array for failed operations

#### 🎭 **Creative Applications**
- **Theater**: Dramatic performances with emotional arcs
- **Gaming**: Dynamic NPC behaviors and reactions
- **Education**: Expressive teaching assistants and demonstrators
- **Entertainment**: Interactive characters and virtual performers
- **Therapy**: Emotional expression and communication aids

#### 🚀 **Advanced Techniques**
- **Multi-Modal**: Combine animations, morphs, and OSC for rich expressions
- **Layered Timing**: Use `wait` operations for precise choreography
- **Conditional Logic**: LLM can make decisions based on context
- **Iterative Refinement**: Start simple, then add complexity
- **Context Awareness**: Include scene information for appropriate responses

#### 🔍 **Debugging & Monitoring**
- **Check Results**: Review the `results` array for operation success/failure
- **Timing Analysis**: Monitor `execution_time_seconds` for performance
- **Iteration Count**: Verify workflows complete within expected bounds
- **Error Messages**: Use failure information to refine prompts and operations

## System Info Tool

Provides system and avatar status information.

### Endpoints
- `GET /api/system/status` - Get system and avatar status
  - Returns: Status information including loaded avatar and animation state

- `GET /api/system/animations` - List available animations
  - Returns: Array of available animation names and their properties

## Error Handling

All endpoints return JSON responses with the following structure:
```json
{
  "status": "success|error",
  "data": {},
  "error": "Error message if status is error"
}
```

## Examples

### Loading an Avatar
```bash
curl -X POST http://localhost:7100/api/avatars/load \
  -H "Content-Type: application/json" \
  -d '{"path": "my-avatar.vrm", "scale": 1.0, "position": {"x": 0, "y": 0, "z": 0}}'
```

### Playing an Animation
```bash
# Play a wave animation once
curl -X POST http://localhost:7100/api/animations/play \
  -H "Content-Type: application/json" \
  -d '{"animation_name": "wave", "loop": false, "speed": 1.0}'

# Start idle animation loop
curl -X POST http://localhost:7100/api/animations/play \
  -H "Content-Type: application/json" \
  -d '{"animation_name": "idle", "loop": true}'

# Stop current animation
curl -X POST http://localhost:7100/api/animations/stop
```

### Getting System Status
```bash
curl http://localhost:7100/api/system/status
```
