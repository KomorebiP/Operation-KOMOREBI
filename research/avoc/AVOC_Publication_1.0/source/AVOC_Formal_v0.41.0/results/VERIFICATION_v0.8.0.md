# AVOC Formal v0.8.0 verification record

## Environment

- Lean: `4.34.0-rc2`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- project version: `0.8.0`

## Source metrics

- theorem/lemma/proposition/corollary declarations: **333**
- definition-like declarations including abbreviations: **159**
- non-audit AVOC Lean source lines: **6845**
- non-audit Lean source files counted by the release metric script: **42**

## Build

A `lake clean` was followed by resumable bounded build slices.  Each next build
was started only after the previous bounded child had exited.  The final slice
rebuilt the v0.8 history/archive tail and reported:

```text
Build completed successfully (1055 jobs).
```

A cached confirmation subsequently reported the same successful count.

## Post-clean checks

PASS under `-DwarningAsError=true`:

- `AVOC/Audit.lean`
- `AVOC/HistoryExamples.lean`
- `AVOC/ArchiveExamples.lean`
- `AVOC/HistoryArchive.lean`

Source scan found zero occurrences of project `axiom`, `sorry`, `admit`, or
unsafe theorem-like declarations under the declared scan pattern.

## Negative tests

All eight deliberately false files returned nonzero compilation status:

- `FalseApproximateZero.lean`
- `FalseArchiveReplay.lean`
- `FalseBayesPosterior.lean`
- `FalseBlackwellReverse.lean`
- `FalseCompression.lean`
- `FalseFeasibilityMerge.lean`
- `FalseProposalPromotion.lean`
- `FalseRetrospectiveRecovery.lean`

The new `FalseArchiveReplay.lean` reaches the intended mathematical contradiction:
a true-favoring replay proved to have posterior mass `9/10` is falsely asserted
to have mass `1/10`; Lean leaves the goal `False` and rejects the file.

## Axiom boundary

No AVOC-specific axiom declaration is present.  The expanded `#print axioms`
audit reports only standard Lean/mathlib foundations such as `propext`,
`Classical.choice`, and `Quot.sound` on the new load-bearing declarations where
applicable.

## Interpretation boundary

These results verify exact finite symbolic models.  They do not establish that a
real LLM transcript admits the declared compiler, that real likelihoods are
correct, or that the chosen research-state/reward coordinates are empirically
sufficient.
