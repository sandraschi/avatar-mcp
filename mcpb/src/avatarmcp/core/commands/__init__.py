"""
Command registration for AvatarMCP server.

This module provides the CommandRegistry class which handles registration and management
of all commands available in the AvatarMCP server.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, TypeVar

# Type variable for generic function type
F = TypeVar("F", bound=Callable[..., Any])


class CommandRegistry:
    """Registry for all MCP commands in the AvatarMCP server.

    This class handles the registration, lookup, and execution of all commands
    available in the server. It provides a decorator-based API for registering
    new commands with metadata like descriptions and examples.
    """

    def __init__(self, app: Any = None):
        """Initialize the command registry.

        Args:
            app: Reference to the main AvatarMCP application instance
        """
        self.app = app
        self._commands: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str | None = None,
        description: str | None = None,
        examples: list[str] | None = None,
        hidden: bool = False,
        **kwargs: Any,
    ) -> Callable[[F], F]:
        """Decorator to register a new command.

        Args:
            name: Command name (defaults to function name if None)
            description: Help text for the command
            examples: List of example usages
            hidden: If True, command won't appear in help listings
            **kwargs: Additional metadata for the command

        Returns:
            A decorator function that registers the command

        Example:
            @registry.register(
                name="example",
                description="An example command",
                examples=["example()", "example(param='value')"],
                hidden=False
            )
            def example_command():
                return {"status": "success"}
        """

        def decorator(func: F) -> F:
            nonlocal name, description

            # Use function name if no explicit name provided
            cmd_name = name or func.__name__

            # Generate signature for help text
            sig = inspect.signature(func)

            # Store command metadata
            self._commands[cmd_name] = {
                "function": func,
                "name": cmd_name,
                "description": description or (func.__doc__ or "").strip(),
                "signature": str(sig),
                "parameters": dict(sig.parameters),
                "examples": examples or [],
                "hidden": hidden,
                **kwargs,
            }

            return func

        return decorator

    def get_command(self, name: str) -> dict[str, Any] | None:
        """Get command metadata by name.

        Args:
            name: Name of the command to look up

        Returns:
            Command metadata dictionary or None if not found
        """
        return self._commands.get(name)

    def get_command_help(self, name: str) -> dict[str, Any] | None:
        """Get help information for a command.

        Args:
            name: Name of the command

        Returns:
            Dictionary with help information or None if command not found
        """
        cmd = self.get_command(name)
        if not cmd:
            return None

        return {
            "name": cmd["name"],
            "description": cmd["description"],
            "signature": f"{cmd['name']}{cmd['signature']}",
            "examples": cmd["examples"],
            "parameters": {
                name: {
                    "type": str(param.annotation) if param.annotation != param.empty else "any",
                    "default": param.default if param.default != param.empty else None,
                    "required": param.default == param.empty
                    and param.kind == param.POSITIONAL_OR_KEYWORD,
                    "kind": str(param.kind).split(".")[-1],
                }
                for name, param in cmd["parameters"].items()
            },
        }

    def list_commands(self, include_hidden: bool = False) -> list[dict[str, Any]]:
        """Get a list of all registered commands.

        Args:
            include_hidden: If True, include hidden commands in the results

        Returns:
            List of command metadata dictionaries
        """
        return [
            {
                "name": cmd["name"],
                "description": cmd["description"].split("\n")[0] if cmd["description"] else "",
                "hidden": cmd.get("hidden", False),
            }
            for cmd in self._commands.values()
            if include_hidden or not cmd.get("hidden", False)
        ]

    async def execute(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a command by name.

        Args:
            name: Name of the command to execute
            *args: Positional arguments to pass to the command
            **kwargs: Keyword arguments to pass to the command

        Returns:
            The result of the command execution

        Raises:
            KeyError: If the command is not found
            Exception: Any exception raised by the command
        """
        cmd = self._commands.get(name)
        if not cmd:
            raise KeyError(f"Unknown command: {name}")

        func = cmd["function"]

        # Inject app instance if the function accepts it
        if "app" in inspect.signature(func).parameters:
            kwargs["app"] = self.app

        # Execute the command
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)


# Create a default registry instance
registry = CommandRegistry()

# Export the decorator for convenience
register = registry.register
