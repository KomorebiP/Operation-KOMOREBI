# AM-SPD 0.3.0 functionality audit

## Scope

Version 0.3.0 extends the 0.2.0 research toolkit into a persistent reconstruction system. The release adds resumable packet searches, overlap-blended tiled models, automatic finite-budget selection, content-aware batch execution, and stronger archive validation while preserving the audited research snapshot and exact paper-replay path.

## Added public functionality

### Resumable packet-search checkpoints

- Added schema 2 of the `.amspd` archive.
- Stored the finite candidate frontier, data-derived seed masks, seed metadata, selected seed identities, quadtree leaves, next seed identifier, and NumPy random-generator state.
- Added exact continuation when search settings are unchanged and all state is retained.
- Added `frontier-exact` continuation when the exact finite frontier is retained but the source is reconstructed from unthresholded residual closure.
- Added deterministic warm continuation for readable schema-1 models that retain packet atoms and recoverable source data.
- Added chained continuation and a public `resume_model` API.
- Added one `am-spd resume` command for both single-image `.amspd` and tiled `.amspdt` checkpoints.

Under unchanged settings, the tested schema-2 continuation path reproduces the uninterrupted packet search bit for bit.

### Tiled large-image reconstruction

- Added `TiledConfig`, `TiledAMSpdResult`, and `TiledAMSpdModel`.
- Added overlap-blended tiling with cosine, linear, and uniform windows.
- Added multiworker tile execution.
- Added exact global residual accounting after overlap blending.
- Added the checksummed `.amspdt` archive format.
- Added optional embedded `.amspd` tile checkpoints.
- Added exact tiled continuation and reblending.
- Added generic archive loading and cross-format model comparison.

The tiled validator checks schema compatibility, finite arrays, nonnegative totals and thresholds, sparse-index bounds and uniqueness, region coverage, overlap validity, embedded-model shape, embedded-model integrity, and aggregate packet and parameter totals.

### Automatic finite-budget selection

- Added a finite-grid tuner over method, packet budget, singular budget, tree depth, and local rank.
- Added rate-distortion, SSIM-rate, RMSE, and target-RMSE objectives.
- Added optional parameter and RMSE constraints.
- Added complete JSON and CSV candidate ledgers.
- Added preview and model export for the selected candidate.
- Added packet-core reuse across downstream methods with identical search settings.

The tuner is an exact selector over the declared finite candidate grid. It is not a continuous optimizer and does not claim global optimality outside that grid.

### Content-aware batch processing

- Added recursive and nonrecursive directory processing.
- Added parallel execution with deterministic per-file seeds.
- Added automatic switching between single-image and tiled reconstruction at a declared size threshold.
- Added per-file images, summaries, optional models, and JSON/CSV manifests.
- Added per-file failure recording and optional fail-fast behavior.
- Added SHA-256 source digests and run fingerprints.
- Added safe `--skip-existing` behavior that skips only when both the source digest and run fingerprint match.

### Expanded CLI and API

The principal new commands are:

```text
resume
tiled
tune
batch
compare
```

The full command surface is:

```text
reconstruct
decompose
resume
tiled
tune
batch
decode
convert-archive
inspect
compare
complete
baselines
benchmark
reproduce-paper
demo
verify
info
```

Public imports now include the continuation, tiling, tuning, batching, and generic model-loading APIs.

## Package verification

### Test suite

- 45 collected tests passed.
- The suite includes 44 explicit test functions and parameterized coverage.
- Tests cover schema-1 compatibility, schema-2 exact continuation, chained continuation, tiled round trips, exact tiled continuation, invalid tiled totals and thresholds, automatic tuning, packet-core reuse, source-hash and run-fingerprint batch semantics, CLI lifecycles, model comparison, and constant-image robustness.

### Full integration verification

`python -m am_spd verify --full` passed all 20 checks.

The checks cover:

- finite output and exact accounting for all four reconstruction methods
- tree and portfolio candidate availability
- exact finite pixel-coordinate closure
- finite baseline output
- dense and sparse model validation and round trips
- exact single-image continuation parity
- tiled accounting, validation, and round trip
- model comparison
- automatic finite-grid tuning
- batch processing and safe repeat skipping

The maximum observed exact-accounting error was approximately `1.11e-16`. The tested uninterrupted/resumed single-image reconstruction difference was exactly zero.

## Historical integrity and paper replay

The preserved source under `research/original` remains byte-identical to its checksum ledger.

- 291 of 291 SHA-256 entries passed.
- 16 core packet-atlas groups passed.
- 8 Singular Packet Decomposition groups passed.
- 15 intermediate AM-SPD groups passed.
- 11 final verification groups passed.
- 12,154 of 12,154 final scenarios passed.
- Zero final failures were reported.

All four packaged paper cases passed the required reference comparison. The final exact RMSE values remained:

| Case | Final exact RMSE | Final parameters |
|---|---:|---:|
| Synthetic geometry | 0.00315546699605173 | 2,224 |
| Synthetic text and curves | 0.00314108384708539 | 2,616 |
| Camera | 0.005063837598566507 | 2,120 |
| Astronaut | 0.01074176985692109 | 5,017 |

Archived intermediate proxy differences remain visible in the replay comparison rather than being rewritten.

## Distribution boundaries

Version 0.3.0 is a functional research reconstruction system, but it is not yet:

- an entropy-coded image codec
- a GPU implementation
- a streaming out-of-core engine for images larger than available storage
- a statistical denoiser with calibrated risk
- a continuous hyperparameter optimizer
- a cryptographically signed provenance system
- a public open-source release

The current license remains all rights reserved until the author chooses another license.
