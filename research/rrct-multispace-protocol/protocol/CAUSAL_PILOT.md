# Qwen2.5-0.5B Causal Multi-Space Pilot

## Target

The first confirmatory target is intentionally narrower than a global-workspace claim:

> A task-local rank-8 causal mediator was independently identified, aligned with an active Jacobian verbal frame, formed by an output-blind fuzzy packet, and reused by three downstream operations.

Failure is informative. Success does not establish a model-general workspace or training-time emergence.

## Frozen shared-state task

Every minimal pair contains both possible values so an instrument cannot succeed by detecting which word appeared in the prompt.

Example:

```text
Bindings: cedar means otter. willow means violin.
The active key is cedar.
Several unrelated facts follow.
Hold the active value.
```

At the same saved prefix state, branch into three unseen queries:

1. report the active value
2. classify it as animal or instrument
3. apply a new rule such as animal to north and instrument to south

The role-swapped pair changes only the active key. Keys, values, classifications, and rule outputs are single tokens with matched token counts.

## Data separation

| Split | Size | Purpose |
|---|---:|---|
| Jacobian corpus | 128 generic sequences | Two disjoint 64-sequence lens fits |
| Predictive corpus | 256 unrelated sequences | Whitening and future-update discovery |
| Intervention corpus | 32 neutral prompts | Randomized causal transmission geometry |
| Calibration | 40 binding pairs × 3 queries | Lock one layer pair, rank, and fuzzy temperature |
| Sealed holdout | 160 binding pairs × 3 queries | Confirmatory causal tests |
| Routine controls | 160 cases | Equivalence test for preserved automatic processing |

The existing 12-prompt lens is forbidden for scientific inference.

## Three independent estimator families

### V — external verbal alignment test

Fit two half-corpus Jacobian lenses at layers 8, 12, 16, and 20 with target layer 23. Require split-half transport and readout stability before merging. Construct sparse nonnegative active cones with k at most 8 for the pilot. V is never used to choose the mediator.

### D — temporal prediction family

Whiten source activations and fit rank-reduced prediction of later residual innovations. Remove current-token, position, length, and residual-carry baselines. Combine future-update prediction and separated-layer persistence as one family.

### K — randomized causal transmission family

On unrelated prompts, inject antithetic covariance-matched perturbations at candidate source layers and measure induced mediator changes. Then perturb the mediator and measure later-state effects at the marker and next four positions. Verify local linearity at three small amplitudes. K identifies directions that are both writable and readable without vocabulary or answer information.

The mediator S is frozen from the common rank-8 geometry of D and K. Only afterward is its excess sparse reconstruction by V tested against covariance- and spectrum-matched rotated dictionaries.

## Output-blind fuzzy formation

At the locked source layer, decompose the marker update into attention-head contributions and fixed hash-assigned MLP contribution groups. The fuzzy learner receives only component activity and later residual changes. It receives no token IDs, lens matrices, unembedding, queries, answers, output logits, or holdout outcomes.

Temperature is chosen from 0.25, 0.5, 1, and 2 using discovery prediction error and membership stability only. Optimization seeds are sensitivity repeats and are not treated as independent models.

## Causal factorial

Both donor directions are tested under these conditions:

1. clean
2. upstream fuzzy donor-packet transplant
3. transplant plus restoration of the clean S mediator component
4. transplant plus restoration of a covariance-matched non-S component
5. direct donor patch inside S
6. direct donor patch inside matched non-S geometry
7. full donor marker patch as an upper bound
8. membership-permuted fuzzy control

Real donor differences are used. Arbitrary semantic steering directions are not substituted for donor patches.

## Confirmatory gates

All must pass:

- D and K overlap exceeds the 99th percentile of at least 999 block-preserving nulls
- convergence replicates across discovery halves
- S has excess sparse V-frame reconstruction over matched rotated frames
- active-minus-inactive V readout reverses under role swap
- direct S donor patches move all three downstream queries toward the donor
- fuzzy packet transplant outperforms membership-permuted transplant
- restoring clean S attenuates treatment more than restoring matched non-S geometry
- both donor directions work
- the 95% upper confidence bound on routine-task loss is below five percentage points

The treatment-by-restoration interaction is the primary mediation statistic. A percentage attenuation ratio alone is not accepted.

## Resource estimate

The expected runtime on the RTX 3070 Ti Laptop GPU is approximately 40 to 100 minutes, potentially up to two hours under thermal throttling. Model inference is microbatched on GPU. Covariance, whitening, null generation, and eigendecomposition run on CPU with disk-backed checkpoints.

