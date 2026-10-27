# Failures and corrections — v0.2

Failures are separated from the completed final cold audit. Incremental logs in
evidence/development include failed and successful checks; empty logs generally
correspond to successful compilation, not a missing proof claim.

## Runtime/setup

The Python zstandard package was absent. A package-install attempt failed with
DNS errors. The existing zstd executable was used instead. A streaming-session
request returned StreamingExecNotEnabledContainerError. Two foreground extraction
calls timed out. Subsequent explicitly tracked bounded restoration processes were
observed through completion during this interaction; none is left running as a
pending verification claim.

Source restoration exited zero. The optional dependency-cache extraction returned
status two because its broad selection named absent optional Plausible members.
That command is NOT reported as wholly successful. The required runtime and actual
imported caches were present and supported both smoke checks and the full strict
library audit. Actual source/cache restore logs are retained under evidence/runtime.
The terminal-only package/session messages are described here, not reconstructed
as fabricated raw logs. The multi-gigabyte runtime is not part of the release.

## Lean development

* StateTerm initially used `variable`, a reserved word, as a field. It now uses index.
* An initial Structure.funMap pattern treated its implicit arity as explicit. The
  accepted definition uses a dependent lambda matching the actual Mathlib API.
* Several semantic proof statements needed explicit local Structure instances to
  bind S and K. Accepted statements and proof bodies name that exact model.
* Reducibility, unused-simp and local-let lints were corrected rather than disabled.
* The graph proof required Fin 3 annotations for numeric literals and extensional
  equality of empty assignments instead of assuming different syntactic lambdas
  were definitionally identical.
* A composed quotient theorem required its actual behaviorSetoid explicitly.
* Back-and-forth and rank proofs required explicit induction/rewrite alignments.

These are implementation/elaboration failures, not counterexamples to the retained
mathematical statements. Separate EXPECTED NEGATIVE controls deliberately assert
false binder, rank, relation, old state-equality and quantified-surjectivity claims,
and a sorry placeholder. All must reject in a successful final audit.

## Verification limitations

The final Lean and Python audits complete successfully with unchanged accepted
input hashes. They are distinct from restoration attempts and intermediate checks.
Upstream Mathlib cache use is not a cold rebuild of Mathlib. Python and documentation
remain outside executable/formal semantic verification. Review is self-review.
