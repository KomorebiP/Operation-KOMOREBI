# Continue here — Large Signal Model Lean 0.9.0

Current coverage: 35 complete, no partial, 52 unformalized, out of the unchanged 87-proposition frozen target. Block 9 completed P14–P17 and P25.

Next mathematical target: P45, exact rational certificate search. Read its full frozen statement and all surrounding hypotheses before designing an enumerator. Prove the certificate objects, checking predicates and the precise termination condition. Do not replace a search theorem with classical existence. After that, P32–P34 are the remaining linear-identification/stability track.

The accepted source-candidate proof evidence is `verification/block9_release_run/report.json`. The external delivery JSON identifies and verifies the exact ZIP. Read `AUDIT.md`, `LEAN_GUIDE.md`, `COVERAGE.json`, `ROADMAP_1.0.json` and `PROGRESS.md`.

All 67 predecessor proof files, 1,178 predecessor declaration records and 62 controls are preserved. Failed development invocations and source snapshots are in `verification/development_block9/`. The two frozen theory source files are unchanged. Publication metadata corrections are recorded separately in `PUBLICATION_STATUS.md`.

Use the pinned runtime. Verify the archive manifest before generating caches or reports. Do not count a missing-import failure as a negative-control rejection. Axiom policy and warnings-as-errors remain unchanged.
