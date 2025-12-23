"""
Shape MObjects: Circle, Rectangle, and Line.
"""

import numpy as np
import cairo
from math import pi

from mini_manim.core.mobject import MObject
from mini_manim.constants import ORIGIN


class Circle(MObject):
    """
    A circle MObject.
    
    Args:
        radius: Radius of the circle.
        **kwargs: Additional arguments passed to MObject.
    """
    
    def __init__(self, radius: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
    
    def get_bounding_box(self) -> tuple[float, float, float, float]:
        """Get bounding box: (x_min, y_min, x_max, y_max)."""
        return (
            self.position[0] - self.radius * self.scale_factor,
            self.position[1] - self.radius * self.scale_factor,
            self.position[0] + self.radius * self.scale_factor,
            self.position[1] + self.radius * self.scale_factor,
        )
    
    def render(self, ctx: cairo.Context) -> None:
        """
        Render the circle to a Cairo context.
        
        The context is already transformed to the object's position/rotation/scale.
        We draw centered at the origin in local coordinates.
        """
        # Draw circle centered at origin
        ctx.arc(0, 0, self.radius, 0, 2 * pi)
        
        # Apply fill if needed
        if self.fill_opacity > 0:
            self._apply_style(ctx)
            ctx.fill_preserve()
        
        # Apply stroke
        if self.stroke_opacity > 0:
            self._apply_style(ctx)
            ctx.stroke()
        elif self.fill_opacity == 0:
            # If no fill and no stroke, at least draw a stroke
            self._apply_style(ctx)
            ctx.stroke()


class Rectangle(MObject):
    """
    A rectangle MObject.
    
    Args:
        width: Width of the rectangle.
        height: Height of the rectangle.
        **kwargs: Additional arguments passed to MObject.
    """
    
    def __init__(self, width: float = 2.0, height: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
    
    def get_bounding_box(self) -> tuple[float, float, float, float]:
        """Get bounding box: (x_min, y_min, x_max, y_max)."""
        half_w = (self.width * self.scale_factor) / 2
        half_h = (self.height * self.scale_factor) / 2
        return (
            self.position[0] - half_w,
            self.position[1] - half_h,
            self.position[0] + half_w,
            self.position[1] + half_h,
        )
    
    def render(self, ctx: cairo.Context) -> None:
        """
        Render the rectangle to a Cairo context.
        
        The context is already transformed to the object's position/rotation/scale.
        We draw centered at the origin in local coordinates.
        """
        half_w = self.width / 2
        half_h = self.height / 2
        
        # Draw rectangle centered at origin
        ctx.rectangle(-half_w, -half_h, self.width, self.height)
        
        # Apply fill if needed
        if self.fill_opacity > 0:
            self._apply_style(ctx)
            ctx.fill_preserve()
        
        # Apply stroke
        if self.stroke_opacity > 0:
            self._apply_style(ctx)
            ctx.stroke()
        elif self.fill_opacity == 0:
            # If no fill and no stroke, at least draw a stroke
            self._apply_style(ctx)
            ctx.stroke()


class Square(Rectangle):
    """
    A square MObject (special case of Rectangle).
    
    Args:
        side_length: Length of each side.
        **kwargs: Additional arguments passed to MObject.
    """
    
    def __init__(self, side_length: float = 1.0, **kwargs):
        super().__init__(width=side_length, height=side_length, **kwargs)
        self.side_length = side_length


class Line(MObject):
    """
    A line segment MObject.
    
    Args:
        start: Starting point of the line (x, y).
        end: Ending point of the line (x, y).
        **kwargs: Additional arguments passed to MObject.
    """
    
    def __init__(
        self,
        start: np.ndarray | tuple[float, float] = (-1.0, 0.0),
        end: np.ndarray | tuple[float, float] = (1.0, 0.0),
        **kwargs
    ):
        super().__init__(**kwargs)
        
        if isinstance(start, tuple):
            self.start = np.array(start, dtype=float)
        else:
            self.start = start.copy()
        
        if isinstance(end, tuple):
            self.end = np.array(end, dtype=float)
        else:
            self.end = end.copy()
    
    def get_bounding_box(self) -> tuple[float, float, float, float]:
        """Get bounding box: (x_min, y_min, x_max, y_max)."""
        # Account for position offset
        start_abs = self.position + self.start * self.scale_factor
        end_abs = self.position + self.end * self.scale_factor
        
        x_min = min(start_abs[0], end_abs[0])
        x_max = max(start_abs[0], end_abs[0])
        y_min = min(start_abs[1], end_abs[1])
        y_max = max(start_abs[1], end_abs[1])
        
        return (x_min, y_min, x_max, y_max)
    
    def render(self, ctx: cairo.Context) -> None:
        """
        Render the line to a Cairo context.
        
        The context is already transformed to the object's position/rotation/scale.
        We draw in local coordinates.
        """
        # Draw line from start to end
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])
        
        # Apply stroke (lines don't have fill)
        if self.stroke_opacity > 0:
            self._apply_style(ctx)
            ctx.stroke()
        else:
            # Default stroke if opacity is 0
            self._apply_style(ctx)
            ctx.stroke()


class Arrow(Line):
    """
    An arrow MObject (extends Line with arrowhead).
    
    Args:
        start: Starting point of the arrow (x, y).
        end: Ending point of the arrow (x, y).
        tip_length: Length of the arrowhead tip.
        tip_width: Width of the arrowhead tip.
        **kwargs: Additional arguments passed to MObject.
    """
    
    def __init__(
        self,
        start: np.ndarray | tuple[float, float] = (-1.0, 0.0),
        end: np.ndarray | tuple[float, float] = (1.0, 0.0),
        tip_length: float = 0.2,
        tip_width: float = 0.15,
        **kwargs
    ):
        super().__init__(start=start, end=end, **kwargs)
        self.tip_length = tip_length
        self.tip_width = tip_width
    
    def render(self, ctx: cairo.Context) -> None:
        """
        Render the arrow (line + arrowhead) to a Cairo context.
        """
        # Draw the main line
        ctx.move_to(self.start[0], self.start[1])
        ctx.line_to(self.end[0], self.end[1])
        
        # Calculate arrowhead
        direction = self.end - self.start
        length = np.linalg.norm(direction)
        if length > 0:
            direction = direction / length  # Normalize
            
            # Perpendicular vector for arrowhead width
            perp = np.array([-direction[1], direction[0]])
            
            # Arrowhead points
            tip_base = self.end - direction * self.tip_length
            tip_left = tip_base + perp * self.tip_width
            tip_right = tip_base - perp * self.tip_width
            
            # Draw arrowhead
            ctx.move_to(self.end[0], self.end[1])
            ctx.line_to(tip_left[0], tip_left[1])
            ctx.move_to(self.end[0], self.end[1])
            ctx.line_to(tip_right[0], tip_right[1])
        
        # Apply stroke
        if self.stroke_opacity > 0:
            self._apply_style(ctx)
            ctx.stroke()
        else:
            self._apply_style(ctx)
            ctx.stroke()

