"""
Unity Tools for AvatarMCP - Unity Avatar Integration and Control

This module contains tools for Unity avatar integration, window management,
system control, and Unity-specific avatar operations.
"""

import os
import time
from typing import Dict, Any


class UnityTools:
    """Container for all Unity-related MCP tools."""

    def __init__(self, mcp_server):
        """Initialize Unity tools with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tools()

    def _register_tools(self):
        """Register all Unity tools with the MCP server."""
        # Register viewer_show tool
        @self.mcp_server.mcp.tool()
        def viewer_show(params: Dict[str, Any]) -> Dict[str, Any]:
            """Display avatar in Unity viewer window.

            Opens or updates a Unity-based avatar viewer window to display
            the specified VRM avatar with current animations and expressions.
            Essential for visual avatar inspection and testing.

            Parameters:
                avatar_id: Avatar to display (required)
                    - Must be loaded with avatar_load or unity_avatar_load
                    - Avatar will be rendered in Unity viewer
                    - Case-sensitive avatar identifier
                window_mode: How to display the viewer window (default: "windowed")
                    - "windowed" = standard resizable window
                    - "fullscreen" = full screen display
                    - "borderless" = borderless windowed mode
                    - "popup" = small popup window for quick viewing
                camera_position: Initial camera position relative to avatar (optional)
                    - Dictionary with x, y, z coordinates
                    - Distance and angle from avatar center
                    - If not provided, uses default viewing position
                lighting_preset: Lighting setup for the viewer (default: "studio")
                    - "studio" = professional studio lighting
                    - "outdoor" = natural outdoor illumination
                    - "indoor" = warm indoor lighting
                    - "dramatic" = theatrical spotlight setup
                background_color: Viewer background color (optional)
                    - RGB color values for background
                    - Affects avatar visibility and mood
                    - Default depends on lighting preset
                show_fps: Whether to display frame rate counter (default: False)
                    - True = show performance metrics
                    - False = clean viewing experience
                    - Useful for performance monitoring

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - avatar_id: Avatar being displayed
                    - window_handle: Unity window identifier
                    - viewer_resolution: Display resolution used
                    - rendering_active: Whether avatar is actively rendering
                    - fps_display: Whether FPS counter is shown

            Usage:
                Use this tool to visually inspect avatars, test animations,
                and verify avatar appearance in a Unity-based viewer environment.
                Essential for avatar development and quality assurance.

            Examples:
                Basic avatar viewing:
                    result = await viewer_show({
                        'avatar_id': 'nekomimi_chan',
                        'window_mode': 'windowed',
                        'lighting_preset': 'studio'
                    })
                    # Opens Unity viewer window showing Nekomimi-chan

                Fullscreen dramatic presentation:
                    result = await viewer_show({
                        'avatar_id': 'hero_character',
                        'window_mode': 'fullscreen',
                        'lighting_preset': 'dramatic',
                        'camera_position': {'x': 2, 'y': 1.5, 'z': 3},
                        'show_fps': True
                    })
                    # Fullscreen dramatic presentation with FPS monitoring

                Quick popup inspection:
                    result = await viewer_show({
                        'avatar_id': 'test_avatar',
                        'window_mode': 'popup',
                        'background_color': {'r': 0.2, 'g': 0.2, 'b': 0.2}
                    })
                    # Small popup window for quick avatar inspection

                Error handling:
                    result = await viewer_show({
                        'avatar_id': 'nonexistent',
                        'window_mode': 'windowed'
                    })
                    if result['status'] == 'error':
                        print(f"Viewer display failed: {result['message']}")
                    # Check avatar exists and Unity viewer is available

            Raises:
                ValueError: If avatar_id invalid or viewer parameters malformed
                RuntimeError: If Unity viewer unavailable or fails to initialize
                ConnectionError: If unable to communicate with Unity application

            Notes:
                - Viewer window persists until explicitly closed
                - Real-time updates reflect avatar state changes
                - Performance depends on avatar complexity and system capabilities
                - Multiple viewers can be open simultaneously
                - Window mode affects available screen space
                - Lighting presets optimize avatar visibility
                - Camera position affects viewing perspective

            See Also:
                - avatar_load: Load avatars before viewing
                - animation_play: Play animations in viewer
                - avatar_appearance_modify: Modify appearance before viewing
                - performance_recording_system: Record viewer sessions
            """
            return self.mcp_server._execute_viewer_show(params)

        @self.mcp_server.mcp.tool()
        def unity_system_status(params: Dict[str, Any]) -> Dict[str, Any]:
            """Query Unity application system status and performance metrics.

            Retrieves comprehensive status information from the Unity avatar
            application including performance metrics, system resources, and
            operational state. Essential for monitoring and troubleshooting.

            Parameters:
                include_performance: Whether to include detailed performance metrics (default: True)
                    - True = comprehensive performance data
                    - False = basic status only
                    - Performance metrics include frame rate, memory usage
                include_resources: Whether to include system resource information (default: True)
                    - True = CPU, memory, GPU statistics
                    - False = exclude resource monitoring
                    - Resource data helps identify bottlenecks
                include_unity_logs: Whether to include recent Unity console logs (default: False)
                    - True = last 50 log entries
                    - False = exclude logs for privacy
                    - Logs useful for debugging issues
                detail_level: Level of detail in status report (default: "standard")
                    - "basic" = essential status only
                    - "standard" = comprehensive status with key metrics
                    - "detailed" = full system analysis with all available data
                    - "diagnostic" = troubleshooting-focused information

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - unity_version: Unity application version
                    - system_info: Operating system and hardware details
                    - performance_metrics: Frame rate, memory usage, render stats
                    - resource_usage: CPU, GPU, memory consumption
                    - avatar_count: Number of loaded avatars
                    - active_windows: Number of open viewer windows
                    - last_update: Timestamp of last successful status check

            Usage:
                Use this tool to monitor Unity application health, diagnose performance
                issues, and ensure optimal avatar display and interaction performance.
                Essential for system maintenance and troubleshooting.

            Examples:
                Standard system status check:
                    result = await unity_system_status({
                        'include_performance': True,
                        'detail_level': 'standard'
                    })
                    # Comprehensive status with performance metrics

                Quick health check:
                    result = await unity_system_status({
                        'include_performance': False,
                        'include_resources': False,
                        'detail_level': 'basic'
                    })
                    # Basic connectivity and operational status

                Diagnostic troubleshooting:
                    result = await unity_system_status({
                        'include_performance': True,
                        'include_resources': True,
                        'include_unity_logs': True,
                        'detail_level': 'diagnostic'
                    })
                    # Full diagnostic information for troubleshooting

                Performance monitoring:
                    result = await unity_system_status({
                        'include_performance': True,
                        'include_resources': True,
                        'detail_level': 'detailed'
                    })
                    # Detailed performance and resource monitoring

                Error handling:
                    result = await unity_system_status({
                        'detail_level': 'standard'
                    })
                    if result['status'] == 'error':
                        print(f"System status check failed: {result['message']}")
                    # Check Unity application is running and accessible

            Raises:
                RuntimeError: If Unity application unavailable or communication fails
                ConnectionError: If unable to reach Unity system
                TimeoutError: If status query times out

            Notes:
                - Status queries have minimal performance impact
                - Performance metrics update in real-time
                - Resource usage helps identify optimization opportunities
                - Unity logs contain debugging information
                - Detail level affects response size and query time
                - Regular monitoring helps maintain system health
                - Status information is cached briefly to reduce overhead

            See Also:
                - unity_window_position: Control window positioning
                - avatar_load: Monitor avatar loading impact
                - performance_recording_system: Record performance metrics
                - system_status: General system status (non-Unity specific)
            """
            return self.mcp_server._execute_unity_system_status(params)

        @self.mcp_server.mcp.tool()
        def unity_window_position(params: Dict[str, Any]) -> Dict[str, Any]:
            """Control Unity viewer window position and display settings.

            Manages Unity avatar viewer window positioning, size, and display
            properties for optimal viewing experience and multi-window setups.
            Essential for professional avatar display and multi-screen configurations.

            Parameters:
                window_action: Type of window operation to perform (required)
                    - "position" = set window position on screen
                    - "size" = resize window dimensions
                    - "focus" = bring window to front and focus
                    - "minimize" = minimize window to taskbar
                    - "maximize" = maximize window to fill screen
                    - "close" = close the viewer window
                    - "arrange" = automatically arrange multiple windows
                window_handle: Specific window to control (optional)
                    - Unity window identifier from viewer_show result
                    - If not provided, controls the most recently active window
                    - Allows control of specific viewer windows
                position_coords: New window position for "position" action (required for position)
                    - Dictionary with x, y screen coordinates
                    - Coordinates are in pixels from top-left of primary display
                    - Negative coordinates allowed for multi-monitor setups
                size_dimensions: New window size for "size" action (required for size)
                    - Dictionary with width, height in pixels
                    - Minimum size restrictions may apply
                    - Affects avatar display quality and performance
                arrange_layout: Window arrangement pattern for "arrange" action (optional for arrange)
                    - "grid" = arrange in grid pattern
                    - "cascade" = overlapping cascade arrangement
                    - "tile" = tile windows to fill screen space
                    - "stack" = stack windows in corner
                monitor_target: Target monitor for window placement (optional)
                    - Monitor index (0 = primary, 1 = secondary, etc.)
                    - If not specified, uses current monitor
                    - Useful for multi-monitor setups

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable result description
                    - window_action: Action that was performed
                    - window_handle: Window that was affected
                    - new_position: Updated window position (if applicable)
                    - new_size: Updated window size (if applicable)
                    - monitor_used: Monitor where window is positioned
                    - windows_affected: Number of windows modified (for arrange)

            Usage:
                Use this tool to organize and control Unity viewer windows for
                professional avatar display, multi-avatar monitoring, and optimal
                viewing experiences across single or multiple monitors.

            Examples:
                Position window on specific monitor:
                    result = await unity_window_position({
                        'window_action': 'position',
                        'position_coords': {'x': 1920, 'y': 100},
                        'monitor_target': 1
                    })
                    # Position window on secondary monitor

                Resize viewer window:
                    result = await unity_window_position({
                        'window_action': 'size',
                        'size_dimensions': {'width': 1280, 'height': 720},
                        'window_handle': 'viewer_123'
                    })
                    # Resize specific viewer window to 720p

                Focus active viewer:
                    result = await unity_window_position({
                        'window_action': 'focus'
                    })
                    # Bring most recent viewer window to front

                Arrange multiple viewers:
                    result = await unity_window_position({
                        'window_action': 'arrange',
                        'arrange_layout': 'grid'
                    })
                    # Arrange all viewer windows in grid pattern

                Minimize background viewers:
                    result = await unity_window_position({
                        'window_action': 'minimize',
                        'window_handle': 'background_viewer'
                    })
                    # Minimize specific background viewer window

                Error handling:
                    result = await unity_window_position({
                        'window_action': 'position',
                        'position_coords': {'x': 100, 'y': 100}
                    })
                    if result['status'] == 'error':
                        print(f"Window positioning failed: {result['message']}")
                    # Check Unity application is running and windows exist

            Raises:
                ValueError: If window_action invalid or coordinates malformed
                RuntimeError: If Unity window control unavailable
                ConnectionError: If unable to communicate with Unity application
                IndexError: If monitor_target is invalid

            Notes:
                - Window operations are immediate and persistent
                - Position coordinates are absolute screen coordinates
                - Size changes may affect rendering quality and performance
                - Focus operations bring windows to foreground
                - Arrange operations affect all open viewer windows
                - Monitor targeting supports multi-display setups
                - Window handles persist across operations

            See Also:
                - viewer_show: Create viewer windows to control
                - unity_system_status: Monitor window and system status
                - avatar_load: Load avatars into positioned windows
                - animation_play: Play animations in positioned viewers
            """
            return self.mcp_server._execute_unity_window_position(params)
