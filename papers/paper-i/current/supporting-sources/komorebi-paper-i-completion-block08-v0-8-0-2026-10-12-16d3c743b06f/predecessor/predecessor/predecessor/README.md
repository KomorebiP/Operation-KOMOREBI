# Paper I completion Block 05 — v0.5.0

The new geometric-multiplicity corollary is verified for arbitrary finite-dimensional operators over algebraically closed fields, including non-diagonalizable operators. The expanded monograph is not yet fully formalized.

Read `docs/COMPLETION_REPORT.md` for actual results and trust boundaries, `docs/PROOF_GUIDE.md` for the mathematics, and `CONTINUE_HERE.md` for the exact restart. `VERIFICATION.json` points to the hashed accepted command receipt. `coverage/COVERAGE_108.md` tracks every publication record. `PROGRESS_LEDGER.md` records continuity.

## Reproduce

From Linux or WSL with Python 3 and the exact external portable runtime:

```sh
bash scripts/run_block05.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output
```

The output path must not already exist. Do not run `lake update`. The launcher authenticates the predecessor source/object bytes and exact runtime bindings, freshly compiles four new modules, and replays all 37 current production modules serially. Cached upstream dependencies are reused. This is not a fresh all-source/dependency rebuild or an independent verifier.

## Package contents

`predecessor/` is the full unchanged Block 04 package, including earlier sources and evidence. `source/extension/` contains the new mathematical modules. `tests/` includes exact theorem consumers, source-owned gates, replay wrapper, and deliberately invalid fixtures. Invalid fixtures and failed development snapshots are evidence, not production source. `evidence/final_audit/` contains the accepted isolated objects, logs, snapshots, types, and ownership inventory. Other evidence folders preserve unsuccessful or exploratory attempts with explicit status indexes. `scripts/` contains verification and handoff tooling. The large Lean/Mathlib runtime is external.

Mathematical declarations are noncomputable specifications and proofs, not an executable eigensolver or canonical-form algorithm. Prior license-status records are inherited unchanged. No new publication license is selected here.
