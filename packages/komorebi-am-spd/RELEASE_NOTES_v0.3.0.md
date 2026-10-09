# AM-SPD 0.3.0 release notes

AM-SPD 0.3.0 turns the 0.2.0 research toolkit into a persistent reconstruction system. Searches can now be checkpointed and continued, large images can be represented by overlap-blended tile models, finite method and budget grids can be selected automatically, and complete image directories can be processed with restart-safe manifests.

## Main additions

- Schema-2 `.amspd` checkpoints with exact finite search state
- Exact, frontier-exact, and deterministic warm continuation modes
- Chained checkpoint continuation through Python and the CLI
- Overlap-blended tiled reconstruction with cosine, linear, or uniform windows
- Multiworker tile execution
- Checksummed `.amspdt` tiled models
- Resumable embedded tile checkpoints and exact tiled continuation
- Automatic finite-grid method and budget selection
- Rate-distortion, SSIM-rate, RMSE, and target-RMSE objectives
- Packet-core caching during tuning
- Recursive batch execution with deterministic per-file seeds
- Source SHA-256 and run-fingerprint restart validation
- Optional automatic single-versus-tiled routing
- Generic single/tiled model loading and comparison
- Stronger malformed-archive and aggregate-total validation
- Expanded API, CLI, examples, documentation, tests, and monorepo workflows

## Typical checkpoint lifecycle

```powershell
am-spd decompose input.png checkpoint.amspd `
    --method core `
    --packet-budget 16 `
    --include-input

am-spd resume checkpoint.amspd refined.amspd `
    --target-packet-budget 32 `
    --preview refined.png

am-spd inspect refined.amspd --search --packets
am-spd decode refined.amspd exact.npy --mode exact
```

## Tiled reconstruction and continuation

```powershell
am-spd tiled large.png large.amspdt `
    --method core `
    --tile-size 256 `
    --overlap 32 `
    --workers 4 `
    --include-input

am-spd resume large.amspdt large-refined.amspdt `
    --target-packet-budget 32 `
    --workers 4
```

The target packet budget is interpreted per tile. The global image is reblended after every continued tile search, and an exact global residual archive remains available when unthresholded closure is retained.

## Automatic budget selection

```powershell
am-spd tune input.png `
    --output-dir tuning `
    --methods core spd tree portfolio `
    --packet-budgets 8 12 16 24 `
    --objective rate-distortion `
    --rate-weight 0.01 `
    --save-model
```

The selected result is the exact minimum over the explicitly declared finite grid and objective.

## Batch processing

```powershell
am-spd batch .\images .\results `
    --recursive `
    --workers 4 `
    --save-models `
    --tile-size 256 `
    --overlap 32 `
    --tiled-above 512 `
    --embed-tile-models `
    --skip-existing
```

`--skip-existing` requires both the input SHA-256 and the run fingerprint to match. Changed files or changed reconstruction settings are processed again.

## Verification record

- 45 tests passed
- 20 of 20 full package integration checks passed
- Exact uninterrupted/resumed continuation parity passed
- Exact uninterrupted/resumed tiled parity passed
- Maximum integration exact-accounting error was approximately `1.11e-16`
- 291 of 291 preserved-source checksums passed
- 16 core, 8 SPD, 15 intermediate, and 11 final historical groups passed
- 12,154 of 12,154 final historical scenarios passed with zero failures
- All four final paper cases passed the required reference comparison

## Compatibility

- Existing 0.2.0 public reconstruction and reproduction APIs remain available.
- Schema-1 `.amspd` archives remain readable.
- Schema-1 models may continue as deterministic warm starts when their stored state is sufficient.
- New single-image models use schema 2.
- `.amspdt` is a new tiled model format and does not replace `.amspd`.

## Boundary

AM-SPD remains a research reconstruction system rather than an entropy-coded image codec. GPU acceleration, signed provenance, statistical denoising, and true out-of-core streaming remain future work. The repository retains an all-rights-reserved license until a public-use license is selected.
