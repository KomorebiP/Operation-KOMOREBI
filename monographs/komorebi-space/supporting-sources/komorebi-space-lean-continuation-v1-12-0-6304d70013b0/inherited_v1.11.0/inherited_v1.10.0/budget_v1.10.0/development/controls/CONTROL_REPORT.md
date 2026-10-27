# WR03–WR05 boundary control record

The final local set contains four positive compiler fixtures and six deliberately invalid fixtures. Attempt 002 passed all expected outcomes. Each invalid fixture fails at a concrete false mathematical obligation, with both `unsolved goals` and `⊢ False` in the diagnostic. No invalid fixture depends on a missing import, unknown symbol, syntax error, or resource failure.

The machine manifest is `formal/tests/control_manifest.json`. `LOCAL_ACCEPTANCE.json` binds it to source hashes and the final receipt. The compiler used one thread, warnings as errors, and disabled automatic implicit variables. Each numbered run preserved its source snapshots, full diagnostics, commands, environment, and dependency-object hashes. The four current budget module objects were copied into each attempt before checking, so a simultaneous development rebuild could not alter those imported objects during the run.

| Fixture | Required behavior |
| --- | --- |
| `positive/ZeroBudget.lean` | Generic zero-budget profile, zero-to-zero quantitative bound, dual attainment at zero budget, zero-residual attainment at arbitrary nonnegative budget |
| `positive/ScalarProfiles.lean` | Constant zero-map profile, identity exact feasibility, positive identity residual, convex interpolation including a zero-budget endpoint |
| `positive/SharpDualCertificate.lean` | Literal greatest dual value, strict exclusion on a scalar identity example, zero residual witness |
| `positive/RobustnessBoundaries.lean` | Zero-budget uncertainty bound, sharp valid operator allowance, nominal lower certificate, and proved counterexamples showing necessity of operator error, data error, and the budget multiplier |
| `negative/DropDualNormRestriction.lean` | Reject witness `z=2` at the unit-ball obligation |
| `negative/DropBudgetPenalty.lean` | Reject the penalty-free claim `1 ≤ 0` for identity, datum one, budget one |
| `negative/DropOperatorUncertainty.lean` | Reject deleting `η M` with zero versus identity, identical datum one, budget one |
| `negative/DropDataUncertainty.lean` | Reject deleting `δ` with zero operators, data one and zero, budget zero |
| `negative/NegativeBudgetAttainment.lean` | Reject a minimizer claim for radius minus one |
| `negative/DropCandidateBudget.lean` | Reject using correction one in the zero-budget ball |

## Failures and corrections

Attempt 001 accepted two positive files and rejected all six negatives at their intended mathematical obligations. Two positive files failed for implementation details: scalar simplification did not evaluate `|2-1|`, the identity adjoint needed an explicit rewrite, and a `convert ... <;> norm_num` sequence triggered an unnecessary-sequence linter. The corrections used `norm_num`, the named identity-adjoint lemma, and a single subsequent tactic. Attempt 002 accepted all four positive fixtures and retained exactly the intended six rejections.

One intermediate patch did not apply because its expected indentation omitted a bullet marker. The patch tool made no edits in that failed call. The corrected patch was applied before attempt 002.

`RobustnessBoundaries.lean` reuses the WR05 owner's already verified scalar boundary proofs, with two additional positive uncertainty-certificate instances. No numerical approximation is used in any fixture. The theorem statements and counterexamples are exact Lean propositions over real scalars or arbitrary complete real Hilbert spaces.

## Acceptance boundary

These are local development checks. The verifier must rerun the same manifest against the frozen integrated release objects. This record does not replace the final integrated replay, the axiom policy audit, or independent review of the production theorem types. The verifier separately retains the existing policy rejection controls.
