# Reader's guide to the Lean companion

87/87 complete proposition mappings, 0 partial and 0 unformalized.

Start from `KomorebiLSM.lean`, which imports every mathematical module in dependency order. Individual modules use small explicit theorem interfaces. The indexed names, source lines and source hashes for all 87 registered propositions are listed in `COVERAGE.json`.

## The mathematical route

The first part constructs realizations, predictive completions and observable behavior spaces. It distinguishes an exact population realization from finite sampled data and derives minimality, uniqueness and coordinate transport under explicit rank and spanning assumptions.

The probability part constructs positive cones, finite lifts and density instruments. It derives nonnegative normalized record laws and posterior updates on positive-evidence histories. Mass preservation and cone preservation are separate obligations. Robust certificates cover an entire declared uncertainty family, with genuine full-domain bounds.

The learning part links observable tables to state and operator reconstruction. Noise, coverage, conditioning and domain assumptions remain visible in the theorem signatures. Finite tables do not silently establish a global rank bound, an unknown cone or missing interventions.

The dependent-data results use actual filtrations and conditional expectations. The predictable residual certificate covers arbitrary measurable probability spaces, exact interval widths including zero width, and prospectively registered countable budgets. Covered adaptive actions target encountered contexts using recorded positive propensities. Observation-law comparison uses actual causal kernels and expected-under-P local costs.

The curved certificate results preserve orientation as well as squared Lorentz inequalities. Strict rational Bernstein searches retain degree and strict-margin hypotheses. A feasible certificate proves validity of its declared family; it does not manufacture statistical coverage for an unmodified generating process.

The regression result constructs the real Gaussian mixture and its all-time crossing event, then derives the exact determinant-dependent ridge ellipsoid. Predictable regressors, the actual conditional noise bound and the true-parameter norm bound remain hypotheses. No excitation or hidden-state discovery is inferred.

The final structured-learning results propagate rowwise moment confidence through an actual inverse moment map. Worked curved-state and rational rectangle examples keep observation-law error, certificate validity, same-trajectory coverage and selected-stage validity connected through explicit interfaces.

## Important interfaces

| Topic | Entry point |
|---|---|
| Proposition correspondence | `COVERAGE.md`, `COVERAGE.json` |
| Actual conditional residuals | `PredictableResidualP66.lean` |
| Covered adaptive actions | `CoveredActionBoundaries.lean` |
| Causal observation-law comparison | `ObservationLawComparison.lean` |
| Oriented robust margins | `RobustOrientedMargin.lean` |
| Conditional ridge regression | `RegressionConfidence.lean` |
| Observable moment confidence | `ObservableMomentConfidence.lean` |
| Current verification | `verification/current/report.json` |

Only interfaces present in the current root import graph are mathematical source. Files under `verification/` are evidence and tooling unless imported explicitly by the checker. Invalid examples under `negative_controls/` must fail and are never imported by the mathematical root.

The current inventory contains 2887 named theorems, including 331 worked-example results. Read each theorem's actual hypotheses before applying it. The frozen monograph and source register remain the reference for registered proposition scope.
