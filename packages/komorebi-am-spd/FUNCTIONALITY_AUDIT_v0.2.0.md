# AM-SPD 0.2.0 functionality audit

## Scope

This audit records the functionality added after the 0.1.1 research release and the verification performed on the resulting 0.2.0 package.

## Added public functionality

### Portable decomposition models

- Added `AMSpdModel` and schema 1 of the `.amspd` archive.
- Added dense residual, sparse pixel-coordinate residual, and approximation-only storage.
- Added SHA-256 verification for every NumPy array payload.
- Added raw, bounded, and exact decoding.
- Added packet, tree, frontier, singular-mode, and portfolio-trial inspection.
- Added tamper-detection tests.
- Added direct migration from version 0.1.x NPZ result archives.

### Component-level APIs

- Added `fit_packet_core`.
- Added `fit_singular_packets`.
- Added `optimize_trees` with both Lagrange and exact-budget results.
- Added `fit_portfolio`.
- Added `complete_with_pixels` using sparse standard-coordinate residual coefficients.
- Added `compare_baselines` for Fourier, DCT, global SVD, quadtree, and total variation.

### Benchmark and reproduction APIs

- Added `run_builtin_benchmark` with structured CSV and JSON output.
- Added bundled packet histories and compact benchmark ledgers.
- Added `reproduce_paper_case` and `reproduce_paper`.
- Added strict checking of final paper invariants.

### CLI

The CLI now includes:

- `reconstruct`
- `decompose`
- `decode`
- `convert-archive`
- `inspect`
- `complete`
- `baselines`
- `benchmark`
- `reproduce-paper`
- `demo`
- `verify`
- `info`

### Operation-KOMOREBI integration

- Added root workflow templates for CI, full research verification, exact paper replay, and package builds.
- Added a PowerShell monorepo updater that replaces the package, copies root workflows, runs verification, pushes a branch, and opens a browser comparison when token permissions prevent pull-request creation through `gh`.

## Package verification

### Unit and integration tests

- 25 collected package tests passed.
- Tests cover the original API, exact tree frontier behavior, image I/O, the expanded CLI, component APIs, model round trips, checksum tampering, thresholded residual semantics, legacy archive conversion, and bundled replay resources.

### Full package verification

`python -m am_spd verify --full` passed all 11 checks:

- finite outputs for all four reconstruction methods
- exact accounting for all four methods
- tree candidate availability
- three-seed portfolio availability
- exact pixel-coordinate closure
- finite baseline outputs
- dense model validation
- sparse model validation
- dense exact round trip
- sparse exact round trip
- structured model metadata availability

The maximum observed integration identity errors were on the order of `1.11e-16`.

### Built wheel

- Built `komorebi_am_spd-0.2.0-py3-none-any.whl`.
- Installed the wheel outside the source checkout.
- Confirmed package version 0.2.0.
- Confirmed bundled paper cases are visible from the installed wheel.
- Ran full package verification from the installed wheel.
- Produced, inspected, decoded, and legacy-converted models from the installed wheel.
- Replayed the synthetic-geometry paper case from the installed wheel under strict reference checking.

## Historical research verification

The preserved research snapshot remains byte-identical to its ledger:

- 291 of 291 SHA-256 entries passed.
- 16 core packet-atlas groups passed.
- 8 Singular Packet Decomposition groups passed.
- 15 intermediate AM-SPD groups passed.
- 11 final verification groups passed.
- 12,154 of 12,154 final scenarios passed.
- Zero final failures were reported.

## Exact paper replay

All four cases passed the required reference comparison for:

- packet-history replay outputs
- original SPD values
- exact-budget tree values
- parameter budgets
- final exact and bounded RMSE
- final SSIM
- final parameter count
- selected reopened fraction

Final exact RMSE values reproduced:

| Case | Final exact RMSE |
|---|---:|
| Synthetic geometry | 0.00315546699605173 |
| Synthetic text and curves | 0.00314108384708539 |
| Camera | 0.005063837598566507 |
| Astronaut | 0.01074176985692109 |

The comparison ledger also exposes archival intermediate differences:

- Synthetic geometry has two Lagrange-proxy values from an earlier solver revision.
- Camera has two Lagrange-proxy values from that revision and a tie-equivalent seed-label difference. The recovered source selects the exact-budget seed while producing the same final RMSE, final parameter count, and reopened fraction recorded for the archived Lagrange seed.

These differences are retained as diagnostics. They are not silently rewritten.

## Remaining limitations

Version 0.2.0 does not yet provide:

- entropy coding or a true compressed bitstream
- tiled or streaming reconstruction for large images
- GPU acceleration
- a statistical denoising model
- automatic hyperparameter selection
- model continuation from a loaded archive
- signed model provenance
- a public-use license

These are appropriate targets for later releases. The present release is a functional research toolkit and reproducibility package rather than a finalized image codec.

## Legacy archive migration

Version 0.2.0 converts version 0.1.x result NPZ archives into checksummed `.amspd` models. Exact input, approximation, residual accounting, metrics, and configuration survive conversion. Component-level records remain unavailable because the earlier format never stored them.
