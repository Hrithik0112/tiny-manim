"""
Constants for Mini-Manim: colors, directions, and default settings.
"""

import numpy as np

# Direction vectors (Manim-style coordinate system)
UP = np.array([0.0, 1.0])
DOWN = np.array([0.0, -1.0])
LEFT = np.array([-1.0, 0.0])
RIGHT = np.array([1.0, 0.0])
ORIGIN = np.array([0.0, 0.0])

# Colors (RGB tuples, normalized to 0-1 for Cairo)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
YELLOW = (1.0, 1.0, 0.0)
ORANGE = (1.0, 0.5, 0.0)
PURPLE = (0.5, 0.0, 1.0)
PINK = (1.0, 0.0, 1.0)
CYAN = (0.0, 1.0, 1.0)

# Default settings
DEFAULT_FPS = 60
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080

# Resolution presets
RESOLUTION_720P = (1280, 720)
RESOLUTION_1080P = (1920, 1080)
RESOLUTION_4K = (3840, 2160)

# Coordinate system: ~8 units visible by default
DEFAULT_FRAME_WIDTH = 8.0
DEFAULT_FRAME_HEIGHT = 8.0

