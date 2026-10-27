# Neuralese learned-checkpoint causal-completion probe v0.1.0

Author: Komorebi P.

This package is a posthoc mechanistic reanalysis of sealed learned
checkpoints. It asks two narrow questions suggested by the causal-completion
account of Neuralese:

1. Does a finite-horizon reachable/observable quotient remove any learned
   latent directions, or do apparently null directions become visible after
   recurrence?
2. Are repeated D4 identity-loop failures explained by radial gain, angular
   holonomy, or both?

The primary census uses every official v0.4 checkpoint: four matched arms and
three training seeds. The secondary bridge analysis uses the separate v0.3
hard-QR Operator Workspace lineage and must not be described as v0.4's direct
parent.

This is not new training, a replication, or confirmatory evidence. The v0.4
pilot's retained A15 assay failure remains unchanged.

## Result

Across all twelve v0.4 checkpoints and all 32 primary contexts, the reachable
behavioral rank is seven at horizon zero and the full ambient rank twelve from
horizon one through four. The tested persistent additive quotient of dimension
at most eight is therefore unsupported. Hard-polar recurrence keeps repeat-16
absolute log radial gain below `2.90e-5`, yet p95 oriented loop angles reach
`0.72` to `0.97` radians. The residual defect is angular/projective holonomy,
not radial instability alone.

## Package map

- `REPORT.md`: concise synthesis and interpretation
- `ANALYSIS_PROTOCOL.md`: frozen estimands, thresholds, and evidence boundary
- `VERIFICATION.md`: replay, review, and hash record
- `v04_probe/`: primary PyTorch-faithful probe, tests, report, and full JSON
- `v04_crosscheck/`: independent restricted-reader NumPy cross-check
- `v03_probe/`: separately labeled hard-QR bridge analysis

Each probe directory contains its exact invocation. Reproduction requires the
two source archives named and hashed in `ANALYSIS_PROTOCOL.md`, Python 3.12,
NumPy, and CPU PyTorch for the primary and v0.3 scripts. The independent v0.4
cross-check uses NumPy and the Python standard library only.
