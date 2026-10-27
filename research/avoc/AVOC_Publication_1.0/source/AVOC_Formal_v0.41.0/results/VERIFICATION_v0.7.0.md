# AVOC Formal v0.7.0 verification record

- Project version: `0.7.0`
- Lean: `4.34.0-rc2`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Theorem-like declarations: **296**
- Definition-like declarations: **105**
- Non-audit Lean source lines: **5918**

## Build

A clean aggregate rebuild was completed in resumable slices because individual host calls are time bounded. The final slice rebuilt the new v0.7 tail from scratch and reported:

`Build completed successfully (1050 jobs).`

A subsequent cached confirmation also reported the same successful 1050-job target.

## Post-clean checks

- `AVOC/Audit.lean` with warnings as errors: PASS.
- `AVOC/Retrospective.lean` with warnings as errors: PASS.
- Source scan for `sorry`, `admit`, AVOC project axioms, and unsafe theorem-like declarations: zero hits.

## Deliberately false tests

All seven negative tests returned nonzero status:

- `FalseApproximateZero.lean`
- `FalseBayesPosterior.lean`
- `FalseBlackwellReverse.lean`
- `FalseCompression.lean`
- `FalseFeasibilityMerge.lean`
- `FalseProposalPromotion.lean`
- `FalseRetrospectiveRecovery.lean`

The new retrospective negative test reaches the intended false equality and leaves goal `False`.

## Axiom boundary

No AVOC-specific axiom declaration is present. New audited v0.7 theorems report only standard Lean/mathlib foundations (`propext`, `Classical.choice`, `Quot.sound`) where applicable.
