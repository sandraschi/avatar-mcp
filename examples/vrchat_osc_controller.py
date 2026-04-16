"""
VRChat OSC Controller

This script demonstrates how to control a VRChat avatar using OSC (Open Sound Control).
It provides a simple command-line interface to send OSC messages to VRChat.

Usage:
    python -m examples.vrchat_osc_controller [command] [args...]

Available Commands:
    gesture <left|right> <gesture> [strength] - Send a hand gesture
    expression <expression> [strength]        - Send a facial expression
    viseme <viseme> [strength]               - Send a viseme for lip sync
    set <parameter> <value>                  - Set a custom parameter
    get <parameter>                          - Get the current value of a parameter
    list-params                              - List all available parameters
    help                                     - Show this help message

Examples:
    python -m examples.vrchat_osc_controller gesture left Fist 1.0
    python -m examples.vrchat_osc_controller expression Happy 0.8
    python -m examples.vrchat_osc_controller set MyCustomParam 1
"""

import asyncio
import logging

# Add the parent directory to the path so we can import from src
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.avatarmcp.osc_server import VRChatOSCServer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class VRChatOSCController:
    """A simple controller for VRChat OSC parameters."""

    def __init__(self, ip: str = "127.0.0.1", receive_port: int = 9000, send_port: int = 9001):
        """Initialize the OSC controller.

        Args:
            ip: The IP address to bind the OSC server to
            receive_port: The port to receive OSC messages on
            send_port: The port to send OSC messages to
        """
        self.osc = VRChatOSCServer(ip=ip, receive_port=receive_port, send_port=send_port)
        self.running = False

        # Register parameter change handlers
        self.osc.on_parameter_change("*")(self._on_parameter_change)

    async def start(self):
        """Start the OSC server."""
        if self.running:
            return

        await self.osc.start()
        self.running = True
        logger.info("VRChat OSC Controller started")

        try:
            # Keep the server running
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.stop()

    async def stop(self):
        """Stop the OSC server."""
        if not self.running:
            return

        await self.osc.stop()
        self.running = False
        logger.info("VRChat OSC Controller stopped")

    def _on_parameter_change(self, parameter: str, value):
        """Handle parameter changes from VRChat."""
        logger.info(f"Parameter changed: {parameter} = {value}")

    async def send_gesture(self, hand: str, gesture: str, strength: float = 1.0):
        """Send a hand gesture to VRChat.

        Args:
            hand: 'left' or 'right'
            gesture: Gesture name (e.g., 'Fist', 'Open', 'Point', etc.)
            strength: Gesture strength (0.0 to 1.0)
        """
        await self.osc.send_gesture(hand, gesture, strength)
        logger.info(f"Sent gesture: {hand} hand {gesture} (strength: {strength})")

    async def send_expression(self, expression: str, strength: float = 1.0):
        """Send a facial expression to VRChat.

        Args:
            expression: Expression name (e.g., 'Happy', 'Angry', 'Blink', etc.)
            strength: Expression strength (0.0 to 1.0)
        """
        await self.osc.send_expression(expression, strength)
        logger.info(f"Sent expression: {expression} (strength: {strength})")

    async def send_viseme(self, viseme: str, strength: float = 1.0):
        """Send a viseme to VRChat for lip sync.

        Args:
            viseme: Viseme name (e.g., 'aa', 'E', 'O', etc.)
            strength: Viseme strength (0.0 to 1.0)
        """
        await self.osc.send_viseme(viseme, strength)
        logger.info(f"Sent viseme: {viseme} (strength: {strength})")

    async def set_parameter(self, parameter: str, value):
        """Set a custom parameter in VRChat.

        Args:
            parameter: Parameter name
            value: Parameter value (int, float, or bool)
        """
        self.osc.set_parameter(parameter, value)
        logger.info(f"Set parameter: {parameter} = {value}")

    def get_parameter(self, parameter: str, default=None):
        """Get the current value of a parameter.

        Args:
            parameter: Parameter name
            default: Default value if parameter is not found

        Returns:
            The current value of the parameter, or the default value if not found
        """
        return self.osc.get_parameter(parameter, default)


async def main():
    """Run the VRChat OSC Controller with command-line arguments."""
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        return

    controller = VRChatOSCController()

    # Start the controller in the background
    controller_task = asyncio.create_task(controller.start())

    try:
        # Parse command
        command = sys.argv[1].lower()
        args = sys.argv[2:]

        if command == "gesture":
            if len(args) < 2:
                print("Usage: gesture <left|right> <gesture> [strength]")
                return

            hand = args[0]
            gesture = args[1]
            strength = float(args[2]) if len(args) > 2 else 1.0
            await controller.send_gesture(hand, gesture, strength)

        elif command == "expression":
            if len(args) < 1:
                print("Usage: expression <expression> [strength]")
                return

            expression = args[0]
            strength = float(args[1]) if len(args) > 1 else 1.0
            await controller.send_expression(expression, strength)

        elif command == "viseme":
            if len(args) < 1:
                print("Usage: viseme <viseme> [strength]")
                return

            viseme = args[0]
            strength = float(args[1]) if len(args) > 1 else 1.0
            await controller.send_viseme(viseme, strength)

        elif command == "set":
            if len(args) < 2:
                print("Usage: set <parameter> <value>")
                return

            parameter = args[0]
            value = parse_value(args[1])
            await controller.set_parameter(parameter, value)

        elif command == "get":
            if len(args) < 1:
                print("Usage: get <parameter>")
                return

            parameter = args[0]
            value = controller.get_parameter(parameter, "Not set")
            print(f"{parameter} = {value}")

        elif command == "list-params":
            print("Available parameters:")
            print("- Gestures: GestureLeft, GestureRight, GestureLeftWeight, GestureRightWeight")
            print("- Expressions: Neutral, Happy, Angry, Sad, Surprised, Blink, etc.")
            print("- Visemes: Viseme, VisemeWeight")
            print("- Custom: Any parameter defined in your VRChat avatar")

        else:
            print(f"Unknown command: {command}")
            print_help()

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        # Stop the controller
        controller.running = False
        await controller.stop()
        controller_task.cancel()
        try:
            await controller_task
        except asyncio.CancelledError:
            pass


def parse_value(value_str: str):
    """Parse a string value to the appropriate type."""
    if value_str.lower() == "true":
        return True
    elif value_str.lower() == "false":
        return False
    try:
        return int(value_str)
    except ValueError:
        try:
            return float(value_str)
        except ValueError:
            return value_str


def print_help():
    """Print the help message."""
    print(__doc__)
    print("\nAvailable Gestures: Fist, Open, Point, Peace, RockNRoll, Gun, ThumbsUp")
    print("Available Expressions: Neutral, Happy, Angry, Sad, Surprised, Blink, etc.")
    print("Available Visemes: Sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, I, O, U")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
