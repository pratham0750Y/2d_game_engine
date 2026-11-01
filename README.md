# Pygame Engine V2

A lightweight 2D game-engine foundation built on top of **Pygame**. It
provides basic world setup, chunk-based storage for entities and blocks,
camera following, background scrolling, sprite loading, and update/draw
helpers.

> `engineV2.py` is an engine module, not a complete playable game.
> Create your own game loop and subclass `Entity` or `Block` to
> implement game-specific behavior.

## Features

-   World initialization with configurable screen size, world
    dimensions, chunk size, FPS, and gravity
-   `Entity` objects with position, velocity, acceleration, optional
    maximum velocity, tags, and collision callbacks
-   `Block` objects for static or movable world objects
-   Chunk-based lists for organizing entities and blocks
-   Camera following through `Entity.focus()`
-   Background images with configurable scroll speed and optional
    horizontal/vertical looping
-   Image loading, scaling, flipping, and basic sprite-frame storage
-   `update()` and `late_update()` hooks for custom behavior

## Requirements

-   Python 3.10 or newer is recommended
-   Pygame

Install Pygame in the VS Code terminal on Windows:

``` powershell
py -m pip install pygame
```

## Project setup

Place `engineV2.py` in your project folder and import it from your game
script:

``` python
import pygame as pygame
import engineV2 as engine
```

Keep your image assets in your project and pass their paths to the
engine where needed.

## Quick start

The following is a minimal example showing the intended setup pattern.
Save it as `main.py` beside `engineV2.py`.

``` python
import pygame as pygame
import engineV2 as engine

SCREEN_SIZE = (800, 600)
WORLD_SIZE = (10, 10)  # Number of chunks along x and y

screen = engine.init(
    screensize=SCREEN_SIZE,
    world_size=WORLD_SIZE,
    fps=60,
    gravity=0.5,
    chunks_size=100,
)

# Use a colour tuple as a fallback image.
floor = engine.Block(
    pos=(0, 500),
    size=(800, 100),
    status="default",
    colour=(60, 180, 75),
    current_status="default",
)

player = engine.Entity(
    pos=(100, 100),
    size=(40, 50),
    status="default",
    colour=(220, 60, 60),
    gravity=0.5,
)

player.focus()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    engine.objupdate()
    engine.drawall()
    pygame.display.flip()

pygame.quit()
```

This example illustrates the API shape. The engine's current collision
and image-loading behavior may require adjustments for your specific
game; see **Important implementation notes** below.

## Main API

### `init(screensize, world_size, freezex=False, freezey=False, fps=60, gravity=None, chunks_size=100)`

Initializes Pygame and the engine's world state.

-   `screensize`: window dimensions, such as `(800, 600)`
-   `world_size`: number of world chunks in `(x, y)` order
-   `freezex`, `freezey`: freeze camera/background following on the
    corresponding axis
-   `fps`: target frame rate
-   `gravity`: default vertical acceleration for entities; `None` means
    no default gravity
-   `chunks_size`: width and height of each square chunk in world units

Returns the Pygame display surface.

Call `init()` before creating `Entity` or `Block` instances.

### `Entity(pos, size, status=None, direction="right", image=None, colour=(255, 0, 0), velocity=(0, 0), acceleration=(0, 0), gravity=World_parameters.gravity, max_velocity=None, tag=None, collision=True)`

Represents a moving or interactive object.

Important attributes:

-   `rec`: Pygame rectangle representing position and size
-   `vel`: velocity vector
-   `acc`: acceleration vector
-   `max_vel`: optional velocity limit
-   `current_status`: sprite/status key to draw
-   `facing_direction`: direction key (`"left"`, `"right"`, `"top"`, or
    `"bottom"`)
-   `tag`: optional user-defined identifier
-   `collision`: whether block collision handling is enabled

Override these methods in a subclass to add game behavior:

``` python
class Player(engine.Entity):
    def update(self):
        # Read input and update player state here.
        pass

    def entity_block_collision(self, block, direction):
        # React to block collisions here.
        pass

    def entity_entity_collision(self, entity):
        # React to other entities here.
        pass

    def late_update(self):
        # Logic that should run after collision processing.
        pass
```

Use `player.focus(offset=(0, 0))` to make the camera follow an entity.

### `Block(pos, size, status=None, direction="right", image=None, colour=(0, 255, 0), tag=None, current_status=None)`

Represents a world block. Blocks are stored separately from entities and
are checked by the engine's entity-versus-block collision logic.

-   `pos`: world position `(x, y)`
-   `size`: `(width, height)`
-   `status`: key used to store its image frames
-   `image`: image path or supported fallback value
-   `colour`: fallback colour when image loading fails
-   `tag`: optional identifier
-   `current_status`: status key used by `drawall()`

`Block` provides `update()`, `late_update()`, and `moveTo(x, y)` methods
that can be overridden or called by game code.

### `image_load(path, alpha=True, size=None, fit_screen=False)`

Loads an image and optionally scales it.

-   `path`: image path
-   `alpha`: use per-pixel alpha when loading
-   `size`: requested output dimensions
-   `fit_screen`: scale to the initialized screen size

If loading fails, the function attempts to create a fallback surface
using `size` and either the supplied RGB tuple or white. Pass a valid
`size` when using this fallback.

### `set_background(image, speed=1, infinitex=False, infinitey=False, start=(0, 0))`

Sets the background surface.

-   `image`: a Pygame surface
-   `speed`: background scroll multiplier relative to the followed
    entity
-   `infinitex`: repeat the background horizontally
-   `infinitey`: repeat the background vertically
-   `start`: starting background offset

Example:

``` python
background = engine.image_load("assets/background.png", size=(1600, 600))
engine.set_background(background, speed=0.5, infinitex=True)
```

### `objupdate()`

Runs the engine's update pass. It ticks the clock, updates entities and
blocks in the visible chunk range, applies entity acceleration and
velocity, performs collision checks, calls `late_update()`, and updates
the camera.

Call it once per frame.

### `drawall()`

Draws the background, visible blocks, and visible entities to the
initialized display surface.

Call it after `objupdate()` and before `pygame.display.flip()`.

### `Image`

A helper for composing an image from multiple surfaces or image paths.
It supports adding images, starting a new row/layer with `next()`,
inserting an image at a position with `insert()`, adding blank space
with `pad()`, and combining the content with `compile()`.

## Typical game loop

``` python
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player input here.
    engine.objupdate()
    engine.drawall()
    pygame.display.flip()

pygame.quit()
```

## Important implementation notes

-   **Initialize first:** call `engine.init(...)` before creating
    entities or blocks.
-   **World bounds:** entities and blocks are placed into chunk lists
    based on their initial positions. Keep positions within the
    configured world dimensions.
-   **Image statuses:** `drawall()` indexes each object's image frames
    using `current_status`; ensure the matching status has been loaded
    before drawing.
-   **Custom behavior:** `Entity.update()`, `Entity.late_update()`, and
    collision callbacks are placeholders intended for subclass
    overrides.
-   **Review before relying on collisions:** the current collision loop
    indexes neighboring chunks without explicit boundary checks, and
    collision handling should be tested at world edges.
-   **Review camera/chunk calculations:** the current code mixes chunk
    coordinates and screen/world dimensions in its visible-range
    calculations. Verify these calculations for your chosen world and
    chunk sizes.
-   **Background setup:** `drawall()` expects a background surface to be
    configured appropriately. Call `set_background()` after
    initialization for predictable behavior.
-   **Image fallback:** if an image path fails to load, the fallback
    surface requires a usable size.
-   **API consistency:** the code uses camelCase names such as
    `moveTo()`; keep that spelling when calling those methods.

## Current scope

This module provides foundational utilities rather than a full engine
framework. It does not include a built-in input system, animation
controller, level editor, audio manager, or complete physics system.
These can be implemented in your game code or added to the module.

## License

No license is specified in the source file. Add a license before
distributing or reusing the project publicly.
