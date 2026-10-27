# Final-edition verification summary

Frozen mathematical source: Sufficient Resolution v0.16.0. Edition date:
6 October 2026. Current machine-readable status is
`../verification/CURRENT_RELEASE_VERIFICATION.json`.

All **93 production Lean proof files** are preserved byte-for-byte. The source
inventory remains **998 theorem/lemma declarations and 1,159 enumerated names**.
These include helpers, definitions, examples and specializations.

Fresh finite verification reproduced **all 16 Python companion suites** with
zero failed suites. Their native counters report **40,466 assertions**, plus
five fixed sanity groups containing six main mathematical `assert` statements.
The suites explicitly report **1,073 rejected controls**. Additional obstruction
examples are checked within the positive assertion counters. These counts are
implementation evidence, not theorem counts or a mathematical completion
percentage.

Sixteen bounded version-2 computation manifests and one separate source/runner
manifest passed full schema, input-freshness and output-hash checks. Runs use
exact rational arithmetic and selected independent exact algebra comparisons.
They do not formally verify Python, JSON parsing, or universal mathematical
claims.

The repaired generic verifier now discovers and topologically orders all 93
production modules. Source-only checks verified all 118 project import edges,
93 preservation hashes, exact declaration inventory, missing-dependency and
cycle rejection, shell syntax, and refusal to proceed without a runtime.

**No fresh Lean compilation, transitive axiom audit, or proof-kernel replay was
performed for this edition.** The matching runtime was absent. Both the initial
materialization and the independently prepared bounded retry of compact chunk
01 failed with HTTP 502. The runtime and imported Mathlib cache are not bundled.
This was an environment/retrieval failure, not a mathematical counterexample.

The inherited v0.16.0 main and separate-tree records each passed a fresh
31-module dependency compilation plus block root, 52 new-name transitive axiom
audits, and 31 same-kernel replays. All allowed axioms are `propext`,
`Classical.choice`, and `Quot.sound`. Imported pinned Mathlib compiled objects
were reused. Neither inherited run is a full fresh 93-module build, and
`leanchecker` is not an independently implemented kernel.

Portable replay prerequisites and exact commands are in `PORTABLE_REPLAY.md`.
The original top-level metadata is retained under `inherited_provenance`.

The release root `AxiomAudit.lean` is regenerated from all **1,159** current
registry names. Source-only correspondence checks verify unique complete
coverage. The original 1,010-command wrapper is preserved under inherited
provenance. Regeneration is not a fresh transitive axiom audit.
