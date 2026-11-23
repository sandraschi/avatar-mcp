# Beautiful Fractal Generator

AvatarMCP now includes a powerful, beautiful fractal generator capable of creating stunning mathematical art with support for multiple fractal types, color palettes, and animations.

## Features

- **Multiple Fractal Types**
  - Mandelbrot Set
  - Julia Sets
  - Burning Ship
  - Tricorn (Mandelbar)

- **Beautiful Color Palettes**
  - Cosmic (deep space colors)
  - Fire (warm fiery tones)
  - Ocean (cool blues and teals)
  - Rainbow (vibrant spectrum)
  - Psychedelic (vibrant multi-frequency colors)
  - Sunset (warm gradient)
  - Monochrome (classic black & white)

- **Advanced Features**
  - Smooth coloring algorithm for beautiful gradients
  - Configurable resolution and iteration counts
  - Zoom and pan capabilities
  - Preset interesting locations
  - Animation support (zoom sequences, palette morphing)
  - Interactive explorer mode

## Installation

Install the fractal visualization dependencies:

```bash
pip install -e ".[fractals]"
```

This installs matplotlib and pillow for image rendering and animation.

## Quick Start

### Simple Example

```python
from avatarmcp.fractals import FractalGenerator, FractalConfig

# Configure the fractal
config = FractalConfig(
    width=1920,
    height=1080,
    max_iterations=256,
    color_scheme="cosmic"
)

# Generate and save
generator = FractalGenerator(config)
image = generator.generate_mandelbrot()

# Save with matplotlib
import matplotlib.pyplot as plt
plt.imsave("fractal.png", image)
```

### Command-Line Usage

Generate a gallery of fractals with different color palettes:

```bash
python examples/fractal_generator.py gallery
```

Generate Julia set variations:

```bash
python examples/fractal_generator.py julia
```

Explore interesting Mandelbrot locations:

```bash
python examples/fractal_generator.py explore
```

Generate all fractal types:

```bash
python examples/fractal_generator.py all
```

Create a zoom animation:

```bash
python examples/fractal_generator.py zoom
```

Interactive explorer (click to zoom):

```bash
python examples/fractal_generator.py interactive
```

Quick single fractal:

```bash
python examples/fractal_generator.py quick --palette psychedelic --width 3840 --height 2160
```

## API Reference

### FractalConfig

Configuration for fractal generation:

```python
@dataclass
class FractalConfig:
    width: int = 1920              # Image width in pixels
    height: int = 1080             # Image height in pixels
    max_iterations: int = 256      # Maximum iterations (higher = more detail)
    zoom: float = 1.0              # Zoom level (higher = more zoomed in)
    center_x: float = 0.0          # X coordinate of center
    center_y: float = 0.0          # Y coordinate of center
    color_scheme: str = "cosmic"   # Color palette name
    smooth_coloring: bool = True   # Use smooth coloring algorithm
```

### FractalGenerator

Main fractal generation class:

```python
generator = FractalGenerator(config)

# Generate different fractal types
mandelbrot = generator.generate_mandelbrot()
julia = generator.generate_julia(c=complex(-0.7, 0.27015))
burning_ship = generator.generate_burning_ship()
tricorn = generator.generate_tricorn()

# Generate zoom sequence (for animations)
frames = generator.generate_zoom_sequence(
    fractal_type="mandelbrot",
    target_x=-0.5,
    target_y=0.0,
    num_frames=60,
    zoom_factor=1.2
)

# Generate palette morph sequence
frames = generator.generate_palette_morph(
    fractal_type="mandelbrot",
    num_frames=60,
    palettes=["cosmic", "fire", "ocean"]
)
```

### Color Palettes

Available color schemes:

```python
from avatarmcp.fractals import ColorPalette

# Get a palette function
palette_func = ColorPalette.get_palette("cosmic")
color = palette_func(0.5)  # Returns (r, g, b) tuple

# Available palettes
palettes = [
    "cosmic",      # Deep space colors
    "fire",        # Warm fiery tones
    "ocean",       # Cool blues and teals
    "rainbow",     # Vibrant spectrum
    "psychedelic", # Multi-frequency vibrant
    "sunset",      # Warm gradient
    "monochrome"   # Black and white
]
```

### Interesting Locations

Pre-defined interesting locations in the Mandelbrot set:

```python
from avatarmcp.fractals import get_interesting_locations

locations = get_interesting_locations()
# Returns dictionary:
# {
#     "seahorse_valley": (-0.75, 0.1),
#     "elephant_valley": (0.28, 0.008),
#     "triple_spiral": (-0.088, 0.654),
#     "scepter_valley": (-1.25, 0.02),
#     "mini_mandelbrot": (-0.16, 1.0405),
#     "san_marco": (-0.75, 0.0),
#     "starfish": (-0.374, -0.659),
#     "dendrite": (-0.1592, -1.0317),
# }

# Use them:
config.center_x, config.center_y = locations["elephant_valley"]
config.zoom = 100.0
```

### Julia Set Parameters

Pre-defined beautiful Julia set parameters:

```python
from avatarmcp.fractals import get_interesting_julia_params

params = get_interesting_julia_params()
# Returns dictionary:
# {
#     "dragon": complex(-0.8, 0.156),
#     "dendrite": complex(-0.7, 0.27015),
#     "rabbit": complex(-0.123, 0.745),
#     "douady": complex(-0.4, 0.6),
#     "san_marco": complex(-0.75, 0.0),
#     "spiral": complex(0.285, 0.01),
#     "nebula": complex(-0.4, -0.59),
#     "crystals": complex(0.355, 0.355),
# }

# Use them:
julia_image = generator.generate_julia(params["dragon"])
```

## Advanced Examples

### High-Resolution Fractal

```python
config = FractalConfig(
    width=3840,      # 4K resolution
    height=2160,
    max_iterations=1024,  # High detail
    zoom=100.0,
    center_x=-0.75,
    center_y=0.1,
    color_scheme="psychedelic",
    smooth_coloring=True
)

generator = FractalGenerator(config)
image = generator.generate_mandelbrot()
```

### Creating an Animation

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

config = FractalConfig(width=1280, height=720)
generator = FractalGenerator(config)

# Generate zoom sequence
frames = generator.generate_zoom_sequence(
    fractal_type="mandelbrot",
    target_x=-0.75,
    target_y=0.1,
    num_frames=120,
    zoom_factor=1.05
)

# Create animation
fig, ax = plt.subplots()
im = ax.imshow(frames[0])

def update(frame):
    im.set_array(frames[frame])
    return [im]

anim = FuncAnimation(fig, update, frames=len(frames), interval=50)
writer = PillowWriter(fps=20)
anim.save('zoom.gif', writer=writer)
```

### Exploring Different Julia Sets

```python
from avatarmcp.fractals import get_interesting_julia_params

config = FractalConfig(
    width=1920,
    height=1080,
    max_iterations=512,
    color_scheme="cosmic"
)

generator = FractalGenerator(config)
julia_params = get_interesting_julia_params()

for name, c in julia_params.items():
    image = generator.generate_julia(c)
    plt.imsave(f"julia_{name}.png", image)
```

### Custom Color Palette

```python
from avatarmcp.fractals import FractalGenerator, FractalConfig, ColorPalette

# Add your own palette
def custom_palette(t: float):
    """Your custom color function"""
    r = t ** 2
    g = t ** 0.5
    b = (1 - t) ** 2
    return (r, g, b)

# Monkey-patch it (or modify ColorPalette class)
ColorPalette.custom = staticmethod(custom_palette)

# Use it
config = FractalConfig(color_scheme="custom")
generator = FractalGenerator(config)
```

## Performance Tips

1. **Resolution vs Speed**: Higher resolutions take significantly longer. Start with 1280x720 for testing.

2. **Iterations**: More iterations reveal more detail but take longer. 256 is usually sufficient, 512-1024 for deep zooms.

3. **Smooth Coloring**: Adds minimal overhead but significantly improves visual quality.

4. **Zoom Levels**: Deep zooms (>1000) may require higher iteration counts to show detail.

## Mathematical Background

### Mandelbrot Set

The Mandelbrot set is defined by iterating the function:
```
z(n+1) = z(n)² + c
```

Starting with z(0) = 0, where c is a complex number corresponding to a pixel position. Points that don't diverge to infinity are in the set.

### Julia Sets

Julia sets use the same iteration formula but with a fixed c and varying starting points z(0):
```
z(n+1) = z(n)² + c
```

Different values of c produce different Julia sets.

### Burning Ship

Uses absolute values before squaring:
```
z(n+1) = (|Re(z(n))| + i|Im(z(n))|)² + c
```

### Tricorn (Mandelbar)

Uses complex conjugate:
```
z(n+1) = conj(z(n))² + c
```

## Gallery

The fractal generator produces stunning mathematical art. Here are some suggested settings:

**Cosmic Elephant Valley**
- Location: (-0.75, 0.1)
- Zoom: 100
- Palette: cosmic
- Iterations: 512

**Fire Spiral**
- Location: (-0.088, 0.654)
- Zoom: 50
- Palette: fire
- Iterations: 256

**Psychedelic Mini-Mandelbrot**
- Location: (-0.16, 1.0405)
- Zoom: 200
- Palette: psychedelic
- Iterations: 1024

## Troubleshooting

**Q: Images are all black**
- Increase max_iterations (try 512 or 1024)
- Check zoom level isn't too high for the iteration count

**Q: Generation is slow**
- Reduce resolution (try 1280x720)
- Lower max_iterations
- The algorithm is computationally intensive, especially at high resolutions

**Q: Colors look banded**
- Enable smooth_coloring (should be True by default)
- Increase max_iterations

**Q: Animation takes forever**
- Reduce frame count
- Lower resolution
- Reduce max_iterations

## Future Enhancements

Potential additions:
- GPU acceleration with CUDA/OpenCL
- More fractal types (Newton fractals, Lyapunov, etc.)
- Real-time interactive WebGL viewer
- Parameter animation (morphing Julia sets)
- Multi-threaded generation
- Arbitrary precision for extreme zooms

## License

Part of the AvatarMCP project, licensed under MIT.
