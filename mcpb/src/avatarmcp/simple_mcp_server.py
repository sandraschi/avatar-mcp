#!/usr/bin/env python3
"""
Minimal MCP server for testing - avoids complex imports that cause Windows issues.
"""

import json
import logging
import sys

# Set up basic logging to stderr only
logging.basicConfig(
    level=logging.INFO, stream=sys.stderr, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run minimal MCP server."""
    logger.info("Starting minimal AvatarMCP server")

    # Pre-defined tools response (hardcoded to avoid import issues)
    tools = [
        {
            "name": "avatar_list",
            "description": "List available avatars",
            "inputSchema": {"type": "object", "additionalProperties": True},
        },
        {
            "name": "avatar_load",
            "description": "Load an avatar",
            "inputSchema": {"type": "object", "additionalProperties": True},
        },
        {
            "name": "animation_play",
            "description": "Play animation on avatar",
            "inputSchema": {"type": "object", "additionalProperties": True},
        },
    ]

    try:
        while True:
            # Read line from stdin
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                method = request.get("method")
                req_id = request.get("id")

                logger.info(f"Received {method} request")

                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {"listChanged": True}},
                            "serverInfo": {"name": "avatarmcp", "version": "1.0.0"},
                        },
                    }
                    print(json.dumps(response), flush=True)

                elif method == "tools/list":
                    response = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}
                    print(json.dumps(response), flush=True)

                elif method == "tools/call":
                    # Simple echo response for testing
                    tool_name = request.get("params", {}).get("name", "unknown")
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "message": f"Tool {tool_name} called successfully",
                            "status": "ok",
                        },
                    }
                    print(json.dumps(response), flush=True)

                elif method == "prompts/list":
                    response = {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}
                    print(json.dumps(response), flush=True)

                elif method == "resources/list":
                    response = {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}
                    print(json.dumps(response), flush=True)

                else:
                    # Unknown method
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Method {method} not found"},
                    }
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                continue
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)},
                }
                print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
        logger.info("Server shutting down")
    except Exception as e:
        logger.error(f"Fatal error in server: {e}")
        sys.stderr.write(f"Fatal error: {e}\n")
        sys.stderr.flush()


if __name__ == "__main__":
    main()
