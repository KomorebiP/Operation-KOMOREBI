# Failure log — Richardson solver block

No failed draft, timeout or interrupted invocation is counted as a proof check.
The machine-readable final receipt records **11 completed failed checks**:
**nine compiler/elaborator/linter failures and two process timeouts**. A separate
interrupted invocation has an attempted source but no completion receipt.

1. Streaming container execution was unavailable. The same runtime was restored
   with the supported ordinary execution path, preserving chunk/combined hashes.
2. The first recurrence source imported a nonexistent Mathlib module name. It was
   replaced with existing matrix/trace and rational algebra imports.
3. An overly broad `Mathlib.Tactic` import stalled an early GeometricFuel call.
   The outer invocation ended without its receipt. Specific tactic imports were
   substituted; the resulting narrow module compiled. A concurrent inherited
   FDGainSampler check exceeded its 40-second process cap. Its final isolated
   retry passed. The final evidence uses only successful matching source hashes.
4. GeometricFuel retained an unnecessary nonnegativity hypothesis and triggered
   the unused-variable linter. Removing it strengthened the statement; the final
   source compiled.
5. The first spectral-vector proof unfolded a continuous linear map before a
   rewrite could match. An explicit type/expression change fixed the elaboration.
6. The first exact-score proof simplified the producer before applying its packet
   energy identity. Controlled unfolding and the proved identity fixed it.
7. The first executable-search proof needed explicit branch equations and the
   shifted-iterate theorem. Its successor used deprecated if_pos/if_neg names,
   which warnings-as-errors rejected. Current ite_eq_left/ite_eq_right proofs
   compiled without weakening the statements.
8. The first posterior bridge reached a 25-second process cap. A longer isolated
   retry exposed elaboration-heartbeat exhaustion caused by underspecified
   candidate/fuel arguments. Explicit arguments removed the search bottleneck,
   and the unchanged intended statement then compiled successfully.
9. The initial scalar instance lacked a finite DecidableEq instance for the
   candidate record and had a rational-to-real target-normalization mismatch.
   A separate executable equality instance and explicit casts fixed these. The
   first equality-instance proof had an injEq elaboration error, corrected with
   an explicit decidable_of_iff proof. Both concrete solver return equations now
   pass kernel reduction.

The final 64 modules each have matching successful final-source receipts. The
complete axiom audit covers all 294 theorem/lemma declarations. The three separate
negative proof controls reject a false arithmetic equality, a placeholder proof,
and a false claim that a known-successful solver returns None. Their expected
rejection is a test result, not one of the development failures above.

The official Mathbox manifest-validator executable was not available in the
working filesystem. The packaged integrity verifier checks final-source receipts,
source/output/direct-dependency hashes and complete axiom coverage. No claim of
running the unavailable official validator is made.

The exact Python producer has explicit resource caps and can return RESOURCE_LIMIT.
Such a bounded outcome does not contradict the ideal exact-arithmetic theorem,
and no certificate is exported from a capped outcome. The tests verify this rule.
