"""
Easing functions for smooth animation interpolation.

All functions take a parameter t in [0, 1] and return a value in [0, 1].
"""

import numpy as np


def linear(t: float) -> float:
    """Linear interpolation (no easing)."""
    return t


def ease_in_quad(t: float) -> float:
    """Quadratic ease-in."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out."""
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out."""
    if t < 0.5:
        return 2 * t * t
    return 1 - pow(-2 * t + 2, 2) / 2


def ease_in_cubic(t: float) -> float:
    """Cubic ease-in."""
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Cubic ease-out."""
    return 1 - pow(1 - t, 3)


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out."""
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def smooth(t: float) -> float:
    """
    Manim's smooth interpolation function.
    Uses a sigmoid-like curve for natural motion.
    """
    return t * t * (3 - 2 * t)


def ease_in_sine(t: float) -> float:
    """Sine ease-in."""
    return 1 - np.cos((t * np.pi) / 2)


def ease_out_sine(t: float) -> float:
    """Sine ease-out."""
    return np.sin((t * np.pi) / 2)


def ease_in_out_sine(t: float) -> float:
    """Sine ease-in-out."""
    return -(np.cos(np.pi * t) - 1) / 2


def ease_in_back(t: float) -> float:
    """Back ease-in (slight overshoot at start)."""
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t


def ease_out_back(t: float) -> float:
    """Back ease-out (slight overshoot at end)."""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def ease_in_out_back(t: float) -> float:
    """Back ease-in-out."""
    c1 = 1.70158
    c2 = c1 * 1.525
    
    if t < 0.5:
        return (pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
    return (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2

