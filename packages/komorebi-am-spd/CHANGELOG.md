# 1.0.0 — 2026-10-09

- Stable public release under the MIT License.
- Preserve integer brightness and require finite normalized float sources.
- Preserve alpha and 16-bit grayscale input; accept normalized NumPy raster files.
- Validate integer configuration, resume budgets, refresh intervals, and finite weights.
- Reject source-inconsistent reused packet cores.
- Reorthogonalize projected directions and reject rounding leakage from duplicate directions.
- Enforce downstream parameter budgets across SPD, trees, and portfolio seeds.
- Validate archive numerical payloads, sparse indices, metadata, and continuation state.
- Distinguish bitwise exact continuation from closure-only roundoff in tests.
- Prevent batch artifact collisions and nested-output recursion; make restart reuse version-aware.
- Make finite-grid selection deterministic and correct target-RMSE selection.
- Require `.npy` for exact CLI decoding and finite pixel-closure thresholds.
- Fail fast in Windows setup/verification, extend CI, and validate wheel/source distributions independently.
- Preserve the research snapshot and paper reference ledgers.

# Changelog

## 0.3.0 - 2026-08-19

- Added schema-2 `.amspd` checkpoints with exact finite candidate-frontier state, data-derived seed masks, quadtree leaves, selected seed identities, and random-generator state.
- Added exact continuation parity for unchanged searches, explicit `frontier-exact` and `warm` classifications, and chained resume support.
- Added overlap-blended tiled reconstruction and the checksummed `.amspdt` archive with optional resumable tile checkpoints.
- Added cosine, linear, and uniform overlap windows plus multiworker tile execution.
- Added automatic finite-grid method and budget selection with rate-distortion, SSIM-rate, RMSE, and target-RMSE objectives.
- Added recursive batch processing with single or tiled execution, per-file failure records, content hashes, run fingerprints, and safe skip-existing behavior.
- Added model comparison and expanded inspection of saved search state.
- Added CLI commands `resume`, `tiled`, `tune`, `batch`, and `compare`.
- Hardened tiled archives with region coverage, overlap, embedded-shape, sparse-index, finite-value, and checksum validation.
- Preserved stored source images across chained single and tiled resumes unless deliberately omitted.
- Expanded package verification and tests for continuation, tiling, tuning, batching, archive compatibility, and CLI lifecycles.

## 0.2.0 - 2026-08-19

- Added the checksummed `.amspd` decomposition archive with dense, sparse, and approximation-only residual modes.
- Added model decoding, inspection, packet tables, tree records, frontier records, and portfolio trial export.
- Added public component APIs for packet cores, singular completion, tree optimization, portfolio reconstruction, finite pixel closure, and baseline comparison.
- Added CLI commands: `decompose`, `decode`, `convert-archive`, `inspect`, `complete`, `baselines`, `benchmark`, and `reproduce-paper`.
- Bundled compact packet histories and reference ledgers for exact four-case paper replay from an installed package.
- Added a built-in benchmark runner and structured CSV/JSON output.
- Added full package integration verification, model tamper detection, legacy-archive conversion, and 25 package tests.
- Renamed the semantic meaning of the large generic preset to `paper-scale`; `paper` remains a compatibility alias.
- Documented two archived Lagrange-proxy diagnostic differences while retaining exact final-result comparison.


## 0.1.1 - 2026-08-18

- Rebuilt the manuscript as a focused 78-page final edition.
- Separated analytic statements from floating-point implementation verification.
- Regenerated principal tables from the authoritative JSON outputs.
- Corrected exact and bounded RMSE labels and grayscale/RGB storage formulas.
- Restored references and moved full source listings out of the manuscript.
- Added a self-contained LaTeX source package, manuscript audit, and reproducible build scripts.
- Preserved the original 147-page archival edition unchanged under `research/original`.

## 0.1.0 — 2026-08-18

- Converted the final AM-SPD research release into an installable Python package.
- Added a stable high-level API with core, SPD, tree, and finite portfolio stages.
- Added image file input and output, exact residual archives, and a command-line interface.
- Added unit tests, CI workflows, examples, publishing scripts, and repository documentation.
- Preserved the complete original final source and verification snapshot under `research/original`.
