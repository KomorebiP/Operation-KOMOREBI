# Failure ledger — v0.27

## Recorded development invocations

The preserved development/ATTEMPTS.jsonl contains 44 actual invocations, including 17 nonzero compiler returns. Each record contains module name, source hash at the time, command, elapsed time, return code and a log path. A failed historical source hash is not counted as an accepted theorem. Only the final sources and fresh replay determine release status.

## Main failures and repairs

1. Some continuity lemmas initially inherited unused topology hypotheses. Warnings-as-errors rejected them. Hypotheses were reduced or locally omitted rather than suppressing the linter.
2. Inference on a representation wrapper did not identify the intended topology on the actual kernel. The continuous two-cocycle predicate was given explicit domain/codomain/topology arguments.
3. Deprecated Set.restrict and old conditional simplification syntax triggered warnings. They were replaced by current pinned APIs (`Set.domRestrict`, `dite_eq_left`).
4. Nested relative quotient rewrites did not elaborate with inferred continuity proofs. An explicitly named datum, typed section-continuity proof, and direct iff applications resolved the mismatch.
5. A relative-averaging normalization had overlapping inherited additive instances. Subtype extensionality reduced the identity to the underlying ring before additive normalization.
6. Finite-quotient composition required an explicit `Continuous LQ` annotation.
7. A matrix scalar-unit simplification did not close automatically. The finite example provides the explicit inverse 5I of 2I modulo 9 and checks both products using `decide`.
8. API probes were moved out of active src into development. Their checks are exploratory, not release theorem declarations.

## Mathematical warning found during construction

Normalizing a provisional section only by changing its value at the identity of a nondiscrete source may destroy continuity. The accepted construction normalizes on the discrete residual unit group and composes with the continuous residual representation. No discontinuous section is used.

## Runtime and final replay

The seven-part portable runtime assembly passed its hashes and the archive extraction completed. No runtime timeout or corrupted Mathlib object was found in this turn.

The fresh release replay was deliberately executed in bounded batches: 8 modules, then 8, then 5 source modules plus the axiom audit. Intermediate PARTIAL statuses are not counted as complete passes. The final RESULT.json records every observed zero return code and all 72 expected axiom reports.

No source-level `sorry`, `admit`, custom `axiom`, custom `opaque`, `native_decide`, or `unsafe` was permitted. Mathematical nonvanishing examples are successful tests, not verification failures.
