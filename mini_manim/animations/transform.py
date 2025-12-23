"""
Transform animation: morphs one MObject into another.

This is a more complex animation that interpolates between two different objects.
"""

from typing import Callable

from mini_manim.core.animation import Animation
from mini_manim.core.mobject import MObject
from mini_manim.easing import linear


class Transform(Animation):
    """
    Animation that transforms one MObject into another.
    
    This interpolates position, scale, rotation, opacity, and color between
    the start and target MObjects. The target MObject is typically not added
    to the scene - it's just used as a reference for the final state.
    
    Args:
        mobject: The MObject to transform (start state).
        target_mobject: The target MObject (end state).
        duration: Duration of the animation in seconds.
        easing: Easing function.
    """
    
    def __init__(
        self,
        mobject: MObject,
        target_mobject: MObject,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ):
        super().__init__(mobject, duration, easing)
        self.target_mobject = target_mobject
    
    def _capture_initial_state(self) -> dict:
        """Capture the initial state of the mobject."""
        return {
            'position': self.mobject.position.copy(),
            'scale_factor': self.mobject.scale_factor,
            'rotation': self.mobject.rotation,
            'opacity': self.mobject.opacity,
            'fill_opacity': self.mobject.fill_opacity,
            'stroke_opacity': self.mobject.stroke_opacity,
            'color': self.mobject.color,
        }
    
    def _capture_final_state(self) -> dict:
        """Capture the target state from target_mobject."""
        return {
            'position': self.target_mobject.position.copy(),
            'scale_factor': self.target_mobject.scale_factor,
            'rotation': self.target_mobject.rotation,
            'opacity': self.target_mobject.opacity,
            'fill_opacity': self.target_mobject.fill_opacity,
            'stroke_opacity': self.target_mobject.stroke_opacity,
            'color': self.target_mobject.color,
        }
    
    def _interpolate(self, alpha: float) -> None:
        """Interpolate all properties from initial to target state."""
        # Position
        start_pos = self._initial_state['position']
        end_pos = self._final_state['position']
        self.mobject.position = start_pos + alpha * (end_pos - start_pos)
        
        # Scale
        start_scale = self._initial_state['scale_factor']
        end_scale = self._final_state['scale_factor']
        self.mobject.scale_factor = start_scale + alpha * (end_scale - start_scale)
        
        # Rotation
        start_rot = self._initial_state['rotation']
        end_rot = self._final_state['rotation']
        # Handle rotation wrapping (shortest path)
        diff = end_rot - start_rot
        # Normalize to [-pi, pi]
        import math
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        self.mobject.rotation = start_rot + alpha * diff
        
        # Opacity
        start_opacity = self._initial_state['opacity']
        end_opacity = self._final_state['opacity']
        self.mobject.opacity = start_opacity + alpha * (end_opacity - start_opacity)
        
        # Fill opacity
        start_fill = self._initial_state['fill_opacity']
        end_fill = self._final_state['fill_opacity']
        self.mobject.fill_opacity = start_fill + alpha * (end_fill - start_fill)
        
        # Stroke opacity
        start_stroke = self._initial_state['stroke_opacity']
        end_stroke = self._final_state['stroke_opacity']
        self.mobject.stroke_opacity = start_stroke + alpha * (end_stroke - start_stroke)
        
        # Color (RGB interpolation)
        start_color = self._initial_state['color']
        end_color = self._final_state['color']
        self.mobject.color = tuple(
            start_color[i] + alpha * (end_color[i] - start_color[i])
            for i in range(3)
        )

