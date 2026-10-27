# Bayesian large signal model implementation ledger

Version 0.4.0 implements the finite static PR-LASM object

```text
L = (X, U, E, P, Z, G, B, R, C)
```

for ARC-AGI-2. The mapping from the mathematical object to executable code is
explicit.

| Component | Runtime implementation | Contract |
|---|---|---|
| `X` | `entry.py` grid parser and validator | Finite grids with dimensions 1 through 30 and colors 0 through 9 |
| `U` | `ARCAtlasAnalyzer` in `atlas.py` | Spatial, color, unitary Fourier, orthonormal Haar, polyphase 2/3/4, and object-relational coordinates |
| `E` | Color, phase, object, row, column, and feature selectors | Deterministic coordinate extraction |
| `P` | Color and polyphase masks plus object packets | Exact finite packet reconstruction where an inverse atlas is declared |
| `Z` | `macro`, `meso`, and `micro` states | Fixed dimensions 48, 96, and 192, kept separate from the exact archive |
| `G` | `RuleCandidate` portfolio in `entry.py` | Typed base, projector, structural, residual-refinement, and fallback programs |
| `B` | `BayesianProjectorResolvedLargeSignalModel` | Normalized posterior over programs, families, atlases, resolutions, and output grids |
| `R` | Route analysis plus restricted residual lookup programs | Residual type changes proposal support without replacing exact verification |
| `C` | Program execution, `exact`, and submission validation | A solved output must match dimensions and every cell exactly |

## Bayesian evidence path

For each candidate, the implementation computes:

```text
exact demonstration rate
shape agreement
cell agreement
multi-atlas residual vector
program complexity
family reliability
route-conditioned reliability
atlas compatibility
resolution compatibility
Bayesian reliability mean and variance
```

The final log weight is a finite sum of the corresponding log likelihood and
log prior terms. Log weights are normalized with log-sum-exp. Programs that
produce the same test grid have their posterior mass combined before the two
attempts are selected.

## Calibration boundary

The embedded calibration was fitted from the public ARC-AGI-2 training split
only. A deterministic task-ID hash assigned 799 tasks to calibration and 201
tasks to a parameter holdout. The holdout solutions are not read by the fitting
stage. Earlier project versions had already examined the complete public
training corpus, so the holdout is described only as a machine-level parameter
holdout.

## Deliberate omissions

ARC-AGI-2 contains independent static transformations. The following
interactive PR-LASM components are therefore not activated:

- state-action transition graphs
- episodic replay
- exploration policies
- action planning
- cross-environment persistent memory

They remain appropriate for ARC-AGI-3, not for static grid induction.
