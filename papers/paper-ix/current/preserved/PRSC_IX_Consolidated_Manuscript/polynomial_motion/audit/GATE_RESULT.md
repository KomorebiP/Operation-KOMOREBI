# First-order root motion gate result

PASS: 58/58 stages, 214.301 seconds.

- 35 mathematical modules compiled from source, including five new motion modules.
- Four positive control modules and nine statement contract modules compiled.
- Seven mathematically invalid controls rejected with the expected type mismatch.
- All 326 explicit declaration closures audited: 266 theorems, 56 definitions,
  and four abbreviations. Only the listed standard axioms were used.
- All 30 inherited mathematical sources remained byte-identical to the previous
  weighted release. All 240 compiled output files were hashed and reconciled.
- Independent raw-proof review and gate provenance reconciliation both passed.

The five new mathematical modules contain 13 theorems and one definition.
Control and contract declarations are included only in the complete audit totals.

Report SHA-256: `9e9ae0bb55d991f7c60b43b48fcdbfdee5aff3565e54e426e434870e95d7c243`.
Inventory SHA-256: `ae7a30f5f372e651b13aa6ab71707659f9e7054accadaba4d10264eec71595cb`.
Reconciliation SHA-256: `dbd67dd5fbbd50583e356c780943c066b29308595712737803f6002be745709d`.

The full report and raw compiler logs are in `verification/` in the release.
The gate started with an empty project build directory. The pinned Lean kernel
and precompiled Mathlib dependencies were reused, as stated in GATE_PROTOCOL.md.

The computation manifest passes the supplied version 1 schema validator when
its artifact root is the fresh gate output directory. An initial validation
call supplied the source directory instead and failed to locate the report;
that invocation and corrected result are preserved in dev/gate_manifest/.
This was an artifact-path validation error, not a Lean proof failure. Version 1
manifest limitations are recorded by the validator; exact source hashes,
commands, output hashes, and timeouts are recorded in the separate gate report.
