# AVOC v0.17.0 — development failures and repairs

Failures below are not counted as successful proof or negative-test evidence.
Historical v0.16 proof sources were not changed to repair this block.

## Environment and build

- An initial request for an interactive container session was unsupported. The
  work used bounded synchronous calls instead.
- Offline-runtime materialization was attempted before inspecting the mounted
  parts. The tool reported paths already existed. The existing seven parts were
  then assembled, checked against the published part/combined hashes and extracted.
- Two host-limited baseline build calls stopped while entering later modules.
  Unfinished targets were rerun after checking no child remained. Every final
  target has a return-code-zero current-source record; interrupted calls are not
  successes. External dependency caches were retained.
- The old payload manifest was initially checked after intentionally updating two
  runner scripts. That expected mismatch did not mean the input archive was
  corrupt. A later independent in-ZIP verification matched all 1,573 original
  payload hashes, and the current 81 inherited non-audit modules matched bytewise.
- A new `--index` path initially called mkdir on an existing build directory
  without exist_ok. It had already written the correct order, but the command
  failed. The directory operation was fixed and the index command rerun. It never
  deleted the existing outputs. Final collection checks all output hashes.

## Lean elaboration repairs

- Initial report-law proofs needed unused section instances omitted, corrected
  documentation placement around `omit ... in`, and a predictive-probability
  rewrite before reducing the silent-posterior equality.
- Record-update layout and proof-dependent option case equalities caused several
  first-pass workflow failures. The final proofs use explicit field goals and
  equality orientations after case splitting.
- The finite action pool, safe optimal-plan result and guarded model adapter
  needed explicit types/instances in several places. Deprecated tactic/lemma
  names were replaced rather than suppressing warnings.
- Finite rational examples initially failed to reduce Fin(3) sums or treated an
  expanded posterior as a different arithmetic atom. Explicit finite-index
  inequalities and separate RHS identities resolved those goals. No native
  evaluation proof shortcut was used.

## A convenience proof not delivered

An attempt to prove that the built-in JSON parser reduces on the literal
`["true"]` via rfl/decide did not succeed. It stalled at the parser expression,
not at the generic source-correspondence theorem. The proposed concrete catalogue
parsing equality was removed and is NOT claimed as a kernel-checked example.

The final release instead proves: every successful parser output is SourceParsed;
a SourceParsed catalogue preserves exact source correspondence under the new
workflow; and permitted admission has the exact parsing witness. Real parser
executions are exercised in the independent runtime/file tests. No native_decide
or extra evaluation axiom was substituted for the failed literal-reduction route.

## Verification tooling

The source scanner now distinguishes the domain action constructor `.admit` and
its pattern cases from the forbidden proof-placeholder tactic `admit`. Full
axiom auditing independently excludes sorryAx and native-evaluation axioms.
The new collector verifies substantive negative errors and all current hashes.

Retained first-pass logs are under `results/v0.17.0/development/`; final proof
and audit records are outside that folder. Not every transient edit was retained
as a separate source snapshot. The final source, commands, output hashes and
axiom reports are the reproducible evidence.
