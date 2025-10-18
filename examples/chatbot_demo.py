"""
Avatar Chatbot Demo

This script demonstrates how to use the avatar's voice and chatbot capabilities.
It creates an interactive session where the avatar can listen, speak, and respond to voice commands.
"""
import asyncio
import logging
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.avatarmcp.core.app import AvatarMCPApp
from src.avatarmcp.ai.voice_controller import VoiceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Initialize the MCP application
    app = AvatarMCPApp()
    
    try:
        # Start the MCP server
        await app.initialize()
        
        # Get the MCP tools
        mcp_tools = app.mcp_server.tools
        
        # Configure voice settings
        voice_config = VoiceConfig(
            rate=180,  # Slightly faster speech
            volume=0.9,
            listen_timeout=5,
            phrase_time_limit=10
        )
        
        # Enable voice
        voice_result = await mcp_tools.enable_voice(voice_config)
        if voice_result["status"] != "success":
            logger.error(f"Failed to enable voice: {voice_result}")
            return
            
        # Enable chatbot
        chatbot_result = await mcp_tools.enable_chatbot()
        if chatbot_result["status"] != "success":
            logger.error(f"Failed to enable chatbot: {chatbot_result}")
            return
        
        # Greet the user
        await mcp_tools.speak({"text": "Hello! I'm your virtual avatar assistant. How can I help you today?"})
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception:
        logger.exception("An error occurred:")
    finally:
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
