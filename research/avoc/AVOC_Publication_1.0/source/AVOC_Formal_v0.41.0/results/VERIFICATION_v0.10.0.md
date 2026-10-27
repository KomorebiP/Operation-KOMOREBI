# AVOC Formal v0.10.0 verification record

- Lean: `4.34.0-rc2`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Project version: `0.10.0`
- Theorem/lemma/proposition/corollary declarations: **406**
- Definition/structure/inductive/abbreviation declarations, including `noncomputable def`: **176**
- Non-audit AVOC Lean source lines: **8,088**
- Non-audit modules: **50**

## Build

`lake clean` was followed by resumable bounded `lake build AVOC` slices.  The final clean graph reported:

```text
Build completed successfully (1070 jobs).
```

A cached confirmation also reported 1070 successful jobs.

## Post-clean checks

- `AVOC/Audit.lean` with `-DwarningAsError=true`: PASS.
- `AVOC/Specification.lean`: PASS.
- `AVOC/FiniteEvents.lean`: PASS.
- `AVOC/VerifierEnsemble.lean`: PASS.
- `AVOC/VerifierExamples.lean`: PASS.
- source scan for `sorry`, `admit`, AVOC project `axiom`, and unsafe theorem-like declarations: zero hits.

## Deliberately false negative tests

All **12 / 12** negative tests were rejected post-clean.

The two new v0.10 tests fail for the intended mathematical reasons:

- `FalseSemanticRecovery.lean`: the proposed constant downstream decoder cannot recover the erased `true` Bool state;
- `FalseIndependentProduct.lean`: perfectly correlated verifier failures have joint probability `1/2`, not the product `1/4`, and the attempted factorization reduces to `False`.

## Axiom boundary

The first draft of the verifier examples used `native_decide` for small finite computations.  The axiom audit exposed the generated native-evaluation axioms.  Those proofs were replaced with ordinary kernel-reduced finite proofs before release.  The final audited declarations contain only standard Lean/mathlib foundations such as `propext`, `Classical.choice`, and `Quot.sound` where applicable.
