# AVOC Formal v0.5.0 verification record

- Lean: `leanprover/lean4:v4.34.0-rc2`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- project version: `0.5.0`
- theorem/lemma/proposition/corollary declarations: **220**
- definition/structure/inductive/abbreviation declarations: **106**
- non-audit AVOC source lines: **4559**

## Build

The inherited v0.4 source first rebuilt successfully against the exact pinned cache. After the v0.5 modules were reconstructed and individually checked, `lake clean` was run. The aggregate target was rebuilt in resumable bounded slices. The final clean slice reported:

```text
Build completed successfully (1042 jobs).
```

A later cached confirmation also returned normally with the same 1042-job success summary.

## Post-clean checks

- `AVOC/Audit.lean` under `-DwarningAsError=true`: PASS.
- `AVOC/ApproximateExamples.lean` under `-DwarningAsError=true`: PASS.
- source scan for `sorry`, `admit`, AVOC `axiom`, and unsafe theorem/lemma/def declarations: zero hits.

## Negative tests

Each file must fail compilation, and each did:

- `FalseCompression.lean`: exit 1.
- `FalseProposalPromotion.lean`: exit 1.
- `FalseFeasibilityMerge.lean`: exit 1.
- `FalseBlackwellReverse.lean`: exit 1.
- `FalseApproximateZero.lean`: exit 1, reaching the intended false claim that opposite Bool point masses have zero `L1` distance.

## Axiom boundary

No AVOC-specific axiom declaration is present. `#print axioms` for load-bearing new declarations reports only standard Lean/mathlib foundations such as `propext`, `Classical.choice`, and `Quot.sound` where applicable.

This validates the formal finite models and their stated implications. It does not establish empirical parameters for production AI systems.
