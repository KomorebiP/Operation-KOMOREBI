# Komorebi Paper I completion, Block 08

Version 0.8.0, 12 October 2026. The nonsplit semisimple formulas and compatible abstract decompositions are verified. The expanded monograph is not entirely formalized.

Start with COMPLETION_REPORT.md for exact scope and observed checks, PROOF_GUIDE.md for the constructions, coverage/COVERAGE_108.md for each publication record, and CONTINUE_HERE.md for the next restart. VERIFICATION.json points to the hashed accepted command receipt.

## Layout

`source/current/` is a flat, byte-identical copy of all 54 production source modules. `source/extension/` contains the eight newly compiled modules. `predecessor/` is the complete unchanged Block 07 package, including historical sources, evidence and license records. `tests/` contains the new exact boundary suite, intentionally invalid controls and audit instrumentation. `evidence/` preserves accepted logs/objects, source snapshots, development failures, identity checks and receipts. `audit/` explains semantic and trust boundaries.

## Reproduce the accepted audit

From Linux or WSL with Python 3 and the pinned offline runtime:

    bash scripts/run_block08.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output

The output directory must not already exist. Do not run `lake update`. Runtime binaries and the large upstream dependency cache are external prerequisites, not embedded in this source/evidence archive. The runner freshly compiles the eight additions, authenticates 46 predecessor source/object pairs and replays the entire logical project closure from upstream-only imports. It does not rebuild every predecessor source or Mathlib.

The development recorder `scripts/devrun.py` retains its original session-specific environment path for provenance. It is not the portable reproduction entry point; use the shell launcher above.

All mathematical constructions are noncomputable. No executable decomposition/eigensolver, external independent verifier or full-monograph completion is asserted. Existing publication license-status records are inherited without a new license selection. Publication PDFs were not rebuilt.
