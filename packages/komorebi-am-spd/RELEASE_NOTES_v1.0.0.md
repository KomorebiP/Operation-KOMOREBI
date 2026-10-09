# AM-SPD 1.0.0

AM-SPD 1.0.0 is a stable release of the finite image decomposition and reconstruction system. It retains moving geometry packets, local singular subspaces, budgeted trees, global refitting, portfolio selection, resumable checkpoints, tiling, tuning, batch processing, and paper replay.

The release fixes correctness gaps found in fresh audits. Morphology thresholds remain compatible with scikit-image 0.24–0.26, and Git checkout rules preserve historical source bytes on Windows. Integer brightness is preserved without observed min/max scaling. Floating input now has an explicit finite normalized contract. Configuration and resume budgets reject fractional or invalid values. Duplicate directions no longer turn roundoff into an added subspace. Every accepted downstream seed respects its declared scalar proxy budget. Archive verification fails safely on malformed numerical data. Batch output collisions are rejected before writing, generated output trees are excluded from recursive inputs, and repeat runs require both compatible settings and the requested artifacts.

The current package code is MIT licensed under Komorebi P. The preserved historical snapshot retains its recorded notices and terms. Schema-1 and schema-2 single models and schema-1 tiled models remain readable. The mathematical research snapshot and paper reference tables are preserved.

## Validation

Current raw reports and computation provenance are under `validation/`. The release checklist identifies local validation separately from future hosted CI or publication. Historical verification distinguishes fresh calculations from checks of archived reported results. Paper replay recomputes downstream stages using checksummed archived source/core fixtures and a frozen v0.3 backend. It checks the bundled reference invariants; it does not rerun the original geometry-discovery experiment. Ordinary v1.0 decomposition uses the corrected backend.

## Stable scope

The release is a CPU finite-raster reconstruction package. A retained unthresholded residual permits normalized floating-point reconstruction up to roundoff. An approximation alone need not be exact or compact. The integer-budget optimizer is exact for the declared combinatorial tree model in mathematical theory; its numerical implementation uses float64 SVD, rank thresholds, and Pareto comparisons with tolerances.

For downstream methods, `parameter_budget` controls added singular/local scalar proxy cost, excluding geometry-core coefficients. It is not an entropy-coded storage limit. Checkpoint parity requires the retained source and frontier, unchanged settings, and a compatible numerical environment. Different library versions or hardware need not produce bitwise identical searches.

Tiling retains the complete source and global arrays. It reduces local solve sizes, and it is not an out-of-core streaming engine. GPU kernels, a statistical denoising model, and entropy coding remain separate development work.

