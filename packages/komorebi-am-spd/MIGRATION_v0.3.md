# Migration to AM-SPD 0.3.0

## From 0.2.0 source code

The 0.2 public reconstruction, component, benchmark, baseline, model, and paper-replay APIs remain available. Existing `.amspd` schema-1 files remain readable.

No source migration is required for ordinary reconstruction:

```python
from am_spd import AMSpdConfig, reconstruct
```

## Model schema

Single-image models written by 0.3.0 use schema 2. Schema 1 remains supported for reading.

```python
from am_spd import AMSpdModel

model = AMSpdModel.load("old-schema-one.amspd")
print(model.schema_version)
print(model.resume_state_quality)
```

A schema-1 model can resume as a deterministic warm start when it contains packet atoms and either its input or exact residual closure. Saving the new result writes schema 2.

## Exact checkpoints

To create a checkpoint capable of exact uninterrupted parity under unchanged settings, retain packet atoms and the normalized source:

```python
result.save_model(
    "checkpoint.amspd",
    include_input=True,
    include_atoms=True,
    residual_storage="sparse",
)
```

Models saved with `--omit-atoms` cannot resume. Models without a stored input can still report `frontier-exact` when the source is recoverable from unthresholded residual closure.

## New tiled format

Large-image models use `.amspdt`. This is a new format and does not replace `.amspd`.

```python
from am_spd import TiledConfig, tiled_reconstruct

result = tiled_reconstruct(image, tiled_config=TiledConfig(tile_size=256, overlap=32))
result.save_model("large.amspdt", include_input=True, include_tile_models=True)
```

Use the generic `load_model_archive` function when the extension can vary:

```python
from am_spd import load_model_archive

model = load_model_archive("large.amspdt")
```

## New CLI names

AM-SPD 0.3.0 adds:

```text
resume
tiled
tune
batch
compare
```

All 0.2.0 command names remain available.

## Batch skip semantics

`batch --skip-existing` now compares both the source-file SHA-256 and a run fingerprint derived from reconstruction and tiling settings. Changing the input or configuration causes reprocessing. Existing output files alone are no longer sufficient for a skip.

## Versioned import compatibility

`TileConfig` and `reconstruct_tiled` are aliases for `TiledConfig` and `tiled_reconstruct`. They are retained for intuitive external naming, while the latter names are canonical in the source.
