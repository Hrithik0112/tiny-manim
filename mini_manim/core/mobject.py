"""
Base class for all mathematical objects (MObjects) in Mini-Manim.

MObjects represent anything that can be drawn on screen and animated.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import numpy as np
import cairo

from mini_manim.constants import ORIGIN, WHITE, BLACK

if TYPE_CHECKING:
    from mini_manim.core.animation import AnimationBuilder


class MObject(ABC):
    """
    Base class for all drawable objects.
    
    MObjects have position, scale, rotation, opacity, and color properties
    that can be animated over time.
    """
    
    def __init__(
        self,
        position: np.ndarray | tuple[float, float] | None = None,
        color: tuple[float, float, float] = WHITE,
        stroke_width: float = 2.0,
        fill_opacity: float = 0.0,
        stroke_opacity: float = 1.0,
    ):
        """
        Initialize an MObject.
        
        Args:
            position: Initial position (x, y). Defaults to ORIGIN.
            color: RGB color tuple (0-1 range). Defaults to WHITE.
            stroke_width: Width of the stroke outline.
            fill_opacity: Opacity of the fill (0-1). Defaults to 0 (no fill).
            stroke_opacity: Opacity of the stroke (0-1). Defaults to 1.
        """
        if position is None:
            self.position = ORIGIN.copy()
        elif isinstance(position, tuple):
            self.position = np.array(position, dtype=float)
        else:
            self.position = position.copy()
        
        self.scale_factor = 1.0
        self.rotation = 0.0  # Rotation in radians
        self.opacity = 1.0
        self.color = color
        self.stroke_width = stroke_width
        self.fill_opacity = fill_opacity
        self.stroke_opacity = stroke_opacity
        
        # Store initial state for animations
        self._initial_state = self._capture_state()
    
    def _capture_state(self) -> dict:
        """Capture current state for animation purposes."""
        return {
            'position': self.position.copy(),
            'scale_factor': self.scale_factor,
            'rotation': self.rotation,
            'opacity': self.opacity,
            'fill_opacity': self.fill_opacity,
            'stroke_opacity': self.stroke_opacity,
        }
    
    def move_to(self, point: np.ndarray | tuple[float, float]) -> "MObject":
        """
        Move the object to a specific point.
        
        Args:
            point: Target position (x, y).
            
        Returns:
            self for method chaining.
        """
        if isinstance(point, tuple):
            self.position = np.array(point, dtype=float)
        else:
            self.position = point.copy()
        return self
    
    def shift(self, delta: np.ndarray | tuple[float, float]) -> "MObject":
        """
        Shift the object by a delta vector.
        
        Args:
            delta: Translation vector (dx, dy).
            
        Returns:
            self for method chaining.
        """
        if isinstance(delta, tuple):
            delta = np.array(delta, dtype=float)
        self.position += delta
        return self
    
    def scale(self, factor: float) -> "MObject":
        """
        Scale the object by a factor.
        
        Args:
            factor: Scale multiplier (1.0 = no change, 2.0 = double size).
            
        Returns:
            self for method chaining.
        """
        self.scale_factor *= factor
        return self
    
    def rotate(self, angle: float) -> "MObject":
        """
        Rotate the object by an angle.
        
        Args:
            angle: Rotation angle in radians.
            
        Returns:
            self for method chaining.
        """
        self.rotation += angle
        return self
    
    def set_color(self, color: tuple[float, float, float]) -> "MObject":
        """
        Set the object's color.
        
        Args:
            color: RGB color tuple (0-1 range).
            
        Returns:
            self for method chaining.
        """
        self.color = color
        return self
    
    def set_opacity(self, opacity: float) -> "MObject":
        """
        Set the object's opacity.
        
        Args:
            opacity: Opacity value (0-1).
            
        Returns:
            self for method chaining.
        """
        self.opacity = max(0.0, min(1.0, opacity))
        return self
    
    def set_fill_opacity(self, opacity: float) -> "MObject":
        """Set the fill opacity."""
        self.fill_opacity = max(0.0, min(1.0, opacity))
        return self
    
    def set_stroke_opacity(self, opacity: float) -> "MObject":
        """Set the stroke opacity."""
        self.stroke_opacity = max(0.0, min(1.0, opacity))
        return self
    
    @property
    def animate(self) -> "AnimationBuilder":
        """
        Return an AnimationBuilder for fluent animation syntax.
        
        Example:
            circle.animate.move_to(RIGHT).scale(1.5)
        """
        # Import here to avoid circular dependency
        from mini_manim.core.animation import AnimationBuilder
        return AnimationBuilder(self)
    
    def get_bounding_box(self) -> tuple[float, float, float, float]:
        """
        Get the bounding box of the object (x_min, y_min, x_max, y_max).
        
        Must be implemented by subclasses for accurate layout and transforms.
        """
        # Default implementation returns a small box around position
        # Subclasses should override this
        return (
            self.position[0] - 0.5,
            self.position[1] - 0.5,
            self.position[0] + 0.5,
            self.position[1] + 0.5,
        )
    
    def _apply_transform(self, ctx: cairo.Context) -> None:
        """
        Apply the object's transform (position, scale, rotation) to a Cairo context.
        
        This is called before render() to set up the coordinate system.
        The renderer has already set up a y-up coordinate system, so we don't flip y here.
        """
        ctx.save()
        
        # Translate to position (y is already flipped by renderer)
        ctx.translate(self.position[0], self.position[1])
        
        # Rotate
        if self.rotation != 0:
            ctx.rotate(self.rotation)  # Positive for counter-clockwise in y-up system
        
        # Scale
        if self.scale_factor != 1.0:
            ctx.scale(self.scale_factor, self.scale_factor)
    
    def _restore_transform(self, ctx: cairo.Context) -> None:
        """Restore the Cairo context after transform."""
        ctx.restore()
    
    def _apply_style(self, ctx: cairo.Context) -> None:
        """Apply color and opacity to the Cairo context."""
        r, g, b = self.color
        
        # Apply fill
        if self.fill_opacity > 0:
            fill_alpha = self.opacity * self.fill_opacity
            ctx.set_source_rgba(r, g, b, fill_alpha)
        
        # Apply stroke
        if self.stroke_opacity > 0:
            stroke_alpha = self.opacity * self.stroke_opacity
            ctx.set_source_rgba(r, g, b, stroke_alpha)
            ctx.set_line_width(self.stroke_width)
    
    @abstractmethod
    def render(self, ctx: cairo.Context) -> None:
        """
        Render the object to a Cairo context.
        
        The context will already have the coordinate system transformed
        to the object's position, rotation, and scale. This method should
        only draw the object's shape in local coordinates (centered at origin).
        
        Args:
            ctx: Cairo context to draw on.
        """
        pass
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"pos={self.position}, "
            f"scale={self.scale_factor:.2f}, "
            f"rot={self.rotation:.2f})"
        )

