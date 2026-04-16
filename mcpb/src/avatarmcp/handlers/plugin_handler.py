"""
Plugin handler for the Avatar MCP server.

This module provides a plugin system for extending the functionality of the
Avatar MCP server. Plugins can register handlers, add routes, and modify
server behavior at runtime.
"""

import importlib
import importlib.util
import inspect
import json
import logging
import os
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, TypeVar

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PluginError(Exception):
    """Base exception for plugin-related errors."""

    pass


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""

    pass


class PluginDependencyError(PluginError):
    """Raised when a plugin's dependencies are not met."""

    pass


class PluginConflictError(PluginError):
    """Raised when there is a conflict between plugins."""

    pass


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""

    name: str
    version: str
    author: str
    description: str = ""
    requires: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] | None = None
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PluginMetadata":
        """Create a PluginMetadata instance from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in inspect.signature(cls).parameters})

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return asdict(self)


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""

    name: str
    version: str
    description: str
    path: str
    enabled: bool
    metadata: dict[str, Any]
    module: ModuleType | None = None
    instance: Any | None = None
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)

    @property
    def is_loaded(self) -> bool:
        """Check if the plugin is currently loaded."""
        return self.module is not None and self.instance is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "path": self.path,
            "enabled": self.enabled,
            "is_loaded": self.is_loaded,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "metadata": self.metadata,
        }


class PluginManager:
    """Manages the loading and unloading of plugins."""

    def __init__(self, plugin_dirs: list[str | Path] | None = None):
        """Initialize the plugin manager.

        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugin_dirs = [Path(d) for d in (plugin_dirs or [])]
        self.plugins: dict[str, PluginInfo] = {}
        self._loaded_modules: set[str] = set()
        self._event_handlers: dict[str, list[Callable]] = {}

    def add_plugin_dir(self, directory: str | Path) -> None:
        """Add a directory to the plugin search path.

        Args:
            directory: Directory to add
        """
        directory = Path(directory).resolve()
        if directory not in self.plugin_dirs:
            self.plugin_dirs.append(directory)

    def discover_plugins(self) -> list[PluginInfo]:
        """Discover plugins in the configured plugin directories.

        Returns:
            List of discovered plugin infos
        """
        discovered = []

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists() or not plugin_dir.is_dir():
                logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue

            for entry in os.scandir(plugin_dir):
                if not entry.is_dir() and not (entry.name.endswith(".py") and entry.name != "__init__.py"):
                    continue

                plugin_path = Path(entry.path)
                plugin_name = plugin_path.stem

                # Skip already loaded plugins
                if plugin_name in self.plugins:
                    continue

                try:
                    metadata = self._load_plugin_metadata(plugin_path)
                    if not metadata:
                        continue

                    plugin_info = PluginInfo(
                        name=metadata.name,
                        version=metadata.version,
                        description=metadata.description,
                        path=str(plugin_path),
                        enabled=metadata.enabled,
                        metadata=metadata.to_dict() if hasattr(metadata, "to_dict") else {},
                        dependencies=metadata.requires,
                    )

                    self.plugins[plugin_name] = plugin_info
                    discovered.append(plugin_info)

                    logger.info(f"Discovered plugin: {plugin_name} v{metadata.version}")

                except Exception as e:
                    logger.error(f"Error discovering plugin {plugin_name}: {e!s}")
                    continue

        return discovered

    def _load_plugin_metadata(self, plugin_path: Path) -> PluginMetadata | None:
        """Load plugin metadata from a plugin file or directory.

        Args:
            plugin_path: Path to the plugin file or directory

        Returns:
            PluginMetadata if valid, None otherwise
        """
        if plugin_path.is_dir():
            # Look for __init__.py or plugin.json
            init_file = plugin_path / "__init__.py"
            json_file = plugin_path / "plugin.json"

            if json_file.exists():
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                        return PluginMetadata.from_dict(data)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Invalid plugin.json in {plugin_path}: {e!s}")
                    return None
            elif init_file.exists():
                plugin_path = init_file
            else:
                return None

        # Try to extract metadata from module docstring or variables
        try:
            spec = importlib.util.spec_from_file_location(plugin_path.stem, str(plugin_path))
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check for PluginMetadata instance
            if hasattr(module, "PLUGIN_METADATA") and isinstance(module.PLUGIN_METADATA, dict):
                return PluginMetadata.from_dict(module.PLUGIN_METADATA)

            # Extract from module attributes
            name = getattr(module, "__name__", plugin_path.stem)
            version = getattr(module, "__version__", "0.1.0")
            author = getattr(module, "__author__", "Unknown")
            description = getattr(module, "__doc__", "").strip() or "No description provided."

            return PluginMetadata(name=name, version=version, author=author, description=description)

        except Exception as e:
            logger.error(f"Error loading plugin metadata from {plugin_path}: {e!s}")
            return None

    def load_plugin(self, plugin_name: str, force_reload: bool = False) -> bool:
        """Load a plugin by name.

        Args:
            plugin_name: Name of the plugin to load
            force_reload: If True, reload the plugin even if already loaded

        Returns:
            True if the plugin was loaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False

        plugin_info = self.plugins[plugin_name]

        # Skip if already loaded and not forcing reload
        if plugin_info.is_loaded and not force_reload:
            return True

        # Check if disabled
        if not plugin_info.enabled:
            logger.warning(f"Plugin {plugin_name} is disabled")
            return False

        # Check dependencies
        missing_deps = []
        for dep in plugin_info.dependencies:
            if dep not in self.plugins or not self.plugins[dep].is_loaded:
                missing_deps.append(dep)

        if missing_deps:
            logger.error(f"Plugin {plugin_name} is missing dependencies: {', '.join(missing_deps)}")
            return False

        # Check for conflicts
        for other_name, other_plugin in self.plugins.items():
            if other_plugin.is_loaded and plugin_name in (other_plugin.metadata.get("conflicts") or []):
                logger.error(f"Plugin {plugin_name} conflicts with loaded plugin {other_name}")
                return False

        try:
            # Load the module
            if plugin_path := Path(plugin_info.path):
                if plugin_path.is_dir():
                    module = self._load_package_plugin(plugin_path, plugin_name)
                else:
                    module = self._load_module_plugin(plugin_path, plugin_name)
            else:
                logger.error(f"Invalid plugin path for {plugin_name}")
                return False

            if not module:
                return False

            # Create plugin instance if it has a Plugin class
            plugin_instance = None
            if hasattr(module, "Plugin"):
                plugin_class = module.Plugin
                if not inspect.isclass(plugin_class):
                    logger.error(f"Plugin {plugin_name} has an invalid Plugin attribute (not a class)")
                    return False

                try:
                    plugin_instance = plugin_class()
                except Exception as e:
                    logger.error(f"Error instantiating plugin {plugin_name}: {e!s}", exc_info=True)
                    return False

            # Update plugin info
            plugin_info.module = module
            plugin_info.instance = plugin_instance

            # Register event handlers
            if plugin_instance:
                self._register_event_handlers(plugin_name, plugin_instance)

            logger.info(f"Loaded plugin: {plugin_name} v{plugin_info.version}")
            return True

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e!s}", exc_info=True)
            return False

    def _load_package_plugin(self, plugin_dir: Path, plugin_name: str) -> ModuleType | None:
        """Load a plugin from a package directory."""
        init_file = plugin_dir / "__init__.py"
        if not init_file.exists():
            logger.error(f"No __init__.py found in plugin directory: {plugin_dir}")
            return None

        # Add parent directory to Python path if needed
        parent_dir = str(plugin_dir.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            module = importlib.import_module(plugin_dir.name)
            importlib.reload(module)  # Ensure we're loading fresh
            return module
        except ImportError as e:
            logger.error(f"Error importing plugin package {plugin_name}: {e!s}")
            return None

    def _load_module_plugin(self, plugin_path: Path, plugin_name: str) -> ModuleType | None:
        """Load a plugin from a single Python file."""
        module_name = f"{__name__}.plugins.{plugin_name}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, str(plugin_path))
            if not spec or not spec.loader:
                logger.error(f"Could not load spec for plugin: {plugin_name}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            return module
        except Exception as e:
            logger.error(f"Error loading plugin module {plugin_name}: {e!s}", exc_info=True)
            return None

    def _register_event_handlers(self, plugin_name: str, plugin_instance: Any) -> None:
        """Register event handlers from a plugin instance."""
        if not hasattr(plugin_instance, "on_event"):
            return

        for attr_name in dir(plugin_instance):
            if not attr_name.startswith("on_") or attr_name == "on_event":
                continue

            event_name = attr_name[3:]  # Remove 'on_' prefix
            handler = getattr(plugin_instance, attr_name)

            if callable(handler):
                if event_name not in self._event_handlers:
                    self._event_handlers[event_name] = []
                self._event_handlers[event_name].append(handler)
                logger.debug(f"Registered event handler: {plugin_name}.{attr_name} for event '{event_name}'")

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if the plugin was unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins or not self.plugins[plugin_name].is_loaded:
            return False

        plugin_info = self.plugins[plugin_name]

        # Check if other plugins depend on this one
        dependent_plugins = [
            name for name, plugin in self.plugins.items() if plugin_name in plugin.dependencies and plugin.is_loaded
        ]

        if dependent_plugins:
            logger.error(
                f"Cannot unload {plugin_name}: the following plugins depend on it: {', '.join(dependent_plugins)}"
            )
            return False

        try:
            # Call plugin's cleanup method if it exists
            if plugin_info.instance and hasattr(plugin_info.instance, "cleanup"):
                try:
                    plugin_info.instance.cleanup()
                except Exception as e:
                    logger.error(f"Error during plugin cleanup for {plugin_name}: {e!s}", exc_info=True)

            # Remove event handlers
            self._unregister_event_handlers(plugin_name)

            # Remove from sys.modules if it's there
            module_name = getattr(plugin_info.module, "__name__", None)
            if module_name and module_name in sys.modules:
                del sys.modules[module_name]

            # Update plugin info
            plugin_info.module = None
            plugin_info.instance = None

            logger.info(f"Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e!s}", exc_info=True)
            return False

    def _unregister_event_handlers(self, plugin_name: str) -> None:
        """Unregister all event handlers for a plugin."""
        for event_name, handlers in list(self._event_handlers.items()):
            self._event_handlers[event_name] = [
                h for h in handlers if not (hasattr(h, "__self__") and h.__self__.__class__.__name__ == plugin_name)
            ]

            if not self._event_handlers[event_name]:
                del self._event_handlers[event_name]

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin.

        Args:
            plugin_name: Name of the plugin to enable

        Returns:
            True if the plugin was enabled, False otherwise
        """
        if plugin_name not in self.plugins:
            return False

        self.plugins[plugin_name].enabled = True
        return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin.

        Args:
            plugin_name: Name of the plugin to disable

        Returns:
            True if the plugin was disabled, False otherwise
        """
        if plugin_name not in self.plugins:
            return False

        # Unload the plugin if it's currently loaded
        if self.plugins[plugin_name].is_loaded:
            self.unload_plugin(plugin_name)

        self.plugins[plugin_name].enabled = False
        return True

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        """Emit an event to all registered handlers.

        Args:
            event_name: Name of the event to emit
            *args: Positional arguments to pass to event handlers
            **kwargs: Keyword arguments to pass to event handlers
        """
        if event_name not in self._event_handlers:
            return

        for handler in self._event_handlers[event_name]:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler for '{event_name}': {e!s}", exc_info=True)

    def get_plugin(self, plugin_name: str) -> PluginInfo | None:
        """Get information about a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            PluginInfo if found, None otherwise
        """
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> list[dict[str, Any]]:
        """Get a list of all plugins.

        Returns:
            List of plugin information dictionaries
        """
        return [plugin.to_dict() for plugin in self.plugins.values()]

    def load_all_plugins(self) -> None:
        """Load all enabled plugins."""
        # First discover all plugins
        self.discover_plugins()

        # Then load them in dependency order
        loaded = set()
        remaining = set(self.plugins.keys())

        while remaining:
            loaded_this_round = False

            for plugin_name in list(remaining):
                plugin = self.plugins[plugin_name]

                # Skip if not enabled
                if not plugin.enabled:
                    remaining.remove(plugin_name)
                    continue

                # Check if all dependencies are loaded
                deps_met = all(dep in loaded for dep in plugin.dependencies)

                if deps_met:
                    if self.load_plugin(plugin_name):
                        loaded.add(plugin_name)
                        loaded_this_round = True
                    remaining.remove(plugin_name)

            if not loaded_this_round and remaining:
                # No plugins were loaded this round, but some remain - we have a
                # dependency cycle or missing deps
                logger.error(f"Could not load all plugins. Remaining: {', '.join(remaining)}")
                for plugin_name in remaining:
                    plugin = self.plugins[plugin_name]
                    missing_deps = [dep for dep in plugin.dependencies if dep not in loaded]
                    if missing_deps:
                        logger.error(f"  {plugin_name}: missing dependencies: {', '.join(missing_deps)}")
                break

    def unload_all_plugins(self) -> None:
        """Unload all plugins."""
        # Unload plugins in reverse order of loading (to handle dependencies)
        for plugin_name in reversed(list(self.plugins.keys())):
            if self.plugins[plugin_name].is_loaded:
                self.unload_plugin(plugin_name)


class PluginHandler(BaseHandler):
    """Handler for managing plugins in the Avatar MCP server."""

    def __init__(self, server: Any = None):
        """Initialize the plugin handler.

        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self.plugin_manager = PluginManager()
        self._plugin_dirs: list[Path] = []
        self._initialized = False

    async def _initialize(self) -> None:
        """Initialize the plugin handler."""
        # Set up default plugin directories
        self._setup_plugin_dirs()

        # Discover and load plugins
        await self.load_plugins()

        self._initialized = True
        logger.info("Plugin handler initialized")

    def _setup_plugin_dirs(self) -> None:
        """Set up the default plugin directories."""
        # Add the default plugins directory
        default_plugin_dir = Path(__file__).parent.parent / "plugins"
        self.add_plugin_dir(default_plugin_dir)

        # Add user plugins directory if it exists
        user_plugin_dir = Path.home() / ".config" / "avatarmcp" / "plugins"
        if user_plugin_dir.exists():
            self.add_plugin_dir(user_plugin_dir)

    def add_plugin_dir(self, directory: str | Path) -> None:
        """Add a directory to the plugin search path.

        Args:
            directory: Directory to add
        """
        directory = Path(directory).resolve()
        if directory not in self._plugin_dirs:
            self._plugin_dirs.append(directory)
            self.plugin_manager.add_plugin_dir(directory)

    async def load_plugins(self) -> None:
        """Load all available plugins."""
        try:
            # Discover and load plugins
            self.plugin_manager.discover_plugins()
            self.plugin_manager.load_all_plugins()

            # Log loaded plugins
            loaded_plugins = [name for name, plugin in self.plugin_manager.plugins.items() if plugin.is_loaded]

            if loaded_plugins:
                logger.info(f"Loaded plugins: {', '.join(loaded_plugins)}")
            else:
                logger.info("No plugins loaded")

        except Exception as e:
            logger.error(f"Error loading plugins: {e!s}", exc_info=True)

    async def unload_plugins(self) -> None:
        """Unload all plugins."""
        self.plugin_manager.unload_all_plugins()
        logger.info("All plugins unloaded")

    def get_plugin(self, plugin_name: str) -> dict[str, Any] | None:
        """Get information about a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin information dictionary, or None if not found
        """
        plugin = self.plugin_manager.get_plugin(plugin_name)
        return plugin.to_dict() if plugin else None

    def list_plugins(self) -> list[dict[str, Any]]:
        """Get a list of all plugins.

        Returns:
            List of plugin information dictionaries
        """
        return self.plugin_manager.list_plugins()

    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin.

        Args:
            plugin_name: Name of the plugin to enable

        Returns:
            True if the plugin was enabled, False otherwise
        """
        return self.plugin_manager.enable_plugin(plugin_name)

    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin.

        Args:
            plugin_name: Name of the plugin to disable

        Returns:
            True if the plugin was disabled, False otherwise
        """
        return self.plugin_manager.disable_plugin(plugin_name)

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin.

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            True if the plugin was reloaded successfully, False otherwise
        """
        if not self.plugin_manager.unload_plugin(plugin_name):
            return False

        return self.plugin_manager.load_plugin(plugin_name)

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        """Emit an event to all loaded plugins.

        Args:
            event_name: Name of the event to emit
            *args: Positional arguments to pass to event handlers
            **kwargs: Keyword arguments to pass to event handlers
        """
        self.plugin_manager.emit_event(event_name, *args, **kwargs)

    async def shutdown(self) -> None:
        """Clean up resources used by the plugin handler."""
        # Unload all plugins
        await self.unload_plugins()

        # Clear plugin directories
        self._plugin_dirs.clear()

        self._initialized = False
        logger.info("Plugin handler shutdown complete")
