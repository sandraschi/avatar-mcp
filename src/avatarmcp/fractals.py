"""
Beautiful Fractal Generator

This module provides high-quality fractal generation with support for various
fractal types, beautiful color palettes, and animation capabilities.
"""

import numpy as np
from typing import Tuple, Optional, Callable, List
from dataclasses import dataclass
import colorsys


@dataclass
class FractalConfig:
    """Configuration for fractal generation"""
    width: int = 1920
    height: int = 1080
    max_iterations: int = 256
    zoom: float = 1.0
    center_x: float = 0.0
    center_y: float = 0.0
    color_scheme: str = "cosmic"
    smooth_coloring: bool = True


class ColorPalette:
    """Beautiful color palettes for fractal rendering"""

    @staticmethod
    def cosmic(t: float) -> Tuple[float, float, float]:
        """Deep space cosmic colors"""
        r = 0.5 + 0.5 * np.sin(3.0 * t + 0)
        g = 0.5 + 0.5 * np.sin(3.0 * t + 2)
        b = 0.5 + 0.5 * np.sin(3.0 * t + 4)
        return (r, g, b)

    @staticmethod
    def fire(t: float) -> Tuple[float, float, float]:
        """Fiery warm colors"""
        if t < 0.33:
            return (t * 3, 0, 0)
        elif t < 0.66:
            return (1.0, (t - 0.33) * 3, 0)
        else:
            return (1.0, 1.0, (t - 0.66) * 3)

    @staticmethod
    def ocean(t: float) -> Tuple[float, float, float]:
        """Cool ocean depths"""
        r = 0.1 + 0.4 * t
        g = 0.3 + 0.5 * np.sin(2 * np.pi * t)
        b = 0.5 + 0.5 * t
        return (r, g, b)

    @staticmethod
    def rainbow(t: float) -> Tuple[float, float, float]:
        """Vibrant rainbow spectrum"""
        return colorsys.hsv_to_rgb(t, 0.8, 0.95)

    @staticmethod
    def psychedelic(t: float) -> Tuple[float, float, float]:
        """Vibrant psychedelic colors"""
        r = 0.5 + 0.5 * np.sin(7.0 * t)
        g = 0.5 + 0.5 * np.sin(13.0 * t + 2)
        b = 0.5 + 0.5 * np.sin(17.0 * t + 4)
        return (r, g, b)

    @staticmethod
    def sunset(t: float) -> Tuple[float, float, float]:
        """Beautiful sunset gradient"""
        r = 0.9 + 0.1 * np.sin(2 * np.pi * t)
        g = 0.3 + 0.4 * t
        b = 0.5 * (1 - t)
        return (r, g, b)

    @staticmethod
    def monochrome(t: float) -> Tuple[float, float, float]:
        """Classic black and white"""
        return (t, t, t)

    @staticmethod
    def get_palette(name: str) -> Callable:
        """Get palette function by name"""
        palettes = {
            "cosmic": ColorPalette.cosmic,
            "fire": ColorPalette.fire,
            "ocean": ColorPalette.ocean,
            "rainbow": ColorPalette.rainbow,
            "psychedelic": ColorPalette.psychedelic,
            "sunset": ColorPalette.sunset,
            "monochrome": ColorPalette.monochrome,
        }
        return palettes.get(name, ColorPalette.cosmic)


class FractalGenerator:
    """High-performance fractal generator"""

    def __init__(self, config: Optional[FractalConfig] = None):
        self.config = config or FractalConfig()

    def mandelbrot(self, c: complex, max_iter: int) -> Tuple[int, float]:
        """
        Calculate Mandelbrot set value for a complex number
        Returns (iterations, smooth value for coloring)
        """
        z = 0j
        for n in range(max_iter):
            if abs(z) > 2:
                if self.config.smooth_coloring:
                    # Smooth coloring algorithm
                    smooth = n + 1 - np.log(np.log(abs(z))) / np.log(2)
                    return n, smooth
                return n, float(n)
            z = z * z + c
        return max_iter, float(max_iter)

    def julia(self, z: complex, c: complex, max_iter: int) -> Tuple[int, float]:
        """
        Calculate Julia set value
        Returns (iterations, smooth value for coloring)
        """
        for n in range(max_iter):
            if abs(z) > 2:
                if self.config.smooth_coloring:
                    smooth = n + 1 - np.log(np.log(abs(z))) / np.log(2)
                    return n, smooth
                return n, float(n)
            z = z * z + c
        return max_iter, float(max_iter)

    def burning_ship(self, c: complex, max_iter: int) -> Tuple[int, float]:
        """
        Calculate Burning Ship fractal value
        Returns (iterations, smooth value for coloring)
        """
        z = 0j
        for n in range(max_iter):
            if abs(z) > 2:
                if self.config.smooth_coloring:
                    smooth = n + 1 - np.log(np.log(abs(z))) / np.log(2)
                    return n, smooth
                return n, float(n)
            z = complex(abs(z.real), abs(z.imag))
            z = z * z + c
        return max_iter, float(max_iter)

    def tricorn(self, c: complex, max_iter: int) -> Tuple[int, float]:
        """
        Calculate Tricorn (Mandelbar) fractal value
        Returns (iterations, smooth value for coloring)
        """
        z = 0j
        for n in range(max_iter):
            if abs(z) > 2:
                if self.config.smooth_coloring:
                    smooth = n + 1 - np.log(np.log(abs(z))) / np.log(2)
                    return n, smooth
                return n, float(n)
            z = np.conj(z) * np.conj(z) + c
        return max_iter, float(max_iter)

    def generate_mandelbrot(self) -> np.ndarray:
        """Generate a Mandelbrot set fractal image"""
        return self._generate_fractal(self.mandelbrot, "mandelbrot")

    def generate_julia(self, c: complex = complex(-0.7, 0.27015)) -> np.ndarray:
        """Generate a Julia set fractal image"""
        return self._generate_fractal(
            lambda z, max_iter: self.julia(z, c, max_iter),
            "julia"
        )

    def generate_burning_ship(self) -> np.ndarray:
        """Generate a Burning Ship fractal image"""
        return self._generate_fractal(self.burning_ship, "burning_ship")

    def generate_tricorn(self) -> np.ndarray:
        """Generate a Tricorn fractal image"""
        return self._generate_fractal(self.tricorn, "tricorn")

    def _generate_fractal(self, fractal_func: Callable, fractal_type: str) -> np.ndarray:
        """
        Internal method to generate fractal with current configuration
        """
        width = self.config.width
        height = self.config.height
        max_iter = self.config.max_iterations

        # Create coordinate arrays
        aspect_ratio = width / height
        x_min = self.config.center_x - 2.0 / self.config.zoom * aspect_ratio
        x_max = self.config.center_x + 2.0 / self.config.zoom * aspect_ratio
        y_min = self.config.center_y - 2.0 / self.config.zoom
        y_max = self.config.center_y + 2.0 / self.config.zoom

        # Adjust for Julia set to show interesting region
        if fractal_type == "julia":
            x_min, x_max = -2.0 / self.config.zoom, 2.0 / self.config.zoom
            y_min, y_max = -2.0 / self.config.zoom, 2.0 / self.config.zoom

        # Adjust for Burning Ship (rotated view)
        if fractal_type == "burning_ship":
            x_min = self.config.center_x - 2.0 / self.config.zoom
            x_max = self.config.center_x + 0.5 / self.config.zoom
            y_min = self.config.center_y - 2.0 / self.config.zoom
            y_max = self.config.center_y + 0.5 / self.config.zoom

        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        # Create image array
        image = np.zeros((height, width, 3))

        # Get color palette
        palette_func = ColorPalette.get_palette(self.config.color_scheme)

        # Generate fractal
        for i in range(height):
            for j in range(width):
                c = complex(x[j], y[i])
                iterations, smooth_value = fractal_func(c, max_iter)

                if iterations < max_iter:
                    # Normalize smooth value
                    t = smooth_value / max_iter
                    # Apply non-linear scaling for more interesting colors
                    t = np.sqrt(t)
                    color = palette_func(t)
                    image[i, j] = color
                else:
                    # Points in the set are black
                    image[i, j] = (0, 0, 0)

        return image

    def generate_zoom_sequence(
        self,
        fractal_type: str = "mandelbrot",
        target_x: float = -0.5,
        target_y: float = 0.0,
        num_frames: int = 60,
        zoom_factor: float = 1.2,
        julia_c: Optional[complex] = None
    ) -> List[np.ndarray]:
        """
        Generate a zoom sequence for animation

        Args:
            fractal_type: Type of fractal ('mandelbrot', 'julia', 'burning_ship', 'tricorn')
            target_x: X coordinate to zoom into
            target_y: Y coordinate to zoom into
            num_frames: Number of frames to generate
            zoom_factor: Zoom factor per frame
            julia_c: Complex parameter for Julia set

        Returns:
            List of image arrays
        """
        frames = []
        original_zoom = self.config.zoom
        original_center_x = self.config.center_x
        original_center_y = self.config.center_y

        for i in range(num_frames):
            # Update zoom and center
            self.config.zoom = original_zoom * (zoom_factor ** i)
            # Smoothly interpolate center position
            t = i / max(num_frames - 1, 1)
            self.config.center_x = original_center_x + (target_x - original_center_x) * t
            self.config.center_y = original_center_y + (target_y - original_center_y) * t

            # Generate frame
            if fractal_type == "mandelbrot":
                frame = self.generate_mandelbrot()
            elif fractal_type == "julia":
                c = julia_c if julia_c else complex(-0.7, 0.27015)
                frame = self.generate_julia(c)
            elif fractal_type == "burning_ship":
                frame = self.generate_burning_ship()
            elif fractal_type == "tricorn":
                frame = self.generate_tricorn()
            else:
                frame = self.generate_mandelbrot()

            frames.append(frame)

        # Restore original config
        self.config.zoom = original_zoom
        self.config.center_x = original_center_x
        self.config.center_y = original_center_y

        return frames

    def generate_palette_morph(
        self,
        fractal_type: str = "mandelbrot",
        num_frames: int = 60,
        palettes: Optional[List[str]] = None
    ) -> List[np.ndarray]:
        """
        Generate a sequence morphing through different color palettes

        Args:
            fractal_type: Type of fractal to generate
            num_frames: Number of frames
            palettes: List of palette names to morph through

        Returns:
            List of image arrays
        """
        if palettes is None:
            palettes = ["cosmic", "fire", "ocean", "psychedelic", "sunset"]

        frames = []
        original_palette = self.config.color_scheme

        frames_per_palette = num_frames // len(palettes)

        for palette in palettes:
            self.config.color_scheme = palette
            for _ in range(frames_per_palette):
                if fractal_type == "mandelbrot":
                    frame = self.generate_mandelbrot()
                elif fractal_type == "julia":
                    frame = self.generate_julia()
                elif fractal_type == "burning_ship":
                    frame = self.generate_burning_ship()
                elif fractal_type == "tricorn":
                    frame = self.generate_tricorn()
                else:
                    frame = self.generate_mandelbrot()
                frames.append(frame)

        self.config.color_scheme = original_palette
        return frames


def get_interesting_locations() -> dict:
    """Return dictionary of interesting locations to explore in the Mandelbrot set"""
    return {
        "seahorse_valley": (-0.75, 0.1),
        "elephant_valley": (0.28, 0.008),
        "triple_spiral": (-0.088, 0.654),
        "scepter_valley": (-1.25, 0.02),
        "mini_mandelbrot": (-0.16, 1.0405),
        "san_marco": (-0.75, 0.0),
        "starfish": (-0.374, -0.659),
        "dendrite": (-0.1592, -1.0317),
    }


def get_interesting_julia_params() -> dict:
    """Return dictionary of interesting Julia set parameters"""
    return {
        "dragon": complex(-0.8, 0.156),
        "dendrite": complex(-0.7, 0.27015),
        "rabbit": complex(-0.123, 0.745),
        "douady": complex(-0.4, 0.6),
        "san_marco": complex(-0.75, 0.0),
        "spiral": complex(0.285, 0.01),
        "nebula": complex(-0.4, -0.59),
        "crystals": complex(0.355, 0.355),
    }
