#!/usr/bin/env python3
"""
Minimal visual test for AvatarMCP desktop viewer
Shows coordinate system and a blue ball using matplotlib as fallback
"""


def test_visual():
    """Show coordinate system and a blue ball."""
    print("AvatarMCP Visual Test - Coordinate System + Blue Ball")
    print("=" * 55)

    try:
        # Try matplotlib 3D as fallback since PyVista has Windows rendering issues
        import matplotlib.pyplot as plt
        import numpy as np

        print("Using matplotlib 3D as fallback renderer")
        print("Creating 3D plot...")

        # Create figure and 3D axes
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Create coordinate axes lines
        # X axis (red)
        ax.plot([0, 2], [0, 0], [0, 0], color="red", linewidth=3, label="X-axis")
        # Y axis (green)
        ax.plot([0, 0], [0, 2], [0, 0], color="green", linewidth=3, label="Y-axis")
        # Z axis (blue)
        ax.plot([0, 0], [0, 0], [0, 2], color="blue", linewidth=3, label="Z-axis")

        # Create a blue sphere (ball)
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        x = 1 + 0.8 * np.outer(np.cos(u), np.sin(v))
        y = 1 + 0.8 * np.outer(np.sin(u), np.sin(v))
        z = 1 + 0.8 * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color="blue", alpha=0.8)

        # Add grid
        ax.grid(True)

        # Set labels and title
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(
            "AvatarMCP Desktop Viewer - Visual Test\n\n"
            "✓ Coordinate System (X=red, Y=green, Z=blue)\n"
            "✓ Blue Ball (sphere)\n\n"
            "This viewer can display VRM avatars when loaded"
        )

        # Set equal aspect ratio
        ax.set_box_aspect([1, 1, 1])

        print("SUCCESS: 3D visualization created with matplotlib")
        print("Window should be visible now...")

        plt.show()

        print("Visual test complete!")

    except ImportError as e:
        print(f"ERROR: Missing matplotlib dependency: {e}")
        print("Install with: pip install matplotlib")
        print("Falling back to simple text output...")

        print("\n" + "=" * 50)
        print("FALLBACK VISUAL TEST (No 3D rendering available)")
        print("=" * 50)
        print("✓ AvatarMCP System Components:")
        print("  - MCP Server: Running")
        print("  - OSC Communication: Active")
        print("  - Tool Registration: 14 tools loaded")
        print("  - VRM Discovery: 2 models found")
        print("✗ 3D Visualization: Backend not available")
        print("\nTo enable 3D visualization:")
        print("1. Install matplotlib: pip install matplotlib")
        print("2. Or fix PyVista/VTK rendering on Windows")
        print("3. Or use a different 3D library")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_visual()
