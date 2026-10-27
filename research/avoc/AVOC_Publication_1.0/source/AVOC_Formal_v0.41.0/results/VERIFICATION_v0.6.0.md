# AVOC Formal v0.6.0 verification record

- Lean: `leanprover/lean4:v4.34.0-rc2`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- project version: `0.6.0`
- theorem/lemma/proposition/corollary declarations: **263**
- definition/structure/inductive/abbreviation declarations: **124**
- non-audit AVOC source lines: **5373**

## Build

The v0.6 Bayesian modules were first checked incrementally against the exact pinned v0.5 environment. After the new aggregate, audit entries, examples, and negative test were installed, `lake clean` was run.

The clean aggregate was rebuilt in bounded resumable slices. Each new slice was started after the previous build child exited. The final slice rebuilt the Bayesian control/evidence/example tail and reported:

```text
Build completed successfully (1046 jobs).
```

A subsequent cached confirmation also returned normally with the same 1046-job success summary.

## Post-clean checks

- `AVOC/Audit.lean` under `-DwarningAsError=true`: PASS.
- `AVOC/BayesianExamples.lean` under `-DwarningAsError=true`: PASS.
- source scan for `sorry`, `admit`, AVOC `axiom`, and unsafe theorem/lemma/def declarations: zero hits.

## Negative tests

Each file must fail compilation, and each did:

- `FalseCompression.lean`: exit 1.
- `FalseProposalPromotion.lean`: exit 1.
- `FalseFeasibilityMerge.lean`: exit 1.
- `FalseBlackwellReverse.lean`: exit 1.
- `FalseApproximateZero.lean`: exit 1.
- `FalseBayesPosterior.lean`: exit 1, reaching the intended false conclusion `0 = 1` after the checked theorem that perfect `true` observation assigns zero posterior mass to `false`.

## Axiom boundary

No AVOC-specific axiom declaration is present. `#print axioms` for the load-bearing Bayesian declarations reports only standard Lean/mathlib foundations such as `propext`, `Classical.choice`, and `Quot.sound` where applicable.

## Interpretation boundary

This verifies the finite rational Bayesian objects and implications declared in the source. It does not establish that a real LLM supplies calibrated Bayesian probabilities, that a scientific likelihood model is correctly specified, or that posterior probability is equivalent to formal proof status.
