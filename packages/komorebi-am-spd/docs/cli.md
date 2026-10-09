# Command-line guide

The `am-spd` command operates on ordinary images, single-image `.amspd` checkpoints, and tiled `.amspdt` checkpoints.

## Inspect the installation

```powershell
am-spd info
am-spd --help
```

## Reconstruct one image

```powershell
am-spd reconstruct input.png output.png --method portfolio --preset quick
```

Optional outputs:

```powershell
am-spd reconstruct input.png output.png `
  --archive output.npz `
  --summary output.json `
  --model output.amspd `
  --residual-storage sparse `
  --include-input
```

The image is the bounded approximation. The NPZ file stores the normalized input, raw approximation, residual, and summary. The `.amspd` model additionally stores structured packet, tree, and portfolio metadata.

## Create a resumable checkpoint

```powershell
am-spd decompose input.png checkpoint.amspd `
  --method core `
  --packet-budget 16 `
  --include-input `
  --preview checkpoint.png
```

Exact continuation requires retained packet atoms, schema-2 search state, and source data. Those are included by default except that the normalized source image must be requested with `--include-input`. An unthresholded residual closure can also reconstruct the source, but that route is labeled `frontier-exact` rather than `exact` because roundoff can affect source values and later decisions.

## Resume a checkpoint

Add eight packet slots:

```powershell
am-spd resume checkpoint.amspd continued.amspd `
  --additional-packets 8 `
  --preview continued.png
```

Resume to an absolute per-image packet budget:

```powershell
am-spd resume checkpoint.amspd continued.amspd `
  --target-packet-budget 32 `
  --summary continued.json
```

The same command resumes tiled checkpoints. For `.amspdt` files, the target packet budget is interpreted per embedded tile:

```powershell
am-spd resume large.amspdt refined.amspdt `
  --additional-packets 8 `
  --workers 4
```

A source image already retained by the input model is preserved in the resumed model. `--omit-atoms`, `--omit-directions`, and `--omit-tile-models` deliberately reduce later inspectability or resumability.

Search parameters can be overridden during resume, for example:

```powershell
am-spd resume checkpoint.amspd alternate.amspd `
  --target-packet-budget 32 `
  --complexity-weight 0.05 `
  --max-candidates 240
```

This is a valid warm continuation, but uninterrupted parity is not claimed after search-affecting settings change.

## Reconstruct a large image by tiles

```powershell
am-spd tiled input.png large.amspdt `
  --preview large.png `
  --method core `
  --preset quick `
  --tile-size 256 `
  --overlap 32 `
  --blend cosine `
  --workers 4 `
  --include-input
```

Blend modes are `cosine`, `linear`, and `uniform`. The default model embeds tile checkpoints. Use `--omit-tile-models` for a smaller archive that cannot resume tile searches.

## Decode a model

```powershell
am-spd decode image.amspd approximation.png --mode bounded
am-spd decode image.amspd raw.npy --mode raw
am-spd decode image.amspd source.npy --mode exact
```

The same commands accept `.amspdt`. Exact decoding requires dense or unthresholded sparse residual closure and recovers the normalized floating-point source up to roundoff. It does not reproduce original image-file bytes or metadata. Use `.npy` for floating-point output; image formats can quantize or compress the decoded values.

## Inspect a model

```powershell
am-spd inspect image.amspd --output summary.json
am-spd inspect image.amspd --packets --trees --trials --search --output full-inspection.json
am-spd inspect large.amspdt --output tiled-inspection.json
```

For single-image models, the optional tables expose selected packets, tree states, portfolio trials, and saved search-frontier metadata. Tiled inspection exposes tile geometry and embedded checkpoint summaries.

## Compare models

```powershell
am-spd compare first.amspd second.amspd --output comparison.json
am-spd compare first.amspdt second.amspdt third.amspd --output comparison.json
```

The report includes archive sizes, shape, parameter and packet counts, closure status, metrics, and pairwise reconstruction differences where shapes agree.

## Select a finite budget automatically

```powershell
am-spd tune input.png `
  --output-dir tuning `
  --methods core spd tree portfolio `
  --packet-budgets 8 12 16 `
  --singular-budgets 4 8 `
  --tree-depths 1 2 `
  --max-ranks 1 2 `
  --objective rate-distortion `
  --rate-weight 0.01 `
  --save-model
```

Available objectives:

- `rate-distortion`: squared RMSE plus a parameter-density penalty
- `ssim-rate`: one minus SSIM plus a parameter-density penalty
- `rmse`: minimum bounded reconstruction RMSE
- `target-rmse`: minimum parameter density among candidates meeting `--target-rmse`

Constraints can be added with `--max-parameters`. Selection is exact only over the declared finite grid.

For `target-rmse`, feasible candidates are ordered by parameter density, then RMSE, then their declared grid index. Other objectives also use deterministic ties without runtime ranking. An infeasible candidate is recorded with `feasible=false`; a nonfinite infeasible score is serialized as JSON `null`. Empty or fractional budget grids and nonfinite weights or targets are rejected.

## Process a directory tree

```powershell
am-spd batch .\images `
  --output-dir .\batch-output `
  --method portfolio `
  --preset quick `
  --workers 4 `
  --save-models `
  --skip-existing
```

Switch large images to tiled execution automatically:

```powershell
am-spd batch .\images `
  --output-dir .\batch-output `
  --workers 4 `
  --tiled-above 1024 `
  --tile-size 256 `
  --overlap 32 `
  --tile-workers 2 `
  --save-models `
  --embed-tile-models `
  --skip-existing
```

Use `--force-tiled` to tile every input. `--no-recursive` limits discovery to the selected directory. `--fail-fast` stops at the first failure instead of recording it in the manifest.

`--skip-existing` is content aware. It skips only when the input SHA-256 and the run fingerprint derived from the current configuration and package version both match the previous summary, and any requested model output is still present.

The output directory must differ from a directory input. Recursive discovery excludes an output directory nested inside the input tree. Inputs whose names would collide in the output, including different image suffixes sharing one stem, are rejected before writes rather than overwriting one another.

## Convert a 0.1.x result archive

```powershell
am-spd convert-archive reconstruction.npz reconstruction.amspd
```

The legacy archive must contain `input_image`, `reconstruction`, `archive_residual`, and `summary_json`. It can preserve exact residual accounting but cannot recover packet, tree, or search-frontier data that were never stored.

## Exact finite pixel closure

```powershell
am-spd complete input.png completed.amspd --preview recovered.npy
```

The default residual threshold is zero. A positive `--residual-threshold` deliberately drops small residual coordinates and produces a lossy closure. A PNG preview is useful for display but is not a floating-point recovery artifact.

## Baseline suite

```powershell
am-spd baselines input.png `
  --output-dir baselines `
  --coefficient-budget 64 `
  --svd-rank 4 `
  --quadtree-leaves 32 `
  --tv-weight 0.07
```

## Built-in benchmark

```powershell
am-spd benchmark `
  --output-dir benchmark `
  --cases synthetic_geometry synthetic_text_curves camera astronaut `
  --methods core spd tree portfolio `
  --size 24 `
  --save-models
```

## Published benchmark replay

```powershell
am-spd reproduce-paper --list-cases
am-spd reproduce-paper --cases camera --output-dir paper-replay --strict-reference
am-spd reproduce-paper --output-dir paper-replay --strict-reference
```

This command replays bundled historical packet-selection rows. It does not conduct a new moving packet search.

## Verification

```powershell
am-spd verify
am-spd verify --full
am-spd verify --full --paper-case synthetic_geometry
```

## Presets

- `quick` uses laptop-oriented budgets.
- `paper-scale` uses 44 packet slots and 22 singular modes for a new search.
- `paper` is retained as a compatibility alias for `paper-scale`.

Exact historical replay is performed only by `reproduce-paper`.
