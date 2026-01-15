# 🎭 AvatarMCP Sampling Workflows Guide (MCPB Edition)

## Agentic Sampling Workflows with FastMCP 2.14.3

This guide covers AvatarMCP's revolutionary **agentic sampling workflows** - a feature that leverages FastMCP 2.14.3's SEP-1577 "sampling with tools" specification to enable LLMs to autonomously orchestrate complex avatar behaviors.

---

## What Are Sampling Workflows?

Traditional avatar control requires manual sequencing of individual tool calls:

```javascript
// Manual orchestration (10+ separate calls)
await animation_controller({"operation": "play", "name": "step1"})
await parameter_manager({"operation": "set", "parameter": "emotion", "value": "joy"})
await bone_control({"bone_name": "arm", "transform": {"rotation": {"x": 0.5}}})
await animation_controller({"operation": "play", "name": "step2"})
```

**Sampling workflows** consolidate this into a single intelligent request:

```javascript
// Agentic orchestration - AI handles everything
await avatar_sampling({
  "workflow_prompt": "Express genuine happiness with a warm smile and celebratory gesture",
  "avatar_id": "companion",
  "available_operations": ["set_morph", "play_animation", "control_bone"],
  "max_iterations": 3
})
```

---

## Core Sampling Capabilities

### 1. **Natural Language Orchestration**
Describe desired behavior in plain English:
- "Express genuine happiness with a warm smile and friendly wave"
- "Perform a joyful 15-second dance with smooth emotional transitions"
- "React dramatically to shocking news with wide eyes and expressive gestures"

### 2. **Intelligent Sequencing**
AI automatically determines optimal operation order and timing based on:
- Emotional context and flow
- Physical constraints and avatar capabilities
- Performance timing and pacing
- Available operation combinations

### 3. **Contextual Understanding**
Sampling workflows understand:
- **Emotional intelligence**: Appropriate facial expressions and body language
- **Timing**: Natural pauses, transitions, and pacing
- **Style**: Different performance styles (dramatic, joyful, subtle, etc.)
- **Constraints**: Avatar limitations and available operations

---

## Available Sampling Operations

The `avatar_sampling` tool supports 10 core avatar operations:

### Animation & Movement
- `load_avatar`: Load and prepare avatar models
- `play_animation`: Execute canned animations
- `control_bone`: Direct skeletal manipulation
- `blend_animations`: Layer multiple animations

### Emotional Expression
- `set_morph`: Facial expressions via blend shapes
- `set_emotion`: Emotional state management

### Communication
- `send_osc`: OSC message transmission
- `get_status`: Avatar state monitoring

### Timing & Control
- `wait`: Controlled pauses and timing

---

## Sampling Workflow Examples

### Basic Emotional Response

```javascript
await avatar_sampling({
  "workflow_prompt": "Show genuine happiness with a warm smile and friendly wave",
  "avatar_id": "companion",
  "available_operations": ["set_morph", "play_animation", "control_bone"],
  "max_iterations": 3
})
```

**AI Orchestration:**
1. Sets facial morphs for warm smile
2. Initiates friendly wave animation
3. Adjusts timing for natural expression

### Complex Dance Performance

```javascript
await avatar_sampling({
  "workflow_prompt": "Perform a 20-second celebratory dance with emotional peaks",
  "avatar_id": "performer",
  "available_operations": ["play_animation", "set_emotion", "blend_animations", "wait"],
  "max_iterations": 8,
  "context": {
    "duration": 20,
    "style": "joyful",
    "emotional_arc": "building_excitement"
  }
})
```

**AI Choreography:**
1. Starts with subtle joyful expressions
2. Builds to energetic dance moves
3. Peaks with maximum celebration
4. Gradually winds down with satisfaction

### Interactive Storytelling

```javascript
await avatar_sampling({
  "workflow_prompt": "React dramatically to surprising shocking news with wide eyes and expressive gestures",
  "avatar_id": "character",
  "available_operations": ["set_emotion", "control_bone", "play_animation"],
  "max_iterations": 5,
  "context": {
    "reaction_type": "shock",
    "intensity": "high",
    "duration": 8
  }
})
```

**AI Direction:**
1. Widens eyes with morph targets
2. Freezes momentarily in surprise
3. Adds dramatic hand gestures
4. Transitions to processing expression

### Personality-Driven Performance

```javascript
await avatar_sampling({
  "workflow_prompt": "Respond to a compliment with shy embarrassment and genuine appreciation",
  "avatar_id": "timid_character",
  "available_operations": ["set_morph", "play_animation", "control_bone"],
  "max_iterations": 4,
  "context": {
    "personality": "shy",
    "emotional_blend": "embarrassment_with_appreciation"
  }
})
```

---

## Advanced Sampling Techniques

### Emotional Arcs
Create performances with emotional progression:

```javascript
await avatar_sampling({
  "workflow_prompt": "Start curious, become excited, then show satisfaction",
  "avatar_id": "learner",
  "available_operations": ["set_emotion", "play_animation"],
  "max_iterations": 6,
  "context": {
    "emotional_progression": ["curious", "excited", "satisfied"],
    "transitions": "smooth"
  }
})
```

### Layered Behaviors
Combine multiple animation layers:

```javascript
await avatar_sampling({
  "workflow_prompt": "Walk confidently while maintaining eye contact and smiling",
  "avatar_id": "confident_walker",
  "available_operations": ["blend_animations", "control_bone", "set_morph"],
  "max_iterations": 5,
  "context": {
    "primary_action": "walking",
    "secondary_expressions": ["eye_contact", "smile"],
    "blend_mode": "additive"
  }
})
```

### Interactive Responses
Adapt to real-time input:

```javascript
await avatar_sampling({
  "workflow_prompt": "Respond to user applause with increasing enthusiasm",
  "avatar_id": "performer",
  "available_operations": ["play_animation", "set_emotion", "control_bone"],
  "max_iterations": 4,
  "context": {
    "reactive_to": "applause",
    "escalation": "increasing_enthusiasm",
    "feedback_loops": true
  }
})
```

---

## Sampling Workflow Prompts

AvatarMCP includes specialized prompts for different workflow types:

### Emotional Performance Prompt
```javascript
await sampling_workflow({
  "workflow_type": "emotional",
  "complexity": "moderate",
  "duration": 10,
  "emotional_focus": "joy"
})
```

### Dance Choreography Prompt
```javascript
await dance_choreography({
  "dance_style": "energetic",
  "duration": 20,
  "emotional_arc": "building_excitement"
})
```

### Interactive Storytelling Prompt
```javascript
await emotional_performance({
  "emotion": "surprise",
  "intensity": "high",
  "duration": 8,
  "reaction_type": "shock"
})
```

---

## Best Practices

### Workflow Design
1. **Clear Intent**: Be specific about desired behavior and emotional context
2. **Appropriate Scope**: Limit `max_iterations` to essential steps
3. **Available Operations**: Include only operations needed for the workflow
4. **Context Rich**: Provide timing, style, and emotional guidance

### Performance Optimization
1. **Selective Operations**: Don't include unnecessary operations
2. **Reasonable Iterations**: Start with 3-5 iterations, increase as needed
3. **Context Constraints**: Use duration and style parameters to guide AI
4. **Avatar Compatibility**: Ensure avatar supports required operations

### Debugging Workflows
1. **Start Simple**: Test basic emotional responses first
2. **Gradual Complexity**: Build up to complex multi-step performances
3. **Monitor Results**: Check avatar state after workflows
4. **Adjust Context**: Fine-tune timing and style parameters

---

## Integration with Portmanteau Tools

Sampling workflows integrate seamlessly with AvatarMCP's portmanteau tools:

```javascript
// Setup with portmanteau tools
await avatar_manager({"operation": "load", "path": "character.vrm", "make_active": true})
await config_manager({"operation": "set", "setting": "emotion_intensity", "value": 0.8})

// Execute sampling workflow
await avatar_sampling({
  "workflow_prompt": "Greet warmly and invite to dance",
  "avatar_id": "character",
  "available_operations": ["set_morph", "play_animation", "control_bone"],
  "max_iterations": 4
})

// Monitor with system tools
await system_monitor({"operation": "get_performance"})
```

---

## Troubleshooting

### Common Issues

**Workflow Too Complex:**
- Reduce `max_iterations`
- Simplify `workflow_prompt`
- Limit `available_operations`

**Avatar Not Responding:**
- Verify avatar is loaded with `avatar_manager`
- Check avatar_id is correct
- Ensure operations are supported by avatar

**Timing Issues:**
- Add explicit `context.duration`
- Use `wait` in `available_operations`
- Adjust `max_iterations` for better pacing

**Emotional Expression Problems:**
- Include `set_morph` and `set_emotion` in operations
- Add `context.emotional_context`
- Check morph target compatibility

### Performance Monitoring

```javascript
// Monitor sampling performance
await system_monitor({"operation": "get_performance"})
await system_monitor({"operation": "get_memory_usage"})
await avatar_manager({"operation": "get_status", "avatar_id": "performer"})
```

---

## Future Capabilities

AvatarMCP sampling workflows will expand to include:

- **Multi-avatar Coordination**: Synchronized performances across multiple avatars
- **Environmental Awareness**: Reactions to virtual environment changes
- **User Interaction**: Real-time adaptation to user behavior
- **Personality Integration**: Consistent character behavior across workflows
- **Advanced Choreography**: Complex multi-step performances with branching logic

---

*This guide is part of AvatarMCP v1.1.0 with FastMCP 2.14.3 sampling capabilities.*