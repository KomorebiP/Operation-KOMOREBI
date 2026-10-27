# Deliberately invalid Lean inputs

These files must fail. They are never imported by the active mathematical library.

The four preserved controls reject a false arithmetic equality, an admitted proof, removal of skewness, and the wrong Hamiltonian current sign. Block 02 adds five controls: omission of the intrinsic term, omission of either moving-frame term, reversal of the commutator sign, and the claim that arbitrary invertible transport is self-adjoint.

The new controls use the exact active shear/corner witnesses. They are not unsupported universal assertions. Each must fail with the specified mathematical diagnostic. The verifier rejects import, missing-object, and environment failures as negative-control successes.

The complete nine-file result is recorded in verification/final/report.json. The positive exact disequality theorems are in KomorebiPhysics/DeformationExamples.lean and are included in the axiom audit.


## Block 06 additions

Seven additional controls bring the cumulative count to 41. They import the checked RefinementExamples module and must produce the intended `unsolved goals` proof diagnostic.

| Control | Deliberately false claim |
|---|---|
| WrongRefinementWeight | First weight 4 cancels the linear term in the source's first step. |
| WrongRefinementQuadraticSign | The surviving quadratic has positive rather than negative sign. |
| RefinementExtraCancellation | The degree-three coefficient vanishes after two levels. |
| RefinementExtraOrder | The first-level quadratic response is O(h^3). |
| RefinementUnitRatio | The constant is preserved at singular ratio b=1. |
| RefinementNoiseContraction | The exhibited unit noise has output norm at most one. |
| WrongRefinementThirdDenominator | The third-level denominator is 7 instead of 21. |

An interrupted preliminary shell batch is retained separately and does not count as a passing control audit. Only the completed cumulative verifier result determines rejection success.

## Cumulative execution in Block 06

The source files remain unchanged. The cumulative verifier hoists their imports and copies each body into a separate namespace in one generated Lean batch. Each control has recorded source hashes and an exact line range. The batch must return an error, **and every body must emit its own designated diagnostic in its own range**. Unassigned header/import errors and timeouts fail the audit. The final report includes all individual mappings; the fresh-extraction audit compares them. The negative batch is not an active mathematical module and is never imported by the proof library.
