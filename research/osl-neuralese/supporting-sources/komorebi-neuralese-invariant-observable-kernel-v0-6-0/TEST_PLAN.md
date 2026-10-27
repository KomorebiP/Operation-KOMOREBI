# Test plan

The first three sections below are inherited v0.1-v0.3 coverage. The v0.4
packet-closure additions and sealing checks are listed afterward.

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

## v0.4 packet-closure coverage

The v0.4 suite additionally checks:

1. hard-polar operator isometry and raw-versus-polar model contracts;
2. exact rank-eight anchor projectors and rank-four ambient complements;
3. endpoint-action rejection, proposal-stream closure, and construction-bank
   exclusion of both reserved terminal-action groups;
4. exhaustive held-out packet enumeration, including the empty continuation;
5. finite-path complement-return and demonstration-aligned composition losses;
6. exact norm/angle-matched state controls and reachable-state specificity;
7. relative-conjugacy-matched orthogonal operator controls and independently
   emitted cross-context controls;
8. validation of supplied post-seal intervention banks, including rejection of
   corrupted tables and identical primary/control banks;
9. exact ambient-projector rank, idempotence, self-adjointness, and
   energy-matching receipts;
10. deterministic switched-word bank completeness and context counts; and
11. mutation tests for every registered profile, arm, threshold, source digest,
    and preregistration-contract field.

The package verifier independently reconstructs and authenticates the retained
pilot chain from contract and source digests through checkpoints, the checkpoint
seal, evaluation banks, results, environment receipt, and run-completion marker.
