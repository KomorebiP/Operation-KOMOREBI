# Failure ledger — v0.33

Only the completed fresh replay in RESULT.json is release proof evidence. Failed drafts and interrupted processes are not passes.

## Runtime and wrapper failures

- Offline archive assembly passed all seven part hashes and the combined SHA-256. The first extraction wrapper timed out after assembly. A complete second tar extraction returned exit code 0 before proof verification. No truncated extraction was treated as a complete runtime.
- An attempted interactive shell failed with StreamingExecNotEnabledContainerError. Verification used ordinary bounded subprocess calls.
- One development dependency batch exceeded its outer 120-second limit during ContinuousGaugeLiftCriterion. No verdict was recorded for the interrupted module. It was rerun separately and returned zero, then compiled again in the fresh release replay.
- The first new verifier invocation had an incorrect parent filename caused by a broad version-string replacement. It failed before compiling a source module. The parent filename was corrected to the exact v0.32 archive. The corrected verifier checked the parent hash and every staged dependency source.

## Rejected Lean drafts

- `SimultaneousPowerFiltration`: return code 1; diagnostics in `development/logs/SimultaneousPowerFiltration.1789195970818719997.log`.
- `SimultaneousOperatorNorm`: return code 1; diagnostics in `development/logs/SimultaneousOperatorNorm.1789196061885524042.log`.
- `SimultaneousPrimaryNorm`: return code 1; diagnostics in `development/logs/SimultaneousPrimaryNorm.1789196133170025731.log`.
- `SimultaneousUnipotentExamples`: return code 1; diagnostics in `development/logs/SimultaneousUnipotentExamples.1789196612321070135.log`.
- `SimultaneousUnipotentExamples`: return code 1; diagnostics in `development/logs/SimultaneousUnipotentExamples.1789196644004567449.log`.

The failures concerned application parentheses, a nonexistent Mathlib.Tactic.Omega import (replaced by Lean.Elab.Tactic.Omega), reassociation before a unit cancellation, unfolding of a target definition, and ambiguous endomorphism annotations in the matrix example. One ambiguous example draft hit the heartbeat limit. The accepted examples use explicit endomorphism types and pass the ordinary heartbeat setting.

## Verification scope

The fresh direct closure contains 44 source modules plus AxiomAudit. All returned zero; all 47 new named constants were checked for axiom dependencies. Pinned Mathlib objects are reused. No full historical-branch replay, new-kernel verification, or independent expert review is claimed.
