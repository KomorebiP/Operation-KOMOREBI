# Analytic implicit function development record

Source: `formalization/PolynomialAnalyticImplicit.lean`.

The source was compiled with the pinned portable Lean 4.34.0-rc2 kit,
`check_low_memory.py`, one thread, a 240-second timeout, the shared development
import directory, warning-as-error behavior, and the default heartbeat limits.
The application-path compatibility adapter was used. No kernel modifications,
custom axioms, admitted proofs, or increased heartbeat limits were introduced.

The following records summarize the actual compiler output returned during
this task. Separate raw log files were not retained for these development
attempts. This note does not claim to reconstruct complete raw logs.

| Attempt | Scope and result | Repair |
|---|---|---|
| 1 | Generic graph helper: rejected because the two continuous-linear-map application lemmas inherited an unused `CompleteSpace` instance, and the composite derivative expression left the solved/free dimensions ambiguous. | Moved the completeness assumption after the elementary projection/injection declarations and supplied the composite map dimensions explicitly. |
| 2 | Generic graph helper: rejected at analytic and derivative composition because the injection map's coercion was not definitionally the `join 0` function. Other errors concerned preimage membership, inference for `interior_subset` and the product rectangle, and a rewrite of the parameter equality that replaced occurrences inside the point itself. | Used the proved injection application identity at composition points, supplied explicit preimage and rectangle types, and replaced the broad parameter rewrite with a `congrArg` equality followed by `join_parts`. |
| 3 | Generic graph helper: passed, with no compiler output. | No change needed. |
| 4 | Full polynomial specialization: rejected because the simplifier did not unfold the evaluation expression into the expected function equality. The final differentiability corollary also inherited an unused completeness assumption. | Stated the evaluation-function equality explicitly with `change`; omitted completeness for the elementary differentiability corollary. |
| 5 | Full module: rejected because `omit` appeared after a declaration documentation comment, where the parser expected a theorem declaration. | Moved `omit` before the documentation comment. |
| 6 | Full module: passed, with exit status 0 and empty compiler output. | Final development compile. |

The final module contains two continuous-linear-map definitions and five
proved theorems. The complete theorem `exists_analytic_implicit` uses only the
actual polynomial system, its exact root, and invertibility of its actual
solved Jacobian as mathematical hypotheses. It constructs the solution map
and open neighborhoods, proves the exact local graph characterization and
analyticity throughout the parameter neighborhood, and proves the strict
Fréchet derivative with matrix `-(J⁻¹ * K)` at the original parameter.

No hypothesis was weakened or strengthened to bypass a failed proof. The
intermediate generic graph helper takes analytic and strict-derivative inputs;
the final polynomial theorem establishes those inputs from actual polynomial
evaluation and its formal partial derivatives. The existence of an analytic
solution map is a conclusion, not an assumption.

The independent fresh release gate is the authoritative reproducible
verification record for the frozen source. This note records development
history only and does not substitute for that gate.
