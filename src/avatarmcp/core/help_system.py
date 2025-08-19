"""
Help System for AvatarMCP

This module provides a comprehensive help system for MCP tools with multi-level
documentation, command registration, and decorator-based help text.
"""

from typing import Dict, List, Optional, Callable, Any, TypeVar, Type, Union
from dataclasses import dataclass, field
from functools import wraps
import inspect
import textwrap

from fastmcp import FastMCP

# Type variable for generic function type
F = TypeVar('F', bound=Callable[..., Any])

@dataclass
class ParameterInfo:
    """Information about a command parameter."""
    name: str
    type: Type
    default: Any = inspect.Parameter.empty
    description: str = ""
    required: bool = True

@dataclass
class CommandInfo:
    """Metadata for an MCP command."""
    name: str
    function: Callable
    description: str = ""
    parameters: Dict[str, ParameterInfo] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    returns: str = ""
    requires_auth: bool = False
    deprecated: bool = False
    
    def get_signature(self) -> str:
        """Generate a signature string for the command."""
        params = []
        for name, param in self.parameters.items():
            if param.default is inspect.Parameter.empty:
                params.append(f"{name}: {param.type.__name__}")
            else:
                default = repr(param.default)
                params.append(f"{name}: {param.type.__name__} = {default}")
        
        return f"{self.name}({', '.join(params)}) -> {self.returns or 'dict'}"
    
    def format_help(self, detailed: bool = False) -> str:
        """Format the help text for this command."""
        lines = [
            f"Command: {self.name}",
            "-" * (len(self.name) + 9),
            self.description,
            "",
            f"Signature: {self.get_signature()}",
            ""
        ]
        
        if self.parameters:
            lines.append("Parameters:")
            for param in self.parameters.values():
                req = "" if param.required else "(optional) "
                default = f" (default: {param.default!r})" if param.default is not inspect.Parameter.empty else ""
                lines.append(f"  {param.name}: {param.type.__name__}{default}")
                if param.description:
                    desc = textwrap.fill(
                        param.description,
                        width=80,
                        initial_indent="    ",
                        subsequent_indent="    "
                    )
                    lines.append(desc)
            lines.append("")
        
        if self.returns:
            lines.extend(["Returns:", f"  {self.returns}", ""])
        
        if self.examples:
            lines.append("Examples:")
            for example in self.examples:
                lines.append(f"  {example}")
            lines.append("")
        
        if self.deprecated:
            lines.append("⚠️  This command is deprecated and may be removed in a future version.")
        
        if self.requires_auth:
            lines.append("🔒  This command requires authentication.")
        
        return "\n".join(lines)

class HelpSystem:
    """Central registry for command documentation and help generation."""
    
    def __init__(self):
        self._commands: Dict[str, CommandInfo] = {}
    
    def register(self, 
                name: Optional[str] = None,
                description: str = "",
                requires_auth: bool = False,
                deprecated: bool = False) -> Callable[[F], F]:
        """Decorator to register a command with help documentation.
        
        Args:
            name: Command name (defaults to function name)
            description: Description of what the command does
            requires_auth: Whether this command requires authentication
            deprecated: Whether this command is deprecated
            
        Returns:
            Decorator function
        """
        def decorator(func: F) -> F:
            cmd_name = name or func.__name__
            
            # Parse function signature
            sig = inspect.signature(func)
            parameters = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                # Get type hints
                param_type = param.annotation
                if param_type is inspect.Parameter.empty:
                    param_type = Any
                
                # Get description from docstring
                doc = inspect.getdoc(func) or ""
                param_doc = ""
                
                # Simple docstring parsing (can be enhanced with a proper parser if needed)
                for line in doc.split('\n'):
                    line = line.strip()
                    if line.startswith(f"{param_name}:"):
                        param_doc = line[len(param_name)+1:].strip()
                        break
                
                parameters[param_name] = ParameterInfo(
                    name=param_name,
                    type=param_type,
                    default=param.default,
                    description=param_doc,
                    required=param.default is param.empty
                )
            
            # Get return type from docstring
            returns = ""
            doc = inspect.getdoc(func) or ""
            if "Returns:" in doc:
                returns = doc.split("Returns:", 1)[1].split("\n", 1)[0].strip()
            
            # Create command info
            cmd_info = CommandInfo(
                name=cmd_name,
                function=func,
                description=description or doc.split('\n')[0] if doc else "",
                parameters=parameters,
                returns=returns,
                requires_auth=requires_auth,
                deprecated=deprecated
            )
            
            # Register the command
            self._commands[cmd_name] = cmd_info
            
            # Preserve the original function
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
                
            # Attach command info to the function
            wrapper._command_info = cmd_info
            
            return wrapper
            
        return decorator
    
    def get_command_info(self, name: str) -> Optional[CommandInfo]:
        """Get command info by name."""
        return self._commands.get(name)
    
    def list_commands(self) -> List[str]:
        """List all registered command names."""
        return sorted(self._commands.keys())
    
    def format_command_help(self, name: str) -> Optional[str]:
        """Get formatted help for a specific command."""
        if name not in self._commands:
            return None
        return self._commands[name].format_help(detailed=True)
    
    def format_general_help(self) -> str:
        """Get general help with a list of all commands."""
        lines = [
            "AvatarMCP - Available Commands",
            "=" * 40,
            "Type 'help <command>' for detailed help on a specific command.",
            ""
        ]
        
        # Group commands by category (based on name prefix)
        categories: Dict[str, List[CommandInfo]] = {}
        
        for cmd in sorted(self._commands.values(), key=lambda c: c.name):
            # Extract category from command name (e.g., 'vrm.load' -> 'vrm')
            category = cmd.name.split('.')[0] if '.' in cmd.name else 'general'
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)
        
        # Format each category
        for category, cmds in sorted(categories.items()):
            lines.append(f"{category.upper()}:")
            for cmd in cmds:
                deprecated = "[DEPRECATED] " if cmd.deprecated else ""
                auth = " [AUTH]" if cmd.requires_auth else ""
                lines.append(f"  {deprecated}{cmd.name}{auth}: {cmd.description}")
            lines.append("")
        
        return "\n".join(lines)

# Global help system instance
help_system = HelpSystem()

def register_help(mcp: FastMCP, help_sys: HelpSystem = help_system):
    """Register help commands with the MCP server."""
    @mcp.command("help")
    def help_command(command: str = "") -> Dict[str, Any]:
        """Show help for commands.
        
        Args:
            command: Optional command name to get detailed help for
            
        Returns:
            Dict with help information
        """
        if command:
            help_text = help_sys.format_command_help(command)
            if not help_text:
                return {"status": "error", "message": f"Command '{command}' not found"}
            return {"status": "success", "help": help_text}
        
        return {"status": "success", "help": help_sys.format_general_help()}
    
    # Register help command info
    help_sys.register(
        name="help",
        description="Show help for commands",
        requires_auth=False
    )(help_command)
    
    return help_sys
