#!/usr/bin/env python3
"""
Simple Fractal Generator Example

A minimal example showing how to generate a beautiful fractal in just a few lines.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from avatarmcp.fractals import FractalGenerator, FractalConfig

# Configure the fractal
config = FractalConfig(
    width=1920,
    height=1080,
    max_iterations=256,
    color_scheme="cosmic"  # Try: cosmic, fire, ocean, rainbow, psychedelic, sunset
)

# Generate the fractal
generator = FractalGenerator(config)
image = generator.generate_mandelbrot()

# Save the image
try:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(19.20, 10.80), dpi=100)
    plt.imshow(image, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)

    os.makedirs("output", exist_ok=True)
    plt.savefig("output/beautiful_fractal.png", dpi=100, bbox_inches='tight', pad_inches=0)
    print("✨ Fractal saved to: output/beautiful_fractal.png")

    # Display it
    plt.show()

except ImportError:
    print("Install matplotlib to save and view the fractal:")
    print("  pip install matplotlib")
    # Save as numpy array instead
    import numpy as np
    os.makedirs("output", exist_ok=True)
    np.save("output/beautiful_fractal.npy", image)
    print("Saved as numpy array: output/beautiful_fractal.npy")
