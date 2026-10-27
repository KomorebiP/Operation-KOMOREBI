# Block 11 mathematical audit

**Primary verdict: incomplete, with the smallest missing implication.** P33 and P34 have complete kernel-checked formal proofs; P32 still lacks the implication from the noisy table hypotheses to the singular-subspace projection-gap estimate. This verdict concerns completion of the requested P32–P34 block, not a refutation of the manuscript.

Review type: self-review against Foundations 1.0.0 §§33–35 and its frozen proof register. No independent referee is claimed. Current source acceptance: all 243 stages passed. Exact-ZIP fresh-run acceptance is recorded separately.

| Obligation | Evidence | Status |
|---|---|---|
| P33 strict gap gives a two-sided square inverse | `core_inverse_laws` | Passed: compile, axiom audit and kernel replay |
| P33 exact residual identities | `core_error_identity`, `core_fitted_residual`, `core_fitted_identity` | Passed: compile, axiom audit and kernel replay |
| P33 true, fitted, checked-fitted denominators | Three `core_*_bound` theorems | Passed: compile, axiom audit and kernel replay |
| P34 actual prediction residual budget | `prediction_error` | Passed: compile, axiom audit and kernel replay |
| P34 strict positivity and exact normalized identity | `fitted_mass_positive`, `normalized_residual` | Passed: compile, axiom audit and kernel replay |
| P34 two denominator bounds | `normalized_error_checked`, `normalized_error_margin` | Passed: compile, axiom audit and kernel replay |
| P34 actual path and contraction | `filtering_step`, `filtering_path`, `filtering_uniform` | Passed: compile, axiom audit and kernel replay |
| P32 coordinate lower bound and inverse from an explicit gap | `coordinate_lower`, `coordinate_injective`, `coordinateEquiv`, `coordinate_inverse_bound` | Passed: compile, axiom audit and kernel replay |
| P32 singular-value perturbation/rank separation | Not implemented | Not addressed |
| P32 leading-subspace tail and equal-rank projection norm identity | Not implemented | Not addressed |
| P32 orthonormal-basis decoder formula | Not implemented | Not addressed |
| Boundary examples | Eight named example theorems | Passed: compile, axiom audit and kernel replay |
| Full cumulative source verification | 243 stages, 80 metadata checks | Passed |
| Exact ZIP fresh extraction and verification | External delivery JSON | Consult actual report |

Dependencies: inherited orthogonal pseudoinverse and adjoint-norm bounds → P33; continuous linear norm bounds and exact scalar normalization → P34 one-step inequalities → inherited P18 recurrence → pathwise bounds. Orthogonal Pythagoras + supplied projection gap → P32 conditional lower bound → injectivity + equal dimensions → constructed continuous inverse. No arrow from noisy table data to that supplied gap has been proved here.

P33 uses the inherited variational `rowGain` convention, with its proved unit-sphere characterization. It does not claim an additional bridge to Mathlib's sorted singular-value API. P34 drops unused cone structure and proves the norm statements under their sufficient radius and mass hypotheses; it does not infer a valid fitted probability cone. P32 keeps the missing hypothesis explicit in both source and coverage.

Frozen source and register hashes remain unchanged. The former 78 proof modules, 1,304 declaration records and 72 rejection controls remain unchanged. The original 0.10.0 ZIP and its hash are included for lineage.

Proofreading self-review covers only the four new modules and current release documents. Mathematical notation was translated to Lean's scalar action and continuous linear maps; no manuscript mathematical tokens were edited. Remaining mathematical issues are listed above, not hidden as copyediting corrections.

Accepted source evidence: 83 compilation targets, one executable-example stage, one declaration-axiom stage, 82 kernel replays and 76 expected proof rejections. All 1,338 declaration records were audited; only propext, Classical.choice and Quot.sound are allowed. No subprocess timeout occurred. P32 is still incomplete despite all implemented proof modules passing.
