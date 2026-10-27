# Progress — Sufficient Resolution v0.4.0

**13 September 2026. Standalone program; not the Papers I–XII theorem census.**

| Measure | v0.3.0 | v0.4.0 | Added |
|---|---:|---:|---:|
| Explicit theorem/lemma declarations | 190 | 272 | 82 |
| Production proof modules | 16 | 22 | 6 |
| Explicitly named declarations | 263 | 357 | 94 |
| Predecessor proof files changed | — | 0 of 16 | All preserved |

Counts include helpers and exact examples, not independent discoveries. The saved
v0.3.0 proof state was freshly rebuilt, axiom-audited and replayed in Lean's kernel
before this extension. Historical logs are not presented as that new run.

## Completed contracts

| Layer | Position |
|---|---|
| Exact resolution | Compatible-kernel representation, reconstruction and composition. |
| Compression defects | Factorization, coherence, powers and two-stage composition. |
| Linear globalization | Actual obstruction quotient and induced transport. |
| Behavioral quotient | All-future quotient and exact kernel-inclusion minimality. |
| Discrete memory | Hidden elimination, closure equivalences and prepared/all-state distinction. |
| Finite memory certificate | Monic-annihilator and hidden-dimension finite certificate. |
| Arbitrary split memory | Canonical ker(C) realization; no orthogonality. |
| Finite observation horizon | Stabilization by dim ker O, exact plateau and bounded distinguishing words. |
| Minimum exact dimension | Surjective image comparison and dimension minimality. |
| Finite observation model | Actual realizable range, induced dynamics/readout and all-future fidelity. |
| Finite minimality certificates | Observation generation, exact intertwining and readout certify minimality. |
| Exact approximate-model algebra | NEW: all-word telescoping, output split, composition and chronological transport terms. |
| Quantitative sufficiency | NEW: heterogeneous whole-map defect bounds, two-rate formulas, output and initial-state errors. |
| Stable approximation | NEW: nonexpansive linear estimate and contractive uniform estimate for arbitrary words. |
| Approximate behavioral equivalence | NEW: bounded future observation difference for states sharing q. |
| Multilevel approximation | NEW: both stages' errors propagated with representation norms. |
| Coordinate conditioning | NEW: split re-encoding preserves outputs, while changing norm constants explicitly. |
| Sharpness and counterexample | NEW: scalar bound attained; small one-step error alone allows unbounded future error. |
| Rational implementations | Exact finite tests; Python minimizer and bound evaluator not formally verified. |

The selected quantitative known-operator block is complete under its stated norm
hypotheses. It is not a proof of approximate minimality or model discovery from data.

## Remaining major obligations

| Direction | Remaining work |
|---|---|
| Continuous-time memory | Matrix-exponential/Volterra identity and closure, including the prepared/all-state distinction. |
| Hilbert-space globalization | Orthogonal obstruction/inconsistency split, conditioning and closed-range hypotheses. |
| Stronger stability certificates | Derive appropriate norms/block-growth certificates from additional model structure; no spectral-radius shortcut for arbitrary switching. |
| Approximate minimality/data | Identify unknown operators with justified uncertainty; approximate state-dimension criteria and robust algorithms. |
| Admissible realization | Positivity, probability normalization, integrality and native constraints. |
| Executable verification | Formally verify exact elimination and arbitrary rational certificate checking. |
| Nonlinear/categorical transport | Actual structures, composition, descent and admissibility theorems. |
| Arithmetic realization | Domain-specific existence remains separate; no global Langlands correspondence. |

No overall percentage is assigned because the wider program has no frozen,
commensurable target inventory.

## Next selected block

Continuous-time finite-dimensional hidden-state elimination: derive the exact
matrix-exponential/Volterra memory equation from full dynamics, then connect its
kernel and semigroup defect to the discrete results. Preserve all initialization
and existence hypotheses explicitly.
