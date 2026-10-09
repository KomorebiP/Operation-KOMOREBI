"""Process an image directory with content-aware manifests."""

from am_spd import AMSpdConfig, TiledConfig, run_batch

report = run_batch(
    "images",
    "batch-output",
    AMSpdConfig.quick(method="portfolio"),
    workers=4,
    save_models=True,
    tile_config=TiledConfig(tile_size=256, overlap=32, workers=2),
    tiled_above=1024,
    save_tile_models=True,
    skip_existing=True,
)

print(report.summary())
