# AvatarMCP Sampling Workflows Guide

## 🎭 Agentic Sampling Workflows with FastMCP 2.14.3

This guide covers AvatarMCP's revolutionary **agentic sampling workflows** - a feature that leverages FastMCP 2.14.3's SEP-1577 "sampling with tools" specification to enable LLMs to autonomously orchestrate complex avatar behaviors.

## What Are Sampling Workflows?

Traditional avatar control requires manual sequencing of individual tool calls:

```python
# Manual orchestration (10+ separate calls)
await play_animation({"avatar_id": "dancer", "animation": "step1"})
await set_morph({"avatar_id": "dancer", "emotion": "joy"})
await control_bone({"avatar_id": "dancer", "bone": "arm"})
await play_animation({"avatar_id": "dancer", "animation": "step2"})
```

**Sampling workflows** consolidate this into a single intelligent request:

```python
# Agentic orchestration (1 call)
await avatar_agentic_workflow({
    "workflow_prompt": "Perform a joyful dance with expressive gestures",
    "avatar_id": "dancer",
    "available_operations": ["play_animation", "set_morph", "control_bone"],
    "max_iterations": 5
})
```

## Quick Start

### 1. Load Your Avatar
```python
await avatar_manager({
    "operation": "load",
    "path": "models/my_avatar.vrm",
    "make_active": True
})
```

### 2. Execute a Simple Workflow
```python
await avatar_agentic_workflow({
    "workflow_prompt": "Express happiness with a smile and wave",
    "avatar_id": "my_avatar",
    "available_operations": ["set_morph", "play_animation"],
    "max_iterations": 3
})
```

### 3. Check Results
```python
{
    "success": true,
    "operations_executed": ["set_morph", "play_animation"],
    "execution_time_seconds": 1.2,
    "results": [...]
}
```

## Available Operations

The sampling system can orchestrate these avatar operations:

| Operation | Purpose | Example Use |
|-----------|---------|-------------|
| `load_avatar` | Load VRM models | Dynamic avatar switching |
| `play_animation` | Trigger animations | Movement and gestures |
| `set_morph` | Control facial expressions | Emotional displays |
| `control_bone` | Manipulate bone positions | Precise posing |
| `send_osc` | Send OSC to VRChat | External system integration |
| `set_emotion` | Set emotional states | Mood and personality |
| `create_sequence` | Build animation sequences | Complex choreography |
| `blend_animations` | Layer multiple animations | Rich performances |
| `get_status` | Check avatar state | Conditional logic |
| `wait` | Add timing delays | Precise choreography |

## Workflow Categories

### 🎭 Emotional Performances
```python
await avatar_agentic_workflow({
    "workflow_prompt": "Show surprise followed by joy, ending with satisfaction",
    "avatar_id": "actor",
    "available_operations": ["set_emotion", "set_morph", "play_animation"],
    "max_iterations": 4,
    "context": {"emotional_arc": ["surprise", "joy", "satisfaction"]}
})
```

### 💃 Dance & Movement
```python
await avatar_agentic_workflow({
    "workflow_prompt": "Perform a 15-second energetic dance with arm flourishes",
    "avatar_id": "dancer",
    "available_operations": ["play_animation", "control_bone", "blend_animations", "wait"],
    "max_iterations": 8,
    "context": {"duration": 15, "style": "energetic"}
})
```

### 🎪 Interactive Storytelling
```python
await avatar_agentic_workflow({
    "workflow_prompt": "React dramatically to shocking news with gestures and expressions",
    "avatar_id": "character",
    "available_operations": ["set_emotion", "control_bone", "play_animation", "send_osc"],
    "max_iterations": 6,
    "context": {"reaction_type": "shock", "intensity": "high"}
})
```

### 🤝 Social Interactions
```python
await avatar_agentic_workflow({
    "workflow_prompt": "Greet someone warmly with a bow and friendly expression",
    "avatar_id": "companion",
    "available_operations": ["play_animation", "set_morph", "control_bone"],
    "max_iterations": 3,
    "context": {"social_context": "greeting", "formality": "warm"}
})
```

## Advanced Configuration

### Context Dictionary
Enhance workflows with environmental and behavioral context:

```python
"context": {
    "duration": 30,           // Time limit in seconds
    "style": "dramatic",      // Performance style
    "intensity": "high",      // Expression intensity
    "emotional_arc": [...],   // Mood progression
    "social_context": "...",  // Interaction type
    "environment": "crowd"    // Setting awareness
}
```

### Operation Selection Strategy

**Start Simple (2-4 operations):**
- Basic emotional responses
- Simple gestures
- Single animations

**Build Complexity (5-10 operations):**
- Multi-step sequences
- Emotional transitions
- Layered animations

**Advanced Orchestration (10-20 operations):**
- Complex choreography
- Interactive storytelling
- Multi-modal performances

## Best Practices

### 🎯 Prompt Engineering

**Be Specific:**
- ✅ "Express joy with a big smile and celebratory arm wave"
- ❌ "Be happy"

**Include Timing:**
- ✅ "Perform a 20-second dance routine"
- ❌ "Dance"

**Specify Style:**
- ✅ "React with subtle surprise and quiet contemplation"
- ❌ "Be surprised"

### ⚙️ Technical Optimization

**Iteration Limits:**
- Simple workflows: 3-5 iterations
- Complex performances: 10-15 iterations
- Maximum safe: 20 iterations

**Operation Balance:**
- Choose operations that match your goal
- Avoid redundant operations
- Consider performance impact

**Error Handling:**
- Monitor `results` array for failures
- Use `strict_mode: false` for experimental workflows
- Refine prompts based on execution feedback

### 🎨 Creative Applications

**Theater & Performance:**
- Dramatic monologues with emotional arcs
- Character reactions to plot developments
- Physical comedy routines

**Gaming & Interactive:**
- Dynamic NPC behaviors
- Quest reaction sequences
- Environmental responses

**Education & Training:**
- Demonstrative teaching assistants
- Emotional expression examples
- Interactive learning scenarios

**Therapeutic & Assistive:**
- Emotional communication aids
- Social skill demonstrations
- Expressive therapy tools

## Troubleshooting

### Common Issues

**Workflow Too Fast/Slow:**
- Adjust `context.duration`
- Use `wait` operations for timing
- Modify `max_iterations`

**Operations Not Executing:**
- Check `available_operations` list
- Verify avatar is loaded
- Review `results` array for errors

**Inconsistent Results:**
- Refine workflow prompts
- Add more context parameters
- Try different operation combinations

**Performance Issues:**
- Reduce `max_iterations`
- Limit operation complexity
- Use targeted operation sets

### Debug Information

Every workflow returns detailed execution data:

```python
{
    "success": true,                    // Overall success
    "operations_executed": [...],       // What ran
    "total_iterations": 5,              // Iterations used
    "execution_time_seconds": 2.1,      // Performance timing
    "results": [                        // Detailed per-operation results
        {
            "operation": "set_morph",
            "success": true,
            "result": {"emotion": "happy"}
        },
        // ... more results
    ]
}
```

## Performance Monitoring

Track these metrics for optimization:

- **Execution Time**: Should be < 5 seconds for most workflows
- **Success Rate**: > 80% operations should succeed
- **Iteration Efficiency**: Most workflows complete in < max_iterations

## Examples Library

### Emotional Expressions
```python
# Happiness
{"workflow_prompt": "Radiate pure joy with beaming smile and open gestures"}

# Sadness
{"workflow_prompt": "Express quiet sadness with downcast eyes and gentle gestures"}

# Anger
{"workflow_prompt": "Show controlled anger with furrowed brow and tense posture"}

# Surprise
{"workflow_prompt": "React with wide-eyed shock and raised hands"}
```

### Social Gestures
```python
# Greeting
{"workflow_prompt": "Give a warm, friendly greeting with smile and welcoming gesture"}

# Farewell
{"workflow_prompt": "Bid a fond farewell with warm expression and gentle wave"}

# Thanks
{"workflow_prompt": "Express sincere gratitude with smile and appreciative nod"}
```

### Performance Routines
```python
# Victory Celebration
{"workflow_prompt": "Celebrate victory with triumphant pose and joyful expression"}

# Thinking/Contemplation
{"workflow_prompt": "Show deep thought with furrowed brow and thoughtful gestures"}

# Agreement/Approval
{"workflow_prompt": "Show strong agreement with enthusiastic nod and affirming gestures"}
```

## Integration with Other Tools

Sampling workflows work seamlessly with existing AvatarMCP tools:

```python
# 1. Load avatar with traditional tool
await avatar_manager({"operation": "load", "path": "hero.vrm"})

# 2. Execute sampling workflow
await avatar_agentic_workflow({
    "workflow_prompt": "Perform a heroic entrance",
    "avatar_id": "hero",
    "available_operations": ["play_animation", "set_emotion", "control_bone"]
})

# 3. Continue with traditional tools
await osc_communicator({"operation": "send", "address": "/hero/lighting", "value": 1.0})
```

This hybrid approach gives you the best of both worlds: the intelligence of sampling workflows combined with the precision of traditional tool calls.
