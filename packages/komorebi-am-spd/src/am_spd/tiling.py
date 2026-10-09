"""Compatibility aliases for the consolidated tiled AM-SPD implementation."""

from .tiled import (
    TiledAMSpdResult,
    resume_tiled_model,
)
from .tiled import (
    TiledConfig as TileConfig,
)
from .tiled import (
    TileRegion as TileBounds,
)
from .tiled import (
    tile_regions as tile_bounds,
)
from .tiled import (
    tiled_reconstruct as reconstruct_tiled,
)

__all__ = [
    "TileBounds",
    "TileConfig",
    "TiledAMSpdResult",
    "reconstruct_tiled",
    "resume_tiled_model",
    "tile_bounds",
]
