# LegalTrace development record

`MachineTheory/LegalTrace.lean` adds 4 definitions and 15 theorem declarations.
These are supporting declarations for the final clause of Core 8.2, not 15 new
source results or discovery claims.

The canonical partial execution returns `some states` exactly when every requested
action is enabled. Its state list contains the initial state and every successor.
The proved list length is the action-word length plus one, and its head is the
initial state. Arbitrary finite action words are covered by induction, without a
fixed testing bound. `Factors.execute_map` gives the complete projected state path,
`Factors.legal_iff` gives legality in both directions, `Factors.labels_eq` preserves
every protected label including the initial label, and `Factors.endpoint_map`
explicitly preserves the final state. `Factors.lift_execution` lifts a quotient
trace from any chosen representative of the initial state. No `Nonempty` instance
is required. `finite_legal_quotient_sequences` exposes the finite source setting.

Two interface-only probes preceded the production compile. In those probes the
announced `Factors.step_map` API was an explicit structure field assumption, not a
proved quotient theorem. They are not production verification evidence. The first
probe failed at the finite source-facing binder because its deliberately minimal
imports did not expose the `Finite` typeclass. The second probe added
`Mathlib.Data.Fintype.Basic` and passed. No generic trace proof failed in those
probes. The same explicit import is present in the production module.

The production compile then imported the actual proved `LegalQuotient` module and
passed on its first attempt with the pinned Lean 4.34.0-rc2 compiler, one worker,
4096 MiB memory option, and warnings treated as errors. Its exact source hash,
command, exit code, and elapsed duration are recorded in `trace_production01.json`.
After the main module appended its direct source bridge theorem, the unchanged
trace source was recompiled against that final main module and again passed;
`trace_production02.json` also records the imported main source hash.
This is a module compilation receipt only. The cumulative kernel replay, axiom
inventory, negative controls, cold rebuild comparison, and release verification
are separate release obligations performed by the coordinating agent.
