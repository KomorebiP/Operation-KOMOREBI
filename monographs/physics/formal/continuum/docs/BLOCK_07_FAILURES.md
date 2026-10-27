# Block 07 — Actual failures and repairs

The completed production audit is PASS. Its result is not inferred from development activity or historical reports. Seven individual development compilations failed; all failed snapshots, commands, logs and receipts are retained under `verification/development/block07/`. Five subsequent individual development compilations succeeded. The fresh Block 06 baseline and the final Block 07 cumulative run both completed successfully.

## Failed compilation groups

| Module | Failed attempts | Failure and repair |
|---|---:|---|
| PositiveEffects | 2 | Derivative-expression normalization and `RCLike.re`/`Complex.re` rewriting failed. Rewrote the actual composed derivative explicitly and supplied the real-inner-product symmetry equality at the required type. |
| EffectRefinement | 2 | Warnings-as-errors rejected unused finite-type section hypotheses. Removed the unused assumptions with explicit `omit`, without weakening mathematical premises. |
| WeightedEffects | 1 | Simplification changed complex-cast real scalar actions too early; an opaque matrix application and unused-section warning also blocked compilation. Used controlled scalar/inner-product rewrites, a fully applied matrix equality, and removal of unused hypotheses. |
| EffectExamples | 2 | Exact norm/inner-product simplification, rational conjugates, derivative typeclass normalization, and an unavailable derivative helper name caused errors. Expanded the actual Hermitian dot product, used controlled normal forms and the existing continuous-linear-map derivative interface. |

These were proof-script/API/lint failures, not discovered counterexamples to the final mathematical statements. No admission, custom axiom, or unchecked evaluation was introduced to resolve them.

## Source retrieval and metadata

Files returned the source text but not the requested image of physical PDF page 27. The exact included master was rendered locally and the image inspected. Page 28 was inspected from the returned page image. No OCR or substitute source was used. The source checksum did not change.

The inherited v0.6.0 `lakefile.toml` still advertised version 0.5.0. The package version was corrected to 0.7.0. Dependency revisions were not changed; all 29 old mathematical source files remained byte-identical. This is a package-metadata correction, not a proof migration.

## Failed receipts

- `verification/development/block07/20260913T212236547284Z/receipt.json` — `KomorebiPhysics.PositiveEffects`, exit 1, 6.420 seconds.

- `verification/development/block07/20260913T212309689079Z/receipt.json` — `KomorebiPhysics.PositiveEffects`, exit 1, 6.747 seconds.

- `verification/development/block07/20260913T212710044359Z/receipt.json` — `KomorebiPhysics.EffectRefinement`, exit 1, 5.605 seconds.

- `verification/development/block07/20260913T212729204387Z/receipt.json` — `KomorebiPhysics.EffectRefinement`, exit 1, 4.717 seconds.

- `verification/development/block07/20260913T212951655113Z/receipt.json` — `KomorebiPhysics.WeightedEffects`, exit 1, 5.987 seconds.

- `verification/development/block07/20260913T213213297068Z/receipt.json` — `KomorebiPhysics.EffectExamples`, exit 1, 18.421 seconds.

- `verification/development/block07/20260913T213327042906Z/receipt.json` — `KomorebiPhysics.EffectExamples`, exit 1, 17.131 seconds.

## Audit interpretation

All 34 active mathematical modules and the aggregate compiled in the complete production run. The 688-name axiom audit passed. All 50 deliberately false controls were rejected at their designated source ranges with the expected proof diagnostic. These expected rejections are successful negative tests, not failures of the active library. A timeout or import failure is never counted as rejection.

The fresh-extraction result is recorded outside the immutable ZIP by the archive-check report. Do not infer that external run from this internal narrative. Earlier blocks' historical failed and incomplete runs remain in their separate evidence directories and are not relabeled as passes.
