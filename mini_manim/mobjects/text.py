"""
Text MObject for rendering text in scenes.
"""

import numpy as np
import cairo
try:
    import cairo
    HAS_PANGO = False
    try:
        import gi
        gi.require_version('Pango', '1.0')
        gi.require_version('PangoCairo', '1.0')
        from gi.repository import Pango, PangoCairo
        HAS_PANGO = True
    except (ImportError, ValueError):
        # Pango not available, fall back to basic Cairo text
        HAS_PANGO = False
except ImportError:
    HAS_PANGO = False

from mini_manim.core.mobject import MObject
from mini_manim.constants import ORIGIN


class Text(MObject):
    """
    A text MObject.
    
    Args:
        text: The text string to display.
        font_size: Font size in points. Defaults to 48.
        font_family: Font family name (e.g., "Arial", "Times New Roman").
                    Defaults to "Sans".
        font_weight: Font weight ("normal" or "bold"). Defaults to "normal".
        **kwargs: Additional arguments passed to MObject.
    """
    
    def __init__(
        self,
        text: str,
        font_size: float = 48.0,
        font_family: str = "Sans",
        font_weight: str = "normal",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = str(text)
        self.font_size = font_size
        self.font_family = font_family
        self.font_weight = font_weight
        
        # Cache for bounding box (calculated on first render)
        self._cached_bounds = None
        self._cached_surface = None
    
    def _get_text_extents(self, ctx: cairo.Context) -> tuple[float, float, float, float]:
        """
        Get text extents (width, height, x_bearing, y_bearing).
        
        Returns:
            (width, height, x_bearing, y_bearing)
        """
        if HAS_PANGO:
            # Use Pango for accurate text measurement
            layout = PangoCairo.create_layout(ctx)
            font_desc = Pango.FontDescription()
            font_desc.set_family(self.font_family)
            font_desc.set_size(int(self.font_size * Pango.SCALE))
            if self.font_weight == "bold":
                font_desc.set_weight(Pango.Weight.BOLD)
            layout.set_font_description(font_desc)
            layout.set_text(self.text, -1)
            
            width, height = layout.get_pixel_size()
            # Pango returns pixel dimensions, convert to our coordinate system
            # We'll need to scale based on the context's coordinate system
            # For now, return pixel dimensions (will be scaled by renderer)
            return (width, height, 0, 0)
        else:
            # Fall back to Cairo's basic text extents
            ctx.select_font_face(
                self.font_family,
                cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_BOLD if self.font_weight == "bold" else cairo.FONT_WEIGHT_NORMAL
            )
            ctx.set_font_size(self.font_size)
            extents = ctx.text_extents(self.text)
            # extents: (x_bearing, y_bearing, width, height, x_advance, y_advance)
            return (extents[2], extents[3], extents[0], extents[1])
    
    def get_bounding_box(self) -> tuple[float, float, float, float]:
        """
        Get bounding box: (x_min, y_min, x_max, y_max).
        
        Note: This is approximate without a Cairo context. For accurate bounds,
        the text needs to be rendered first.
        """
        if self._cached_bounds is not None:
            # Use cached bounds if available
            x_min, y_min, x_max, y_max = self._cached_bounds
            # Account for position and scale
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            width = (x_max - x_min) * self.scale_factor
            height = (y_max - y_min) * self.scale_factor
            
            return (
                self.position[0] + (x_min - center_x) * self.scale_factor,
                self.position[1] + (y_min - center_y) * self.scale_factor,
                self.position[0] + (x_max - center_x) * self.scale_factor,
                self.position[1] + (y_max - center_y) * self.scale_factor,
            )
        
        # Fallback: estimate based on font size
        # Rough estimate: width = len(text) * font_size * 0.6, height = font_size
        estimated_width = len(self.text) * self.font_size * 0.6
        estimated_height = self.font_size
        
        half_w = (estimated_width * self.scale_factor) / 2
        half_h = (estimated_height * self.scale_factor) / 2
        
        return (
            self.position[0] - half_w,
            self.position[1] - half_h,
            self.position[0] + half_w,
            self.position[1] + half_h,
        )
    
    def render(self, ctx: cairo.Context) -> None:
        """
        Render the text to a Cairo context.
        
        The context is already transformed to the object's position/rotation/scale.
        We draw centered at the origin in local coordinates.
        """
        if HAS_PANGO:
            # Use Pango for better text rendering
            layout = PangoCairo.create_layout(ctx)
            font_desc = Pango.FontDescription()
            font_desc.set_family(self.font_family)
            font_desc.set_size(int(self.font_size * Pango.SCALE))
            if self.font_weight == "bold":
                font_desc.set_weight(Pango.Weight.BOLD)
            layout.set_font_description(font_desc)
            layout.set_text(self.text, -1)
            
            # Get text extents for centering
            width, height = layout.get_pixel_size()
            
            # Apply style (color and opacity)
            r, g, b = self.color
            alpha = self.opacity * self.stroke_opacity
            ctx.set_source_rgba(r, g, b, alpha)
            
            # Center the text (Pango draws from top-left)
            ctx.move_to(-width / 2, -height / 2)
            PangoCairo.show_layout(ctx, layout)
            
            # Cache bounds for future use
            self._cached_bounds = (
                -width / 2,
                -height / 2,
                width / 2,
                height / 2,
            )
        else:
            # Fall back to basic Cairo text rendering
            ctx.select_font_face(
                self.font_family,
                cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_BOLD if self.font_weight == "bold" else cairo.FONT_WEIGHT_NORMAL
            )
            ctx.set_font_size(self.font_size)
            
            # Get text extents for centering
            extents = ctx.text_extents(self.text)
            width = extents[2]  # text width
            height = extents[3]  # text height
            x_bearing = extents[0]
            y_bearing = extents[1]
            
            # Apply style (color and opacity)
            r, g, b = self.color
            alpha = self.opacity * self.stroke_opacity
            ctx.set_source_rgba(r, g, b, alpha)
            
            # Center the text
            # Move to position that centers the text bounding box
            ctx.move_to(
                -width / 2 - x_bearing,
                -height / 2 - y_bearing
            )
            ctx.show_text(self.text)
            
            # Cache bounds for future use
            self._cached_bounds = (
                -width / 2 - x_bearing,
                -height / 2 - y_bearing,
                width / 2 - x_bearing,
                height / 2 - y_bearing,
            )

