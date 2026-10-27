# Pinned Lean import and private-declaration probes

These isolated tooling experiments use the recovered Lean 4.34.0-rc2 runtime.
They do not alter or add to Paper X production sources, objects or claims.
`IMPORT_SEMANTICS_REPORT.json` is the checked result; the raw JSON receipts bind
commands, source hashes, exit codes and complete output. The retained AuditCore
source is byte-identical to the October 19 checkpoint.

Two supplementary axiom-policy controls use actual new-module-format fixtures:

* `ProbeModuleGood` compiles and the unchanged legacy auditor accepts all 36
  owned declarations, including 18 names marked private and six declarations
  of kind inductive, constructor or recursor.
* `ProbeModuleBad` adds an unused private axiom. The fixture compiles, while the
  unchanged auditor enumerates 37 declarations, identifies that private axiom,
  rejects it and emits no completion marker.

These two controls are separate from the inherited eighteen-control suite and
from the 122 production modules.

Four import probes establish the relevant boundary:

* A new-module root with `import all ProbeModuleGood` sees the same 36 names
  and transitive axiom sets as the unchanged legacy auditor.
* Ordinary `import ProbeModuleGood` sees 21 declarations, omitting fifteen
  private declarations. It is insufficient for a full private-owner census.
* A new-module root rejects direct import of legacy `AuditCore`.
* It likewise rejects actual legacy production module `PaperX.Counting`.

The pinned Lean source paths and hashes in the report identify the import
propagation rules and the precomputed imported transitive-axiom summaries.
Consequently a simple `module` / `import all owner` wrapper is not a drop-in
replacement for this mixed legacy/new-module project. No alternate importer or
weaker policy was substituted for the production audit.

`RAW_RUNS.json` retains the successful fixture/tool compilations and an initial
wrapper error: `run_elab` expected a term elaborator rather than the command
elaborator returned by AuditCore. The exact failed wrappers and output are in
`failed_attempts/run_elab_wrapper/`. `RAW_AUDIT_RUNS.json` records the corrected
`run_cmd` wrappers and determines the two final policy-control results.

To repeat a recorded command after moving this directory, replace only the
recorded workspace paths with the new directory, external kit and production
object roots. The receipts record the complete `LEAN_PATH` and included
`compat/app_path.so` environment used for these executions. The fixture object
files and their private/server payloads are retained beside their sources.
