"""
Cairo renderer for Mini-Manim.

Handles coordinate system transformation and frame rendering.
"""

import cairo
import io
import subprocess
from typing import List, Generator, TYPE_CHECKING

from mini_manim.core.mobject import MObject
from mini_manim.core.timeline import Timeline

if TYPE_CHECKING:
    from mini_manim.core.scene import Scene
from mini_manim.constants import (
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_FRAME_WIDTH,
    DEFAULT_FRAME_HEIGHT,
    DEFAULT_FPS,
)


class CairoRenderer:
    """
    Renders scenes to frames using Cairo.
    
    Handles coordinate system transformation from Manim-style coordinates
    (origin at center, y-up) to Cairo coordinates (origin at top-left, y-down).
    """
    
    def __init__(
        self,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        frame_width: float = DEFAULT_FRAME_WIDTH,
        frame_height: float = DEFAULT_FRAME_HEIGHT,
    ):
        """
        Initialize the renderer.
        
        Args:
            width: Canvas width in pixels.
            height: Canvas height in pixels.
            frame_width: Width of the visible frame in Manim units.
            frame_height: Height of the visible frame in Manim units.
        """
        self.width = width
        self.height = height
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Calculate scale factor: pixels per unit
        # Use the smaller dimension to maintain aspect ratio
        self.pixels_per_unit = min(width / frame_width, height / frame_height)
    
    def _setup_coordinate_system(self, ctx: cairo.Context) -> None:
        """
        Set up the Cairo context with Manim-style coordinate system.
        
        Transformations:
        1. Translate origin to center of canvas
        2. Flip y-axis (Cairo's y points down, Manim's points up)
        3. Scale to Manim units
        """
        # Save the context state
        ctx.save()
        
        # Translate to center
        ctx.translate(self.width / 2, self.height / 2)
        
        # Flip y-axis (scale y by -1)
        ctx.scale(1, -1)
        
        # Scale to Manim units
        ctx.scale(self.pixels_per_unit, self.pixels_per_unit)
    
    def _restore_coordinate_system(self, ctx: cairo.Context) -> None:
        """Restore the Cairo context state."""
        ctx.restore()
    
    def render_frame(
        self,
        mobjects: List[MObject],
        background_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> bytes:
        """
        Render a single frame with the given MObjects.
        
        Args:
            mobjects: List of MObjects to render.
            background_color: Background color (RGB, 0-1 range).
            
        Returns:
            PNG image bytes.
        """
        # Create Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        ctx = cairo.Context(surface)
        
        # Fill background
        r, g, b = background_color
        ctx.set_source_rgb(r, g, b)
        ctx.paint()
        
        # Set up coordinate system
        self._setup_coordinate_system(ctx)
        
        # Render each MObject
        for mobject in mobjects:
            # Apply object transform (position, rotation, scale)
            mobject._apply_transform(ctx)
            
            # Apply style (color, opacity)
            mobject._apply_style(ctx)
            
            # Render the object
            mobject.render(ctx)
            
            # Restore transform
            mobject._restore_transform(ctx)
        
        # Restore coordinate system
        self._restore_coordinate_system(ctx)
        
        # Convert surface to PNG bytes
        buf = io.BytesIO()
        surface.write_to_png(buf)
        return buf.getvalue()
    
    def render_scene(
        self,
        scene: "Scene",
        fps: int = DEFAULT_FPS,
        background_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> Generator[bytes, None, None]:
        """
        Render all frames of a scene.
        
        Args:
            scene: Scene to render.
            fps: Frames per second.
            background_color: Background color (RGB, 0-1 range).
            
        Yields:
            PNG image bytes for each frame.
        """
        # Update timeline FPS
        scene.timeline.fps = fps
        
        # Get total frames
        total_frames = scene.timeline.total_frames()
        
        # Initialize all animations
        for block, _ in scene.timeline.blocks:
            for anim in block.animations:
                anim.begin()
        
        # Render each frame
        for frame in range(total_frames):
            # Get active animations for this frame
            active_animations = scene.timeline.get_active_animations(frame)
            
            # Update animation states
            for anim, alpha in active_animations:
                anim.interpolate(alpha)
            
            # Render the frame
            frame_bytes = self.render_frame(scene.mobjects, background_color)
            yield frame_bytes
        
        # Ensure all animations finish
        for block, _ in scene.timeline.blocks:
            for anim in block.animations:
                anim.finish()
    
    def render_to_file(
        self,
        scene: "Scene",
        output_path: str,
        fps: int = DEFAULT_FPS,
        background_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        """
        Render a scene and save frames to individual PNG files.
        
        Args:
            scene: Scene to render.
            output_path: Output directory path (frames will be named frame_0000.png, etc.).
            fps: Frames per second.
            background_color: Background color (RGB, 0-1 range).
        """
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Render frames
        for frame_num, frame_bytes in enumerate(self.render_scene(scene, fps, background_color)):
            frame_path = os.path.join(output_path, f"frame_{frame_num:04d}.png")
            with open(frame_path, "wb") as f:
                f.write(frame_bytes)
    
    def render_to_video(
        self,
        scene: "Scene",
        output_path: str,
        fps: int = DEFAULT_FPS,
        background_color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        """
        Render a scene directly to an MP4 video file using FFmpeg.
        
        Frames are piped directly to FFmpeg without saving intermediate PNG files.
        
        Args:
            scene: Scene to render.
            output_path: Path to output MP4 file.
            fps: Frames per second.
            background_color: Background color (RGB, 0-1 range).
            
        Raises:
            FileNotFoundError: If FFmpeg is not found in PATH.
            subprocess.CalledProcessError: If FFmpeg fails.
        """
        # FFmpeg command to pipe PNG frames and encode to MP4
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-f', 'image2pipe',  # Input format: pipe
            '-vcodec', 'png',  # Input codec
            '-r', str(fps),  # Frame rate
            '-s', f'{self.width}x{self.height}',  # Frame size
            '-i', '-',  # Read from stdin
            '-c:v', 'libx264',  # Video codec
            '-pix_fmt', 'yuv420p',  # Pixel format (compatible with most players)
            '-crf', '23',  # Quality (18-28, lower = better quality)
            output_path
        ]
        
        try:
            # Start FFmpeg process
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # Unbuffered
            )
            
            # Render frames and pipe to FFmpeg
            frame_count = 0
            try:
                for frame_bytes in self.render_scene(scene, fps, background_color):
                    if proc.stdin is None:
                        break
                    proc.stdin.write(frame_bytes)
                    proc.stdin.flush()  # Ensure frame is written
                    frame_count += 1
            except BrokenPipeError:
                # FFmpeg closed the pipe early, check for errors
                pass
            finally:
                # Close stdin to signal end of input
                if proc.stdin:
                    proc.stdin.close()
            
            # Wait for FFmpeg to finish
            stdout, stderr = proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                raise subprocess.CalledProcessError(
                    proc.returncode,
                    cmd,
                    f"FFmpeg failed: {error_msg}"
                )
            
        except FileNotFoundError:
            raise FileNotFoundError(
                "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.\n"
                "Visit https://ffmpeg.org/download.html for installation instructions."
            )

