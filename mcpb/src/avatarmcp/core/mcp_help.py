"""
FastMCP 2.10+ compatible help system.

Provides decorator-based help documentation for MCP commands.
"""

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, TypeVar

# Type variable for generic function type
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class CommandDoc:
    """Documentation for an MCP command."""

    name: str
    description: str = ""
    parameters: dict[str, str] = field(default_factory=dict)
    returns: str = ""
    examples: list[str] = field(default_factory=list)
    deprecated: bool = False
    requires_auth: bool = False


class MCPHelpSystem:
    """FastMCP 2.10+ compatible help system."""

    def __init__(self):
        self._commands: dict[str, CommandDoc] = {}

    def command(
        self,
        name: str | None = None,
        description: str = "",
        deprecated: bool = False,
        requires_auth: bool = False,
    ) -> Callable[[F], F]:
        """Decorator to document an MCP command.

        Args:
            name: Command name (defaults to function name)
            description: Description of the command
            deprecated: Whether the command is deprecated
            requires_auth: Whether the command requires authentication

        Returns:
            Decorator function
        """

        def decorator(func: F) -> F:
            cmd_name = name or func.__name__

            # Parse docstring for parameter and return info
            doc = inspect.getdoc(func) or ""
            doc_lines = [line.strip() for line in doc.split("\n")]

            # Extract description if not provided
            cmd_description = description
            if not cmd_description and doc_lines:
                cmd_description = doc_lines[0]

            # Parse parameters
            parameters = {}
            in_params = False
            in_returns = False

            for line in doc_lines[1:]:
                if not line:
                    continue

                if line.lower().startswith("args:"):
                    in_params = True
                    in_returns = False
                    continue

                if line.lower().startswith("returns:"):
                    in_params = False
                    in_returns = True
                    continue

                if in_params and ":" in line:
                    param, desc = line.split(":", 1)
                    parameters[param.strip()] = desc.strip()

                if in_returns and not line.startswith("    "):
                    returns = line.strip()

            # Create command documentation
            cmd_doc = CommandDoc(
                name=cmd_name,
                description=cmd_description,
                parameters=parameters,
                returns=returns if "returns" in locals() else "",
                deprecated=deprecated,
                requires_auth=requires_auth,
            )

            # Register the command
            self._commands[cmd_name] = cmd_doc

            # Preserve the original function
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # Store command doc as an attribute
            wrapper._mcp_doc = cmd_doc

            return wrapper

        return decorator

    def get_command_doc(self, name: str) -> CommandDoc | None:
        """Get documentation for a command."""
        return self._commands.get(name)

    def get_help_text(self, command_name: str | None = None) -> str:
        """Get help text for a command or general help."""
        if command_name:
            return self._format_command_help(command_name)
        return self._format_general_help()

    def _format_command_help(self, command_name: str) -> str:
        """Format help for a specific command."""
        cmd = self._commands.get(command_name)
        if not cmd:
            return f"Command '{command_name}' not found. Type 'help' for a list of commands."

        lines = [f"Command: {cmd.name}", "=" * (len(cmd.name) + 9), cmd.description, ""]

        # Add parameters
        if cmd.parameters:
            lines.append("Parameters:")
            for param, desc in cmd.parameters.items():
                lines.append(f"  {param}: {desc}")
            lines.append("")

        # Add return value
        if cmd.returns:
            lines.extend(["Returns:", f"  {cmd.returns}", ""])

        # Add examples
        if cmd.examples:
            lines.append("Examples:")
            for example in cmd.examples:
                lines.append(f"  {example}")
            lines.append("")

        # Add metadata
        if cmd.deprecated:
            lines.append("⚠️  This command is deprecated.")
        if cmd.requires_auth:
            lines.append("🔒  This command requires authentication.")

        return "\n".join(lines)

    def _format_general_help(self) -> str:
        """Format general help text."""
        lines = [
            "AvatarMCP - Available Commands",
            "=" * 40,
            "Type 'help <command>' for detailed help on a specific command.",
            "",
        ]

        # Group commands by category (first part of name)
        categories: dict[str, list[CommandDoc]] = {}

        for cmd in self._commands.values():
            category = cmd.name.split(".")[0] if "." in cmd.name else "general"
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)

        # Format each category
        for category, cmds in sorted(categories.items()):
            lines.append(f"{category.upper()}:")
            for cmd in sorted(cmds, key=lambda c: c.name):
                deprecated = "[DEPRECATED] " if cmd.deprecated else ""
                auth = " [AUTH]" if cmd.requires_auth else ""
                lines.append(f"  {deprecated}{cmd.name}{auth}: {cmd.description}")
            lines.append("")

        return "\n".join(lines)


# Global instance
mcp_help = MCPHelpSystem()


def register_help_command(mcp_instance):
    """Register the help command with an MCP instance."""

    @mcp_instance.tool()
    @mcp_help.command(name="help", description="Show help for commands", examples=["help()", "help('load_vrm')"])
    def help_command(command: str = "") -> dict[str, Any]:
        """Show help for commands.

        Args:
            command: Optional command name to get detailed help for

        Returns:
            Dict with help information:
            - status: 'success' or 'error'
            - help: Formatted help text
            - command: The command help was requested for (if any)
        """
        try:
            return {
                "status": "success",
                "help": mcp_help.get_help_text(command if command else None),
                "command": command if command else None,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get help: {e!s}",
                "command": command if command else None,
            }

    # Also register as a direct MCP command for convenience
    @mcp_instance.command("help")
    def help_command_cli(command: str = "") -> str:
        """CLI version of help command that returns plain text."""
        result = help_command(command)
        if result["status"] == "success":
            return result["help"]
        return f"Error: {result.get('error', 'Unknown error')}"

    return mcp_help
