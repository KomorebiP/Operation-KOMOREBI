# AM-SPD model formats

AM-SPD 1.0.0 supports two checksummed ZIP-based interchange formats:

- `.amspd` for one image reconstruction and its packet-search checkpoint
- `.amspdt` for an overlap-blended tiled reconstruction and optional embedded tile checkpoints

These are reproducibility and continuation formats. They are not entropy-coded compression standards and do not provide cryptographic authorship signatures.

## What exact decoding preserves

The source is the normalized `float64` raster supplied to packet fitting, after image loading and any API normalization. `decode("exact")` adds an unthresholded residual to the raw approximation and recovers that raster up to floating-point subtraction and addition. It is not a promise of bit-for-bit floating-point recovery or original-file recovery.

Original image metadata, file bytes, color profiles, dtype, and intensity scaling are outside this closure identity. Use `.npy` for normalized array output. PNG and other image exports are display encodings; integer conversion can quantize values and JPEG adds lossy compression.

## Single-image `.amspd`

### Container

The minimum archive contains:

```text
manifest.json
arrays/reconstruction.npy
```

Additional `.npy` arrays are included according to storage options. Every array record includes its SHA-256 digest, dtype, shape, and byte count. NumPy arrays are loaded with `allow_pickle=False`.

### Schema compatibility

The current single-image schema is **2**. Readers accept schema 1 and schema 2.

| Schema | Meaning |
|---|---|
| 1 | Structured decomposition and residual closure, without an exact saved candidate frontier |
| 2 | Schema 1 plus finite frontier state required for exact continuation when retained |

Unknown schema versions are rejected rather than guessed.

### Principal arrays

| Array | Meaning |
|---|---|
| `reconstruction` | Raw finite AM-SPD approximation |
| `archive_residual` | Dense unresolved residual |
| `residual_indices` | Sparse residual `(row, column)` coordinates |
| `residual_values` | Sparse residual channel values |
| `input_image` | Optional normalized source image |
| `core_atoms` | Selected spatial packet atoms |
| `core_coefficients` | Per-channel packet coefficients |
| `singular_directions` | Singular packet directions |
| `singular_coefficients` | Singular-stage projection coefficients |
| `lagrange_directions` | Directions selected by the Lagrange tree |
| `exact_directions` | Directions selected by exact-budget dynamic programming |
| `replacement_directions` | Directions retained by backward replacement |
| `search_seed_masks` | Saved data-derived masks in the finite generator state |
| `search_seed_ids` | Stable identifiers for those masks |

The manifest also records packet specifications, packet-selection history, singular records, tree selections, exact Pareto frontier states, portfolio trials, replacement blocks, configuration, metrics, provenance, and the saved packet-search frontier.

### Residual storage

#### `dense`

Stores the full floating-point residual.

#### `sparse`

Stores coordinates and channel residuals. With `residual_threshold=0`, it is an exact standard-coordinate closure up to floating-point roundoff. A positive threshold is intentionally lossy.

#### `none`

Stores no residual closure. `decode("exact")` and continuation without an explicitly stored source become unavailable.

### Resume state

A model reports one of four continuation qualities:

| Quality | Conditions and guarantee |
|---|---|
| `exact` | Schema 2 frontier, packet atoms, and stored input are present. An unchanged search can reproduce the uninterrupted floating-point path |
| `frontier-exact` | Schema 2 frontier is present, but the source is reconstructed from residual closure. The saved candidate frontier is retained; source values and later decisions can differ due to floating-point roundoff |
| `warm` | Packet atoms and source data exist, but exact frontier state does not. Continuation is deterministic from the reconstructed active span |
| `unavailable` | Required atoms, packet specifications, or source closure are absent |

Exact continuation requires search-affecting configuration values to remain unchanged. Changing candidate limits, random seed, complexity weight, refresh cadence, quadtree cadence, or tolerance intentionally defines a different continuation.

`--omit-atoms` removes the data needed to rebuild the active packet span. Omitting the input still permits `frontier-exact` continuation when an unthresholded residual closure is retained.

## Tiled `.amspdt`

The current tiled schema is **1**.

A tiled model stores:

- the globally blended approximation
- dense, sparse, or omitted global residual closure
- optional normalized source image
- AM-SPD configuration
- tile size, overlap, blend mode, and worker configuration
- one region record and result summary per tile
- optionally one complete `.amspd` archive per tile
- SHA-256 digests for global arrays and embedded tile archives

Typical layout:

```text
manifest.json
arrays/reconstruction.npy
arrays/residual_indices.npy
arrays/residual_values.npy
tiles/tile_00000.amspd
tiles/tile_00001.amspd
...
```

The loader validates reconstruction finiteness, residual dimensions, sparse-coordinate bounds and uniqueness, tile-region bounds, complete image coverage, overlap bounds, embedded tile dimensions, and each embedded model.

A tiled archive is resumable only when every tile has an embedded resumable `.amspd` checkpoint. If the tiled source was saved with `include_input=True`, embedded tile checkpoints retain their corresponding tile sources and report exact resume quality.

## Decoding

Both formats support:

- `raw`: the unbounded finite approximation
- `bounded`: the approximation clipped to `[0, 1]`
- `exact`: approximation plus unthresholded residual closure

Use `.npy` output when preserving exact floating-point coordinates matters.

## Integrity and security boundary

SHA-256 records detect accidental corruption and direct payload modification. They do not authenticate the author and are not a digital signature. Treat untrusted files as untrusted compressed archives and enforce ordinary size, provenance, and storage controls.

## Migration

### From 0.1.x NPZ

```powershell
am-spd convert-archive reconstruction.npz reconstruction.amspd
```

This preserves the source, approximation, residual closure, metrics, configuration, and candidate errors available in the old result. It cannot recreate structured components that were not recorded.

### From schema 1 `.amspd`

Schema 1 remains directly readable in 1.0.0. It can be continued as a deterministic warm start when packet atoms and source data are present. Saving the resumed result writes schema 2.

### From 0.2.0 schema 1 models

No conversion command is required. Load the model with `AMSpdModel.load`, inspect `resume_state_quality`, and save a new checkpoint after reconstruction or continuation to obtain schema 2 metadata.
