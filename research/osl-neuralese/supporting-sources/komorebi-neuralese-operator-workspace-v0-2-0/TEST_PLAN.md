# V0.2 test and verification plan

## Unit and integration tests

The 53-test suite covers:

- complete and disjoint 60/20/20 map partitions
- deterministic split sampling for every family
- correct row-table and column-latent composition order
- SPD metric positivity, determinant normalization, conditioning, whitening,
  and gradient flow
- independently encoded composition targets and train-only filtering
- zero-loss exact-oracle closure and nonzero reversed-order controls
- neighboring-depth and G-norm stability schemas
- cross-context patch construction and on-manifold controls
- balanced transport depths, no h0 anchors, shuffled fitting, metric pullback,
  and operator intertwining

## Primary completeness checks

Verification fails if any of the following is missing or inconsistent:

- all 8 arms × 10 seeds
- all five specified transport pairs
- all 26 gate records
- complete coordinate split audit
- matching package version, code digest, protocol digest, and split digest
- primary protocol bytes differing from the result copy
- any checksum or manifest file mismatch
- prior v0.1.1 archive hash mismatch

## Reproducibility check

The `metric_composition`, seed-200 cell was retrained and reevaluated. Parameters
and metrics were exactly identical. The receipt is stored at
`results/v0.2.0/preregistered_primary/REPRODUCIBILITY.json`.

## Scientific decision

All primary gates are evaluated even when earlier gates fail. Missing or
nonfinite metrics fail closed. Operational completion and scientific success are
separate fields.

