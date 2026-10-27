# Paper IX v0.6.0 — checked sixth block

**Author: Komorebi P.**

This source-and-evidence release continues the unchanged 28-page status-corrected Paper IX. It adds the companion-jump theorem (9.1) and the Fibonacci packet recurrence (9.2).

## Verified scope

**22 of 24 named manuscript-proved items are covered.** The cumulative source inventory has **382 theorem declarations and 84 explicit definitions in 31 modules**. This block adds 49 supporting/main theorems and seven definitions in three modules. These are not counts of independent mathematical discoveries.

The remaining manuscript items are **7.5**, the corrected global odd-prime finite-difference theorem, and **8.5**, the uniform standard-window period. Three classical inputs and two conjectures are tracked separately. No statement about those pending results is promoted by this release.

The characteristic recurrence has order at most the state dimension, not necessarily minimal order. The general theorem is over a commutative ring and includes singular matrices, empty state spaces, zero steps and arbitrary offsets. The Fibonacci sequence is Mathlib's `Nat.fib`; Lucas numbers are independently defined by their ordinary recurrence. No eigenvalue, Binet-formula or desired recurrence hypothesis is assumed.

## Read first

- `docs/Paper_IX_Sixth_Lean_Block_Supplement.pdf`: six-page mathematical development.
- `docs/Paper_IX_Sixth_Block_Amendments.md`: exact hypotheses, signs and endpoint conventions.
- `docs/Paper_IX_Sixth_Block_Ledger.md` and `coverage.json`: complete item-by-item scope.
- `verification/sixth_release/verification.json`: the fresh cumulative Lean build and axiom audit.
- `verification/sixth_unit_tests.log`: 131 passing infrastructure and release tests.
- `verification/sixth_regressions/`: independent exact finite checks, not Lean extraction.

The older manuscript, supplements and historical verification records remain available and are not relabelled as new runs. All 28 upstream proof files are unchanged.

## Run from a fresh extraction

The portable Lean runtime is separate from this small source bundle. Extract the offline kit and use its root directory, not a part ZIP. This release expects Lean **4.34.0-rc2** and the nine package revisions in `provenance/dependency_pins.json`.

```bash
python3 scripts/check_manifest.py
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The launcher runs all 131 unit tests, all six independent finite regression programs and a clean cumulative Lean build. Each build starts with a new local output directory. It audits all 466 explicit declarations and runs 20 invalid-proof controls with warnings treated as errors. Logs are written under `verification/`. A missing import, timeout or compiler panic does not count as a valid negative control.

For only the proof build:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

To rebuild the supplement, with pdflatex installed:

```bash
python3 scripts/build_sixth_supplement.py
```

## Trust and reproducibility boundary

Transitive axiom dependencies are checked against `propext`, `Classical.choice` and `Quot.sound`. The included source and diagnostic records can be inspected and rerun; the bundle contains no runtime installation or prebuilt project modules. Pinned Mathlib's compiled cache is reused, not independently reconstructed from source. Matrix polynomial results and the basic Fibonacci theory are imported classical mathematics, not new discoveries. The source-to-manuscript correspondence is mathematical review rather than a Lean theorem identifying informal prose with formal types.

The current pure-Python mirrors are rerunnable, but they are not extraction from Lean. The original historical numerical suite and Papers I–VIII are not rerun. No GPU timing, complexity, infinite p-adic convergence or minimal-polynomial claim is made. See `DEVELOPMENT_NOTES.md` for retained development failures.
