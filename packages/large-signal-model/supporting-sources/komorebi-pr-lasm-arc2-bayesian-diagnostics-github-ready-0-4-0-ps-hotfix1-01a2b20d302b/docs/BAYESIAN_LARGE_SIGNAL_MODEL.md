# Bayesian Projector-Resolved Large Signal Model

## Finite model

For a static ARC task, the implemented model is the tuple

```text
L = (X, U, E, P, Z, G, B, R, C)
```

where:

- `X` is the finite grid space
- `U` is the exact coordinate-atlas family
- `E` is the family of coordinate selectors
- `P` is the pulled-back projector family
- `Z` is the macro, meso, and micro statistical state hierarchy
- `G` is the typed program grammar
- `B` is the Bayesian posterior over programs and mechanisms
- `R` is the residual classifier and refinement grammar
- `C` is the exact execution and reconstruction contract

The interactive memory and action graph used by the broader PR-LASM world model
are omitted because ARC-AGI-2 supplies independent static transformations.

## Exact archive versus statistical state

The implementation makes a strict distinction between:

```text
complete coordinate record  ≠  compressed statistical state
```

The complete record supports exact reconstruction and exact program checking.
The statistical states support program calibration, route inference, and
uncertainty estimation. A small prediction error in a projected state is never
reported as an exact grid result.

## Likelihood

Each candidate is executed on every demonstration. The model records:

- exact demonstration rate
- output-shape agreement
- cell agreement
- total incorrect cells
- residual norms in spatial, color, Fourier, Haar, polyphase, and object atlases

Shape, cell, and exact agreement are converted to Beta-binomial marginal
likelihood terms. This makes exact execution evidence dominate an approximate
visual resemblance while retaining graded evidence when no exact program is
available.

## Hierarchical priors

For family `f`, the calibration stores:

```text
p(success | f)
p(success | task_route, f)
```

as Beta distributions. Their posterior means contribute to candidate ranking.
Their finite concentration prevents a rare family with one success from being
treated as certain.

## Bayesian reliability regression

A Bayesian ridge model is fitted to candidate held-out success using:

- exactness and shape evidence
- cell accuracy
- complexity
- family and route priors
- atlas compatibility
- resolution compatibility
- all atlas residuals
- the task route distribution
- the task atlas distribution
- the task resolution distribution
- a fixed task summary vector
- candidate family identity

The model retains a coefficient covariance matrix and predictive variance. The
logistic-normal approximation maps the latent reliability distribution to a
candidate success probability.

## Calibration protocol

The model calibration script reads only the public ARC-AGI-2 training split.
Task identifiers are assigned deterministically to an 80 percent calibration
partition and a 20 percent parameter holdout using a BLAKE2 hash. Parameters
are fitted on the calibration partition. The holdout is used to report
selection behavior, not to update the saved model.

This is a machine-level parameter holdout. It is not described as a historically
unseen research benchmark because earlier project versions were already tested
on the full public training corpus.

## Residual refinement

A seed program is refined only through typed low-dimensional keys. For example:

```text
(input color, predicted color) → corrected color
(row mod N, column mod N, predicted color) → corrected color
(input color, predicted color, local object degree) → corrected color
```

Every mapping must be consistent across all demonstrations. The mapping size is
bounded. Local residual families receive separate empirical priors because an
exact demonstration fit does not imply strong test generalization.

## Uncertainty outputs

Optional diagnostics expose:

- posterior program probabilities
- posterior family probabilities
- posterior atlas probabilities
- posterior resolution probabilities
- posterior output probabilities
- posterior entropy
- model disagreement
- Bayesian calibration mean and variance

These records make it possible to distinguish a concentrated exact solution
from a diffuse collection of incompatible hypotheses.

## Claim boundary

Version 0.3.0 is a real finite Bayesian PR-LASM implementation for static ARC
tasks. It does not implement universal program induction, a learned visual
foundation model, interactive memory, or general intelligence. Its performance
is limited by the typed grammar and by the ambiguity of few-shot exact fits.
