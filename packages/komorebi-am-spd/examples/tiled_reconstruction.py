"""Reconstruct a larger image with overlap-blended resumable tiles."""

from am_spd import AMSpdConfig, TiledConfig, load_image, tiled_reconstruct

image = load_image("input.png")
result = tiled_reconstruct(
    image,
    AMSpdConfig.quick(method="core"),
    TiledConfig(tile_size=256, overlap=32, blend="cosine", workers=4),
)
result.save_model(
    "large-image.amspdt",
    include_input=True,
    include_tile_models=True,
)

print(result.summary())
