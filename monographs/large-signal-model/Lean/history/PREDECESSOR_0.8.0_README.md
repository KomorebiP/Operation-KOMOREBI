# Komorebi Large Signal Model — Lean 0.8.0

A cumulative formalization of frozen **Foundations 1.0.0**, with **30 of 87 proposition mappings complete** and 57 unformalized. This is not Lean 1.0, and version numbers are not percentages. Production PR-LASM 2.3.0 is unchanged.

The current block formalizes strong fixed-horizon refinement, typed defect propagation, stable recursive memory, nonlinear packet truncation and coherent atlas reconciliation. Read `LEAN_GUIDE.md`, `COVERAGE.md`, `PROGRESS.md` and `AUDIT.md` before using the results. `ROADMAP_1.0.json` accounts for every remaining proposition.

## Reproduce the checks

Use a fresh extraction. Integrity checks must run before Python caches, compiled objects or reports are generated.

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The final command removes this project's compiled objects and sequentially compiles every module with warnings as errors, audits explicitly named declarations, replays the project modules through the pinned upstream Lean kernel routine, runs all isolated negative controls and verifies the source snapshot. It does not reuse a saved PASS. Logs are written to `.verification-run/` by default. The packaged source-candidate evidence remains under `verification/release_run/`.

The runtime is a separate Linux x86-64 kit with Lean 4.34.0-rc2 at commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` and Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency revisions are checked. The runtime and dependency binaries are not redistributed in this ZIP. Python uses the standard library for the verifier. `Check.ps1` is a supplied WSL launcher, not a tested native Windows build.

## Trust and counting boundaries

There are 67 active proof modules, 1,178 explicitly named declarations and 904 named theorems. Of the theorems, 613 are foundations/supporting results and 291 occur in example modules. The count is not a novelty measure. Coverage counts refer to the separately reviewed statements in the frozen manuscript, not to source-line volume.

Axiom dependencies are checked against `propext`, `Classical.choice` and `Quot.sound`. The module replay uses Lean's own implementation, not a second independent prover. Imported Mathlib is pinned but not exhaustively rebuilt or freshly replayed. The kernel does not read the English mapping or authenticate observations.

The package contains the unchanged immediate predecessor archive, not redundant top-level copies of every older archive. Historical reports keep their versions and original outcomes. Use the separate delivered extraction-verification JSON for the actual checks on this exact ZIP. No publication, license change, empirical model training or production-code verification is claimed.
