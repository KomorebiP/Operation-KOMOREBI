# Paper IX — second checked Lean block

**Author: Komorebi P.** · Release **0.2.0**

## Result

**10 of 24 named manuscript-proved items have formal coverage. Fourteen remain pending.** Three classical inputs and two conjectures are tracked separately. The cumulative project has **163 explicit theorem declarations and 37 explicit definitions in 13 modules**. This block adds 74 theorems and 15 definitions in five modules. All eight first-block proof files are unchanged.

The new coverage is **4.1, 4.2 and 4.3**: the actual odd-power generating function and its even part, the exact Euler reconstruction formula, and the uniform integer congruence ladder. The signed zigzag coefficient bridge is proved using the actual formal sine, cosine, secant and tangent series. It is not assumed. These identities hold for every positive odd integer length, with the manuscript's odd-prime statement as a specialization.

The original 28-page status-corrected manuscript and first supplement remain unchanged. This is a formalization companion, not a rewritten or completed Paper IX.

## Reading and evidence

- `docs/Paper_IX_Second_Lean_Block_Supplement.pdf`: six-page mathematical explanation.
- `docs/Paper_IX_Second_Block_Ledger.md` and `coverage.json`: precise coverage and remaining items.
- `verification/Paper_IX_Second_Block_Verification.json`: authoritative clean cumulative run, also retained with raw logs under `verification/second_release/`.
- `verification/second_exact_regressions.json`: independent exact-arithmetic checks.
- `verification/second_unit_tests.log`: 33 passing infrastructure and release tests.
- `DEVELOPMENT_NOTES.md`: failures, preliminary runs and provenance boundaries.

The clean run rebuilt all 13 local modules with warnings treated as errors, matched all 200 expected axiom reports, checked all nine dependency revisions, and rejected five negative proof controls. Allowed transitive axioms are `propext`, `Classical.choice` and `Quot.sound`. Counts cover explicit project declarations, not all automatically generated declarations or imported Mathlib theorems.

## Reproduce

Requirements: Python 3.10+, Linux x86-64 (or a compatible WSL environment), and the separately extracted Komorebi portable Lean kit. The runtime is not included in this ZIP. Pins: **Lean 4.34.0-rc2**, **Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. Full dependency pins are in `provenance/dependency_pins.json`.

```bash
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

This runs the unit tests, both independent exact-arithmetic regression suites and a fresh cumulative Lean build. Separate commands:

```bash
python scripts/check_manifest.py
python -m unittest discover -s tests -v
python scripts/regressions.py
python scripts/second_regressions.py
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

No network access is needed once the exact kit is present. The verifier refuses to reuse an existing run directory, validates active source and manuscript hashes, checks the unchanged upstream sources and target coverage, and builds in dependency order. It does not alter global environment settings or the kit. Native Windows execution was not tested.

## Mathematical boundaries

The new assertions are formal power-series and coefficient statements. No new analytic convergence theorem is claimed. The zigzag convention is defined by coefficients of the actual formal `sec + tan` series; no additional theorem counting alternating permutations is claimed.

The truncation bound is divisibility **in the integers**, not in a field. The exact manuscript example has Euler value 1385, depth-two truncation 2731001385, and error -2731000000. Lean proves divisibility by 5^6 and nondivisibility by 5^7. A second checked counterexample shows that odd length cannot be dropped. Negative controls also retain the original normalized finite-difference boundary.

The weighted dyadic reconstruction and corrected global finite-difference theorem remain pending. Three classical inputs and both conjectures remain outside the covered register. Neither the historical numerical suite nor Papers I–VIII were rerun. Mathlib's pinned compiled cache was reused, not independently rebuilt. The Python regressions are independent mirrors, not Lean-extracted executables or replacements for universal proofs.

No Lean build products or runtime binaries are distributed. Observed build hashes remain in the run report; future compilations need not produce byte-identical binaries. Manuscript-to-Lean correspondence is a mathematical review, not an automated semantic-equivalence theorem.
