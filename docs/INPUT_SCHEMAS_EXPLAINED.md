# MCPB Input Schemas - What They Were Supposed To Be

The `inputSchema` fields were **detailed JSON Schema definitions** that specified exactly what parameters each MCP tool expected, their types, validation rules, and documentation. Here are some examples:

## Example 1: `avatar_load` Tool

```json
{
  "name": "avatar_load",
  "description": "Load a VRM avatar model",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to VRM file or model ID"
      },
      "make_active": {
        "type": "boolean",
        "description": "Set as active avatar",
        "default": true
      },
      "metadata": {
        "type": "object",
        "description": "Additional metadata for the avatar"
      }
    },
    "required": ["path"]
  }
}
```

## Example 2: `unity_window_position` Tool

```json
{
  "name": "unity_window_position",
  "description": "Control Unity desktop avatar window position and size",
  "inputSchema": {
    "type": "object",
    "properties": {
      "x": {
        "type": "integer",
        "description": "X-coordinate for window position"
      },
      "y": {
        "type": "integer",
        "description": "Y-coordinate for window position"
      },
      "width": {
        "type": "integer",
        "description": "Window width in pixels"
      },
      "height": {
        "type": "integer",
        "description": "Window height in pixels"
      },
      "monitor": {
        "type": "integer",
        "description": "Target monitor index",
        "default": 0
      },
      "center_on_monitor": {
        "type": "boolean",
        "description": "Center window on specified monitor",
        "default": false
      }
    }
  }
}
```

## Example 3: `unity_avatar_expression` Tool

```json
{
  "name": "unity_avatar_expression",
  "description": "Control facial expressions on Unity desktop avatar",
  "inputSchema": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "Name of the facial expression"
      },
      "strength": {
        "type": "number",
        "description": "Expression strength (0.0 to 1.0)",
        "default": 1.0,
        "minimum": 0.0,
        "maximum": 1.0
      },
      "transition_time": {
        "type": "number",
        "description": "Transition duration in seconds",
        "default": 0.2,
        "minimum": 0.0,
        "maximum": 2.0
      },
      "blend_with_current": {
        "type": "boolean",
        "description": "Blend with current expressions",
        "default": false
      }
    },
    "required": ["expression"]
  }
}
```

## What These Schemas Provided:

1. **Parameter Validation**: Exact types (string, number, boolean, object)
2. **Required Fields**: Which parameters must be provided
3. **Default Values**: Fallback values when not specified
4. **Value Constraints**: Min/max ranges, enums, etc.
5. **Documentation**: Human-readable descriptions for each parameter
6. **Type Safety**: Ensured correct data types were passed

## Why They Were Removed:

The current MCPB specification (version 0.2) doesn't support `inputSchema` fields in the manifest. The MCPB validator was rejecting them with errors like:

```
tools.0: Unrecognized key(s) in object: 'inputSchema'
```

## Impact:

- ✅ **Tools still work** - the actual MCP server implementation handles parameter validation
- ❌ **No manifest-level validation** - can't validate parameters before calling tools
- ❌ **No auto-generated UI** - MCPB can't create forms based on schemas
- ❌ **Less discoverability** - users can't see what parameters each tool expects

## Future:

When MCPB adds support for `inputSchema` in future versions, we can restore these detailed schemas to provide better tool discovery and validation.

