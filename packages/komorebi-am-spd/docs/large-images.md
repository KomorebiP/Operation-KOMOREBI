# Large-image execution

## Purpose

A global moving packet search can become expensive as raster size and candidate count increase. AM-SPD 1.0.0 provides overlap-blended tiling to bound the size of each local search. Total memory still grows with the full image, retained tile results, and concurrent workers.

Tiling does not claim equivalence to one global AM-SPD solve. Each tile has its own finite packet problem. The tile approximations are blended, and a global residual archive preserves exact finite accounting after blending.

## Region construction

For a tile size `T` and overlap `O`, adjacent tile starts are separated by `T - O`. The final tile on each axis is aligned with the image boundary so the raster is completely covered. Images smaller than the requested tile size use one tile.

Every saved tiled model validates:

- tile bounds
- overlap dimensions
- unique tile indices
- complete raster coverage
- embedded tile dimensions

## Blend windows

### Cosine

Uses a raised cosine ramp across overlaps. This is the default because it gives a smooth transition while retaining full tile weights away from overlaps.

### Linear

Uses a linear ramp.

### Uniform

Assigns equal weight to every overlapping tile coordinate.

All windows are normalized by the accumulated per-pixel weight.

## Exact residual accounting

Let `W_j` be a normalized tile blend window and `A_j` a local AM-SPD approximation. The global approximation is

\[
\widehat F = \sum_j W_j A_j.
\]

The saved residual is computed after assembly:

\[
R = F - \widehat F.
\]

Therefore

\[
F = \widehat F + R
\]

up to floating-point roundoff, independently of local seam behavior.

## Resumable tiled models

When tile models are embedded, every tile retains its own packet-search state. Resuming a `.amspdt` checkpoint continues each tile independently and then recomputes the global blend and residual.

An absolute target packet budget is interpreted per tile. Worker count affects scheduling, not the declared local budgets.

For exact chained continuation, save the tiled source with `include_input=True` and do not omit embedded tile models or packet atoms.

## Choosing tile parameters

A practical starting point is:

```text
tile_size = 256
overlap = 32
blend = cosine
```

Increase overlap when visible tile boundaries persist. Increase tile size when globally extended structures matter and memory permits. Decrease tile size when candidate generation or local SVD becomes the dominant constraint.

## Nested parallelism

The batch runner has two worker levels:

- `--workers` controls concurrent input files
- `--tile-workers` controls concurrent tiles inside one input

Avoid setting both to the full hardware thread count. Dense linear algebra libraries can also create native threads. For repeatable runs, set:

```powershell
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
```

## Current limitations

- Tiling is overlap-blended rather than a globally coupled optimization.
- Packet choices do not communicate across tile boundaries during local fitting.
- The implementation materializes the complete normalized source and global accumulation arrays.
- Retained packet atoms and embedded tile checkpoints can also consume substantial memory; tiling does not make total memory independent of image dimensions.
- It is not a streaming codec.
- No GPU kernels are included.
