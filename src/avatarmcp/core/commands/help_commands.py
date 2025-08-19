"""
Help system commands for AvatarMCP.
"""
from typing import Dict, Any, List, Optional


def register_commands(registry):
    """Register help system commands."""
    app = registry.app
    
    @registry.register(
        name="help",
        description="Get help about available commands.",
        examples=[
            "help()",
            "help('load_vrm')",
            "help(command_name='set_blend_shape')"
        ]
    )
    def help_command(command_name: Optional[str] = None) -> Dict[str, Any]:
        """Get help about available commands or a specific command.
        
        Args:
            command_name: Optional name of the command to get help for.
                        If not provided, lists all available commands.
            
        Returns:
            Dict with help information.
        """
        if command_name:
            # Get help for a specific command
            cmd_help = registry.get_command_help(command_name)
            if not cmd_help:
                return app.create_error_response(f"Unknown command: {command_name}")
                
            return {
                'status': 'success',
                'command': cmd_help
            }
        
        # List all commands
        commands = registry.list_commands()
        return {
            'status': 'success',
            'commands': commands,
            'message': "Use help('command_name') for detailed help about a specific command."
        }
    
    @registry.register(
        name="list_commands",
        description="List all available commands.",
        examples=["list_commands()"]
    )
    def list_commands() -> Dict[str, Any]:
        """List all available commands.
        
        Returns:
            Dict with list of commands and their descriptions.
        """
        commands = registry.list_commands()
        return {
            'status': 'success',
            'commands': commands
        }
    
    @registry.register(
        name="get_command_info",
        description="Get detailed information about a command.",
        examples=["get_command_info('load_vrn')"],
        hidden=True  # Not shown in command list
    )
    def get_command_info(command_name: str) -> Dict[str, Any]:
        """Get detailed information about a command.
        
        Args:
            command_name: Name of the command to get info for.
            
        Returns:
            Dict with detailed command information.
        """
        cmd_help = registry.get_command_help(command_name)
        if not cmd_help:
            return app.create_error_response(f"Unknown command: {command_name}")
            
        return {
            'status': 'success',
            'command': cmd_help
        }
