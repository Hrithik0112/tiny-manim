# Mini-Manim

A minimal, programmatic animation engine inspired by Manim.

Mini-Manim is a lightweight 2D animation engine that enables developers to create educational animations using simple, readable Python code. It preserves Manim's mental model while being easy to understand, modify, and extend.

## Features

- **Manim-like API**: Familiar programming model for Manim users
- **Lightweight**: Small codebase (<3k LOC) that's easy to understand
- **2D Rendering**: Cairo-based rendering with high-quality output
- **Fluent Animation DSL**: `circle.animate.move_to(RIGHT).scale(1.5)`
- **Video Export**: Direct MP4 export via FFmpeg
- **Extensible**: Easy to add new MObjects and animations

## Installation

### Prerequisites

- Python 3.10+
- FFmpeg (for video export)

Install FFmpeg:
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (RHEL/CentOS)
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Install Mini-Manim

**Option 1: Using a virtual environment (recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install Mini-Manim
pip install -e .
```

**Option 2: Using `uv` (if installed)**

```bash
uv pip install -e .
```

**Note:** After installation, make sure to activate your virtual environment before using the `mini-manim` command.

## Quick Start

Create a scene file `my_scene.py`:

```python
from mini_manim import Scene, Circle, Text
from mini_manim.constants import LEFT, RIGHT

class MyScene(Scene):
    def construct(self):
        circle = Circle(radius=1).move_to(LEFT * 2)
        text = Text("Hello, Mini-Manim!")
        
        self.add(circle, text)
        self.play(
            circle.animate.move_to(RIGHT * 2),
            text.animate.scale(1.5),
            duration=2.0
        )
```

Render it:
```bash
mini-manim render my_scene.py MyScene --out output.mp4
```

## Usage

### Basic Scene Structure

```python
from mini_manim import Scene, Circle, Rectangle, Text
from mini_manim.constants import LEFT, RIGHT, UP, DOWN, RED, BLUE

class MyScene(Scene):
    def construct(self):
        # Create objects
        circle = Circle(radius=1, color=RED)
        rect = Rectangle(width=2, height=1, color=BLUE)
        
        # Add to scene
        self.add(circle, rect)
        
        # Animate
        self.play(
            circle.animate.move_to(RIGHT * 3),
            rect.animate.move_to(LEFT * 3),
            duration=2.0
        )
        
        # Wait
        self.wait(1.0)
```

### MObjects

Available MObjects:

- **Shapes**: `Circle`, `Rectangle`, `Square`, `Line`, `Arrow`
- **Text**: `Text`

All MObjects support:
- `move_to(point)` - Move to position
- `shift(delta)` - Translate by vector
- `scale(factor)` - Scale by factor
- `rotate(angle)` - Rotate by angle (radians)
- `set_color(color)` - Set color
- `set_opacity(opacity)` - Set opacity (0-1)

### Animations

Use the fluent `.animate` syntax:

```python
circle.animate.move_to(RIGHT * 2).scale(1.5)
text.animate.fade_out()
rect.animate.rotate(3.14159)  # 180 degrees
```

Or use animation classes directly:

```python
from mini_manim import Move, Scale, FadeIn, FadeOut, Rotate

self.play(
    Move(circle, target=RIGHT * 2, duration=2.0),
    Scale(text, target_scale=1.5, duration=1.5),
)
```

### Easing Functions

Apply easing for smooth motion:

```python
from mini_manim.easing import ease_in_out_cubic, smooth, ease_out_back

self.play(
    circle.animate.move_to(RIGHT),
    duration=2.0,
    easing=ease_in_out_cubic
)
```

Available easing functions:
- `linear` - No easing
- `ease_in_quad`, `ease_out_quad`, `ease_in_out_quad`
- `ease_in_cubic`, `ease_out_cubic`, `ease_in_out_cubic`
- `ease_in_sine`, `ease_out_sine`, `ease_in_out_sine`
- `ease_in_back`, `ease_out_back`, `ease_in_out_back`
- `smooth` - Manim's smooth interpolation

### Constants

Pre-defined constants:

**Directions:**
- `UP`, `DOWN`, `LEFT`, `RIGHT`, `ORIGIN`

**Colors:**
- `WHITE`, `BLACK`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `ORANGE`, `PURPLE`, `PINK`, `CYAN`

## CLI Usage

```bash
# Basic usage
mini-manim render scene.py MyScene --out output.mp4

# With options
mini-manim render scene.py MyScene \
    --fps 60 \
    --resolution 1080p \
    --out video.mp4 \
    --background 0.1,0.1,0.1

# Export PNG frames instead of video
mini-manim render scene.py MyScene --export-frames --frames-dir frames/

# Custom resolution
mini-manim render scene.py MyScene --width 1280 --height 720
```

### CLI Options

- `--scene/-s`: Scene class name (auto-detects if not specified)
- `--output/-o/--out`: Output file path (default: `output.mp4`)
- `--fps`: Frames per second (default: 60)
- `--resolution/-r`: Resolution preset: `720p`, `1080p`, `4k` (default: `1080p`)
- `--width/--height`: Custom resolution (overrides preset)
- `--export-frames`: Export PNG frames instead of video
- `--frames-dir`: Directory for exported frames (default: `frames`)
- `--background/--bg`: Background color as R,G,B (0-1 range, default: `0,0,0`)

## Examples

See `examples/demo.py` for a complete example showcasing various features.

Run the example:
```bash
mini-manim render examples/demo.py DemoScene --out demo.mp4
```

## Architecture

Mini-Manim is built around three core abstractions:

```
Scene → MObjects → Animations
```

- **Scene**: Orchestrates animations and rendering
- **MObject**: Represents drawable objects (shapes, text, etc.)
- **Animation**: Defines how MObject properties change over time

The rendering pipeline:
1. Scene state → Frame (via Cairo)
2. Frame → PNG image
3. Image sequence → MP4 video (via FFmpeg)

## Development

### Project Structure

```
mini_manim/
├── core/           # Core engine (Scene, MObject, Animation, Timeline, Renderer)
├── mobjects/       # MObject implementations (shapes, text)
├── animations/    # Animation implementations (move, scale, fade, etc.)
├── constants.py   # Constants (colors, directions, defaults)
├── easing.py      # Easing functions
└── cli.py         # Command-line interface
```

### Adding New MObjects

1. Create a class inheriting from `MObject`
2. Implement `render(ctx)` method
3. Optionally override `get_bounding_box()`

Example:
```python
from mini_manim.core.mobject import MObject
import cairo

class MyShape(MObject):
    def render(self, ctx: cairo.Context) -> None:
        # Draw your shape in local coordinates (centered at origin)
        ctx.arc(0, 0, 1, 0, 2 * 3.14159)
        self._apply_style(ctx)
        ctx.stroke()
```

### Adding New Animations

1. Create a class inheriting from `Animation`
2. Implement `_capture_final_state()` and `_interpolate(alpha)`

Example:
```python
from mini_manim.core.animation import Animation

class MyAnimation(Animation):
    def _capture_final_state(self) -> dict:
        return {'some_property': target_value}
    
    def _interpolate(self, alpha: float) -> None:
        start = self._initial_state['some_property']
        end = self._final_state['some_property']
        self.mobject.some_property = start + alpha * (end - start)
```

## Limitations

- 2D only (no 3D rendering)
- Software rendering (CPU-based, not GPU-accelerated)
- No LaTeX math rendering (use Text with Unicode)
- No audio support
- Offline rendering only (no real-time preview)

## License

MIT License

## Contributing

Contributions welcome! This is a learning-focused project, so feel free to:
- Add new MObjects
- Add new animations
- Improve documentation
- Fix bugs
- Share examples

## Acknowledgments

Inspired by [Manim](https://github.com/3b1b/manim) by 3Blue1Brown.
