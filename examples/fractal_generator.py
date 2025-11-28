#!/usr/bin/env python3
"""
Beautiful Fractal Generator Example

This script demonstrates how to generate beautiful fractals with various
color palettes and configurations.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from avatarmcp.fractals import (
    FractalGenerator,
    FractalConfig,
    get_interesting_locations,
    get_interesting_julia_params
)

try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Install it for visualization:")
    print("  pip install matplotlib")

import numpy as np
import argparse


def save_fractal(image: np.ndarray, filename: str):
    """Save fractal image to file"""
    if not MATPLOTLIB_AVAILABLE:
        # Save as raw numpy array
        np.save(filename.replace('.png', '.npy'), image)
        print(f"Saved as numpy array: {filename.replace('.png', '.npy')}")
        return

    plt.figure(figsize=(19.20, 10.80), dpi=100)
    plt.imshow(image, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(filename, dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Saved: {filename}")


def display_fractal(image: np.ndarray, title: str = "Fractal"):
    """Display fractal image"""
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib not available for display")
        return

    plt.figure(figsize=(12, 8))
    plt.imshow(image, interpolation='bilinear')
    plt.title(title, fontsize=16, color='white', backgroundcolor='black')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def generate_gallery():
    """Generate a gallery of fractals with different color schemes"""
    print("Generating fractal gallery...")

    palettes = ["cosmic", "fire", "ocean", "rainbow", "psychedelic", "sunset", "monochrome"]
    config = FractalConfig(
        width=1920,
        height=1080,
        max_iterations=256,
        zoom=1.0,
        center_x=-0.5,
        center_y=0.0
    )

    os.makedirs("fractal_gallery", exist_ok=True)

    for palette in palettes:
        print(f"Generating {palette} Mandelbrot...")
        config.color_scheme = palette
        generator = FractalGenerator(config)
        image = generator.generate_mandelbrot()
        save_fractal(image, f"fractal_gallery/mandelbrot_{palette}.png")


def generate_julia_gallery():
    """Generate a gallery of Julia sets with different parameters"""
    print("Generating Julia set gallery...")

    julia_params = get_interesting_julia_params()
    config = FractalConfig(
        width=1920,
        height=1080,
        max_iterations=256,
        zoom=1.0,
        color_scheme="cosmic"
    )

    os.makedirs("fractal_gallery", exist_ok=True)

    for name, c in julia_params.items():
        print(f"Generating Julia set: {name}")
        generator = FractalGenerator(config)
        image = generator.generate_julia(c)
        save_fractal(image, f"fractal_gallery/julia_{name}.png")


def explore_mandelbrot():
    """Explore interesting locations in the Mandelbrot set"""
    print("Exploring interesting Mandelbrot locations...")

    locations = get_interesting_locations()
    config = FractalConfig(
        width=1920,
        height=1080,
        max_iterations=512,
        zoom=100.0,
        color_scheme="psychedelic"
    )

    os.makedirs("fractal_gallery", exist_ok=True)

    for name, (x, y) in locations.items():
        print(f"Generating {name} at ({x}, {y})...")
        config.center_x = x
        config.center_y = y
        generator = FractalGenerator(config)
        image = generator.generate_mandelbrot()
        save_fractal(image, f"fractal_gallery/mandelbrot_{name}.png")


def generate_zoom_animation():
    """Generate a zoom animation into the Mandelbrot set"""
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib required for animation")
        return

    print("Generating zoom animation...")
    config = FractalConfig(
        width=1280,
        height=720,
        max_iterations=256,
        zoom=1.0,
        center_x=-0.5,
        center_y=0.0,
        color_scheme="cosmic"
    )

    generator = FractalGenerator(config)

    # Zoom into an interesting location
    target_x, target_y = get_interesting_locations()["elephant_valley"]
    frames = generator.generate_zoom_sequence(
        fractal_type="mandelbrot",
        target_x=target_x,
        target_y=target_y,
        num_frames=120,
        zoom_factor=1.05
    )

    # Create animation
    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    ax.axis('off')

    im = ax.imshow(frames[0], interpolation='bilinear')

    def update(frame):
        im.set_array(frames[frame])
        return [im]

    anim = FuncAnimation(fig, update, frames=len(frames), interval=50, blit=True)

    os.makedirs("fractal_gallery", exist_ok=True)
    writer = PillowWriter(fps=20)
    anim.save('fractal_gallery/mandelbrot_zoom.gif', writer=writer)
    print("Saved: fractal_gallery/mandelbrot_zoom.gif")
    plt.close()


def generate_all_fractals():
    """Generate one example of each fractal type"""
    print("Generating all fractal types...")

    config = FractalConfig(
        width=1920,
        height=1080,
        max_iterations=256,
        zoom=1.0,
        color_scheme="cosmic"
    )

    os.makedirs("fractal_gallery", exist_ok=True)

    generator = FractalGenerator(config)

    # Mandelbrot
    print("Generating Mandelbrot set...")
    image = generator.generate_mandelbrot()
    save_fractal(image, "fractal_gallery/mandelbrot.png")

    # Julia
    print("Generating Julia set...")
    image = generator.generate_julia(complex(-0.7, 0.27015))
    save_fractal(image, "fractal_gallery/julia.png")

    # Burning Ship
    print("Generating Burning Ship...")
    config.center_x = -0.5
    config.center_y = -0.5
    generator = FractalGenerator(config)
    image = generator.generate_burning_ship()
    save_fractal(image, "fractal_gallery/burning_ship.png")

    # Tricorn
    print("Generating Tricorn...")
    config.center_x = 0.0
    config.center_y = 0.0
    generator = FractalGenerator(config)
    image = generator.generate_tricorn()
    save_fractal(image, "fractal_gallery/tricorn.png")


def interactive_mode():
    """Interactive fractal explorer"""
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib required for interactive mode")
        return

    print("\n=== Interactive Fractal Explorer ===")
    print("Click on the fractal to zoom in!")
    print("Press 'r' to reset, 'q' to quit")

    config = FractalConfig(
        width=1280,
        height=720,
        max_iterations=256,
        zoom=1.0,
        center_x=-0.5,
        center_y=0.0,
        color_scheme="cosmic"
    )

    generator = FractalGenerator(config)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    image = generator.generate_mandelbrot()
    im = ax.imshow(image, interpolation='bilinear', extent=[-2, 2, -2, 2])

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            config.center_x = event.xdata
            config.center_y = event.ydata
            config.zoom *= 2.0
            print(f"Zooming to ({config.center_x:.4f}, {config.center_y:.4f}), zoom={config.zoom:.2f}")
            image = generator.generate_mandelbrot()
            im.set_array(image)
            fig.canvas.draw()

    def onkey(event):
        if event.key == 'r':
            config.zoom = 1.0
            config.center_x = -0.5
            config.center_y = 0.0
            print("Reset view")
            image = generator.generate_mandelbrot()
            im.set_array(image)
            fig.canvas.draw()
        elif event.key == 'q':
            plt.close()

    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('key_press_event', onkey)

    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Beautiful Fractal Generator")
    parser.add_argument(
        "mode",
        choices=["gallery", "julia", "explore", "zoom", "all", "interactive", "quick"],
        help="Generation mode"
    )
    parser.add_argument(
        "--palette",
        default="cosmic",
        choices=["cosmic", "fire", "ocean", "rainbow", "psychedelic", "sunset", "monochrome"],
        help="Color palette"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Image width"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Image height"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=256,
        help="Maximum iterations"
    )

    args = parser.parse_args()

    if args.mode == "gallery":
        generate_gallery()
    elif args.mode == "julia":
        generate_julia_gallery()
    elif args.mode == "explore":
        explore_mandelbrot()
    elif args.mode == "zoom":
        generate_zoom_animation()
    elif args.mode == "all":
        generate_all_fractals()
    elif args.mode == "interactive":
        interactive_mode()
    elif args.mode == "quick":
        # Quick mode: generate a single beautiful fractal
        config = FractalConfig(
            width=args.width,
            height=args.height,
            max_iterations=args.iterations,
            zoom=1.0,
            center_x=-0.5,
            center_y=0.0,
            color_scheme=args.palette
        )
        generator = FractalGenerator(config)
        image = generator.generate_mandelbrot()

        if MATPLOTLIB_AVAILABLE:
            display_fractal(image, f"Mandelbrot Set - {args.palette}")

        os.makedirs("fractal_gallery", exist_ok=True)
        save_fractal(image, f"fractal_gallery/fractal_{args.palette}.png")

    print("\nDone! Check the 'fractal_gallery' directory for output.")


if __name__ == "__main__":
    main()
