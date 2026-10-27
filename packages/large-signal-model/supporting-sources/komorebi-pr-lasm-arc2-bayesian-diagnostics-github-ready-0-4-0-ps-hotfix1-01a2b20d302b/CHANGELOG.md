# Changelog

## 0.4.0 PowerShell hotfix 1 — 2026-08-19

- Replaced bare `conda` shell-function calls in every PowerShell runner with a shared executable resolver.
- Added discovery through `CONDA_EXE`, `_CONDA_EXE`, `Get-Command`, and common Miniconda, Anaconda, Miniforge, and Mambaforge locations.
- Added an explicit `-CondaExecutable` override to every runner.
- Made all Conda failures terminating and prevented stale `$LASTEXITCODE` values from masking command-not-found errors.
- Added input-file and diagnostic-atlas existence checks.
- Added static regression tests covering the complete PowerShell runner set.

## 0.4.0 — 2026-08-18

- Replaced shape-only failure messages with exact cell-level diagnostics.
- Added wrong-cell counts, cell agreement, mismatch bounding boxes, mismatch
  coordinates, and expected-to-predicted color-confusion ledgers.
- Added a browsable problem/solution diagnostic atlas with complete training
  demonstrations, held-out inputs, expected outputs, both attempts, mismatch
  overlays, and Bayesian posterior records.
- Added static SVG problem/solution sheets, JSON task records, JSONL archives,
  CSV output ledgers, residual category maps, and a near-miss index.
- Added automatic failure-stage classification separating operator or
  representation coverage from posterior selection and few-shot generalization.
- Added marker-conditioned recoloring, enclosed-region filling, periodic
  resizing, Kronecker motif variants, modular affine tiling, object-chain
  packing, object-shape or hole-conditioned recoloring, and periodic stripe
  construction.
- Added exact-fit support mass and exact-fit candidate counts to output
  posteriors.
- Updated two-attempt selection to prioritize posterior-supported exact-fit
  outputs before approximate fallbacks.
- Refit all family, route, and Bayesian ridge calibration parameters on the
  fixed 799-task public-training calibration partition.
- Increased the locked 201-task parameter-holdout result from 28/219 to 32/219
  exact outputs.
- Added a same-candidate-portfolio Bayesian-versus-deterministic comparison and
  candidate-oracle ledger.

## 0.3.0 — 2026-08-18

- Implemented exact spatial, color, Fourier, Haar, polyphase, and
  object-relational coordinate atlases.
- Added deterministic macro, meso, and micro signal states while preserving the
  exact archive separately.
- Replaced deterministic posterior-like ranking with a finite Bayesian program
  posterior.
- Added hierarchical Beta priors for program families and route-conditioned
  reliability.
- Added Bayesian ridge reliability calibration with predictive uncertainty.
- Added posterior distributions over programs, families, atlases, resolutions,
  and predicted outputs.
- Added posterior entropy, disagreement, and machine-readable diagnostics.
- Added restricted residual-refinement programs and family-diverse posterior
  pruning.
- Added a deterministic public-training calibration and parameter-holdout
  protocol.

## 0.2.0 — 2026-08-18

- Combined the ARC-KAT MDL baseline with exact projector and structural channels.
- Added repeated-shape, unique-symmetry, color-contrast, and anomaly relations.
- Added hard-isolated Kaggle execution and deterministic fallbacks.
- Added complete GitHub packaging, tests, freeze metadata, and benchmark ledgers.
- Recorded the first frozen public-evaluation audit without post-evaluation tuning.
