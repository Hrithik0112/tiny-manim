"""
Scene: the main orchestrator for Mini-Manim animations.

Scenes manage MObjects, schedule animations, and coordinate rendering.
"""

from typing import List, Union, Callable
from abc import ABC, abstractmethod

from mini_manim.core.mobject import MObject
from mini_manim.core.animation import Animation, AnimationBuilder
from mini_manim.core.timeline import Timeline
from mini_manim.core.renderer import CairoRenderer
from mini_manim.easing import linear
from mini_manim.constants import DEFAULT_FPS, DEFAULT_WIDTH, DEFAULT_HEIGHT


class Scene(ABC):
    """
    Base class for all scenes.
    
    Users subclass Scene and implement construct() to define their animation.
    
    Example:
        class MyScene(Scene):
            def construct(self):
                circle = Circle()
                self.add(circle)
                self.play(circle.animate.move_to(RIGHT))
    """
    
    def __init__(self):
        """Initialize a scene."""
        self.mobjects: List[MObject] = []
        self.timeline = Timeline(fps=DEFAULT_FPS)
        self._renderer: CairoRenderer | None = None  # Will be set when rendering
    
    def add(self, *mobjects: MObject) -> None:
        """
        Add MObjects to the scene.
        
        Args:
            *mobjects: One or more MObjects to add.
        """
        for mobject in mobjects:
            if mobject not in self.mobjects:
                self.mobjects.append(mobject)
    
    def remove(self, *mobjects: MObject) -> None:
        """
        Remove MObjects from the scene.
        
        Args:
            *mobjects: One or more MObjects to remove.
        """
        for mobject in mobjects:
            if mobject in self.mobjects:
                self.mobjects.remove(mobject)
    
    def play(
        self,
        *animations: Union[Animation, AnimationBuilder],
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ) -> None:
        """
        Play animations.
        
        Animations can be:
        - Animation objects directly
        - AnimationBuilder objects (from .animate syntax)
        
        All animations passed will run in parallel.
        
        Args:
            *animations: Animation objects or AnimationBuilder objects.
            duration: Duration for animations (used for AnimationBuilders).
            easing: Easing function (used for AnimationBuilders).
        """
        animation_list: List[Animation] = []
        
        for anim in animations:
            if isinstance(anim, AnimationBuilder):
                # Build animations from the builder
                built_anims = anim.build(duration=duration, easing=easing)
                animation_list.extend(built_anims)
            elif isinstance(anim, Animation):
                # Direct animation object
                animation_list.append(anim)
            else:
                raise TypeError(f"Expected Animation or AnimationBuilder, got {type(anim)}")
        
        if animation_list:
            # Add to timeline as a parallel block
            # Use the maximum duration of all animations
            max_duration = max(anim.duration for anim in animation_list)
            self.timeline.add_parallel(animation_list, max_duration)
    
    def wait(self, duration: float = 1.0) -> None:
        """
        Wait for a specified duration (no animations).
        
        Args:
            duration: Duration to wait in seconds.
        """
        # Add an empty block to the timeline
        self.timeline.add_block([], duration, sequential=False)
    
    @abstractmethod
    def construct(self) -> None:
        """
        Define the scene's animation sequence.
        
        This method must be implemented by subclasses.
        """
        pass
    
    def render(
        self,
        output_path: str,
        fps: int = DEFAULT_FPS,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        background_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        """
        Render the scene to a video file.
        
        Args:
            output_path: Path to output video file (MP4).
            fps: Frames per second.
            width: Video width in pixels.
            height: Video height in pixels.
            background_color: Background color (RGB, 0-1 range).
        """
        # Create renderer
        renderer = CairoRenderer(width=width, height=height)
        
        # Render directly to video using FFmpeg
        renderer.render_to_video(self, output_path, fps, background_color)
    
    def get_mobjects(self) -> List[MObject]:
        """
        Get all MObjects in the scene.
        
        Returns:
            List of MObjects.
        """
        return self.mobjects.copy()
    
    def clear(self) -> None:
        """Clear all MObjects from the scene."""
        self.mobjects.clear()
        self.timeline.reset()

