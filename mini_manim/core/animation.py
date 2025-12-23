"""
Animation system for Mini-Manim.

This module contains the base Animation class and AnimationBuilder for the fluent DSL.
"""

from abc import ABC, abstractmethod
from typing import Callable, Any
import numpy as np

from mini_manim.easing import linear
from mini_manim.core.mobject import MObject

if False:  # TYPE_CHECKING:
    pass


class Animation(ABC):
    """
    Base class for all animations.
    
    Animations define how an MObject's properties change over time.
    They are driven by an alpha value that goes from 0 to 1, which is
    passed through an easing function for smooth motion.
    """
    
    def __init__(
        self,
        mobject: MObject,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ):
        """
        Initialize an animation.
        
        Args:
            mobject: The MObject to animate.
            duration: Duration of the animation in seconds.
            easing: Easing function that takes t in [0, 1] and returns [0, 1].
        """
        self.mobject = mobject
        self.duration = duration
        self.easing = easing
        
        # Store initial state
        self._initial_state: dict[str, Any] = {}
        self._final_state: dict[str, Any] = {}
        self._started = False
    
    def begin(self) -> None:
        """Called when the animation starts. Captures initial state."""
        self._initial_state = self._capture_initial_state()
        self._final_state = self._capture_final_state()
        self._started = True
    
    def finish(self) -> None:
        """Called when the animation ends. Ensures final state is set."""
        if not self._started:
            self.begin()
        # Set to final state (alpha = 1.0)
        self.interpolate(1.0)
    
    def _capture_initial_state(self) -> dict[str, Any]:
        """Capture the initial state of the mobject."""
        return {
            'position': self.mobject.position.copy(),
            'scale_factor': self.mobject.scale_factor,
            'rotation': self.mobject.rotation,
            'opacity': self.mobject.opacity,
            'fill_opacity': self.mobject.fill_opacity,
            'stroke_opacity': self.mobject.stroke_opacity,
        }
    
    @abstractmethod
    def _capture_final_state(self) -> dict[str, Any]:
        """
        Capture the target/final state for the animation.
        
        This should be implemented by subclasses to define what
        the animation is moving towards.
        """
        pass
    
    def interpolate(self, alpha: float) -> None:
        """
        Interpolate the animation state based on alpha.
        
        Args:
            alpha: Interpolation factor in [0, 1]. 0 = start, 1 = end.
        """
        if not self._started:
            self.begin()
        
        # Apply easing function
        eased_alpha = self.easing(alpha)
        
        # Clamp to [0, 1]
        eased_alpha = max(0.0, min(1.0, eased_alpha))
        
        # Perform interpolation
        self._interpolate(eased_alpha)
    
    @abstractmethod
    def _interpolate(self, alpha: float) -> None:
        """
        Perform the actual interpolation.
        
        Args:
            alpha: Eased interpolation factor in [0, 1].
        """
        pass
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"{self.__class__.__name__}(mobject={self.mobject}, duration={self.duration})"


class AnimationBuilder:
    """
    Builder class for fluent animation syntax.
    
    Example:
        circle.animate.move_to(RIGHT).scale(1.5)
        
    The builder queues operations and returns Animation objects when
    the scene calls play().
    """
    
    def __init__(self, mobject: MObject):
        self.mobject = mobject
        self._pending_operations: list[tuple[str, Any]] = []
    
    def move_to(self, target: np.ndarray | tuple[float, float]):
        """Queue a move_to animation."""
        if isinstance(target, tuple):
            target = np.array(target, dtype=float)
        self._pending_operations.append(("move_to", target))
        return self
    
    def shift(self, delta: np.ndarray | tuple[float, float]):
        """Queue a shift animation."""
        if isinstance(delta, tuple):
            delta = np.array(delta, dtype=float)
        self._pending_operations.append(("shift", delta))
        return self
    
    def scale(self, factor: float):
        """Queue a scale animation."""
        self._pending_operations.append(("scale", factor))
        return self
    
    def rotate(self, angle: float):
        """Queue a rotation animation."""
        self._pending_operations.append(("rotate", angle))
        return self
    
    def fade_in(self):
        """Queue a fade in animation."""
        self._pending_operations.append(("fade_in", None))
        return self
    
    def fade_out(self):
        """Queue a fade out animation."""
        self._pending_operations.append(("fade_out", None))
        return self
    
    def set_color(self, color: tuple[float, float, float]):
        """Queue a color change animation."""
        self._pending_operations.append(("set_color", color))
        return self
    
    def set_opacity(self, opacity: float):
        """Queue an opacity change animation."""
        self._pending_operations.append(("set_opacity", opacity))
        return self
    
    def build(self, duration: float = 1.0, easing: Callable[[float], float] = linear) -> list[Animation]:
        """
        Build animation objects from pending operations.
        
        This will be called by the Scene when play() is invoked.
        Returns a list of Animation objects that can be run in parallel.
        
        Args:
            duration: Duration for all animations.
            easing: Easing function to use.
            
        Returns:
            List of Animation objects.
        """
        from mini_manim.animations.move import Move
        from mini_manim.animations.scale import Scale
        from mini_manim.animations.fade import FadeIn, FadeOut
        from mini_manim.animations.rotate import Rotate
        
        animations = []
        
        for op_type, op_value in self._pending_operations:
            if op_type == "move_to":
                animations.append(Move(self.mobject, target=op_value, duration=duration, easing=easing))
            elif op_type == "shift":
                # Shift is relative, so we need to calculate target
                target = self.mobject.position + op_value
                animations.append(Move(self.mobject, target=target, duration=duration, easing=easing))
            elif op_type == "scale":
                animations.append(Scale(self.mobject, target_scale=op_value, duration=duration, easing=easing))
            elif op_type == "rotate":
                animations.append(Rotate(self.mobject, angle=op_value, duration=duration, easing=easing))
            elif op_type == "fade_in":
                animations.append(FadeIn(self.mobject, duration=duration, easing=easing))
            elif op_type == "fade_out":
                animations.append(FadeOut(self.mobject, duration=duration, easing=easing))
            # Note: set_color and set_opacity will be implemented as separate animations if needed
            # For now, we'll handle them as instant changes or add them later
        
        # Clear pending operations after building
        self._pending_operations.clear()
        
        return animations
