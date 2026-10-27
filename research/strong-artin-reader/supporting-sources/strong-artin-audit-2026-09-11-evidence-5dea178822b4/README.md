# Strong Artin audit evidence, 11 September 2026

Read `AUDIT_REPORT.md` first, then `AUDIT_SUMMARY.json` for machine-readable scope.

- Current v0.25 ancestry: 741 theorem/lemma declarations in 128 unique source files.
- Available all-branch union: 960 declarations in 178 unique source files. This is not one compiled release.
- Fresh v0.25 replay: 17 source modules plus all-new-constant axiom audit, PASS.
- Expanded ancestry attempt: 30 additional source modules passed, but the whole-ancestry run remained incomplete.
- Exact counterexamples test application shortcuts, not Strong Artin or the correctly stated conditional Lean theorems.

`source_blobs/` contains original active source snapshots deduplicated by exact SHA-256. `inventory.json` records branch provenance. No source theorem is modified here.

`tools/inventory.py` reads supplied `Strong_Artin_Lean_v*.zip` files under `/mnt/data`. Its root constants can be edited for local use. `tools/negative_checks.py` uses only the Python standard library. The v0.25 verifier requires the original release directory and exact portable Lean kit; the large kit is deliberately not bundled.

This is a self-audit, not an independent expert review. Do not interpret source counts or partial replay logs as a complete end-to-end automorphy proof.
