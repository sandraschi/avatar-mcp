"""
Settings handler for the Avatar MCP server.

This module provides a centralized configuration management system for the
Avatar MCP server, handling loading, saving, and validating configuration
settings from various sources.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar, Union

import yaml

from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SettingsError(Exception):
    """Base exception for settings-related errors."""

    pass


class SettingsValidationError(SettingsError):
    """Raised when settings validation fails."""

    pass


class SettingsSection:
    """Base class for settings sections."""

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to a dictionary."""
        if is_dataclass(self):
            return asdict(self)
        return {
            k: getattr(self, k)
            for k in dir(self)
            if not k.startswith("_") and not callable(getattr(self, k))
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SettingsSection":
        """Create settings from a dictionary."""
        if is_dataclass(cls):
            field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
            validated_data = {}

            for key, value in data.items():
                if key in field_types:
                    field_type = field_types[key]
                    validated_data[key] = _convert_value(value, field_type)

            return cls(**validated_data)
        else:
            instance = cls()
            for key, value in data.items():
                if hasattr(instance, key) and not key.startswith("_"):
                    setattr(instance, key, value)
            return instance

    def validate(self) -> None:
        """Validate the settings.

        Subclasses should override this method to implement custom validation.
        """
        pass


@dataclass
class ServerSettings(SettingsSection):
    """Server-related settings."""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    log_file: str | None = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    api_keys: list[str] = field(default_factory=list)


@dataclass
class DatabaseSettings(SettingsSection):
    """Database-related settings."""

    url: str = "sqlite:///./avatarmcp.db"
    echo: bool = False
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class OSCSettings(SettingsSection):
    """OSC-related settings."""

    enabled: bool = True
    server_ip: str = "127.0.0.1"
    server_port: int = 9001
    client_ip: str = "127.0.0.1"
    client_port: int = 9000


@dataclass
class WebUISettings(SettingsSection):
    """Web UI-related settings."""

    enabled: bool = True
    theme: str = "dark"
    language: str = "en"
    show_debug_info: bool = False


@dataclass
class PathsSettings(SettingsSection):
    """Path-related settings."""

    avatars: str = "data/avatars"
    animations: str = "data/animations"
    plugins: str = "data/plugins"
    cache: str = "data/cache"
    logs: str = "logs"
    config: str = "config"


class SettingsHandler(BaseHandler):
    """Handles loading, saving, and validating application settings."""

    def __init__(self, server: Any = None):
        """Initialize the settings handler.

        Args:
            server: Reference to the main server instance
        """
        super().__init__(server)
        self._settings: dict[str, SettingsSection] = {}
        self._default_settings: dict[str, type[SettingsSection]] = {
            "server": ServerSettings,
            "database": DatabaseSettings,
            "osc": OSCSettings,
            "webui": WebUISettings,
            "paths": PathsSettings,
        }
        self._config_dir: Path | None = None
        self._config_file: Path | None = None

    async def _initialize(self) -> None:
        """Initialize the settings handler and load settings."""
        # Initialize default settings
        self._initialize_default_settings()

        # Set up configuration paths
        self._setup_paths()

        # Load settings from file if it exists, otherwise create it
        if self._config_file and self._config_file.exists():
            await self.load_settings()
        else:
            await self.save_settings()

        # Create necessary directories
        self._create_directories()

        logger.info("Settings handler initialized")

    def _initialize_default_settings(self) -> None:
        """Initialize all settings sections with their default values."""
        self._settings = {
            name: section_class() for name, section_class in self._default_settings.items()
        }

    def _setup_paths(self) -> None:
        """Set up configuration paths."""
        # Use the 'config' directory in the current working directory by default
        self._config_dir = Path(os.getcwd()) / "config"
        self._config_file = self._config_dir / "config.yaml"

        # If we have a server reference, check for config in the server's config dir
        if hasattr(self.server, "config") and "config_dir" in self.server.config:
            self._config_dir = Path(self.server.config["config_dir"])
            self._config_file = self._config_dir / "config.yaml"

        # Ensure config directory exists
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def _create_directories(self) -> None:
        """Create necessary directories defined in the settings."""
        paths = self.get_section("paths")
        if not paths:
            return

        for path_name in ["avatars", "animations", "plugins", "cache", "logs"]:
            path = getattr(paths, path_name, None)
            if path:
                try:
                    path_obj = Path(path)
                    if not path_obj.is_absolute():
                        path_obj = self._config_dir.parent / path
                    path_obj.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logger.warning(f"Failed to create directory '{path}': {str(e)}")

    async def load_settings(self, file_path: str | Path | None = None) -> None:
        """Load settings from a file.

        Args:
            file_path: Path to the settings file. If not provided, uses the default.
        """
        if file_path is None:
            if not self._config_file:
                raise SettingsError("No configuration file path specified")
            file_path = self._config_file

        file_path = Path(file_path)

        if not file_path.exists():
            logger.warning(f"Settings file not found: {file_path}")
            return

        try:
            with open(file_path, encoding="utf-8") as f:
                if file_path.suffix.lower() in (".yaml", ".yml"):
                    data = yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    raise SettingsError(f"Unsupported file format: {file_path.suffix}")

            # Update settings from the loaded data
            for section_name, section_data in data.items():
                if section_name in self._settings and isinstance(section_data, dict):
                    section = self._settings[section_name]
                    updated_section = type(section).from_dict(section_data)
                    self._settings[section_name] = updated_section

            # Validate all settings
            self.validate()

            logger.info(f"Settings loaded from {file_path}")

        except Exception as e:
            logger.error(f"Error loading settings from {file_path}: {str(e)}", exc_info=True)
            raise SettingsError(f"Failed to load settings: {str(e)}") from e

    async def save_settings(self, file_path: str | Path | None = None) -> None:
        """Save settings to a file.

        Args:
            file_path: Path to save the settings file. If not provided, uses the default.
        """
        if file_path is None:
            if not self._config_file:
                raise SettingsError("No configuration file path specified")
            file_path = self._config_file

        file_path = Path(file_path)

        try:
            # Validate before saving
            self.validate()

            # Convert settings to a dictionary
            data = {
                section_name: section.to_dict() for section_name, section in self._settings.items()
            }

            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to file
            with open(file_path, "w", encoding="utf-8") as f:
                if file_path.suffix.lower() in (".yaml", ".yml"):
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                elif file_path.suffix.lower() == ".json":
                    json.dump(data, f, indent=2)
                else:
                    raise SettingsError(f"Unsupported file format: {file_path.suffix}")

            logger.info(f"Settings saved to {file_path}")

        except Exception as e:
            logger.error(f"Error saving settings to {file_path}: {str(e)}", exc_info=True)
            raise SettingsError(f"Failed to save settings: {str(e)}") from e

    def validate(self) -> None:
        """Validate all settings."""
        errors = []

        for section_name, section in self._settings.items():
            try:
                if hasattr(section, "validate"):
                    section.validate()
            except Exception as e:
                errors.append(f"{section_name}: {str(e)}")

        if errors:
            error_message = "\n- ".join(["Validation failed:"] + errors)
            logger.error(error_message)
            raise SettingsValidationError(error_message)

    def get_section(self, section_name: str) -> SettingsSection | None:
        """Get a settings section by name.

        Args:
            section_name: Name of the settings section

        Returns:
            The settings section, or None if not found
        """
        return self._settings.get(section_name)

    def get(self, section_name: str, key: str, default: Any = None) -> Any:
        """Get a setting value by section and key.

        Args:
            section_name: Name of the settings section
            key: Setting key
            default: Default value if the setting is not found

        Returns:
            The setting value, or the default if not found
        """
        section = self.get_section(section_name)
        if section and hasattr(section, key):
            return getattr(section, key)
        return default

    def set(self, section_name: str, key: str, value: Any) -> None:
        """Set a setting value.

        Args:
            section_name: Name of the settings section
            key: Setting key
            value: New value for the setting
        """
        section = self.get_section(section_name)
        if section and hasattr(section, key):
            setattr(section, key, value)
        else:
            logger.warning(f"Setting not found: {section_name}.{key}")

    def get_all_settings(self) -> dict[str, dict[str, Any]]:
        """Get all settings as a nested dictionary."""
        return {section_name: section.to_dict() for section_name, section in self._settings.items()}

    def update_from_dict(self, updates: dict[str, dict[str, Any]]) -> None:
        """Update settings from a nested dictionary.

        Args:
            updates: Nested dictionary of section names to setting updates
        """
        for section_name, section_updates in updates.items():
            if section_name in self._settings and isinstance(section_updates, dict):
                section = self._settings[section_name]
                for key, value in section_updates.items():
                    if hasattr(section, key):
                        setattr(section, key, value)

    def reset_to_defaults(self) -> None:
        """Reset all settings to their default values."""
        self._initialize_default_settings()

    def create_backup(self, backup_dir: str | Path | None = None) -> Path:
        """Create a backup of the current settings.

        Args:
            backup_dir: Directory to save the backup. If not provided, uses the config directory.

        Returns:
            Path to the backup file
        """
        if backup_dir is None:
            if not self._config_dir:
                raise SettingsError("No configuration directory specified")
            backup_dir = self._config_dir / "backups"

        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"config_backup_{timestamp}.yaml"

        # Save current settings to the backup file
        data = self.get_all_settings()

        with open(backup_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        return backup_file

    def restore_from_backup(self, backup_file: str | Path) -> None:
        """Restore settings from a backup file.

        Args:
            backup_file: Path to the backup file
        """
        backup_file = Path(backup_file)

        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        # Create a backup of current settings before restoring
        try:
            self.create_backup()
        except Exception as e:
            logger.warning(f"Failed to create backup before restore: {str(e)}")

        # Load settings from backup
        with open(backup_file, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Update settings from the backup
        for section_name, section_data in data.items():
            if section_name in self._settings and isinstance(section_data, dict):
                section = self._settings[section_name]
                updated_section = type(section).from_dict(section_data)
                self._settings[section_name] = updated_section

        # Save the restored settings
        if self._config_file:
            self.save_settings(self._config_file)

    async def shutdown(self) -> None:
        """Clean up resources used by the handler."""
        # Save settings on shutdown
        if self._config_file:
            try:
                await self.save_settings()
            except Exception as e:
                logger.error(f"Error saving settings on shutdown: {str(e)}")

        logger.info("Settings handler shutdown complete")


def _convert_value(value: Any, target_type: type[T]) -> T:
    """Convert a value to the specified type."""
    if value is None or isinstance(value, target_type):
        return value

    # Handle Optional types
    if hasattr(target_type, "__origin__") and target_type.__origin__ is Union:
        if type(None) in target_type.__args__:
            # This is an Optional[SomeType]
            non_none_types = [t for t in target_type.__args__ if t is not type(None)]
            if non_none_types:
                return _convert_value(value, non_none_types[0])

    # Handle List types
    if hasattr(target_type, "__origin__") and target_type.__origin__ is list:
        if not isinstance(value, list):
            value = [value]
        item_type = target_type.__args__[0] if hasattr(target_type, "__args__") else str
        return [_convert_value(item, item_type) for item in value]

    # Handle Enum types
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        try:
            return target_type(value)
        except ValueError:
            return target_type[value.upper()]  # Try case-insensitive lookup

    # Standard type conversion
    try:
        if target_type is bool and isinstance(value, str):
            return value.lower() in ("true", "1", "t", "y", "yes")
        return target_type(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot convert {value!r} to {target_type.__name__}: {str(e)}") from e
