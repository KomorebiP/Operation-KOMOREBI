# Block 06 — Actual failures and repairs

All entries below are development/configuration failures, not a mathematical counterexample to a claimed source theorem. Deliberately false controls are a separate category and must fail for their intended proof diagnostics.

## Six failed development compilations

### 1. KomorebiPhysics.RefinementCancellation — 20260913T203022699630Z

Return code: 1. A simp rewrite involving one_smul ran recursively. Replaced the backward simplification with explicit scalar factorization and cancellation using a proved nonzero denominator.

Receipt and failed source/log: `verification/development/block06/20260913T203022699630Z/`.

### 2. KomorebiPhysics.RefinementAsymptotics — 20260913T203211510142Z

Return code: 1. Scaled-power and function-valued scalar-action forms did not normalize to the expected expression. Two unused normed-space variables were also rejected by warnings-as-errors. Reordered the power/division rewrite, used the exact function-valued proof term, explicitly omitted unused variables, and specified the limiting-set argument.

Receipt and failed source/log: `verification/development/block06/20260913T203211510142Z/`.

### 3. KomorebiPhysics.RefinementBounds — 20260913T203442256041Z

Return code: 1. Unfolding a recursively defined bound at an unknown depth left a match expression. Used the defining successor equation without unfolding the unknown recursive argument.

Receipt and failed source/log: `verification/development/block06/20260913T203442256041Z/`.

### 4. KomorebiPhysics.RefinementAsymptotics — 20260913T203634752200Z

Return code: 1. The guessed API name Filter.Eventually.false did not exist. Obtained a witness from the nontrivial filter and eliminated the resulting False directly.

Receipt and failed source/log: `verification/development/block06/20260913T203634752200Z/`.

### 5. KomorebiPhysics.RefinementExamples — 20260913T203800785659Z

Return code: 1. The first source formula mixed inferred natural scalar multiplication with real scalar multiplication. Annotated the scalar as a real number.

Receipt and failed source/log: `verification/development/block06/20260913T203800785659Z/`.

### 6. KomorebiPhysics.RefinementExamples — 20260913T203935383705Z

Return code: 1. A cubic polynomial rewrite did not match the implicit coefficient one. Instantiated the general cubic response and normalized one_mul explicitly.

Receipt and failed source/log: `verification/development/block06/20260913T203935383705Z/`.

## Interrupted preliminary control batch

A shell command containing a sequence of control checks exceeded the outer tool's execution window before the full sequence completed. The first false-weight control produced its expected proof error, but the batch did not establish seven passing rejection tests. No completed cumulative verifier was launched by that interrupted shell command. The partial batch is explicitly recorded as incomplete in `verification/block06_control_precheck/INTERRUPTED.json`.

The cumulative verifier was then launched as a separately tracked process with bounded per-command limits and polled for its completed report. The interrupted precheck is not counted as a passing audit.

## Recovery and retained evidence

The portable runtime's seven parts and combined archive checksum passed restoration. The prior 402-theorem Block 05 baseline passed a fresh full audit. All four new modules subsequently compiled without admissions or custom axioms. The final cumulative result and any fresh-extraction result are authoritative only when their status is PASS. No timeout is promoted to a successful proof check.

All six failed source snapshots remain in the development evidence tree. The active mathematical files contain the repaired proofs. Subsequent successful revisions are retained rather than overwriting the failed receipts.

## Audit execution refinement

The initial cumulative run successfully rebuilt every local mathematical module and began the complete axiom inventory as separate module batches, each reimporting the whole aggregate. It was intentionally cancelled before completion after a separate bounded all-at-once probe successfully printed and validated exactly all 579 names with only the allowed axioms (98.70 seconds under concurrent load). That initial cumulative report is marked CANCELLED_INCOMPLETE under `verification/block06_initial_batched_audit/`; it is not a pass certificate. Its verifier snapshot and logs are retained.

The revised cumulative verifier audits the same complete name inventory in one bounded Lean invocation, checking exact output-name equality and every axiom dependency as before. No mathematical source or proof obligation was removed. The final run starts over with fresh compilation of every local module and the full negative-control suite. Its status is authoritative only when completed. The revised per-command cap is 240 seconds; a timeout still fails the contract. The probe is supplemental evidence, not a substitute for that final run.

## Negative-control batching

The first complete-inventory axiom run rebuilt all mathematical files and validated all 579 axiom outputs, then entered a slow per-file control loop. A second bounded probe combined the 41 unchanged control bodies under separate namespaces with their imports hoisted. It produced exactly 41 mapped diagnostic messages, one intended rejection per control, with no unassigned diagnostics (46.19 seconds under concurrent load). The incomplete per-file run was then intentionally superseded and retained at `verification/block06_initial_perfile_controls/`; it is not reported as a pass.

The final verifier restarts from a clean local build, rechecks every proof and axiom dependency, and uses the same namespace-isolated control batch. Its contract rejects a mere nonzero exit without a matching diagnostic in every control's mapped line range. Every original control source remains byte-identical. The generated batch, line map, source hashes and complete output are retained. The final fresh-extraction recheck also compares the individual control records. The two superseded audit runs are distinct from the six failed development compilations and the outer-timeout precheck.

## Completed production result

The final cumulative audit completed with PASS after fresh compilation of all 29 mathematical modules and the aggregate, exact validation of all 579 axiom outputs, intended rejection of all 41 individually mapped controls, and verification of all 25 prior-source hashes. This completed result is in `verification/final/report.json`; the earlier incomplete attempts remain separate. A fresh-extraction result is delivered outside the unchanged ZIP.
