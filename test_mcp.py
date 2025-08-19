"""
Test script for FastMCP 2.10+ server
"""
import json
import subprocess
import sys
from pathlib import Path

def test_mcp_server():
    # Start the server as a subprocess
    server = subprocess.Popen(
        [sys.executable, "-m", "src.avatarmcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Test list_models command
        cmd = {
            "jsonrpc": "2.0",
            "method": "list_models",
            "params": {},
            "id": 1
        }
        
        print("Sending command:", json.dumps(cmd))
        server.stdin.write(json.dumps(cmd) + "\n")
        server.stdin.flush()
        
        # Read response
        response = server.stdout.readline()
        print("Received response:", response)
        
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    test_mcp_server()
