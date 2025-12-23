"""
Mini-Manim: A minimal, programmatic animation engine inspired by Manim.
"""

__version__ = "0.1.0"

# Core exports
from mini_manim.core import Scene, MObject, Animation, AnimationBuilder, Timeline

# MObject exports
from mini_manim.mobjects import (
    Circle,
    Rectangle,
    Square,
    Line,
    Arrow,
    Text,
)

# Animation exports
from mini_manim.animations import (
    Move,
    Scale,
    FadeIn,
    FadeOut,
    Rotate,
    Transform,
)

# Constants
from mini_manim.constants import (
    UP,
    DOWN,
    LEFT,
    RIGHT,
    ORIGIN,
    WHITE,
    BLACK,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    ORANGE,
    PURPLE,
    PINK,
    CYAN,
)

__all__ = [
    # Core
    "Scene",
    "MObject",
    "Animation",
    "AnimationBuilder",
    "Timeline",
    # MObjects
    "Circle",
    "Rectangle",
    "Square",
    "Line",
    "Arrow",
    "Text",
    # Animations
    "Move",
    "Scale",
    "FadeIn",
    "FadeOut",
    "Rotate",
    "Transform",
    # Constants
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "ORIGIN",
    "WHITE",
    "BLACK",
    "RED",
    "GREEN",
    "BLUE",
    "YELLOW",
    "ORANGE",
    "PURPLE",
    "PINK",
    "CYAN",
]

