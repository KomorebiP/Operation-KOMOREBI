# Observation recorder core

`AVOC/ObservationRecorder.lean` contains 37 proved theorems and compiled with warnings as errors in `recorder_build07.log`.

The state machine uses one operation-id namespace for pending intents and terminal records. Begin and terminal exact replays are idempotent, conflicting key or outcome reuse is rejected, unbegun terminal records are rejected, and late begin replay does not reopen a completed operation. Pending intent is separate from calibration observations. An unfinished terminal is rejected. Fault termination consumes its pending intent but contributes no statistical observation.

For every accepted run from the empty state, pending and terminal operation ids are unique and disjoint, terminal entries exclude unfinished outcomes, and terminal logs only grow by suffix append. An accepted terminal event occurs exactly once and persists exactly once through every later accepted command sequence. Successful/rejected fresh terminals add exactly one true/false sample to their identity, while faults and events of other identities add none. The terminal log effect equals inherited `CalibrationLog.record`.

The model is pure. It does not authenticate an external source, certify complete host logging, prove arbitrary Python equivalence, or infer any statistical law from records.

## Development failures

- Build 01: using `unfold step` left dependent command-match branches, and the initial invariant theorem inherited an unused decidable-equality variable. Replaced unfolding with equation simplification and explicitly omitted the unused variable.
- Build 02: one begin branch needed state equality elimination before projection equality. Added explicit constructor equality elimination.
- Build 03: initial API passed.
- Build 04: unused equality variables in invariant helper theorems, a filter/map rewrite needed explicit function composition, and Lean 4.34 deprecated `if_pos`/`if_neg`. Explicit omissions, a typed filter identity, and current `ite_eq_left`/`ite_eq_right` names repaired these.
- Build 05: invariants and conflicts passed.
- Build 06: prefix reflexivity was not closed automatically after rewriting. Added explicit prefix reflexivity.
- Build 07: full module passed with no warnings.

A mathematical obstruction is preserved by `inherited_unfinished_terminal_conflict`: placing an unfinished event in the old terminal log permanently occupies its operation id, so the later terminal event is rejected. This is why the new machine stores pending intents separately.

All three new negative tests failed because Lean's kernel-backed `decide` proved the stated proposition false, not from missing imports, parser errors, or timeouts. Logs and invocation hashes are preserved in `recorder_FalseRecorder*.log/json`.
