# Paper IX v0.4.0: Checked Fourth Block

**Author: Komorebi P.**

This continues the status-corrected Paper IX manuscript and the checked third block. It covers finite Mahler reconstruction, weighted differences and p-adic unit modes.

## Recorded scope

- 17 of 24 named manuscript-proved items checked; seven pending.
- 272 explicit theorem declarations, 60 explicit definitions, 21 modules.
- New this block: three manuscript items (7.2, 7.3, 7.4), 53 supporting/main theorems and seven definitions in four modules.
- Three classical inputs and two conjectures remain separately tracked.

Read `docs/Paper_IX_Fourth_Lean_Block_Supplement.pdf`, `docs/Paper_IX_Fourth_Block_Ledger.md` and `docs/Paper_IX_Fourth_Block_Amendments.md`. The original manuscript and earlier supplements are preserved, so the amendments are part of the current reading contract.

## Run

Requires the separately supplied Linux x86-64 portable Lean kit (Lean 4.34.0-rc2) with the pinned Mathlib cache. No runtime binary is included in this source archive.

```bash
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Python 3.10+ is required. The launcher runs the unit suites and independent exact mirrors, then creates a new build directory, compiles every active module with warnings as errors, checks all declared dependency pins and explicit declaration axioms, and rejects deliberately invalid proof controls.

For only the Lean checks:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The corresponding recorded successful run is in `verification/fourth_release/`. Repeating verification adds a new run; it does not overwrite the preserved evidence. `MANIFEST.json` covers distributed files, not newly created verification directories. Verify it with `python3 scripts/check_manifest.py`.

## Evidence boundaries

Actual checked facts use the iterated forward-difference operator, finite binomial interpolants, completed p-adic integers, the residue field and its kernel. Zero is assigned infinite valuation. A finite sample determines a difference only on its contained forward stencil. Pinned Mathlib supplies the Gregory-Newton formula, binomial-difference identities, p-adic structure and finite-field Fermat theorem; these imported results were not rebuilt from source.

The independent Python programs are exact-rational mirrors, not executable extraction of Lean functions or universal proofs. Historical paper experiments were not rerun. Convergence for infinite Mahler expansions, the global Euler difference theorem, and the remaining conjectures are not certified by this block.

All 17 upstream proof files and the three previous mathematical supplements remain unchanged. Original metadata and tests are saved under `provenance/third_block/`; historical version-specific assertions in the active test suite use those immutable snapshots, while current release counts and scope are checked separately.
