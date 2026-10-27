# Development failures — v0.7

1. The first enclosing warmup command hit its 20-second tool limit. No complete
command receipt was retained for that invocation. No process remained running.
The dependency was rerun separately and completed; it was also rebuilt in the final
cold audit. An unrecorded or partial invocation is not counted as successful evidence.

2. Five draft checks failed before correction: two EchelonNormalize checks
(elaboration/definitional rewriting and an unused simp argument under warnings as
errors), one EchelonCanonical check (simplification changed a membership goal),
one EchelonModularNormal check (an unnecessary namespace open), and one
NormalizedExamples check (a missing closing bracket). The final accepted sources
correct these issues without adding assumptions or weakening mathematical scope.
An API probe also tested names that were absent; its output is retained separately.

3. The retained cold audit and exact Python audit are the evidence of completion.
No field-rank approximation, modular nonunit division, or false membership flag
was used to repair these development failures. The negative controls are intentional
invalid claims and not solver counterexamples.

4. Runtime restoration completed with exit zero. Optional static/native artifacts
were excluded while required Lean/Mathlib execution artifacts were restored.
The compiler hash, reported version, Mathlib metadata pin, and selected exact source
hashes were checked. This is reuse of the pinned compiled cache, not a Mathlib rebuild.

5. After all 44 cold proof builds and five axiom groups passed, axiom group 05
reached its 90-second wall cap. The complete failed state and original driver log
are retained in v07_evidence/protocol_revision/. The uncompleted axiom groups were
split from at most 160 names to at most 80 names. All mathematical source, prior
artifact and completed-log hashes were verified unchanged before resuming. The
failed check is not counted among successful tasks. The revised plan still covers
every declaration and all negative controls.

6. The 80-name group 06_split1 also hit the same cap. A module-mode import probe
passed, and all unfinished audit/control drivers were changed to module-mode
imports while keeping the same standard #print axioms calls and declaration
inventory. No mathematical source or completed build changed. The second failed
state and full revised plan are preserved. The final records count only completed
expected outcomes, not either timed-out attempt.

Any later packaging or extraction failure must be appended with its actual outcome.
