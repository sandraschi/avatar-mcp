# AvatarMCP Portmanteau Tools Architecture Plan

## Overview
Consolidate 28 individual tools into 15 portmanteau tools following FastMCP 2.12 standards with multiline docstrings (no triple quotes inside).

## Portmanteau Tool Design

### 1. **avatar_manager** - Avatar Lifecycle Management
**Consolidates:** `avatar_load`, `avatar_unload`, `avatar_list`, `avatar_set_active`, `avatar_get_active`, `avatar_get_metadata`
**Operations:** load, unload, list, set_active, get_active, get_metadata

### 2. **animation_controller** - Animation Control & Management  
**Consolidates:** `animation_play`, `animation_stop`, `animation_list`
**Operations:** play, stop, list

### 3. **parameter_manager** - Avatar Parameter Control
**Consolidates:** `parameter_set`, `parameter_get`
**Operations:** set, get

### 4. **osc_communicator** - OSC Communication Hub
**Consolidates:** `osc_send`, `osc_receive`
**Operations:** send, receive

### 5. **unity_integration** - Unity Desktop Avatar Control
**Consolidates:** `unity_system_status`, `unity_avatar_load`, `unity_avatar_expression`, `unity_avatar_animation`
**Operations:** status, load_avatar, set_expression, control_animation

### 6. **unity_window_manager** - Unity Window Control
**Consolidates:** `unity_window_position`, `unity_window_transparency`, `unity_window_visibility`, `unity_window_mode`
**Operations:** set_position, set_transparency, set_visibility, set_mode

### 7. **unity_config_manager** - Unity Configuration & Plugins
**Consolidates:** `unity_osc_bridge`, `unity_plugin_load`, `unity_config_update`
**Operations:** configure_bridge, load_plugin, update_config

### 8. **chat_manager** - Chat Session Management
**Consolidates:** `chat_start`, `chat_send_message`, `chat_stop`, `chat_get_state`
**Operations:** start_session, send_message, stop_session, get_state

### 9. **system_monitor** - System Health & Diagnostics
**Consolidates:** `system_status`
**Operations:** get_status, get_health, get_metrics

### 10. **server_controller** - Server Lifecycle Management
**Consolidates:** `initialize`, `shutdown`
**Operations:** initialize, shutdown

### 11. **debug_tools** - Debug & Testing Utilities
**Consolidates:** `debug_echo`, `debug_log`
**Operations:** echo, log, test_connection

### 12. **viewer_manager** - 3D Viewer Control
**Consolidates:** `viewer_show`
**Operations:** show, hide, configure, capture

### 13. **file_manager** - File & Asset Management
**Consolidates:** File operations, asset loading, path management
**Operations:** load_file, save_file, list_files, validate_path

### 14. **network_manager** - Network & Connection Management
**Consolidates:** Network operations, connection handling, protocol management
**Operations:** connect, disconnect, test_connection, get_status

### 15. **config_manager** - Configuration & Settings Management
**Consolidates:** Configuration loading, settings updates, environment management
**Operations:** load_config, update_setting, get_config, validate_config

## Implementation Strategy

### Phase 1: Core Portmanteau Tools (Priority 1)
1. `avatar_manager` - Core avatar functionality
2. `animation_controller` - Animation control
3. `parameter_manager` - Parameter management
4. `osc_communicator` - OSC communication
5. `unity_integration` - Unity integration

### Phase 2: Management Tools (Priority 2)
6. `chat_manager` - Chat functionality
7. `system_monitor` - System monitoring
8. `server_controller` - Server lifecycle
9. `debug_tools` - Debug utilities
10. `viewer_manager` - 3D viewer control

### Phase 3: Advanced Tools (Priority 3)
11. `unity_window_manager` - Unity window control
12. `unity_config_manager` - Unity configuration
13. `file_manager` - File management
14. `network_manager` - Network management
15. `config_manager` - Configuration management

## FastMCP 2.12 Standards Compliance

### Docstring Format
```python
def operation_name(self, params: dict[str, Any]) -> dict[str, Any]:
    """Operation description.
    
    Detailed description of what this operation does.
    Can span multiple lines for comprehensive documentation.
    
    Parameters:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        Dictionary with operation results
        
    Examples:
        Basic usage example
        Advanced usage example
        
    Notes:
        Important implementation notes
        Usage considerations
    """
```

### Tool Registration Pattern
```python
@self.mcp_server.mcp.tool()
def portmanteau_tool_name(params: dict[str, Any]) -> dict[str, Any]:
    """Portmanteau tool description.
    
    Comprehensive description of the portmanteau tool's purpose
    and all operations it provides.
    
    Parameters:
        operation: The specific operation to perform
        ... other parameters based on operation
        
    Returns:
        Dictionary with operation results
    """
    operation = params.get("operation")
    
    if operation == "operation1":
        return self._handle_operation1(params)
    elif operation == "operation2":
        return self._handle_operation2(params)
    # ... etc
```

## Benefits

1. **Reduced Tool Count**: 28 tools → 15 tools (47% reduction)
2. **Better Organization**: Related functionality grouped logically
3. **Easier Maintenance**: Single class per functional area
4. **Improved Discoverability**: Clearer tool purposes
5. **Standards Compliance**: FastMCP 2.12 compliant
6. **Better Documentation**: Comprehensive multiline docstrings
7. **Cleaner API**: More intuitive tool structure



