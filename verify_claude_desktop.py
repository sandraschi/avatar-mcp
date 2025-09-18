#!/usr/bin/env python3
"""
Claude Desktop Integration Verification Script

This script verifies that the AvatarMCP server is properly configured 
and working with Claude Desktop.
"""
import json
import sys
import os
import subprocess
import time
import threading
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "info": "\033[94m",      # Blue
        "success": "\033[92m",   # Green
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
        "reset": "\033[0m"       # Reset
    }
    
    prefix = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    print(f"{colors.get(status, '')}{prefix.get(status, '')} {message}{colors['reset']}")

def check_dependencies():
    """Check if required dependencies are installed."""
    print_status("Checking dependencies...", "info")
    
    try:
        import fastmcp
        print_status("FastMCP is installed", "success")
    except ImportError:
        print_status("FastMCP is not installed. Run: pip install fastmcp", "error")
        return False
    
    # Check if MCP server module exists
    mcp_server_path = Path("src/avatarmcp/mcp_server.py")
    if mcp_server_path.exists():
        print_status("MCP server module found", "success")
    else:
        print_status("MCP server module not found", "error")
        return False
    
    return True

def test_mcp_server_protocol():
    """Test the MCP server protocol compliance."""
    print_status("Testing MCP server protocol compliance...", "info")
    
    try:
        # Import the module directly to avoid package import issues
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server", "src/avatarmcp/mcp_server.py")
        mcp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_module)
        
        # Create server with captured output
        import io
        import asyncio
        
        stdout_capture = io.StringIO()
        server = mcp_module.MCPServer(output_stream=stdout_capture)
        
        # Test initialize method
        async def test_init():
            await server.handle_initialize({}, 1)
            return stdout_capture.getvalue()
        
        output = asyncio.run(test_init())
        
        # Check output format
        if "Content-Length:" in output and "\r\n\r\n" in output:
            print_status("MCP server outputs proper Content-Length headers", "success")
            
            # Check JSON validity
            json_start = output.find('\r\n\r\n') + 4
            json_data = output[json_start:]
            
            try:
                response = json.loads(json_data)
                print_status("MCP server outputs valid JSON", "success")
                
                # Check response structure
                if response.get("jsonrpc") == "2.0" and "result" in response:
                    print_status("MCP server follows JSON-RPC 2.0 protocol", "success")
                    return True
                else:
                    print_status("Invalid JSON-RPC response structure", "error")
                    return False
                    
            except json.JSONDecodeError as e:
                print_status(f"Invalid JSON output: {e}", "error")
                return False
        else:
            print_status("Missing Content-Length headers", "error")
            return False
            
    except Exception as e:
        print_status(f"MCP server test failed: {e}", "error")
        return False

def check_claude_desktop_config():
    """Check if Claude Desktop is properly configured."""
    print_status("Checking Claude Desktop configuration...", "info")
    
    # Look for Claude Desktop config file
    config_paths = [
        Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
        Path("claude_desktop_config.json"),
        Path(".") / "claude_desktop_config.json"
    ]
    
    config_found = False
    for config_path in config_paths:
        if config_path.exists():
            print_status(f"Found config at: {config_path}", "success")
            config_found = True
            
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                if "mcpServers" in config:
                    print_status("MCP servers configuration found", "success")
                    
                    # Check for avatarmcp server
                    avatarmcp_configs = [k for k in config["mcpServers"].keys() if "avatar" in k.lower()]
                    if avatarmcp_configs:
                        print_status(f"AvatarMCP server configured as: {avatarmcp_configs}", "success")
                    else:
                        print_status("No AvatarMCP server found in configuration", "warning")
                        print_status("You need to add AvatarMCP to your Claude Desktop configuration", "info")
                else:
                    print_status("No MCP servers configured", "warning")
                    
            except Exception as e:
                print_status(f"Error reading config: {e}", "error")
            
            break
    
    if not config_found:
        print_status("Claude Desktop configuration not found", "warning")
        print_status("Create ~/.config/Claude/claude_desktop_config.json (Linux/Mac) or", "info")
        print_status("%APPDATA%\\Claude\\claude_desktop_config.json (Windows)", "info")
    
    return config_found

def show_setup_instructions():
    """Show Claude Desktop setup instructions."""
    print_status("Claude Desktop Setup Instructions", "info")
    print("\nTo configure AvatarMCP with Claude Desktop, add this to your claude_desktop_config.json:")
    print("\n" + "="*60)
    
    config_example = {
        "mcpServers": {
            "avatarmcp": {
                "command": "python",
                "args": ["src/avatarmcp/mcp_main.py"],
                "cwd": str(Path.cwd()),
                "env": {
                    "PYTHONPATH": str(Path.cwd() / "src"),
                    "PYTHONUNBUFFERED": "1"
                }
            }
        }
    }
    
    print(json.dumps(config_example, indent=2))
    print("="*60)
    
    print("\nSteps:")
    print("1. Close Claude Desktop if it's running")
    print("2. Edit your claude_desktop_config.json file")
    print("3. Add the configuration above (merge with existing config)")
    print("4. Restart Claude Desktop")
    print("5. Look for 'AvatarMCP' in the available tools")

def main():
    """Main verification function."""
    print_status("AvatarMCP Claude Desktop Integration Verification", "info")
    print("="*60)
    
    all_checks_passed = True
    
    # Check dependencies
    if not check_dependencies():
        all_checks_passed = False
    
    print()
    
    # Test MCP server protocol
    if not test_mcp_server_protocol():
        all_checks_passed = False
    
    print()
    
    # Check Claude Desktop configuration
    check_claude_desktop_config()
    
    print()
    
    if all_checks_passed:
        print_status("All technical checks passed! ✨", "success")
        print_status("Your AvatarMCP server should work with Claude Desktop", "success")
    else:
        print_status("Some issues were found", "error")
        print_status("Please fix the issues above before using with Claude Desktop", "warning")
    
    print()
    show_setup_instructions()

if __name__ == "__main__":
    main()
