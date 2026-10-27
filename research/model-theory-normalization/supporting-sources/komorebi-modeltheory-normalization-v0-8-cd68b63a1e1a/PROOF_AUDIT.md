# Self-review of v0.8 mathematical statements

Primary verdict: proved as written for the accepted Lean statements and their
explicit arithmetic trace model. The written cost composition is NOT a Lean
runtime theorem. This review is not independent external refereeing.

| Obligation | Verdict | Evidence |
|---|---|---|
| Genuine Bezout identity, signed inputs and zero remainder | Passed | euclidCoeff_correct, smallBezout_correct, concrete examples |
| Coefficient bounds and individual product tracking | Passed | euclidCoeff_bounds, euclidPeak_bound, insertionPeak definition |
| Integer rather than rational span preservation | Passed | boundedInsert_correct and determinant-one inverse |
| Same canonical answer despite different raw coefficients | Passed | boundedNormalizedInsert_eq using reduced uniqueness |
| Negative floor-division bounds | Passed | abs_ediv_bound, signed finite tests |
| Normalize lower basis before using m-bound | Passed | normalizationPeak_bound explicitly uses normalized lower basis |
| Constant peak budget across arbitrarily many queue steps | Passed | StateCorrect and Reduced propagated in runPeak_bound |
| r=0,d=0,zero inputs | Passed within precise signatures | General proofs, nil/zero cases, inherited total correctness |
| Word order and intended observational semantics | Passed relative to literal matrices | Existing rowRight/FiniteCodeCertificate bridge plus new equality |
| Actual reference outputs, not supplied search witnesses | Passed | 203 decide +kernel computations of boundedPrimeDiscover |
| Every runtime implementation temporary covered | Out of scope | Internal division/gcd implementations, allocations and source-row evaluation excluded |
| Costed interpreter projection and full machine bit-cost theorem | Not addressed | COST_MODEL.md gives a separate written array-model derivation |
| Python/extractor/source-to-human-problem fidelity | Finite audit only | Independent literal comparisons, exact port tests, not verified extraction |
| Broad novelty or held-out discovery | Out of scope | No such claim |

The proof-only monitor is written adjacent to the corresponding recursion and
tracks the indicated coefficient operations. A compiler-level trace refinement
is not inferred merely because the definitions compile. The falsity of the stronger
'all temporaries are <=m' claim is demonstrated at m=4,d=2 with actual peak12.
