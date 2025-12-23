"""
Demo scene showcasing Mini-Manim features.

Run with:
    mini-manim render examples/demo.py DemoScene --out demo.mp4
"""

from mini_manim import Scene, Circle, Rectangle, Text, Line
from mini_manim.constants import LEFT, RIGHT, UP, DOWN, ORIGIN, RED, BLUE, GREEN, YELLOW, WHITE
from mini_manim.easing import ease_in_out_cubic, smooth


class DemoScene(Scene):
    """A demo scene showing various Mini-Manim features."""
    
    def construct(self):
        # Create objects
        circle = Circle(radius=1, color=RED).move_to(LEFT * 3)
        square = Rectangle(width=1.5, height=1.5, color=BLUE).move_to(RIGHT * 3)
        text = Text("Mini-Manim", font_size=48, color=WHITE).move_to(UP * 2)
        
        # Add objects to scene
        self.add(circle, square, text)
        
        # Animate: move circle to right, square to left
        self.play(
            circle.animate.move_to(RIGHT * 3),
            square.animate.move_to(LEFT * 3),
            duration=2.0,
            easing=ease_in_out_cubic
        )
        
        # Wait a bit
        self.wait(0.5)
        
        # Scale and fade animations
        self.play(
            circle.animate.scale(1.5),
            square.animate.scale(0.5),
            text.animate.fade_out(),
            duration=1.5
        )
        
        # Wait
        self.wait(0.5)
        
        # Fade in text again and rotate
        text.set_opacity(1.0)  # Reset opacity
        self.play(
            text.animate.fade_in(),
            circle.animate.rotate(3.14159),  # 180 degrees
            duration=1.0,
            easing=smooth
        )


class SimpleDemo(Scene):
    """A simpler demo for quick testing."""
    
    def construct(self):
        circle = Circle(radius=1, color=RED)
        self.add(circle)
        self.play(circle.animate.move_to(RIGHT * 2), duration=2.0)

