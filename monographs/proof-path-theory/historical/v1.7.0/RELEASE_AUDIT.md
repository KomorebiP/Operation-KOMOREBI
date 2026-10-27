# Release audit — Proof Path Theory 1.7.0

Publication 1.7.0 contains Python 1.5.0 and fresh formal evidence on the pinned
Lean 4.34.0-rc2 runtime. Read `FINALIZATION_REPORT.md` for the mathematical
extensions, failure record, verification scopes and remaining obligations.

The integrated release verifier rebuilds all 13 production modules and replays
them through Lean's own kernel against cached imports, runs 169 source tests
and the same suite against the installed wheel, executes the exact finite
comparisons, rebuilds the paper, and cross-checks the publication ledgers.
It fails rather than silently skipping an unavailable compiler or PDF build.

The complete release manifest is checked before any local command rewrites
reports. The final delivery receipt checks ZIP integrity, every extracted hash,
and exact member coverage. Hash checks establish file identity, not theorem
validity. Historical evidence remains separately dated. License selection and
independent review remain open.
