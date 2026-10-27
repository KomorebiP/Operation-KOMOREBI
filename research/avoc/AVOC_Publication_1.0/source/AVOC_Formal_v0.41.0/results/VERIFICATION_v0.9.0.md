# AVOC Formal v0.9.0 verification record

- Lean: `leanprover/lean4:v4.34.0-rc2`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Project version: `0.9.0`
- Non-audit theorem/lemma/proposition/corollary declarations: **365**
- Non-audit definition/structure/inductive/abbreviation declarations: **166**
- Non-audit AVOC Lean source lines: **7,501**
- Non-audit AVOC modules: **46**

## Clean build

A `lake clean` was followed by resumable host-time-bounded build slices.  Each slice reused only artifacts produced by the same clean build.  The final slice rebuilt the v0.9 AVOC tail and reported:

```text
Build completed successfully (1066 jobs).
```

A subsequent cached confirmation also returned:

```text
Build completed successfully (1066 jobs).
```

## Post-clean checks

- `AVOC/Audit.lean` under `-DwarningAsError=true`: PASS.
- `AVOC/ApproximateBayesian.lean`: PASS.
- `AVOC/BayesianInstability.lean`: PASS.
- `AVOC/ApproximateBayesianCompression.lean`: PASS.
- `AVOC/RateDistortionLower.lean`: PASS.
- `AVOC/RateDistortionExamples.lean`: PASS.
- Source scan for `sorry`, `admit`, AVOC-defined `axiom`, and unsafe theorem-like declarations: zero hits.

## Deliberately false negative suite

All ten files must fail compilation and all ten did:

- `FalseApproximateZero.lean`
- `FalseArchiveReplay.lean`
- `FalseBayesPosterior.lean`
- `FalseBlackwellReverse.lean`
- `FalseCompression.lean`
- `FalseFeasibilityMerge.lean`
- `FalseProposalPromotion.lean`
- `FalseRareEvidenceStable.lean`
- `FalseRateDistortionMerge.lean`
- `FalseRetrospectiveRecovery.lean`

The two new tests fail at the intended mathematics.  `FalseRareEvidenceStable` reaches `2 = 0`; `FalseRateDistortionMerge` leaves `False` on the separated endpoint states.

## Axiom boundary

No AVOC-specific axiom declaration is present.  `#print axioms` on the new load-bearing theorems reports only standard Lean/mathlib foundations such as `propext`, `Classical.choice`, and `Quot.sound` where applicable.
