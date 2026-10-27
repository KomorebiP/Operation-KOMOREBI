# Paper IX v0.7.0 — checked seventh block

**Author: Komorebi P.**

This source-and-evidence release continues the unchanged 28-page status-corrected Paper IX. It proves the standard-window period (8.5) directly over the finite field, independently of the still-pending global higher finite-difference theorem (7.5).

## Verified scope

**23 of 24 named manuscript-proved items are covered.** The cumulative inventory has **439 theorem declarations and 94 explicit definitions in 38 modules**. The seven new modules add 57 theorem declarations and ten definitions. These counts include supporting lemmas, exact examples and explicitly conditional implications, not independent mathematical discoveries.

The sole remaining registered item is **7.5, the global odd-prime Euler finite-difference theorem**. Three classical inputs and two conjectures remain separately tracked. In particular, neither the Dwork-flatness criterion nor the factorial-loss transfer theorem asserts its hypothesis for the whole Euler family.

The new period concerns the independently constructed Lucas-reduced inverse and the actual integral lifts of the rational standard-window coefficients. Its assumptions are primality, m dividing p-1, and positive row n. It proves a period, not the least period. All primes, including 2, are covered. The higher-difference consequence supplies one power of p; it is not the full min(k,m*n) precision.

## Read first

- `docs/Paper_IX_Seventh_Lean_Block_Supplement.pdf`: six-page mathematical development.
- `docs/Paper_IX_Seventh_Block_Amendments.md`: the replacement period proof and the precise global boundary.
- `docs/Paper_IX_Seventh_Block_Ledger.md` and `coverage.json`: complete coverage register and separate partial targets.
- `verification/seventh_release/verification.json`: clean cumulative Lean build, exact source hashes and axiom audit.
- `verification/seventh_infrastructure/tests.log`: 162 passing infrastructure/release tests.
- `verification/seventh_regressions/`: independent exact finite checks, not Lean extraction.
- `provenance/global_argument_source/`: unchanged 18-page supporting prose proof for the remaining global theorem. Its title's word “formal” does not mean kernel-checked Lean.

The original manuscript, six earlier supplements and 31 upstream active proof files remain byte-identical. Prior failed and successful runs retain their original statuses. Current metadata, verifier controls and tests were extended; historical census tests read frozen snapshots instead of being counted against later totals.

## Repeat the checks

The portable runtime is separate from this source bundle. Use the extracted kit root, not a part ZIP. The required version is **Lean 4.34.0-rc2**, with the nine package revisions recorded in `provenance/dependency_pins.json`.

```bash
python3 scripts/check_manifest.py
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The launcher runs all 162 unit tests, the seven cumulative independent regression programs, and a clean cumulative Lean build. The build audits all 533 explicit declarations and executes 23 invalid-proof controls with warnings treated as errors. Missing imports, timeouts and compiler panics do not count as successful rejection controls. Run outputs are created under `verification/` without overwriting the frozen evidence.

For only the proof build:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

For document rebuilding, with pdflatex installed:

```bash
python3 scripts/build_seventh_supplement.py
```

## Trust and limitations

The transitive axiom allowlist is `propext`, `Classical.choice`, and `Quot.sound`. The package contains source and run evidence, not the runtime or prebuilt local proof modules. The pinned Mathlib cache is reused, not independently rebuilt. The independent Python mirrors are not extracted Lean programs.

The higher-power, all-residue global estimate remains pending. The 4,096 exact finite tests of that estimate in this block are observations, not a universal proof. No least-period, infinite interpolation, new hardware performance, or quantum-spacetime conclusion is claimed. Papers I–VIII and the original historical numerical suite were not rerun. Manuscript-to-Lean correspondence is mathematical review, not an automatically checked equivalence between prose and formal types.

A separate accompanying release audit records archive CRC/hash checks and the fresh-extraction launcher replay. See `DEVELOPMENT_NOTES.md` for failed development checks, infrastructure corrections and recovery limitations.
