# Test plan

## Automated tests

The suite covers:

1. exact D4 relations, conjugation, target generation, and slot randomization
2. model tensor contracts and known affine transport recovery
3. exact anchor-closed table execution and metric isometry
4. projective normalization preserving finite linear predictions
5. rank-safe float64 decoder centering
6. scale-invariant projective anchor and conformal-metric defects
7. projective tangent Jacobian annihilating the radial direction
8. finite-horizon observability detecting delayed visibility
9. metric-polar isometry
10. switched Feshbach detection of delayed cross-generator return
11. depth-128 exact anchor closure and depth-256 semantic-chart closure
12. checkpoint-shape compatibility of the projective model

## Frozen-checkpoint pilot

`run_stability_experiment.py --profile pilot` evaluates the two original terminal and relation checkpoints under five variants, paired episode streams, four operator families, deep causal edits, null cycles, observability, and cross-seed exact intertwining.

## Projective-training pilot

`run_projective_training.py --profile pilot` trains two fresh terminal-only projective models on D4 lengths 1–4 and evaluates depths through 256, four families, deep interventions, null cycles, and cross-seed transport. `--reuse-checkpoints` repeats evaluation without retraining.

## Confirmation requirements

Before a confirmatory claim:

- freeze a new archive, source digest, seeds, thresholds, and cycle/suffix banks
- use at least ten fresh model seeds
- evaluate through depth 512 or higher
- include uncertainty intervals and multiplicity correction
- add a generic recurrent architecture and a second implementation
- separate terminal-only, anonymous-structural, and exact-compiler arms
- report projective holonomy even when endpoint accuracy passes
- treat arbitrary-permutation transfer separately from structured-family transfer
