# Failure and recovery record

No failed or incomplete run is counted as a successful theorem check.

## Formal-development failures

The archive retains 11 completed unsuccessful Lean attempts: nine compiler,
linter, elaborator, or heartbeat failures, plus two process timeouts. There is
also one attempted-source snapshot from an invocation interrupted before its
completion receipt was written.

- PrecisionBudget initially needed explicit nonnegativity hypotheses, the finite
  sum distributivity import, and corrected absolute-value syntax. Broad inferred
  inequalities and automation exceeded a process cap. Explicit intermediate
  inequalities and restricted arithmetic automation made the final proof pass.
- One PrecisionBudget invocation was interrupted by the outer tool cap. Its
  orphaned process was stopped. It is not counted as a success; the final source
  subsequently passed a separate recorded check.
- PrecisionMatrix needed explicit entry indices in aggregate-budget statements.
- PrecisionScoreAlgebra carried unused section assumptions. They were removed.
- A RoundedPosteriorSound dependency run exceeded its 45-second cap while an
  inherited rebuild overlapped. The inherited sequential run later succeeded on
  the unchanged source. Only the successful receipt is used in the seal.
- HybridPosteriorSolver initially attempted substitution from an unextracted
  conjunction and used a deprecated if-rewrite lemma. Both were corrected.
- HybridPrecisionSchedule initially used the Lean keyword `prefix` as a binder.
  It was renamed `probes`.
- PrecisionBoundaryChecks needed an explicit empty-finset type and a more explicit
  application of the exact-candidate lemma to avoid elaboration expansion. Its
  final linter pass also required omitting unused packet equality instances.

Every one of the 83 final active modules has a successful receipt matching its
current source, output and direct dependencies. Full details and elapsed times
are in FINAL_VERIFICATION_RECEIPT.json and the immutable audit subdirectories.

## Tooling and restoration

The preceding interrupted assistant attempt was resumed from the retained v9
and v8 archives; its vanished temporary work was not treated as proof evidence.
The compact runtime was restored and its part and combined hashes verified.
Streaming terminal sessions were unavailable, so ordinary bounded processes and
recorded polling were used.

The inventory parser initially rejected Lean's permitted implicit EOF closure
of a top-level noncomputable section. It now tracks nested namespaces and sections,
allows only top-level section closure at EOF, checks every per-file declaration
count, and obtains inherited names from preserved inventories. The full emitted
axiom audit compiled and covered every one of the 386 declarations.

The official Mathbox manifest-validator executable was not present. The packaged
project verifier checked final-source receipt provenance, output and dependency
hashes, declaration coverage, and allowed axiom sets instead. It is not described
as an official-validator run.

## Negative controls

Three separate deliberately invalid Lean test inputs were correctly rejected:
a false natural-number equality, a placeholder proof, and an enclosure claim that
dropped a nonzero rounding radius. Those isolated inputs are under
results/negative_controls, not in active Komorebi proof sources.

All Python results are provisional until their exported Lean instances compile.
The examples included here have completed that additional check. Resource-capped
Python runs report RESOURCE_LIMIT and cannot export success theorems.

After regenerating the example exports from the final producer, a seal attempt
was made before their replacement axiom audit had finished. It correctly rejected
the now-stale audit dependency receipt. The final seal was performed only after
the replacement audit completed and the dependency hashes matched again.
