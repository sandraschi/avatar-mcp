"""
Unity Config Manager Portmanteau Tool for AvatarMCP

Consolidates all Unity desktop avatar configuration management operations into a single tool
following FastMCP 2.12 standards with multiline docstrings.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class UnityConfigManagerTool:
    """Portmanteau tool for comprehensive Unity desktop avatar configuration management."""

    def __init__(self, mcp_server):
        """Initialize Unity config manager tool with reference to MCP server."""
        self.mcp_server = mcp_server
        self._register_tool()

    def _send_unity_osc(self, address: str, *args) -> bool:
        """Send OSC message to Unity desktop avatar."""
        try:
            if not self.mcp_server.osc_manager or not self.mcp_server.osc_manager.osc_client:
                return False

            self.mcp_server.osc_manager.osc_client.send_message(address, *args)
            return True
        except Exception as e:
            logger.error(f"Failed to send OSC to Unity: {e}")
            return False

    def _get_unity_config_path(self) -> str:
        """Get the path to Unity configuration file."""
        # Look for Unity config in common locations
        config_paths = [
            os.path.join(
                os.getcwd(), "unity-desktop-avatar", "Assets", "Resources", "Config", "config.json"
            ),
            os.path.join(os.getcwd(), "config", "unity_config.json"),
            os.path.join(os.getcwd(), "unity_config.json"),
        ]

        for path in config_paths:
            if os.path.exists(path):
                return path

        # Return default path if none found
        return config_paths[0]

    def _load_unity_config(self) -> dict[str, Any]:
        """Load Unity configuration from file."""
        try:
            config_path = self._get_unity_config_path()
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Return default config
                return {
                    "osc": {"enabled": True, "server_port": 9000, "client_port": 9001},
                    "window": {"transparent": True, "always_on_top": True, "click_through": False},
                    "avatar": {"auto_load": False, "default_avatar": None},
                }
        except Exception as e:
            logger.error(f"Failed to load Unity config: {e}")
            return {}

    def _save_unity_config(self, config: dict[str, Any]) -> bool:
        """Save Unity configuration to file."""
        try:
            config_path = self._get_unity_config_path()
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save Unity config: {e}")
            return False

    def _register_tool(self):
        """Register the Unity config manager portmanteau tool."""

        @self.mcp_server.mcp.tool()
        def unity_config_manager(params: dict[str, Any]) -> dict[str, Any]:
            """Comprehensive Unity desktop avatar configuration management tool.

            Provides unified interface for all Unity desktop avatar configuration
            operations including OSC bridge configuration, plugin management, and
            general settings. This portmanteau tool consolidates configuration
            management functionality into a single, well-organized interface.

            Parameters:
                operation: The specific operation to perform (required)
                    - "get_config": Get current Unity configuration
                    - "update_config": Update Unity configuration
                    - "osc_bridge": Configure OSC bridge settings
                    - "plugin_load": Load Unity plugin
                    - "plugin_list": List available plugins

                Additional parameters depend on the operation:
                    - For "get_config": section (optional) - specific config section
                    - For "update_config": config (required) - configuration object
                    - For "osc_bridge": enabled (optional), server_port (optional),
                      client_port (optional)
                    - For "plugin_load": plugin_name (required), plugin_path (optional)
                    - For "plugin_list": None

            Returns:
                Dictionary containing:
                    - status: Either "success" or "error"
                    - message: Human-readable operation result
                    - operation: The operation that was performed
                    - Additional fields based on operation type

            Examples:
                Get current configuration:
                    result = await unity_config_manager({
                        "operation": "get_config"
                    })

                Update OSC settings:
                    result = await unity_config_manager({
                        "operation": "osc_bridge",
                        "enabled": True,
                        "server_port": 9000,
                        "client_port": 9001
                    })

                Load plugin:
                    result = await unity_config_manager({
                        "operation": "plugin_load",
                        "plugin_name": "gesture_recognition"
                    })

                List available plugins:
                    result = await unity_config_manager({
                        "operation": "plugin_list"
                    })

            Notes:
                - All operations require server to be initialized
                - Configuration changes are saved to file automatically
                - OSC bridge changes take effect immediately
                - Plugin loading requires Unity application restart
                - Configuration file is located in Unity project Resources/Config/
            """
            try:
                if not self.mcp_server.initialized:
                    raise RuntimeError("Server not initialized. Call 'initialize' first.")

                operation = params.get("operation")
                if not operation:
                    return {"status": "error", "message": "Operation parameter is required"}

                if operation == "get_config":
                    return self._handle_get_config(params)
                elif operation == "update_config":
                    return self._handle_update_config(params)
                elif operation == "osc_bridge":
                    return self._handle_osc_bridge(params)
                elif operation == "plugin_load":
                    return self._handle_plugin_load(params)
                elif operation == "plugin_list":
                    return self._handle_plugin_list(params)
                else:
                    return {
                        "status": "error",
                        "message": f"Unknown operation '{operation}'. Valid operations: "
                        "get_config, update_config, osc_bridge, plugin_load, plugin_list",
                    }

            except Exception as e:
                logger.error(f"Unity config manager operation failed: {str(e)}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Unity config manager operation failed: {str(e)}",
                }

    def _handle_get_config(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity configuration retrieval operation."""
        try:
            section = params.get("section")
            config = self._load_unity_config()

            if section:
                if section in config:
                    return {
                        "status": "success",
                        "message": f"Retrieved Unity config section '{section}'",
                        "operation": "get_config",
                        "section": section,
                        "config": config[section],
                    }
                else:
                    return {"status": "error", "message": f"Config section '{section}' not found"}
            else:
                return {
                    "status": "success",
                    "message": "Retrieved Unity configuration",
                    "operation": "get_config",
                    "config": config,
                }

        except Exception as e:
            return {"status": "error", "message": f"Failed to get Unity config: {str(e)}"}

    def _handle_update_config(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity configuration update operation."""
        try:
            new_config = params.get("config")
            if not new_config:
                return {
                    "status": "error",
                    "message": "Config parameter is required for update_config operation",
                }

            # Load current config and merge
            current_config = self._load_unity_config()
            current_config.update(new_config)

            # Save updated config
            if self._save_unity_config(current_config):
                return {
                    "status": "success",
                    "message": "Updated Unity configuration",
                    "operation": "update_config",
                    "config": current_config,
                }
            else:
                return {"status": "error", "message": "Failed to save Unity configuration"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to update Unity config: {str(e)}"}

    def _handle_osc_bridge(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle OSC bridge configuration operation."""
        try:
            enabled = params.get("enabled")
            server_port = params.get("server_port")
            client_port = params.get("client_port")

            # Load current config
            config = self._load_unity_config()
            if "osc" not in config:
                config["osc"] = {}

            # Update OSC settings
            if enabled is not None:
                config["osc"]["enabled"] = bool(enabled)
            if server_port is not None:
                config["osc"]["server_port"] = int(server_port)
            if client_port is not None:
                config["osc"]["client_port"] = int(client_port)

            # Save config
            if self._save_unity_config(config):
                # Send OSC command to Unity to update bridge settings
                success = self._send_unity_osc(
                    "/unity/config/osc",
                    config["osc"]["enabled"],
                    config["osc"]["server_port"],
                    config["osc"]["client_port"],
                )

                return {
                    "status": "success",
                    "message": "Updated OSC bridge configuration",
                    "operation": "osc_bridge",
                    "osc_config": config["osc"],
                    "unity_command_sent": success,
                }
            else:
                return {"status": "error", "message": "Failed to save OSC bridge configuration"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to configure OSC bridge: {str(e)}"}

    def _handle_plugin_load(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity plugin loading operation."""
        try:
            plugin_name = params.get("plugin_name")
            if not plugin_name:
                return {
                    "status": "error",
                    "message": "Plugin name is required for plugin_load operation",
                }

            plugin_path = params.get("plugin_path")
            if not plugin_path:
                # Default plugin path
                plugin_path = f"StreamingAssets/Plugins/{plugin_name}.dll"

            # Send OSC command to Unity to load plugin
            success = self._send_unity_osc("/unity/plugin/load", plugin_name, plugin_path)

            if success:
                return {
                    "status": "success",
                    "message": f"Loading Unity plugin '{plugin_name}'",
                    "operation": "plugin_load",
                    "plugin_name": plugin_name,
                    "plugin_path": plugin_path,
                    "unity_command_sent": True,
                }
            else:
                return {"status": "error", "message": "Failed to send Unity plugin load command"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to load Unity plugin: {str(e)}"}

    def _handle_plugin_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle Unity plugin listing operation."""
        try:
            # For now, return a static list of available plugins
            # In a real implementation, this would query Unity for loaded plugins
            available_plugins = [
                {
                    "name": "gesture_recognition",
                    "description": "Hand gesture recognition plugin",
                    "loaded": False,
                },
                {
                    "name": "facial_tracking",
                    "description": "Facial expression tracking plugin",
                    "loaded": False,
                },
                {
                    "name": "voice_synthesis",
                    "description": "Text-to-speech voice synthesis plugin",
                    "loaded": False,
                },
            ]

            return {
                "status": "success",
                "message": "Retrieved Unity plugin list",
                "operation": "plugin_list",
                "plugins": available_plugins,
                "count": len(available_plugins),
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to list Unity plugins: {str(e)}"}
