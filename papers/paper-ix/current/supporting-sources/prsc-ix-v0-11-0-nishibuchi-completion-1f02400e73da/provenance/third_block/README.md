# Paper IX — third checked Lean block

**Author: Komorebi P.** · Release **0.3.0**

## Result

**14 of 24 named manuscript-proved items now have formal coverage. Ten remain pending.** Three classical inputs and two conjectures are tracked separately. The cumulative corpus contains **219 explicit theorem declarations and 53 explicit definitions in 17 modules**. This block adds 56 theorems and 16 definitions in four modules. All 13 upstream proof files remain unchanged.

New coverage is **5.1–5.4**: dyadic integrality of the actual reciprocal coefficients, integrality of the explicit even source, the exact weighted Euler reconstruction identity, and uniform truncation modulo powers of two in the actual completed integer ring `ℤ_[2]`. The source result is strengthened to unit status: its rational 2-adic valuation is exactly zero, and its embedded value is proved invertible in `ℤ_[2]`.

The original corrected manuscript and both earlier supplements remain unchanged. This is a formalization companion, not a rewritten or completed Paper IX.

## Reading and evidence

- `docs/Paper_IX_Third_Lean_Block_Supplement.pdf`: mathematical construction and exact boundaries.
- `docs/Paper_IX_Third_Block_Ledger.md`, `coverage.json`: coverage and remaining items.
- `verification/Paper_IX_Third_Block_Verification.json`: clean cumulative build, also present with raw logs under `verification/third_release/`.
- `verification/third_exact_regressions.json`: independent exact-rational dyadic checks.
- `verification/third_first_suite_replay.json`, `verification/third_second_suite_replay.json`: fresh replays of the earlier independent Python mirrors.
- `verification/third_unit_tests.log`: 49 passing infrastructure and release tests.
- `verification/third_development/`: all 15 captured development checks, including the eight failures before repair.
- `DEVELOPMENT_NOTES.md`: engineering history and trust boundaries.

The clean release build compiled all 17 local modules with warnings treated as errors, matched all **272 expected transitive axiom reports**, checked all nine dependency revisions and rejected all eight invalid-proof controls. The reported axioms are restricted to `propext`, `Classical.choice` and `Quot.sound`. Explicit declarations are counted, not all generated declarations or imported Mathlib theorems.

## Reproduce

Requirements: Python 3.10+, Linux x86-64 (or compatible WSL), and the separately extracted Komorebi portable Lean kit. The runtime is not included in this ZIP. Pins: **Lean 4.34.0-rc2**, **Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. All dependency pins are recorded under `provenance/`.

```bash
python scripts/check_manifest.py
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The launcher runs all 49 unit tests, the three independent Python regression suites and a fresh cumulative Lean build. Separate commands:

```bash
python -m unittest discover -s tests -v
python scripts/regressions.py
python scripts/second_regressions.py
python scripts/third_regressions.py
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier refuses to reuse an existing output directory. It checks active source and original manuscript hashes, unchanged upstream sources, target coverage and compiler/dependency pins. It invokes the original bundled Lean with temporary local environment settings. No network is needed after the kit is present. Native Windows execution was not tested.

To rebuild the new supplement with a TeX installation:

```bash
python scripts/build_third_supplement.py
```

## Mathematical boundary

The beta coefficients are **ordinary** coefficients of the normalized reciprocal, not exponential coefficients. The proof constructs the reciprocal only after its constant term is proved to be one. It connects this reciprocal to the actual formal hyperbolic functions by multiplying through by the forced monomial; it does not invert the zero-constant series `sinh` as a power-series unit.

The source is the explicit rational formula `(3^(2*n+2)-1)/(4*(2*n+1)*(2*n+2))`. Its numerator and denominator valuations are derived, using the pinned Mathlib LTE theorem. The exact Euler identity is obtained from the proved source/reciprocal series product and coefficient extraction, with the genuine descending factorial. The 2-adic congruence is derived from that identity and the established integrality witnesses, not postulated as a premise.

The error bound is divisibility **in `ℤ_[2]`**, not vacuous divisibility in a field. A second theorem proves rational integrality of the error divided by `2^(2*M+2)`. Zero errors and full retention are included. The actual degree-eight example has valuations five at depth zero and fifteen at depth three, both proved from the definitions.

The unnumbered Bernoulli closed form for beta is compared in 48 finite regression cases but is not universally formalized here. Formal series identities do not add analytic convergence results. The corrected global odd-prime finite-difference theorem remains pending. The three classical inputs and two conjectures remain separately tracked.

The independent exact-rational mirrors passed 49 reconstruction rows and 2,548 truncation-depth cases through even degree 96. They are not Lean-extracted programs and are not the original historical numerical study. Papers I–VIII and Mathlib's entire source tree were not rebuilt. The pinned compiled Mathlib cache was reused.

No Lean binaries, compiled project modules or font files are distributed. Recompilations need not produce identical binary hashes. The saved sources, hashes and raw run reports define the verified snapshot. Independent review of the intended mathematical specification remains valuable.
