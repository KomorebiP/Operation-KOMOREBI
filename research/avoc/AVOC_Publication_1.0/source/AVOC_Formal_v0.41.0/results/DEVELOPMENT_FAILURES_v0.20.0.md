# AVOC v0.20.0 — failures and repairs

## Lean proof-script failures, repaired

1. In a case-split acknowledgement proof, the success equality had already been reduced to reflexivity. Passing the original equation produced a type mismatch. The branch was repaired with the correct reflexivity witness and recompiled.
2. The abstract atomic-store proof had the analogous reduced equality problem. A natural-number projection needed an explicit `change`, and a product-equality projection required an explicitly typed equality. These were fixed and dependent modules rebuilt.
3. A concrete example attempted `decide` before exposing a closed natural-number goal; the free job parameter prevented reduction. An explicit `change` isolated `0 ≠ 1`, then the ordinary kernel-checking decision proof succeeded.
4. Early dependent-module import failures occurred while a prerequisite new module had not yet compiled. They were not counted as mathematical negative tests. The completed graph was rebuilt successfully.

## Execution/environment failures, handled

5. An attempted interactive container session failed with `StreamingExecNotEnabledContainerError` before runtime assembly executed. Ordinary bounded calls were used; no result was inferred from that failed launch.
6. Host execution limits interrupted build/test batches. Child-process state was checked and unfinished files were rerun. In particular, an interrupted negative batch was completed in later slices; every final negative record is substantive and has no timeout.

## Evidence-collector failure, repaired

7. The first v0.20 source scanner naively treated every `admit` token as a proof placeholder. That falsely rejected the legitimate `.admit` workflow action constructor in inherited code. The collector was changed to the prior context-aware tactic/declaration scan while retaining an independent declaration census and full axiom audit. No mathematical source was changed to suppress a real placeholder.

## Intended injected failures

The crash suite intentionally kills coordinators with SIGKILL, substitutes stale records or changes inputs, and creates incomplete initialization. These are recorded test inputs, not successful operational runs. A committed operation followed by a kill is recoverable. An intent without a durable result remains an explicit abort, not a claimed successful recovery.

The suite exercises transaction rollback after the store write and after the result write, before commit. No partial authoritative admission is counted. It does not physically cut electrical power or claim a complete SQLite/OS proof.

## Remaining limitations are not hidden failures

No proof of universal Python/SQLite correspondence, arbitrary crash retry, hostile rollback resistance, arbitrary Lean-file checking or physical-cost optimality was attempted and declared complete. See PROOF_BOUNDARY.md. New mathematical sources and runtime source pins are frozen before the final complete collector and packaging checks.
