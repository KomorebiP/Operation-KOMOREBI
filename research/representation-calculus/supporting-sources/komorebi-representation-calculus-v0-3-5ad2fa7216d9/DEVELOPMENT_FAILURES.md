# Development and execution failures — v0.3

## Mathematical status

No counterexample to the accepted matrix adapter was found. This does not supply
external mathematical review. The general numerical minimum-free-coordinate
application was NOT completed; it remains an explicit obligation. The large
fixture's sharp bound was proved separately by a compact cardinality argument.

## Environment

1. Container DNS prevented downloading a toolchain from the attempted GitHub URL.
   The saved five-part runtime was retrieved from the user's Library instead.
   All chunk hashes and the concatenated archive hash matched their saved values.
2. Two whole-archive extraction attempts exceeded their enclosing execution limits.
   The core toolchain was recovered; full Mathlib cache restoration is not claimed.
   This release imports only Lean/Std, so it does not depend on that partial cache.
3. An attempted streaming container session returned StreamingExecNotEnabledContainerError.
   That invocation did not launch a usable streaming job. Work proceeded synchronously.

## Lean development

`development/matrix_core_01.log` records initial failures involving finite
indicator sums and names available in Mathlib but not Std. The accepted proof
uses explicit semiring laws and finite-index cases.

`development/matrix_certificate_01.log` records universe alignment, decidability
and deprecated subtype-equality issues. Independent universes, an explicit
Decidable instance and Subtype.ext resolved them. Subsequent incremental logs
record accepted MatrixCore, MatrixCertificates, MatrixSmith, shared row witness,
cardinality and generated large-example checks.

API probes outside the accepted project also tested unavailable Std names for
bijections and finite injection. They were not proof attempts counted as results.
The project instead proves the needed bijection and finite-pigeonhole helpers.

## Final audit interruption

The first long enclosing audit invocation was interrupted after 18 complete
module tasks had been checkpointed. It did not record a complete run. Subsequent
synchronous batches required identical accepted input hashes and exact toolchain
version. The unfinished next module was rebuilt. The final ledger records all
213 completed module builds, the complete axiom audit, and seven expected-outcome
controls. Only those completed tasks support PASS. Invocation and task records
are retained under evidence; no background process is presumed to remain running.

## Manifest classification failure

The validator initially rejected LEAN_MANIFEST.json because the auditor called
`evidence/LEAN_TASKS_PROGRESS.json` a scientific result, but that progress log was
not in declared_results. This was a metadata classification error, not a proof
failure. `tools/normalize_lean_manifest.py` changes ONLY that output kind to log,
retaining the raw manifest and a one-field correction record. It does not
post-declare a mathematical result, alter source hashes, or rerun/replace results.
Both final manifests then validated against the actual files.

## Deliberate rejected controls

BadEncoding, BadSmith, BadGrowthWitness and ReboundWrongSource are intentionally
corrupted symbolic exports. They bypass the Python prechecker so Lean itself must
reject the false concrete identities. False and Placeholder test basic proof
rejection. Positive checks the accepted large endpoint. These expected rejections
are not ordinary development failures; their exact diagnostics are saved.
